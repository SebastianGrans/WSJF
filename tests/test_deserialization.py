from pathlib import Path

from WSJF.models import WATSReport


def test_deserializing_our_data():
    # This is just a smoke test to check that we can deserialize our own data without errors.
    # TODO: Check that the deserialized data matches the original data.
    our_serialized_data = Path(__file__).parent / "test_data" / "test_report_from_us.json"
    WATSReport.model_validate_json(our_serialized_data.read_text())


def test_deserializing_their_data():
    # This report from above was uploaded to WATS and then downloaded again.
    # This is also just a smoke test to check that we can deserialize their data without errors.
    their_serialized_data = Path(__file__).parent / "test_data" / "test_report_from_wats.json"
    WATSReport.model_validate_json(their_serialized_data.read_text())

    # There are some differences in the data that make it hard to compare with a simple equality check.
    # Floats in the report from WATS are slightly different from the original report.
    # And some fields are not included or over-written in the report from WATS.
    # E.g.
    # * `AdditionalDataProperty.comment` is dropped.
    # * `AdditionalDataProperty.name` will be null.
    # * `AdditionalDataArrayIndex.text` will be over-written with something else.

    # assert our_report == their_report
