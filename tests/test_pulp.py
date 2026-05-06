from pulp import LpVariable, LpConstraint

from gsimplex.vertex import DEFAULT_ABS_TOLERANCE

def test_dual_simplex():

    x = LpVariable("x")
    y = LpVariable("y")

    constraint = LpConstraint(x + y == 1)

    for (xVal, yVal) in [(.1, .1), (.3, .7), (1, 1)]:
        x.varValue = xVal
        y.varValue = yVal

        value = constraint.value()
        assert value is not None

        assert abs(value - (xVal + yVal - 1.0)) <= DEFAULT_ABS_TOLERANCE
    