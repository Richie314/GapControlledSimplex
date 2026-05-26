import pytest
from pulp import LpMaximize, LpMinimize

from .lptest import LinearProgrammingTest
from gsimplex.solvers import (
    PrimalSimplex,
    DualSimplex,
    GapDoubleSimplex,
    MutualGapSimplex,
    MutualPrimalDualSimplex,
)

test_data = [
]

"""
=============================================================
                      Primal Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_dantzig(test_case):
    solver = PrimalSimplex(pivot_rule="dantzig")
    test_case.test_with_optimal_detection(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex_bland(test_case):
    solver = PrimalSimplex(pivot_rule="bland")
    test_case.test_with_optimal_detection(solver)


"""
=============================================================
                    Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex_dantzig(test_case):
    solver = DualSimplex(pivot_rule="dantzig")
    test_case.test_with_optimal_detection(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex_bland(test_case):
    solver = DualSimplex(pivot_rule="bland")
    test_case.test_with_optimal_detection(solver)


"""
=============================================================
                  Gap-controlled Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_dantzig(test_case):
    solver = GapDoubleSimplex(pivot_rule="dantzig")
    test_case.test_with_optimal_detection(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_bland(test_case):
    solver = GapDoubleSimplex(pivot_rule="bland")
    test_case.test_with_optimal_detection(solver)

"""
=============================================================
                 Mutual Primal-Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_dantzig(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="dantzig")
    test_case.test_with_optimal_detection(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_bland(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="bland")
    test_case.test_with_optimal_detection(solver)


@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_dantzig(test_case):
    solver = MutualGapSimplex(pivot_rule="dantzig")
    test_case.test_with_optimal_detection(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_bland(test_case):
    solver = MutualGapSimplex(pivot_rule="bland")
    test_case.test_with_optimal_detection(solver)
