"""The sub-models of the WATS report."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from WSJF.enums import ChartType, MeasurementStatusCode


class AdditionalData(BaseModel):
    """TODO: Add a docstring for AdditionalData."""

    name: str = Field(
        description="The name of the additional data.",
        min_length=1,
        max_length=200,
    )
    props: list[AdditionalDataProperty] = Field(
        default_factory=list,
        description="list of properties in the additional data.",
    )


class AdditionalDataArray(BaseModel):
    """TODO: Add a docstring for AdditionalData."""

    dimension: int = Field(
        description="Dimension of array.",
    )
    type: str = Field(
        description="Type of the values in the array.",
    )
    indexes: list[AdditionalDataArrayIndex] = Field(
        description="list of indexes in the array.",
    )


class AdditionalDataArrayIndex(BaseModel):
    """TODO: ADD DOCSTRING"""

    """
    TODO: ADD DOCSTRING
    """

    text: str = Field(
        description="The index as text.",
    )
    indexes: list[int] = Field(
        description="list of indexes ordered by dimension.",
    )
    value: AdditionalDataProperty | None = None


class AdditionalDataProperty(BaseModel):
    """TODO: ADD DOCSTRING"""

    name: str
    type: str
    flags: int | None = Field(
        default=None,
        description="Bit flags of property.",
    )
    value: str | None = Field(
        default=None,
        description="Value string of property.",
    )
    comment: str | None = Field(
        default=None,
        description="Comment of property.",
    )
    props: list[AdditionalDataProperty] = Field(
        default_factory=list,
        description="Array of sub-properties. Used for type Obj.",
    )
    array: AdditionalDataArray | None = Field(
        default=None,
        description="Array information. Used for type Array.",
    )


class Asset(BaseModel):
    """TODO: ADD DOCSTRING"""

    assetSN: str = Field(
        description="The Serial number of the asset.",
        max_length=100,
    )
    usageCount: int = Field(
        description="How much the asset was used.",
    )


class Attachment(BaseModel):
    """TODO: ADD DOCSTRING"""

    name: str = Field(
        description="The name of the attachment.",
        min_length=1,
        max_length=100,
    )
    contentType: str = Field(
        description="The Mime-type of the attachment. E.g. image/png, application/pdf.",
        min_length=1,
        max_length=100,
    )
    data: str = Field(
        description="The base64 encoded data of the attachment.",
        min_length=1,
    )


class BooleanMeasurement(BaseModel):
    """TODO: ADD DOCSTRING"""

    name: str | None = Field(
        default=None,
        description=(
            "The Name of the measurement. Required if there are multiple measurements in the same step."
            "Do not use if there is only one measurement in the step."
        ),
        min_length=0,
        max_length=100,
    )
    status: MeasurementStatusCode = Field(
        description="The Status of the measurement.",
        min_length=1,
        max_length=1,
    )


class Chart(BaseModel):
    """TODO: ADD DOCSTRING"""

    chartType: ChartType = Field(
        description="The type of chart.",
        examples=[list(ChartType)],
        min_length=1,
        max_length=30,
    )
    label: str = Field(
        description="The name of the chart.",
        min_length=1,
        max_length=100,
    )
    xLabel: str = Field(
        description="The name of the x-axis.",
        min_length=1,
        max_length=50,
    )
    xUnit: str | None = Field(
        default=None,
        description="The unit of the x-axis.",
        min_length=0,
        max_length=20,
    )
    yLabel: str = Field(
        description="The name of the y-axis.",
        min_length=1,
        max_length=50,
    )
    yUnit: str | None = Field(
        default=None,
        description="The unit of the y-axis.",
        min_length=0,
        max_length=20,
    )
    series: list[ChartSeries] = Field(
        default_factory=list,
        description="A list of chart series.",
    )

    def add_series(
        self,
        name: str,
        xdata: str,
        ydata: str,
    ) -> None:
        """Adds a series to the chart.

        **Note**:
        * `xdata` and `ydata` must be semicolon (;) separated lists of values.
        * `xdata` and `ydata` must contain the same number of elements.
        * A maximum of 10 series is allowed to be added to a step.

        """
        if len(self.series) == 10:
            errmsg = "A maximum of 10 series is allowed to be added to a step"
            raise RuntimeError(errmsg)

        if len(xdata.split(";")) != len(ydata.split(";")):
            errmsg = "xdata and ydata must have the same number of elements"
            raise ValueError(errmsg)

        if len(xdata) > 10_000:
            errmsg = "x- and ydata must be less than 10 000 characters"
            raise ValueError(errmsg)

        series = ChartSeries(
            name=name,
            xdata=xdata,
            ydata=ydata,
        )
        self.series.append(series)


class ChartSeries(BaseModel):
    """TODO: ADD DOCSTRING"""

    dataType: Literal["XYG"] = Field(default="XYG")
    name: str = Field(
        description="The name of the series.",
        min_length=1,
        max_length=100,
    )
    xdata: str = Field(
        description="A semicolon (;) separated list of values on the x-axis.",
    )
    ydata: str = Field(
        description="A semicolon (;) separated list of values on the y-axis.",
        min_length=1,
    )


class MiscInfo(BaseModel):
    """TODO: ADD DOCSTRING"""

    description: str
    typedef: str | None = Field(
        default=None,
        description="The type definition of the misc info.",
        min_length=0,
        max_length=30,
        # I have now idea what this is supposed to be, and it doesn't show up in the web interface
    )
    text: str | None = Field(
        None,
        description="The text value of the misc info.",
        min_length=0,
        max_length=100,
    )
    numeric: int | None = Field(
        default=None,
        description="The numeric value of the misc info.",
    )


class NumericMeasurement(BaseModel):
    """TODO: ADD DOCSTRING"""

    """
    This is a docstring for NumericMeasurement.

    It's used by `WSJF.models.SingleNumericLimitStep` and `WSJF.models.MultipleNumericLimitStep`
    """

    compOp: str = Field(
        description="The comparison operator used to compare the value to the limit(s).",
        min_length=1,
        max_length=10,
    )
    name: str | None = Field(
        default=None,
        description=(
            "The Name of the measurement. Required if there are multiple measurements in the same step."
            "Do not use if there is only one measurement in the step."
        ),
        min_length=0,
        max_length=100,
    )
    status: MeasurementStatusCode = Field(
        description="The status of the measurement.",
        min_length=1,
        max_length=1,
    )
    unit: str = Field(
        description="The unit of the measured value.",
        min_length=0,
        max_length=20,
    )
    value: float = Field(
        description="The measured value.",
    )
    highLimit: float | None = Field(
        default=None,
        description="The high limit. Used in less than comparisons.",
    )
    lowLimit: float | None = Field(
        default=None,
        description="The low limit. Used in greater than and equals comparisons.",
    )


class SequenceCall(BaseModel):
    """TODO: ADD DOCSTRING"""

    path: str = Field(
        description="The path to the sequence file.",
        min_length=1,
        max_length=500,
    )
    name: str = Field(
        description="The name of the sequence.",
        min_length=1,
        max_length=200,
    )
    version: str = Field(
        description="The version of the sequence file.",
        min_length=1,
        max_length=30,
    )


class StringMeasurement(BaseModel):
    """TODO: ADD DOCSTRING."""

    compOp: str = Field(
        description="The comparison operator used to compare the value to the limit.",
        min_length=1,
        max_length=10,
    )
    name: str | None = Field(
        default=None,
        description=(
            "The Name of the measurement. Required if there are multiple measurements in the same step."
            " Do not use if there is only one measurement in the step."
        ),
        min_length=0,
        max_length=100,
    )
    status: MeasurementStatusCode = Field(
        description="The status of the measurement.",
        min_length=1,
        max_length=1,
    )
    value: str = Field(
        description="The measured text value.",
        min_length=0,
        max_length=100,
    )

    limit: str | None = Field(
        default=None,
        description="The limit to compare the measured value to.",
        min_length=0,
        max_length=100,
    )


class SubUnit(BaseModel):
    """TODO: ADD DOCSTRING"""

    partType: str = Field(
        description="The type of sub unit.",
        min_length=1,
        max_length=50,
    )
    pn: str = Field(
        description="The partnumber of the sub unit.",
        min_length=1,
        max_length=100,
    )
    rev: str = Field(
        description="The revision of the sub unit.",
        min_length=0,
        max_length=100,
    )
    sn: str = Field(
        description="The serial number of the sub unit.",
        min_length=1,
        max_length=100,
    )


class UUT(BaseModel):
    """TODO: ADD DOCSTRING."""

    execTime: float | None = Field(
        default=None,
        description="The total time for the test to be executed.",
    )
    testSocketIndex: int | None = Field(
        default=None,
        description="The index of the test socket the unit was plugged into.",
    )
    batchSN: str | None = Field(
        default=None,
        description="The serial number of the batch the unit belongs to.",
        min_length=0,
        max_length=100,
    )
    comment: str | None = Field(
        default=None,
        description="A comment about the test.",
        min_length=0,
        max_length=5000,
    )
    errorCode: int | str | None = Field(
        default=None,
        description="The error code of the error that occurred during the test.",
    )
    errorMessage: str | None = Field(
        default=None,
        description="The error message of the error that occurred during the test.",
    )
    fixtureId: str | None = Field(
        default=None,
        description="The id of the fixture used to perform the test.",
        min_length=0,
        max_length=100,
    )
    user: str = Field(
        description="The operator of the test.",
        min_length=1,
        max_length=100,
    )
    batchFailCount: int | None = Field(
        default=None,
        description="The number of failed tests in the batch.",
    )
    batchLoopIndex: int | None = Field(
        default=None,
        description="The index in the batch loop.",
    )


# This is for excluding some members from the documentation
_classes: list[type[BaseModel]] = [
    AdditionalData,
    AdditionalDataArray,
    AdditionalDataArrayIndex,
    AdditionalDataProperty,
    Asset,
    Attachment,
    BooleanMeasurement,
    Chart,
    ChartSeries,
    MiscInfo,
    NumericMeasurement,
    SequenceCall,
    StringMeasurement,
    SubUnit,
    UUT,
]
_members_to_exclude = ["model_config"]

__pdoc__ = {f"{name.__name__}.{member}": False for name in _classes for member in _members_to_exclude}
