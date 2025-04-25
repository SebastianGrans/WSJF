from pathlib import Path

from WSJF.models import (
    BinaryCompOp,
    SequenceCallStep,
    SingleBooleanLimitStep,
    SingleNumericLimitStep,
    WATSReport,
)

# First we use the factory method to create a report
report = WATSReport.factory(
    name="TestReport",
    part_number="9999",
    serial_number="123456",
    revision="x",
    process_code=10,
    machine_name="TestMachine",
    location="TestLocation",
    purpose="development",
    operator_name="whoareyou?",
)

# Then we add a test sequence. It's a `SequenceCall` object, and can contain other steps
first_sequence: SequenceCallStep = report.add_test_sequence("VoltageTests", "TestReport")

# We can then add a test step to the sequence.
numeric_step = first_sequence.add_test_step("5V", SingleNumericLimitStep)

result = numeric_step.compare_binary(
    value=5.0,
    unit="V",
    limit=5.0,
    operator=BinaryCompOp.EQUAL,
)


# We can add another test step to the sequence
bool_step = first_sequence.add_test_step("3.3V", SingleBooleanLimitStep)
# We create a dummy measurement that has passed
V3_3_good = True
result = bool_step.add_result(result=False)


# And then we can continue adding another test sequence
second_sequence = report.add_test_sequence("CurrentTest", "TestReport")
bool_step = second_sequence.add_test_step("CurrentLimit", SingleBooleanLimitStep)
result = bool_step.add_result(result=True)

# Then we can save it to a file if we want to use the WATS Client
save_path = report.save_as_json(path=Path("/tmp/"))
print(f"Report saved to {save_path}")

# OR: We can directly upload the report using the WATSREST client

# from WSJF.restclient import WATSREST
# wrest = WATSREST(base_url="https://<your-domain>.wats.com")
# wrest.upload_report(report)
