import logging

import pytest

from WSJF.models import (
    MultipleBooleanLimitStep,
    SequenceCallStep,
    SingleBooleanLimitStep,
)

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "value",
    [True, False],
)
def test_single_bool(value: bool, step: SequenceCallStep):
    string_measurement = step.add_test_step(f"Single Boolean Limit Step [{value}]", SingleBooleanLimitStep)
    result = string_measurement.add_result(value)
    log.info(f"{value} = {result}")


@pytest.mark.parametrize(
    ("names", "values"),
    [(["First", "Second"], [True, False])],
)
def test_multiple_string_limits(
    names: list[str],
    values: list[bool],
    step: SequenceCallStep,
):
    numeric_measurement = step.add_test_step(
        "Multiple String Limit Step",
        MultipleBooleanLimitStep,
    )
    for name, value in zip(names, values, strict=True):
        result = numeric_measurement.add_result(name, value)
        log.info(f"{name}: {value} = {result}")
