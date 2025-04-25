import logging

import pytest

from WSJF.enums import BinaryCompOp, StringCaseOp
from WSJF.models import (
    MultipleStringLimitStep,
    SequenceCallStep,
    SingleStringLimitStep,
)

log = logging.getLogger(__name__)


def test_log_value(step: SequenceCallStep):
    string_measurement = step.add_test_step(
        "Single string LOG",
        SingleStringLimitStep,
    )
    result = string_measurement.log("1337")
    log.info(f"LOG value: {result}")


@pytest.mark.parametrize(
    ("value", "limit", "operator"),
    [
        ("a", "a", BinaryCompOp.EQUAL),
        ("a", "b", BinaryCompOp.NOT_EQUAL),
        # ("b", "a", BinaryCompOp.GREATER_THAN), # Documentation say this should be supported, but it doesn't work
        # ("b", "b", BinaryCompOp.GREATER_OR_EQUAL), # Ditto
    ],
)
def test_single_numeric_low_limit_pass(value: str, limit: str, operator: BinaryCompOp, step: SequenceCallStep):
    string_measurement = step.add_test_step(
        f"SingleStringLimitStep[{operator.name}]",
        SingleStringLimitStep,
    )
    result = string_measurement.compare_binary(value, limit, operator)
    log.info(f"{value} {operator.name} {limit} = {result}")


@pytest.mark.parametrize(
    ("names", "values", "limits", "operators"),
    [
        (
            ["First", "Second"],
            ["a", "b"],
            ["a", "a"],
            [BinaryCompOp.EQUAL, BinaryCompOp.NOT_EQUAL],
        ),
    ],
)
def test_multiple_string_limits(
    names: list[str],
    values: list[str],
    limits: list[str],
    operators: list[BinaryCompOp],
    step: SequenceCallStep,
):
    numeric_measurement = step.add_test_step(
        "Multiple String Limit Step",
        MultipleStringLimitStep,
    )
    for name, value, limit, operator in zip(names, values, limits, operators, strict=True):
        result = numeric_measurement.compare_binary(name, value, limit, operator)
        log.info(f"{value} {operator.name} {limit} = {result}")


def test_string_case_sensitive(step: SequenceCallStep):
    string_measurement = step.add_test_step(
        "Single string case sensitive",
        SingleStringLimitStep,
    )
    result = string_measurement.compare_case("a", "A", StringCaseOp.CASE_SENSITIVE)
    log.info(f"Case sensitive check: {result}")


def test_string_ignorecase(step: SequenceCallStep):
    string_measurement = step.add_test_step(
        "Single string case sensitive",
        SingleStringLimitStep,
    )
    result = string_measurement.compare_case("a", "A", StringCaseOp.IGNORECASE)
    log.info(f"Case sensitive check: {result}")
