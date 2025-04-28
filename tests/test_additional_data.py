from copy import deepcopy

from WSJF.enums import AdditionalDataPropertyType
from WSJF.models import SequenceCallStep
from WSJF.sub_models import AdditionalDataProperty


def test_add_additional_data(step: SequenceCallStep):
    additional_data = step.add_additional_data("Some strings")
    additional_data.add_additional_data_property(
        "hello",
        AdditionalDataPropertyType.STRING,
        value="world",
        comment="hello world",
    )
    # Is this allowed?
    additional_data.add_additional_data_property(
        "number",
        AdditionalDataPropertyType.NUMBER,
        flags=0b001,
        value=str(42),
        comment="number",
    )


def test_add_additional_data_obj(step: SequenceCallStep):
    additional_data = step.add_additional_data("an obj")
    add_data_obj = additional_data.add_additional_data_property(
        "hello",
        AdditionalDataPropertyType.OBJ,
    )
    add_data_obj.add_additional_data_property(
        "number",
        AdditionalDataPropertyType.NUMBER,
        flags=0b001,
        value=str(42),
        comment="number",
    )
    add_data_obj.add_additional_data_property(
        "hello",
        AdditionalDataPropertyType.STRING,
        value="world",
        comment="hello world",
    )
    obj_in_obj = add_data_obj.add_additional_data_property(
        "obj_in_obj",
        AdditionalDataPropertyType.OBJ,
    )
    obj_in_obj.add_additional_data_property(
        "number",
        AdditionalDataPropertyType.NUMBER,
        flags=0b001,
        value=str(42),
        comment="number",
    )


def test_add_additional_data_array(step: SequenceCallStep):
    # Not exactly sure what the usecase for this is. The interface is very clunky.
    additional_data = step.add_additional_data("an array")
    add_data_array = additional_data.add_additional_data_property(
        "hello",
        AdditionalDataPropertyType.ARRAY,
    )
    array = add_data_array.add_additional_data_array(2, AdditionalDataPropertyType.NUMBER)
    x1 = AdditionalDataProperty(
        name="one",
        type=AdditionalDataPropertyType.NUMBER,
        value="1",
        comment="hello world",
    )

    y1 = deepcopy(x1)
    x2 = deepcopy(x1)
    x2.value = "2"
    y2 = deepcopy(x1)
    y2.value = "2"

    array.add_additional_data_array_index("what", [0, 0], x1)
    array.add_additional_data_array_index("what", [0, 1], y1)
    array.add_additional_data_array_index("what", [1, 0], x2)
    array.add_additional_data_array_index("what", [1, 1], y2)


def test_add_additional_data_to_report(step: SequenceCallStep):
    # Instead of adding the data to the step itself, we add it to the report.
    additional_data = step.add_additional_data_to_report("reportdata")
    additional_data.add_additional_data_property(
        "hello",
        AdditionalDataPropertyType.STRING,
        value="world",
        comment="hello world",
    )
    additional_data.add_additional_data_property(
        "number",
        AdditionalDataPropertyType.NUMBER,
        value=str(42),
        comment="number",
    )
