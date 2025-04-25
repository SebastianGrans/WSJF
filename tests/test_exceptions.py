import pytest_check as check


def leaf():
    errmsg = "This is a test exception"
    raise ValueError(errmsg)


def node1():
    return leaf()


def node2():
    return node1()


def root():
    return node2()


def test_raise_exception():
    """An exception should result in the test failing, and the stack trace to be added to the step `reportText`,
    and the exception name added as the `errorMessage`.
    """
    root()


def test_pytest_fail():
    """A pytest.fail also should not add any information to the step."""


def test_assert():
    """An assert should not add any information to the step."""
    assert False, "Dummy assert"  # noqa: PT015 # The purpose is to test that asserts work.


def test_pytest_check():
    """A pytest.check should not add any information to the step."""
    check.is_true(False, "Dummy check")
