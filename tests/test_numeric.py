import logging

import pytest

from WSJF.enums import BinaryCompOp, TernaryCompOp
from WSJF.models import (
    MultipleNumericLimitStep,
    SequenceCallStep,
    SingleNumericLimitStep,
)

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    ("value", "limit", "operator", "unit"),
    [
        (1.0, 1.0, BinaryCompOp.EQUAL, "mm"),
        (1.1, 1.0, BinaryCompOp.NOT_EQUAL, "mm"),
        (2.0, 1.0, BinaryCompOp.GREATER_THAN, "mm"),
        (1.0, 1.0, BinaryCompOp.GREATER_OR_EQUAL, "mm"),
        (1.0, 1.0, BinaryCompOp.LESS_THAN, "mm"),
        (1.0, 1.0, BinaryCompOp.LESS_OR_EQUAL, "mm"),
    ],
)
def test_single_numeric(
    value: float,
    limit: float,
    operator: BinaryCompOp,
    unit: str,
    step: SequenceCallStep,
):
    numeric_measurement = step.add_test_step(
        f"Single {operator.name}] compare",
        SingleNumericLimitStep,
    )
    numeric_measurement.compare_binary(value, limit, operator, unit)


@pytest.mark.parametrize(
    ("names", "values", "limits", "operators", "units"),
    [
        (
            ["First", "Second", "Third"],
            [1, 2, 3],
            [2, 4, 5],
            [BinaryCompOp.LESS_THAN] * 3,
            ["mm"] * 3,
        ),
        (
            ["First", "Second", "Third"],
            [2, 2, 5],
            [2, 4, 5],
            [BinaryCompOp.LESS_OR_EQUAL] * 3,
            ["mm"] * 3,
        ),
    ],
)
def test_multiple_numeric_high_limit_pass(
    names: list[str],
    values: list[float],
    limits: list[float],
    operators: list[BinaryCompOp],
    units: list[str],
    step: SequenceCallStep,
):
    numeric_measurement = step.add_test_step(
        "MultipleNumericLimitStep",
        MultipleNumericLimitStep,
    )
    for name, value, limit, operator, unit in zip(names, values, limits, operators, units, strict=True):
        numeric_measurement.compare_binary(name, value, limit, operator, unit)


def test_log_value(step: SequenceCallStep):
    numeric_measurement = step.add_test_step(
        "SingleNumericLimitStep[LOG]",
        SingleNumericLimitStep,
    )
    result = numeric_measurement.log(1337, "speed")
    log.info(f"LOG value: {result}")


@pytest.mark.parametrize(
    ("value", "low_limit", "high_limit", "operator", "unit", "expected"),
    [
        (1.5, 1.0, 2.0, TernaryCompOp.GREATER_THAN_OR_LESS_THAN, "mm", True),
        (1.0, 1.0, 2.0, TernaryCompOp.GREATER_EQUAL_OR_LESS_EQUAL, "mm", True),
        (1.99, 1.0, 2.0, TernaryCompOp.GREATER_EQUAL_OR_LESS_THAN, "mm", True),
        (2.0, 1.0, 2.0, TernaryCompOp.GREATER_THAN_OR_LESS_EQUAL, "mm", True),
        (0.9, 1.0, 2.0, TernaryCompOp.LESS_THAN_OR_GREATER_THAN, "mm", True),
        (1.0, 1.0, 2.0, TernaryCompOp.LESS_EQUAL_OR_GREATER_EQUAL, "mm", True),
        (2.1, 1.0, 2.0, TernaryCompOp.LESS_EQUAL_OR_GREATER_THAN, "mm", True),
        (2.0, 1.0, 2.0, TernaryCompOp.LESS_THAN_OR_GREATER_EQUAL, "mm", True),
    ],
)
def test_single_ternary_limit(
    value: float,
    low_limit: float,
    high_limit: float,
    operator: TernaryCompOp,
    unit: str,
    expected: bool,
    step: SequenceCallStep,
):
    numeric_measurement = step.add_test_step(
        f"Single {operator.name} compare",
        SingleNumericLimitStep,
    )
    result = numeric_measurement.compare_ternary(value, low_limit, high_limit, operator, unit)
    log.info(f"{value} {operator.name} {low_limit} < {high_limit} = {result}")
