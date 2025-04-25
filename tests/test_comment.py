from WSJF.models import SequenceCallStep


def test_add_comment(step: SequenceCallStep):
    step.add_comment("This is a test comment")


def test_add_html_comment(step: SequenceCallStep):
    step.add_comment("<pre>Hello, World!</pre>")


def test_add_html_image(step: SequenceCallStep):
    step.add_comment("<img src='https://c.tenor.com/40BdfMplFhwAAAAC/tenor.gif' />")


def test_add_html_link(step: SequenceCallStep):
    step.add_comment("<a href='https://asdf.com'>This is a test link</a>")
