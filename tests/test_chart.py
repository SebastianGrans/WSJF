import math
import random

from WSJF.compare import TernaryCompOp
from WSJF.enums import BinaryCompOp
from WSJF.models import ChartStep, MultipleNumericLimitStep, SequenceCallStep


def test_add_chart(step: SequenceCallStep):
    chart_step = step.add_test_step(
        "Chart step",
        ChartStep,
    )
    chart = chart_step.add_chart("trig functions", xlabel="t", ylabel="f(t)")

    x_values = [i * 0.1 for i in range(int((2 * math.pi) / 0.1) + 1)]
    y_values = [math.sin(x) for x in x_values]
    xdata = ";".join(map(str, x_values))
    ydata = ";".join(map(str, y_values))

    chart.add_series(
        name="y = sin(t)",
        xdata=xdata,
        ydata=ydata,
    )


def test_add_chart_to_sequence_call(step: SequenceCallStep):
    """Charts do not require to be added as a seperate test step.
    """
    chart = step.add_chart("sinewaves", xlabel="t", ylabel="sin(t)")

    x_values = [i * 0.1 for i in range(int((2 * math.pi) / 0.1) + 1)]
    y_values = [math.sin(x) for x in x_values]
    xdata = ";".join(map(str, x_values))
    ydata = ";".join(map(str, y_values))

    chart.add_series(
        name="y = sin(x)",
        xdata=xdata,
        ydata=ydata,
    )


def test_add_to_numeric_test_step(step: SequenceCallStep):
    """Charts can be added to numeric test steps.
    """
    numeric_step = step.add_test_step(
        "Numeric step",
        MultipleNumericLimitStep,
    )

    # Let's say we're measuring a 3.3V voltage rail over time
    # We have some limits on the mean, min, max, and standard deviation
    # In this case it would be very useful to use a MultipleNumericLimitStep
    # but also to add a chart to visualize the data

    # Let's first generate some data
    voltage = [random.gauss(3.28, 0.1) for _ in range(50)]
    time = [i * 0.1 for i in range(len(voltage))]

    # We can compute the mean, and standard deviation
    mean = sum(voltage) / len(voltage)
    stddev = (sum((x - mean) ** 2 for x in voltage) / len(voltage)) ** 0.5
    max_value = max(voltage)
    min_value = min(voltage)

    # The mean should be close to 3.3V
    mean_min = 3.15
    mean_max = 3.45
    numeric_step.compare_ternary(
        name="Mean",
        value=mean,
        low_limit=mean_min,
        high_limit=mean_max,
        operator=TernaryCompOp.GREATER_EQUAL_OR_LESS_EQUAL,
        unit="V",
    )

    # We want the voltage to be stable,
    numeric_step.compare_binary(
        name="Standard deviation",
        value=stddev,
        limit=0.1,
        operator=BinaryCompOp.LESS_OR_EQUAL,
        unit="V",
    )

    # We allow the voltage to sometimes spike to 3.5V
    max_limit = 3.5
    numeric_step.compare_binary(
        name="Max",
        value=max_value,
        limit=max_limit,
        operator=BinaryCompOp.LESS_OR_EQUAL,
        unit="V",
    )

    # We also allow the voltage to sometimes drop to 3.1V
    min_limit = 3.1
    numeric_step.compare_binary(
        name="Min",
        value=min_value,
        limit=min_limit,
        operator=BinaryCompOp.GREATER_OR_EQUAL,
        unit="V",
    )

    chart = step.add_chart("Voltage", xlabel="t", ylabel="V")

    voltage_string = ";".join(map(str, voltage))
    time_string = ";".join(map(str, time))

    chart.add_series(
        name="y = sin(x)",
        xdata=time_string,
        ydata=voltage_string,
    )

    # If we want to be extra fancy, we can even add the limits to the chart
    time_min_max = f"{min(time)};{max(time)}"
    mean_min_string = f"{mean_min};{mean_min}"
    mean_max_string = f"{mean_max};{mean_max}"
    max_limit_string = f"{max_limit};{max_limit}"
    min_limit_string = f"{min_limit};{min_limit}"

    chart.add_series(
        name="Mean min",
        xdata=time_min_max,
        ydata=mean_min_string,
    )
    chart.add_series(
        name="Mean max",
        xdata=time_min_max,
        ydata=mean_max_string,
    )
    chart.add_series(
        name="Min",
        xdata=time_min_max,
        ydata=min_limit_string,
    )
    chart.add_series(
        name="Max",
        xdata=time_min_max,
        ydata=max_limit_string,
    )
