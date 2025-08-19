

from WSJF.enums import BinaryCompOp
from WSJF.models import MultipleNumericLimitStep, SequenceCallStep, MultipleBooleanLimitStep, MultipleStringLimitStep


def test_multiple_numeric_limit_test(step: SequenceCallStep):
    """
    If you add a multiple numeric limit test step, but only add a single measurement. WATS will not be happy.
    Even though it is defined as a _multiple_ numeric limit test step, it will be interpreted as a single numeric limit
    test step, and will not allow for the measurement to have a name.
    """
    numeric_measurement = step.add_test_step(
        "MultipleNumericLimitStep",
        MultipleNumericLimitStep,
    )
    numeric_measurement.compare_binary("SingleMeasurement", 1.0, 1.0, BinaryCompOp.EQUAL, "mm")

def test_multiple_boolean_limit_test(step: SequenceCallStep):
    """
    If you add a multiple boolean limit test step, but only add a single measurement. WATS will not be happy.
    Even though it is defined as a _multiple_ boolean limit test step, it will be interpreted as a single boolean limit
    test step, and will not allow for the measurement to have a name.
    """
    boolean_measurement = step.add_test_step(
        "MultipleBooleanLimitStep",
        MultipleBooleanLimitStep
    )
    boolean_measurement.add_result("Something", result=False)

def test_multiple_string_limit_test(step: SequenceCallStep):
    """
    If you add a multiple string limit test step, but only add a single measurement. WATS will not be happy.
    Even though it is defined as a _multiple_ string limit test step, it will be interpreted as a single string limit
    test step, and will not allow for the measurement to have a name.
    """
    string_measurement = step.add_test_step(
        "MultipleStringLimitStep",
        MultipleStringLimitStep
    )
    string_measurement.compare_binary("SingleMeasurement", "Test", "Test", BinaryCompOp.EQUAL)
