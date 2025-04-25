"""Pytest plugin for generating WATS reports."""

import logging
import re
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Literal

import pytest
from _pytest.config import ExitCode
from _pytest.main import Session
from _pytest.nodes import Item
from _pytest.reports import TestReport
from _pytest.runner import CallInfo

from WSJF.models import (
    RootSequenceCallStep,
    SequenceCallStep,
    StepStatusCode,
    UUTStatusCode,
    WATSReport,
)
from WSJF.restclient import DEFAULT_REST_API_TOKEN_ENV_NAME, WATSREST

log = logging.getLogger(__name__)
# Note: --capture=tee-sys and uncomment this line to see the logs in the console
# Even if --log-cli-level is set to DEBUG, the logs will not be shown in the console
# Therefore we need to override the log level
logging.getLogger().setLevel(logging.DEBUG)


def _absolute_path(argvalue: str) -> Path:
    path = Path(argvalue)
    if not path.is_absolute():
        errmsg = f"Path {path} is not absolute."
        raise ValueError(errmsg)
    if not path.is_dir():
        errmsg = f"Path {path} is not a directory or does not exist."
        raise ValueError(errmsg)

    return path


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add command line options to pytest."""
    main = parser.getgroup("WSJF Plugin arguments", "A pluging that generates WATS reports")
    main.addoption(
        "--name",
        type=str,
        required=True,
        help="Name of the test sequence",
    )
    main.addoption(
        "--part-number",
        type=str,
        required=True,
        help="Part number of the unit under test",
    )
    main.addoption(
        "--serial-number",
        type=str,
        required=True,
        help="Serial number of the unit under test",
    )
    main.addoption(
        "--revision",
        type=str,
        required=True,
        help="Revision of the unit under test",
    )
    main.addoption(
        "--process-code",
        type=int,  # Hm... this might not fly well
        required=True,
        help="Process code for the test sequence",
    )
    main.addoption(
        "--machine-name",
        type=str,
        required=True,
        help="Name of the machine running the test",
    )
    main.addoption(
        "--location",
        type=str,
        required=True,
        help="Location where the test is being conducted",
    )
    main.addoption(
        "--purpose",
        type=str,
        required=True,
        help="Purpose of the test sequence",
    )
    main.addoption(
        "--operator-name",
        type=str,
        required=True,
        help="Name of the operator conducting the test",
    )
    main.addoption(
        "--report-save-path",
        type=_absolute_path,
        help="Path where to save the report. The path must be absolute and exist.",
    )

    rest_client_group = parser.getgroup("WATS plugin REST Client arguments")
    rest_client_group.addoption(
        "--base-url",
        type=str,
        help="Base URL of the WATS server. E.g.: https://company.wats.com",
    )
    rest_client_group.addoption(
        "--token-environment-variable",
        type=str,
        default=DEFAULT_REST_API_TOKEN_ENV_NAME,
        help="Name of the environment variable that contains the API token.",
    )


def _get_option[T](config: pytest.Config, option_name: str, typ: type[T]) -> T:
    """Get an option from the config and cast it to the specified type.

    `config.getoption` returns `Any | Notset`, which makes the type checker unhappy.
    Which makes me unhappy.

    This function assures that the option is the correct type and makes the type checker happy.
    Which makes me happy.
    """
    value = config.getoption(option_name, skip=True)
    if value is None:
        errmsg = f"Option {option_name} not found"
        raise ValueError(errmsg)
    if not isinstance(value, typ):
        errmsg = f"Option {option_name} is not of type {typ}"
        raise TypeError(errmsg)
    return value


def _get_optional_option[T](config: pytest.Config, option_name: str, typ: type[T]) -> T | None:
    """Get an optional option from the config and cast it to the specified type or return None.

    `config.getoption` returns `Any | Notset`, which makes the type checker unhappy.
    Which makes me unhappy.

    This function assures that the option is the correct type and makes the type checker happy.
    Which makes me happy.
    """
    value = config.getoption(option_name)
    if value is None:
        return None
    if not isinstance(value, typ):
        errmsg = f"Option {option_name} is not of type {typ}"
        raise TypeError(errmsg)
    return value


def pytest_configure(config: pytest.Config) -> None:
    """Called when pytest is configured."""
    # It would be nice of we could populate this as part of a test
    # instead of having the user specify it on the command line.

    # This is a bit of a hack.
    # If we just run `pytest --help`, pytest will crash because it of the calls to `_get_option` below.
    if config.getoption("help"):
        return

    name = _get_option(config, "name", str)
    part_number = _get_option(config, "part_number", str)
    serial_number = _get_option(config, "serial_number", str)
    revision = _get_option(config, "revision", str)
    process_code = _get_option(config, "process_code", int)
    machine_name = _get_option(config, "machine_name", str)
    location = _get_option(config, "location", str)
    purpose = _get_option(config, "purpose", str)
    operator_name = _get_option(config, "operator_name", str)

    # Handle optional arguments
    report_save_path = _get_optional_option(config, "report_save_path", Path)
    base_url = _get_optional_option(config, "base_url", str)
    token_environment_variable = _get_optional_option(config, "token_environment_variable", str)

    log.debug(f"Name: {name}")
    log.debug(f"Part Number: {part_number}")
    log.debug(f"Serial Number: {serial_number}")
    log.debug(f"Revision: {revision}")
    log.debug(f"Process Code: {process_code}")
    log.debug(f"Machine Name: {machine_name}")
    log.debug(f"Location: {location}")
    log.debug(f"Purpose: {purpose}")
    log.debug(f"Operator Name: {operator_name}")
    log.debug(f"Report Save Path: {report_save_path}")
    log.debug(f"Base URL: {base_url}")
    log.debug(f"Token Environment Variable: {token_environment_variable}")

    config.pluginmanager.register(
        WATSReportPlugin(
            name=name,
            part_number=part_number,
            serial_number=serial_number,
            revision=revision,
            process_code=process_code,
            machine_name=machine_name,
            location=location,
            purpose=purpose,
            operator_name=operator_name,
            report_save_path=report_save_path,
            base_url=base_url,
            token_environment_variable=token_environment_variable,
        ),
    )


class WATSReportPlugin:
    """Pytest plugin for generating WATS reports.

    what
    """

    def __init__(
        self,
        name: str,
        part_number: str,
        serial_number: str,
        revision: str,
        process_code: int,
        machine_name: str,
        location: str,
        purpose: str,
        operator_name: str,
        report_save_path: Path | None = None,
        base_url: str | None = None,
        token_environment_variable: str | None = None,
    ):
        """Initialize the WATS report plugin."""
        self.test_start_time = datetime.now()

        self.report_save_path = report_save_path
        self.base_url = base_url
        self.token_environment_variable = token_environment_variable

        self._report = WATSReport.factory(
            name=name,
            part_number=part_number,
            serial_number=serial_number,
            revision=revision,
            process_code=process_code,
            machine_name=machine_name,
            location=location,
            purpose=purpose,
            operator_name=operator_name,
        )
        self._step = self._report.root

    @pytest.fixture(autouse=True)
    def step(self) -> SequenceCallStep:
        """A fixture for accessing the current step.

        For each test, a new `models.SequenceCall` step is created. The test can use this fixture to add sub-steps.
        """
        if not isinstance(self._step, SequenceCallStep):
            # You shouldn't be able to end up here, unless your doing something funky.
            errmsg = "This should only be called once a test is running"
            raise RuntimeError(errmsg)
        return self._step

    @property
    def _root(self) -> RootSequenceCallStep:
        return self._report.root

    @pytest.hookimpl(wrapper=True)
    def pytest_runtest_protocol(self, item: Item, nextitem: Item | None) -> Generator[None, None, None]:  # noqa: ARG002
        """Pre test hook to handle the test start.

        See the pytest documentation for more information.
        """
        (file_name, _, function_name) = item.location
        # TODO: Why do we do this? Windows paths maybe?
        file_name = file_name.replace("\\", "/")

        self._step = self._root.add_sequence_call(name=function_name, path=file_name, version="1.0")

        test_start = datetime.now()
        yield
        test_end = datetime.now()

        test_duration = test_end - test_start
        self._step.set_total_time(test_duration.total_seconds())

    @pytest.hookimpl(tryfirst=True, wrapper=True)
    def pytest_runtest_makereport(self, item: Item, call: CallInfo) -> Generator[None, TestReport, None | TestReport]:  # noqa: ARG002
        """Post test hook to handle the test result.

        See the pytest documentation for more information.

        In this function, we:

        * Set the test result of the step
        * If an exception was raised, we set the error message to the exception type
          and include the stack trace in the `WSJF.models.Step.reportText` field.

        """
        result: TestReport = yield

        if call.when == "call":
            outcome = result.outcome
            if outcome not in ("passed", "failed", "skipped"):
                errmsg = f"Unexpected outcome: {outcome}"
                raise ValueError(errmsg)

            status = self._outcome_to_step_status_code(outcome)
            self._step.set_status(status)

            if status == StepStatusCode.FAILED:
                # Strip out ansi color codes from pytest error string to avoid them being included in the WATS report
                # Because the WATS client does not handle them correctly.
                # https://regex101.com/r/yK7pjy/1
                # TODO: Use a library for this?
                pattern = re.compile(r"(\x1B\[\d+(;\d+){0,2}m)|(\u001b\[\d+(;\d+){0,2}m)")
                result_error_message = pattern.sub("\xa0", result.longreprtext)

                result_error_message = self._exception_str_to_pre_html(result_error_message)

                # Depending on the size of the terminal, pytest adds separators to the error message.
                # Replacing them with 30 dash-space pairs to avoid overflow.
                result_error_message = re.sub(r"(_ )+_*", lambda _: "- " * 30, result_error_message)

                # Using assert, or pytest_check will raise an AssertionError. This is expected and we
                # should not add the stack trace to the WATS report.
                if call.excinfo is not None and not isinstance(call.excinfo.value, AssertionError):
                    # TODO: How does this work?
                    exception_without_ansi = pattern.sub("", str(call.excinfo.value))
                    self._step.errorMessage = exception_without_ansi

                    # It the test failed due to pytest.fail, we don't need to print the stack trace.
                    if not isinstance(call.excinfo.value, pytest.fail.Exception):
                        self._step.reportText = result_error_message

        return result

    def pytest_sessionfinish(self, session: Session, exitstatus: ExitCode):  # noqa: ANN201, ARG002
        """Called after the test session has finished.

        In this function, we:
        * Set the execution time of the entire test sequence
        * Set the report result and the `UUT.status` to the exit code

        If `--report-save-path` was provided, we save the report to the specified path.
        See `WSJF.models.WATSReport.save_as_json` for more information.

        If `--base-url` and `--token-environment-variable` were provided, we upload the report to the WATS server.
        See `WSJF.restclient.WATSREST.upload_report` for more information.
        """
        exit_code = self._exitcode_to_report_status_code(exitstatus)

        # The exit code is already being propagated during the tests.
        # Only if a test has not passed, e.g. skipped or some other pytest failure,
        # should we update the exit code.
        if exit_code != UUTStatusCode.PASSED:
            self._report.result = exit_code
            self._report.root.status = StepStatusCode(exit_code)

        self._report.uut.execTime = (datetime.now() - self.test_start_time).total_seconds()

        if self.report_save_path is not None:
            report_path = self._report.save_as_json(self.report_save_path)
            log.info(f"Report saved to: {report_path}")

        if self.base_url is not None and self.token_environment_variable is not None:
            rest_client = WATSREST(base_url=self.base_url, token_environment_variable=self.token_environment_variable)
            rest_client.upload_report(self._report)

    @staticmethod
    def _exitcode_to_report_status_code(exit_code: ExitCode) -> UUTStatusCode:
        """Convert the exit code to a WATS status code."""
        match exit_code:
            case ExitCode.OK:
                return UUTStatusCode.PASSED
            case ExitCode.INTERRUPTED:
                return UUTStatusCode.TERMINATED
            case ExitCode.TESTS_FAILED:
                return UUTStatusCode.FAILED
            case ExitCode.INTERNAL_ERROR | ExitCode.USAGE_ERROR | ExitCode.NO_TESTS_COLLECTED:
                return UUTStatusCode.FAILED
            case _:
                errmsg = f"Unknown exit code: {exit_code}"
                raise ValueError(errmsg)

    def _outcome_to_step_status_code(self, outcome: Literal["passed", "failed", "skipped"]) -> StepStatusCode:
        match outcome:
            case "passed":
                return StepStatusCode.PASSED
            case "failed":
                return StepStatusCode.FAILED
            case "skipped":
                return StepStatusCode.SKIPPED
            case _:
                errmsg = f"Unknown outcome: {outcome}"
                raise ValueError(errmsg)

    def _exception_str_to_pre_html(self, exception: str) -> str:
        # WATS replaces subsequent spaces.
        # Replacing them with non-breaking spaces to keep the stack trace properly formatted.
        result_error_message = re.sub(r"[ ] +", lambda m: "\u00a0" * len(m.group()), exception)

        return f"<pre>{result_error_message[-4950:]}</pre>"
