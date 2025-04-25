from WSJF.models import SequenceCallStep


def test_add_miscinfo(step: SequenceCallStep):
    step.add_misc_info("key1", "value1", numeric=1)
