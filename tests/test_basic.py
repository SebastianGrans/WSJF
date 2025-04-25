import logging

import pytest
import pytest_check as check

log = logging.getLogger(__name__)


def test_pass() -> None:
    log.info("This test is supposed to pass")


def test_fail() -> None:
    log.info("This test is supposed to fail")
    assert False, "This test is supposed to fail"  # noqa: PT015


def test_fail_pytest_check():
    log.info("This test is supposed to fail")
    check.fail("This test is supposed to fail")


def test_skipped() -> None:
    pytest.skip("This test is supposed to be skipped")
