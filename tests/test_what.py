from WSJF.models import SequenceCallStep


def test_setup(step: SequenceCallStep):
    step.group = "S"
    step.reportText = "hello"


def test_main(step: SequenceCallStep):
    step.group = "M"
    step.reportText = "world"


def test_cleanup(step: SequenceCallStep):
    step.group = "C"
    step.reportText = "goodbye"
