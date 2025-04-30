"""The main models for the WATS report."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path
from uuid import UUID, uuid4

import pytest_check as check
from pydantic import BaseModel, Field, PrivateAttr

from WSJF.compare import compare_binary, compare_case, compare_ternary
from WSJF.enums import (
    BinaryCompOp,
    ChartType,
    MeasurementStatusCode,
    StepStatusCode,
    StepType,
    StringCaseOp,
    TernaryCompOp,
    UUTStatusCode,
)
from WSJF.sub_models import (
    UUT,
    AdditionalData,
    Asset,
    Attachment,
    BooleanMeasurement,
    Chart,
    MiscInfo,
    NumericMeasurement,
    SequenceCall,
    StringMeasurement,
    SubUnit,
)

log = logging.getLogger(__name__)


class WATSReport(BaseModel):
    """"""

    type: str = Field(
        description="The unique identifier for a type of report.",
        min_length=1,
        max_length=1,
        default="T",  # We default to test report
    )
    id: UUID = Field(
        description="The unique identifier for a report.",
        default_factory=uuid4,
    )
    pn: str = Field(
        description="The Partnumber of the Unit.",
        min_length=1,
        max_length=100,
    )
    sn: str = Field(
        description="The Serialnumber of the Unit.",
        min_length=1,
        max_length=100,
    )
    rev: str = Field(
        description="The Revision number of the Unit.",
        min_length=1,
        max_length=100,
    )
    productName: str | None = Field(
        default=None,
        description="The Product name of the Unit. This property is not used for incoming report (read-only).",
        min_length=0,
        max_length=100,
    )
    processCode: int = Field(
        description="The Process identifier (code) for the report.",
    )
    processName: str | None = Field(
        default=None,
        description="The Process identifier (name) for a report.",
        min_length=0,
        max_length=100,
    )
    result: UUTStatusCode = Field(
        description=(
            "The outcome (result) of a test. Must be one of Passed, Failed, Error or Terminated. UUR must be Passed."
        ),
        min_length=1,
        max_length=1,
    )
    machineName: str = Field(
        description="The machine name where the report was produced.",
        min_length=1,
        max_length=100,
    )
    location: str = Field(
        description="The location where the report was produced.",
        min_length=1,
        max_length=100,
    )
    purpose: str = Field(
        description="The primary (or current) purpose of the tester used to produce the report.",
        min_length=1,
        max_length=100,
    )
    # TODO: Look into making this a datetime field
    start: str = Field(
        description="The date and time when the report was created including timezone.",
        examples=[["2019-09-12T14:26:16.977+02:00"]],
    )
    startUTC: str | None = Field(
        default=None,
        description=(
            "The date and time when the report was created in UTC."
            "If specified, the time must be equal to start, but in +00:00 or Z timezone."
        ),
        examples=[["2019-09-12T12:26:16.977Z"]],
    )
    root: RootSequenceCallStep = Field(
        description="The root step of the report. Only for UUT reports.",
    )
    uut: UUT = Field(
        description="The header data for a UUT report. The documentation say it's optional, but it is required.",
    )
    miscInfos: list[MiscInfo] = Field(
        default_factory=list,
        description="A list of miscellaneous information.",
    )
    subUnits: list[SubUnit] = Field(
        default_factory=list,
        description="A list of subunits. In UUR reports, may be hierarchical.",
    )
    additionalData: list[AdditionalData] = Field(
        default_factory=list,
        description="A list of additional header data.",
    )
    assets: list[Asset] = Field(
        default_factory=list,
        description="A list of assets used in test.",
    )

    def save_as_json(self, path: Path) -> Path:
        """Save the report as a JSON file.

        The file name is in the format `YYYY-MM-DDTHHMMSS-{part_number}-{serial_number}_WATS.json`.
        """
        filename = f"{datetime.now().strftime('%Y-%m-%dT%H%M%S')}-{self.root.name}-{self.sn}_WATS.json"
        filepath = path / filename
        filepath.write_text(self.model_dump_json(indent=4, exclude_none=True))
        return filepath

    def set_result(self, result: UUTStatusCode) -> None:
        """Set the result of the report.

        The result must be the same as the root step status.
        """
        if self.root.status != result:
            errmsg = "Root step status must be the same as the report status"
            raise ValueError(errmsg)
        self.result = result

    def add_asset(self, asset_sn: str, usage_count: int) -> None:
        """Add an asset to the report.

        **Note**: The asset needs to be set up in the WATS client before it can be used.
        This requires there to be an asset with this serial number in the asset manager.

        https://[your-domain].wats.com/dist/#/control-panel/asset-manager

        """
        asset = Asset(assetSN=asset_sn, usageCount=usage_count)
        self.assets.append(asset)

    def add_comment(self, comment: str) -> str:
        """Add a comment to the report.

        If the comment already contains text, a newline in the form of a `</br>` is added before the new comment.

        Note: This field supports HTML, although everything will be formatted bold italic.

        Returns:
            The comment with the new text added.

        """
        if self.uut.comment is None:
            self.uut.comment = comment
        else:
            self.uut.comment += f"</br>{comment}"

        return self.uut.comment

    def add_misc_info(self, description: str, text: str | None = None, numeric: int | None = None) -> None:
        """Add a misc info to the report."""
        miscinfo = MiscInfo(description=description, text=text, numeric=numeric)
        self.miscInfos.append(miscinfo)

    def add_subunit(
        self,
        part_type: str,
        part_number: str,
        revision: str,
        serial_number: str,
    ) -> None:
        """Add a subunit to the report.

        **Note:** The part type, part number, revision and serial number should be set up in the WATS.

        https://[your-domain].wats.com/dist/#/control-panel/product-manager
        """
        subunit = SubUnit(partType=part_type, pn=part_number, rev=revision, sn=serial_number)
        self.subUnits.append(subunit)

    def add_test_sequence(self, name: str, path: str, version: str = "0") -> SequenceCallStep:
        """Add a test sequence to the report."""
        return self.root.add_sequence_call(name=name, path=path, version=version)

    def add_additional_data(self, name: str) -> AdditionalData:
        """Add additional data to the report."""
        additional_data = AdditionalData(name=name)
        self.additionalData.append(additional_data)
        return additional_data

    def find_steps_by_name(self, name: str) -> list[Step]:
        """Find steps by name.

        This will search the entire report for steps with the given name and return them as a list.
        """
        return self.root.find_steps_by_name(name=name)

    @classmethod
    def factory(
        cls,
        name: str,
        part_number: str,
        serial_number: str,
        revision: str,
        process_code: int,
        machine_name: str,  # TODO: If the WATS client is used, this isn't required. Maybe set to optional?
        location: str,  # TODO: Also not needed if the WATS client is used
        purpose: str,  # TODO: Ditto.
        operator_name: str,
    ) -> WATSReport:
        """A convenience method to create a `WATSReport`.

        It will create a root step with the given name and a sequence call with the same name.
        """
        root = RootSequenceCallStep(
            name=name,
            status=StepStatusCode.PASSED,
            seqCall=SequenceCall(
                path=name,  # TODO: Expose this?
                name=name,
                version="1.0",  # TODO: Expose this
            ),
        )

        report = WATSReport(
            pn=part_number,
            sn=serial_number,
            rev=revision,
            processCode=process_code,
            result=UUTStatusCode.PASSED,
            machineName=machine_name,
            location=location,
            purpose=purpose,
            start=str(datetime.now().astimezone().replace(microsecond=0).isoformat()),
            root=root,
            uut=UUT(user=operator_name),
        )
        root._report = report  # noqa: SLF001
        return report


class Step(BaseModel):
    """ """

    id: int | str | None = Field(
        default=None,
        description="The id of the step.",
    )
    group: str = Field(
        default="M",
        description="The step group. S(Startup), M(Main), or C(Cleanup)",
        pattern=r"^[SMC]$",
        min_length=1,
        max_length=1,
    )
    stepType: StepType = Field(
        description="The step type, a textual description of the step.",
        # TODO: make this a string enum
        min_length=1,
    )
    name: str = Field(
        description="Name of the step.",
        min_length=1,
        max_length=100,
    )
    start: str | None = Field(
        default=None,
        description="The start date and time of the step with timezone.",
    )
    status: StepStatusCode = Field(
        description="The status of the step.",
        min_length=1,
        max_length=1,
    )
    errorCode: int | str | None = Field(
        default=None,
        description="The error code of the error that occurred during the step execution, if any.",
    )
    errorMessage: str | None = Field(
        default=None,
        description="The error message of the error that occurred during the step execution, if any.",
    )

    totTime: float | None = Field(
        default=0.0,
        description="The total time spent executing this step.",
    )
    causedSeqFailure: bool | None = Field(
        default=None,
        description="A flag indicating if this step caused the sequence to fail.",
    )
    causedUUTFailure: bool | None = Field(
        default=None,
        description="A flag indicating if this step caused the UUT report to fail.",
    )
    reportText: str | None = Field(
        default=None,
        description="The step comment.",
    )
    additionalResults: list[AdditionalData] = Field(
        default_factory=list,
        description="A list of additional results for the step.",
    )
    chart: Chart | None = Field(
        default=None,
        description="The chart belonging to this step.",
    )
    attachment: Attachment | None = Field(
        default=None,
        description="The attachment belonging to this step.",
    )

    def find_steps_by_name(self, name: str) -> list[Step]:
        """Find steps by name.

        See `WATSReport.find_steps_by_name` for more information.
        """
        if isinstance(self, (RootSequenceCallStep, SequenceCallStep)):
            steps_found = []
            for step in self.steps:
                found = step.find_steps_by_name(name=name)
                if step:
                    steps_found.extend(found)

            if self.name == name:
                steps_found.append(self)

            return steps_found

        if isinstance(self, StepTypeUnion) and self.name == name:
            return [self]

        return []

    def add_chart(
        self,
        label: str,
        xlabel: str,
        ylabel: str,
        chart_type: ChartType = ChartType.LINE,
        xunit: str | None = None,
        yunit: str | None = None,
    ) -> Chart:
        """Add a chart to the step.

        Then call `WSJF.sub_models.Chart.add_series` to add a series to the chart.

        **Note:** This function can only be called once.
        """
        if self.chart is not None:
            errmsg = "Chart already exists. This function should only be called once"
            raise RuntimeError(errmsg)
        chart = Chart(
            chartType=chart_type,
            label=label,
            xLabel=xlabel,
            yLabel=ylabel,
            xUnit=xunit,
            yUnit=yunit,
        )
        self.chart = chart
        return chart

    # callExe: Optional[CallExe] = Field(
    #     default=None,
    #     description="Information about the executable called by this step.",
    # )
    # Not expecting us to use this function
    # messagePopup: Optional[MessagePopup] = Field(
    #     default=None, description="Information about the popup message belonging to this step."
    # )

    def set_total_time(self, time: float) -> None:
        """Set the total time spent executing this step."""
        self.totTime = time

    def add_attachment(self, name: str, content_type: str, data: str) -> None:
        """Add an attachment to the step.

        * `name`: Name of the attachment
        * `content_type`: The MIME-type of the attachment.</br>
            E.g.: `application/pdf`, `image/png`, etc.
        * `data`: base64 encoded data of the attachment

        **Note:** This function can only be called once per step.
        """
        if self.attachment is not None:
            errmsg = "Attachment already exists. This function should only be called once"
            raise RuntimeError(errmsg)
        attachment = Attachment(name=name, contentType=content_type, data=data)
        self.attachment = attachment

    def add_additional_data(self, name: str) -> AdditionalData:
        """Add additional data to the step

        Example:
        ```
        additional_data = step.add_additional_data("Some strings")
        additional_data.add_additional_data_property(
            "hello",
            AdditionalDataPropertyType.STRING,
            value="world",
            comment="hello world",
        )
        ```
        """
        additional_data = AdditionalData(name=name)
        self.additionalResults.append(additional_data)
        return additional_data


class _NonRootStep(BaseModel):
    _parent: _NonRootStep | RootSequenceCallStep = PrivateAttr()

    def set_status(self, status: StepStatusCode) -> None:
        """Set the status of the step and if propagate the status if it failed."""
        self.status = status
        if status == StepStatusCode.FAILED:
            self._parent.set_status(status)

    def add_misc_info(self, description: str, text: str | None = None, numeric: int | None = None) -> None:
        """Add misc info to the report."""
        self._parent.add_misc_info(description=description, text=text, numeric=numeric)

    def add_asset(self, asset_sn: str, usage_count: int) -> None:
        """See `WSJF.models.WATSReport.add_asset`"""
        self._parent.add_asset(asset_sn=asset_sn, usage_count=usage_count)

    def add_subunit(self, part_type: str, part_number: str, revision: str, serial_number: str) -> None:
        """See `WSJF.models.WATSReport.add_subunit`"""
        self._parent.add_subunit(
            part_type=part_type,
            part_number=part_number,
            revision=revision,
            serial_number=serial_number,
        )

    def add_comment(self, comment: str) -> str:
        """Add a comment to `WSJF.models.WATSReport`

        See ``WSJF.models.WATSReport`.add_comment`

        Returns the content of the comment field.
        """
        return self._parent.add_comment(comment=comment)

    def add_additional_data_to_report(self, name: str) -> AdditionalData:
        """Add additional data to the `WSJF.models.WATSReport`"""
        return self._parent.add_additional_data_to_report(name=name)


class RootSequenceCallStep(Step):
    """The root step of the report."""

    _report: WATSReport = PrivateAttr()
    stepType: StepType = Field(
        default=StepType.SEQUENCE_CALL,
        description="The step type, a textual description of the step.",
        min_length=1,
    )
    # NOTE! The order of this union is important!
    # Or maybe not?
    # If you put Step first, a serialized SequenceCallStep will be deserialized as a Step
    steps: list[
        ChartStep
        | MultipleBooleanLimitStep
        | MultipleNumericLimitStep
        | MultipleStringLimitStep
        | SequenceCallStep
        | SingleBooleanLimitStep
        | SingleNumericLimitStep
        | SingleStringLimitStep
    ] = Field(
        default_factory=list,
        description="A list of sub steps for this step. Only for steps of type SequenceCall.",
    )
    seqCall: SequenceCall = Field(
        description="The information about the sequence call.",
    )

    def add_sequence_call(
        self,
        name: str,
        path: str,
        version: str,
    ) -> SequenceCallStep:
        """Add a sequence call to the step."""
        step = SequenceCallStep(
            name=name,
            status=StepStatusCode.PASSED,
            seqCall=SequenceCall(path=path, name=name, version=version),
        )
        # Private attributes in Pydantic aren't included in the `init` method
        # so we need to set it manually
        step._parent = self  # noqa: SLF001
        self.steps.append(step)
        return step

    def set_status(self, status: StepStatusCode) -> None:
        """Set the status of the step and if propagate the status if it failed."""
        self.status = status
        if status == StepStatusCode.FAILED:
            self._report.set_result(UUTStatusCode.FAILED)

    def add_misc_info(self, description: str, text: str | None = None, numeric: int | None = None) -> None:
        """Add misc info to the report."""
        self._report.add_misc_info(description=description, text=text, numeric=numeric)

    def add_asset(self, asset_sn: str, usage_count: int) -> None:
        """See `WSJF.models.WATSReport.add_asset`"""
        self._report.add_asset(asset_sn=asset_sn, usage_count=usage_count)

    def add_subunit(
        self,
        part_type: str,
        part_number: str,
        revision: str,
        serial_number: str,
    ) -> None:
        """See `WSJF.models.WATSReport.add_subunit`"""
        self._report.add_subunit(
            part_type=part_type,
            part_number=part_number,
            revision=revision,
            serial_number=serial_number,
        )

    def add_comment(self, comment: str) -> str:
        """See `WSJF.models.WATSReport.add_comment`

        Returns the content of the comment field.
        """
        return self._report.add_comment(comment=comment)

    def add_additional_data_to_report(self, name: str) -> AdditionalData:
        """Add additional data to the `WSJF.models.WATSReport`"""
        return self._report.add_additional_data(name=name)


class SequenceCallStep(_NonRootStep, RootSequenceCallStep):
    """A step of type SequenceCall.

    This step can contain other steps.
    """

    def add_test_step[T: StepTypeUnion](self, name: str, step_type: type[T]) -> T:
        """Add a test step to the sequence call.

        Example:

        ```
        report = WATSReport.factory(...)
        step = report.add_test_sequence("TestSequence", "TestReport")
        numeric_limit_step = step.add_test_step("TestStep", SingleNumericLimitStep)
        numeric_limit_step.compare_binary(1, 1, BinaryCompOp.EQUAL, "V")
        ```
        """
        step = step_type(name=name, status=StepStatusCode.PASSED)
        # Private attributes in Pydantic aren't included in the `init` method
        # so we need to set it manually
        step._parent = self  # noqa: SLF001
        self.steps.append(step)
        return step


class SingleNumericLimitStep(_NonRootStep, Step):
    """A step of type NumericLimit."""

    stepType: StepType = Field(
        default=StepType.NUMERIC_LIMIT_SINGLE,
        description="The step type, a textual description of the step.",
        min_length=1,
    )
    numericMeas: list[NumericMeasurement] = Field(
        default_factory=list,
        description="A list of numeric measurements belonging to this step.",
        max_length=1,
    )

    @property
    def data(self) -> list[NumericMeasurement]:
        """Return the data of the step."""
        return self.numericMeas

    def compare_binary(
        self,
        value: float,
        limit: float,
        operator: BinaryCompOp,
        unit: str,
    ) -> bool:
        """Compare a value against a single limit and a given operator.

        Adds the measurement to the step and returns the result.

        **Note**: For `SingleNumericLimitStep`, only a single value can be added.
        Would raise a `ValueError` if the step already contains a measurement.
        """
        return _compare_binary_impl(self, value, limit, operator, unit)

    def compare_ternary(
        self,
        value: float,
        low_limit: float,
        high_limit: float,
        operator: TernaryCompOp,
        unit: str,
    ) -> bool:
        """Compare a value against two limits and a given operator.

        Adds the measurement to the step and returns the result.

        **Note**: For `SingleNumericLimitStep`, only a single value can be added.
        Would raise a `ValueError` if the step already contains a measurement.
        """
        return _compare_ternary_impl(self, value, low_limit, high_limit, operator, unit)

    def log(self, value: float, unit: str) -> None:
        """Log a measurement to the step.

        **Note**: For `SingleNumericLimitStep`, only a single value can be added.
        """
        _measurement_assertions(self, name=None)
        measurement = NumericMeasurement(
            value=value,
            compOp="LOG",
            status=MeasurementStatusCode.PASSED,
            unit=unit,
        )
        self.numericMeas.append(measurement)


class MultipleNumericLimitStep(_NonRootStep, Step):
    """A step of type MultipleNumericLimit."""

    stepType: StepType = Field(
        default=StepType.NUMERIC_LIMIT_MULTIPLE,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )
    numericMeas: list[NumericMeasurement] = Field(
        default_factory=list,
        description="A list of numeric measurements belonging to this step.",
    )

    @property
    def data(self) -> list[NumericMeasurement]:
        """Return the data of the step."""
        return self.numericMeas

    def compare_binary(
        self,
        name: str,
        value: float,
        limit: float,
        operator: BinaryCompOp,
        unit: str,
    ) -> bool:
        """Compare a value against a single limit and a given operator.

        Adds the measurement to the step and returns the result.

        **Note**: The name must be unique for each measurement in the step.
        Would raise ValueError error if the name already exists in the step.
        """
        return _compare_binary_impl(self, value, limit, operator, unit, name=name)

    def compare_ternary(
        self,
        name: str,
        value: float,
        low_limit: float,
        high_limit: float,
        operator: TernaryCompOp,
        unit: str,
    ) -> bool:
        """Compare a value against two limits and a given operator.

        Adds the measurement to the step and returns the result.

        **Note**: The name must be unique for each measurement in the step.
        Would raise ValueError error if the name already exists in the step.
        """
        return _compare_ternary_impl(self, value, low_limit, high_limit, operator, unit, name=name)

    def log(self, name: str, value: float, unit: str) -> None:
        """Log a measurement to the step.

        **Note**: The name must be unique for each measurement in the step.
        Would raise ValueError error if the name already exists in the step.
        """
        _measurement_assertions(self, name=name)
        measurement = NumericMeasurement(
            name=name,
            value=value,
            compOp="LOG",
            status=MeasurementStatusCode.PASSED,
            unit=unit,
        )
        self.numericMeas.append(measurement)


def _measurement_assertions[T: (
    SingleMeasurementSteps,
    MultipleMeasurementSteps,
)](step: T, name: str | None = None) -> None:
    """Various assertions to check before adding a measurement.

    Measurements in SingleMeasurementSteps CAN NOT have a name.
    Measurements in MultipleMeasurementSteps MUST have UNIQUE names.
    """
    if isinstance(step, SingleMeasurementSteps):
        if len(step.data) > 0:
            errmsg = "Only one measurement is allowed in a SingleMeasurementStep"
            raise ValueError(errmsg)
        if name is not None:
            errmsg = "Name should not be set for Single Limit Step"
            raise TypeError(errmsg)
    else:
        if len(step.data) >= 10:
            errmsg = "Maximum of 10 measurements are allowed in a Multiple Limit Step"
            raise ValueError(errmsg)
        if name is None:
            errmsg = "Name must be set for Multiple Limit Steps"
            raise TypeError(errmsg)
        names = [m.name for m in step.data]
        if name in names:
            errmsg = f"Name `{name}` already exists in the step"
            raise ValueError(errmsg)


def _compare_binary_impl[T: (
    SingleNumericLimitStep,
    MultipleNumericLimitStep,
)](step: T, value: float, limit: float, operator: BinaryCompOp, unit: str, name: str | None = None) -> bool:
    _measurement_assertions(step, name=name)

    result = compare_binary(value, limit, operator)
    status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
    if operator in [
        BinaryCompOp.GREATER_THAN,
        BinaryCompOp.GREATER_OR_EQUAL,
        BinaryCompOp.EQUAL,
        BinaryCompOp.NOT_EQUAL,
    ]:
        # These operators require the low_limit to be set
        measurement = NumericMeasurement(
            name=name,
            value=value,
            lowLimit=limit,
            compOp=operator,
            status=status,
            unit=unit,
        )
    elif operator in [BinaryCompOp.LESS_THAN, BinaryCompOp.LESS_OR_EQUAL]:
        measurement = NumericMeasurement(
            name=name,
            value=value,
            lowLimit=limit,
            compOp=operator,
            status=status,
            unit=unit,
        )
    else:
        errmsg = f"Operator {operator} is not implemented"
        raise NotImplementedError(errmsg)

    step.numericMeas.append(measurement)
    step.set_status(StepStatusCode(status))

    pass_fail_str = "passed" if result else "failed"
    result_message = f"Measurement {name} {pass_fail_str}. {value} {operator.as_symbol()} {limit} = {result}"
    if result:
        log.info(result_message)
    else:
        log.error(result_message)

    check.is_true(result, result_message)
    return result


def _compare_ternary_impl[T: (
    SingleNumericLimitStep,
    MultipleNumericLimitStep,
)](
    step: T,
    value: float,
    low_limit: float,
    high_limit: float,
    operator: TernaryCompOp,
    unit: str,
    name: str | None = None,
) -> bool:
    _measurement_assertions(step, name=name)

    result = compare_ternary(value, low_limit, high_limit, operator)
    status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
    measurement = NumericMeasurement(
        name=name,
        value=value,
        lowLimit=low_limit,
        highLimit=high_limit,
        compOp=operator,
        status=status,
        unit=unit,
    )
    step.numericMeas.append(measurement)
    step.set_status(StepStatusCode(status))

    pass_fail_str = "passed" if result else "failed"
    result_message = (
        f"Measurement {name} {pass_fail_str}."
        f"{low_limit} {operator.as_symbols()[0]} {value} {operator.as_symbols()[1]} = {result}"
    )

    if result:
        log.info(result_message)
    else:
        log.error(result_message)

    check.is_true(result, result_message)
    return result


class SingleBooleanLimitStep(_NonRootStep, Step):
    """A step of type SingleBooleanLimit."""

    stepType: StepType = Field(
        default=StepType.BOOLEAN_VALUE_SINGLE,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )
    booleanMeas: list[BooleanMeasurement] = Field(
        default_factory=list,
        description="A list of boolean measurements belonging to this step.",
    )

    @property
    def data(self) -> list[BooleanMeasurement]:
        """Return the data of the step."""
        return self.booleanMeas

    def add_result(self, *, result: bool) -> bool:
        """Add a measurement to the step."""
        _measurement_assertions(self, name=None)
        status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
        measurement = BooleanMeasurement(status=status)
        self.booleanMeas.append(measurement)

        self.set_status(StepStatusCode(status))
        check.is_true(result)
        return result


class MultipleBooleanLimitStep(_NonRootStep, Step):
    """A step of type MultipleBooleanLimit."""

    stepType: StepType = Field(
        default=StepType.BOOLEAN_VALUE_MULTIPLE,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )
    booleanMeas: list[BooleanMeasurement] = Field(
        default_factory=list,
        description="A list of boolean measurements belonging to this step.",
    )

    @property
    def data(self) -> list[BooleanMeasurement]:
        """Return the data of the step."""
        return self.booleanMeas

    def add_result(self, name: str, *, result: bool) -> bool:
        """Add a measurement to the step."""
        _measurement_assertions(self, name=name)
        status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
        measurement = BooleanMeasurement(name=name, status=status)
        self.booleanMeas.append(measurement)

        self.set_status(StepStatusCode(status))
        check.is_true(result)
        return result


class SingleStringLimitStep(_NonRootStep, Step):
    """A step of type SingleStringLimit."""

    stepType: StepType = Field(
        default=StepType.STRING_VALUE_SINGLE,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )
    stringMeas: list[StringMeasurement] = Field(
        default_factory=list,
        description="A list of string measurements belonging to this step.",
    )

    @property
    def data(self) -> list[StringMeasurement]:
        """Return the data of the step."""
        return self.stringMeas

    def compare_binary(self, value: str, limit: str, operator: BinaryCompOp) -> bool:
        """Compare a value against a single limit and a given operator.

        Adds the measurement to the step and returns the result.
        **Note**: For `SingleStringLimitStep`, only a single value can be added.


        """
        if operator in [
            BinaryCompOp.GREATER_THAN,
            BinaryCompOp.LESS_THAN,
            BinaryCompOp.GREATER_OR_EQUAL,
            BinaryCompOp.LESS_OR_EQUAL,
        ]:
            # These operators are supposed to work according to the documentation, but they don't
            errmsg = f"Operator {operator} is broken for strings"
            raise NotImplementedError(errmsg)

        return _string_compare_binary_impl(self, value, limit, operator)

    def compare_case(self, value: str, limit: str, operator: StringCaseOp) -> bool:
        """Compare a string against another string.

        See `WSJF.compare.compare_case` for more info.
        """
        return _string_compare_case_impl(self, value, limit, operator)

    def log(self, value: str) -> None:
        """Add a string to the step as a log entry."""
        _string_log_impl(self, value)


class MultipleStringLimitStep(_NonRootStep, Step):
    """A step of type MultipleStringLimit."""

    stepType: StepType = Field(
        default=StepType.STRING_VALUE_MULTIPLE,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )
    stringMeas: list[StringMeasurement] = Field(
        default_factory=list,
        description="A list of string measurements belonging to this step.",
    )

    @property
    def data(self) -> list[StringMeasurement]:
        """Return the data of the step."""
        return self.stringMeas

    def compare_binary(self, name: str, value: str, limit: str, operator: BinaryCompOp) -> bool:
        """Compare a value against a single limit and a given operator.

        See `WSJF.compare.compare_binary` for more info.

        **Note**: The name must be unique for each measurement in the step.
        """
        return _string_compare_binary_impl(self, value, limit, operator, name=name)

    def compare_case(self, name: str, value: str, limit: str, operator: StringCaseOp) -> bool:
        """Compare a string against another string.

        See `WSJF.compare.compare_case` for more info.

        **Note**: The name must be unique for each measurement in the step.
        """
        return _string_compare_case_impl(self, value, limit, operator, name=name)

    def log(self, value: str, name: str) -> None:
        """Add a string to the step as a log entry.

        **Note**: The name must be unique for each measurement in the step.
        """
        _string_log_impl(self, value, name=name)


def _string_compare_binary_impl[T: (
    SingleStringLimitStep,
    MultipleStringLimitStep,
)](step: T, value: str, limit: str, operator: BinaryCompOp, name: str | None = None) -> bool:
    _measurement_assertions(step, name=name)
    result = compare_binary(value, limit, operator)
    status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
    measurement = StringMeasurement(
        name=name,
        value=value,
        limit=limit,
        compOp=operator,
        status=status,
    )
    step.stringMeas.append(measurement)
    step.set_status(StepStatusCode(status))
    return result


def _string_compare_case_impl[T: (
    SingleStringLimitStep,
    MultipleStringLimitStep,
)](step: T, value: str, limit: str, operator: StringCaseOp, name: str | None = None) -> bool:
    _measurement_assertions(step, name=None)

    result = compare_case(value, limit, operator)
    status = MeasurementStatusCode.PASSED if result else MeasurementStatusCode.FAILED
    measurement = StringMeasurement(
        name=name,
        value=value,
        limit=limit,
        compOp=operator,
        status=status,
    )
    step.stringMeas.append(measurement)
    step.set_status(StepStatusCode(status))
    return result


def _string_log_impl[T: (
    SingleStringLimitStep,
    MultipleStringLimitStep,
)](step: T, value: str, name: str | None = None) -> None:
    _measurement_assertions(step, name=name)
    measurement = StringMeasurement(
        value=value,
        compOp="LOG",
        status=MeasurementStatusCode.PASSED,
    )
    step.stringMeas.append(measurement)


class ChartStep(_NonRootStep, Step):
    """A step of type Chart."""

    stepType: StepType = Field(
        default=StepType.CHART,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )


class AttachmentStep(_NonRootStep, Step):
    """A step of type Attachment."""

    stepType: StepType = Field(
        default=StepType.ATTACHMENT,
        description="The step type, a textual description of the step.",
        min_length=1,
        frozen=True,
    )


StepTypeUnion = (
    ChartStep
    | MultipleBooleanLimitStep
    | MultipleNumericLimitStep
    | MultipleStringLimitStep
    | SingleBooleanLimitStep
    | SingleNumericLimitStep
    | SingleStringLimitStep
)

SingleMeasurementSteps = SingleBooleanLimitStep | SingleNumericLimitStep | SingleStringLimitStep
MultipleMeasurementSteps = MultipleBooleanLimitStep | MultipleNumericLimitStep | MultipleStringLimitStep


# This is for excluding some members from the documentation
_classes: dict[type[BaseModel], list[str]] = {
    AttachmentStep: ["model_config", "model_post_init", "stepType"],
    ChartStep: ["model_config", "model_post_init", "stepType"],
    MultipleBooleanLimitStep: ["model_config", "model_post_init", "stepType"],
    MultipleNumericLimitStep: ["model_config", "model_post_init", "stepType"],
    MultipleStringLimitStep: ["model_config", "model_post_init", "stepType"],
    RootSequenceCallStep: ["model_config", "model_post_init", "stepType"],
    SequenceCallStep: ["model_config", "model_post_init"],
    SingleBooleanLimitStep: ["model_config", "model_post_init", "stepType"],
    SingleNumericLimitStep: ["model_config", "model_post_init", "stepType"],
    SingleStringLimitStep: ["model_config", "model_post_init", "stepType"],
    Step: ["model_config"],
}

__pdoc__: dict[str, bool] = {}
for cls, _members_to_exclude in _classes.items():
    for member in _members_to_exclude:
        __pdoc__[f"{cls.__name__}.{member}"] = False
