import pytest
from pulp.constants import LpMaximize, LpMinimize

from .lptest import LinearProgrammingTest
from gsimplex.solvers import (
    PrimalSimplex,
    DualSimplex,
    GapDoubleSimplex,
    CrissCross,
)

"""
test_data = [
    LinearProgrammingTest(
        filename="problems/transportation.mps",
        sense=LpMinimize,
        expected_value=39500,
    ),
    LinearProgrammingTest(
        filename="problems/transport-multi-commodity.mps",
        sense=LpMinimize,
        expected_value=26175,
    ),
    LinearProgrammingTest(
        filename="problems/transhipment.mps",
        sense=LpMinimize,
        expected_value=114960,
    ),
    LinearProgrammingTest(
        filename="problems/shortest-path.mps",
        sense=LpMinimize,
        expected_value=22,
    ),
    LinearProgrammingTest(
        filename="problems/emptyRuns.mps",
        sense=LpMinimize,
        expected_value=420,
    ),
]
"""

"""
=============================================================
                      Primal Simplex
=============================================================
"""

"""

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_dantzig(test_case):
    solver = PrimalSimplex(pivot_rule="dantzig")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_bland(test_case):
    solver = PrimalSimplex(pivot_rule="bland")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_phase_I_dantzig(test_case):
    solver = PrimalSimplex(pivot_rule="dantzig")
    test_case.test(solver, use_start_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_phase_I_bland(test_case):
    solver = PrimalSimplex(pivot_rule="bland")
    test_case.test(solver, use_start_basis=False)
"""