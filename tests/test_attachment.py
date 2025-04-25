from pathlib import Path

import pytest

from WSJF.models import SequenceCallStep


@pytest.mark.skip(reason="Skipped to not upload to much data while testing")
def test_add_attachment(step: SequenceCallStep):
    """This test adds an jpeg image of cat as an attachment to the step. Meow!
    """
    cat_base64_string = (Path(__file__).parent / "cat.base64").read_text()
    step.add_attachment(
        name="cat.jpg",
        content_type="image/jpeg",
        data=cat_base64_string,
    )
