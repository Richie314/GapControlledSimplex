from pulp import LpVariable, LpConstraint, LpProblem, LpMaximize
from pulp.constants import LpSolutionOptimal

from gsimplex.vertex import DEFAULT_ABS_TOLERANCE
from gsimplex.solvers.primal_simplex import PrimalSimplex


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


def test_primal_simplex_solver_solve_forwards_kwargs():
    x = LpVariable("x", lowBound=0, upBound=1)
    y = LpVariable("y", lowBound=0, upBound=1)

    problem = LpProblem("TestProblem", LpMaximize)
    problem.setObjective(x + y)
    assert problem.objective

    problem.addConstraint(x + y <= 2)
    problem.addConstraint(x <= 1)
    problem.addConstraint(y <= 1)
    problem.addConstraint(x >= 0)
    problem.addConstraint(y >= 0)

    basis = list(problem.constraints.values())[:2]
    solver = PrimalSimplex()

    status = problem.solve(solver, start_basis=basis, pivot_rule="bland")
    assert status == LpSolutionOptimal

    value = problem.objective.value()
    assert value is not None
    assert abs(value - 2.0) <= DEFAULT_ABS_TOLERANCE
    