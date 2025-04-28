"""Various enums used in the library."""

from enum import StrEnum


class AdditionalDataPropertyType(StrEnum):
    """Enum of valid property types for the AdditionalDataProperty class."""

    NUMBER = "Number"
    STRING = "String"
    BOOL = "Bool"
    OBJ = "Obj"
    ARRAY = "Array"


class BinaryCompOp(StrEnum):
    """Used in `WSJF.compare.compare_binary` to compare a value with a limit.

    \\(v\\) - the value to compare\n
    \\(a\\) - the limit to compare against
    """

    #: \\( v = a \\)
    EQUAL = "EQ"

    #: \\( v \\neq a \\)
    NOT_EQUAL = "NE"

    #: \\( v > a \\)
    GREATER_THAN = "GT"

    #: \\( v \\geq a \\)
    GREATER_OR_EQUAL = "GE"

    #: \\( v < a \\)
    LESS_THAN = "LT"

    #: \\( v \\leq a \\)
    LESS_OR_EQUAL = "LE"

    def as_symbol(self) -> str:
        """Returns the symbol for the operator.

        Example:
        ```
        >>> BinaryCompOp.GREATER_OR_EQUAL()
        '≥'
        ```

        """
        match self:
            case BinaryCompOp.EQUAL:
                return "="
            case BinaryCompOp.NOT_EQUAL:
                return "≠"
            case BinaryCompOp.GREATER_THAN:
                return ">"
            case BinaryCompOp.GREATER_OR_EQUAL:
                return "≥"
            case BinaryCompOp.LESS_THAN:
                return "<"
            case BinaryCompOp.LESS_OR_EQUAL:
                return "≤"
            case _:
                errmsg = f"Operator {self} not implemented."
                raise NotImplementedError(errmsg)


class ChartType(StrEnum):
    """Enum that defines which chart type to use.

    Used in `WSJF.sub_models.Chart`
    """

    #: Standard cartesian chart
    LINE = "LINE"
    #: Logarithmic X and Y axis
    LINELOGXY = "LineLogXY"
    #: Logarithmic X axis
    LINELOGX = "LineLogX"
    #: Logarithmic Y axis
    LINELOGY = "LineLogY"


class MeasurementStatusCode(StrEnum):
    """A measurement, as part of a step, can have these status codes.

    Used in these classes:

    * `WSJF.sub_models.BooleanMeasurement`
    * `WSJF.sub_models.NumericMeasurement`
    * `WSJF.sub_models.StringMeasurement`


    """

    #: WATS Code `P`
    PASSED = "P"

    #: WATS Code `F`
    FAILED = "F"

    #: WATS Code `S`
    SKIPPED = "S"


class StepStatusCode(StrEnum):
    """A step can have any of these status codes"""

    #: WATS Code `P`
    PASSED = "P"
    #: WATS Code `F`
    FAILED = "F"
    #: WATS Code `D`
    DONE = "D"
    #: WATS Code `E`
    ERROR = "E"
    #: WATS Code `T`
    TERMINATED = "T"
    #: WATS Code `S`
    SKIPPED = "S"


class StepType(StrEnum):
    """A step can be of these types."""

    #: WATS Code `SequenceCall`
    SEQUENCE_CALL = "SequenceCall"

    #: WATS Code `ET_NLT`
    NUMERIC_LIMIT_SINGLE = "ET_NLT"

    #: WATS Code `ET_MNLT`
    NUMERIC_LIMIT_MULTIPLE = "ET_MNLT"

    #: WATS Code `ET_SLT`
    STRING_VALUE_SINGLE = "ET_SVT"

    #: WATS Code `ET_MSVT`
    STRING_VALUE_MULTIPLE = "ET_MSVT"

    #: WATS Code `ET_PFT`
    BOOLEAN_VALUE_SINGLE = "ET_PFT"

    #: WATS Code `ET_MPFT`
    BOOLEAN_VALUE_MULTIPLE = "ET_MPFT"

    #: WATS Code `Chart`
    CHART = "Chart"

    #: WATS Code `Attachment`
    ATTACHMENT = "Attachment"  # Ditto.
    # CALL_EXE = "CallExe" # Not implemented yet.
    # MESSAGE_POPUP = "MessagePopup"  # Ditto.
    # ACTION = "Action"  # Ditto.


class StringCaseOp(StrEnum):
    """Used in `WSJF.compare.compare_case` to compare a string."""

    #: WATS Code `CASESENSIT`
    CASE_SENSITIVE = "CASESENSIT"

    #: WATS Code `IGNORECASE`
    IGNORECASE = "IGNORECASE"


class TernaryCompOp(StrEnum):
    """Used in `WSJF.compare.compare_ternary` to compare a value with two limits.

    \\(v\\) - the value to compare\n
    \\(a\\) - the "lower" limit to compare against\n
    \\(b\\) - the "upper" limit to compare against\n

    """

    GREATER_THAN_OR_LESS_THAN = "GTLT"  # Greater than low limit, less than high limit
    """
    \\(a < v < b\\)\n\n
    \\(v \\in (a, b)\\)
    """

    GREATER_EQUAL_OR_LESS_EQUAL = "GELE"  # Greater or equal than low limit, less or equal than high limit
    """
    \\(a \\leq v \\leq b\\)\n\n
    \\(v \\in [a, b]\\)
    """

    GREATER_EQUAL_OR_LESS_THAN = "GELT"  # Greater or equal than low limit, less than high limit
    """
    \\(a \\leq v < b\\)\n\n
    \\(v \\in [a, b)\\)
    """

    GREATER_THAN_OR_LESS_EQUAL = "GTLE"  # Greater than low limit, less or equal than high limit
    """
    \\(a < v \\leq b\\)\n\n
    \\(v \\in (a, b]\\)
    """

    LESS_THAN_OR_GREATER_THAN = "LTGT"  # Less than low limit, greater than high limit
    """
    \\(a > v > b\\)\n\n
    \\(v \\notin [a, b]\\)
    """

    LESS_EQUAL_OR_GREATER_EQUAL = "LEGE"  # Less or equal than low limit, greater or equal than high limit
    """
    \\(a \\geq v \\geq b\\)\n\n
    \\(v \\notin (a, b)\\)
    """

    LESS_EQUAL_OR_GREATER_THAN = "LEGT"  # Less or equal than low limit, greater than high limit
    """
    \\(a \\geq v < b\\)\n\n
    \\(v \\notin (a, b]\\)\n
    """

    LESS_THAN_OR_GREATER_EQUAL = "LTGE"  # Less than low limit, greater or equal than high limit
    """
    \\(v < a\\) or \\(v \\geq b\\)\n\n
    \\(v \\notin [a, b)\\)\n
    """

    def as_symbols(self) -> tuple[str, str]:
        """Returns a `tuple` with symbols of the ternary operator.

        E.g.:
        ```
        >>> TernaryCompOp.GREATER_THAN_OR_LESS_EQUAL.as_symbols()
        ('<', '≤')
        ```

        """
        match self:
            case TernaryCompOp.GREATER_THAN_OR_LESS_THAN:
                return "<", "<"
            case TernaryCompOp.GREATER_EQUAL_OR_LESS_EQUAL:
                return "≤", "≤"
            case TernaryCompOp.GREATER_EQUAL_OR_LESS_THAN:
                return "≤", "<"
            case TernaryCompOp.GREATER_THAN_OR_LESS_EQUAL:
                return "<", "≤"
            case TernaryCompOp.LESS_THAN_OR_GREATER_THAN:
                return ">", ">"
            case TernaryCompOp.LESS_EQUAL_OR_GREATER_EQUAL:
                return "≥", "≥"
            case TernaryCompOp.LESS_EQUAL_OR_GREATER_THAN:
                return "≥", ">"
            case TernaryCompOp.LESS_THAN_OR_GREATER_EQUAL:
                return ">", "≥"
            case _:
                errmsg = f"Operator {self} not implemented."
                raise NotImplementedError(errmsg)


class UUTStatusCode(StrEnum):
    """Enum of status codes for the report and root step.

    This is applicable to:

    * `WSJF.models.WATSReport`
    * `WSJF.models.WATSReport.root`

    **Note:** The report and root step **must** have the same status code.
    """

    #: WATS Code `P`
    PASSED = "P"
    #: WATS Code `F`
    FAILED = "F"
    #: WATS Code `E`
    ERROR = "E"
    #: WATS Code `T`
    TERMINATED = "T"
