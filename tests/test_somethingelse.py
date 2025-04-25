import pytest
import pytest_check as check

from WSJF.enums import BinaryCompOp
from WSJF.models import SequenceCallStep, SingleNumericLimitStep


def sometest():
    check.is_true(True, "This should pass")


@pytest.mark.xfail(reason="This test is expected to fail")
def test_asdf(step: SequenceCallStep):
    """Test that the test step is not skipped
    """
    # This test should be skipped
    ns = step.add_test_step("test", SingleNumericLimitStep)
    ns.compare_binary(1, 2, BinaryCompOp.GREATER_THAN, "mm")
