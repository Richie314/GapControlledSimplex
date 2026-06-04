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

rel_eps = 1.0e-6
abs_eps = 5.0e-4

test_data = [
    LinearProgrammingTest(
        filename="problems/medium/10x02.mps",
        sense=LpMaximize,
        # expected_value=8_068.4059, # best integer solution
        expected_value=17_312.2558, # best continuous solution
    ),
]

"""
=============================================================
                  Primal and Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex(test_case):
    solver = PrimalSimplex(abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex_dantzig(test_case):
    solver = DualSimplex(abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)


"""
=============================================================
                  Gap-controlled Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_dantzig(test_case):
    solver = GapDoubleSimplex(pivot_rule="dantzig", abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_bland(test_case):
    solver = GapDoubleSimplex(pivot_rule="bland", abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)

"""
=============================================================
                 Mutual Primal-Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex(test_case):
    solver = MutualPrimalDualSimplex( abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex(test_case):
    solver = MutualGapSimplex(abs_eps=abs_eps, rel_eps=rel_eps)
    test_case.test(solver)

