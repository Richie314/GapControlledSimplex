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
abs_eps = 5.0e-3

test_data = [
    LinearProgrammingTest(
        filename="problems/medium/10x02.mps",
        sense=LpMaximize,
        expected_value=8_068.4059,
    ),
    LinearProgrammingTest(
        filename="problems/medium/10x04.mps",
        sense=LpMinimize,
        expected_value=468.1287,
    ),
    LinearProgrammingTest(
        filename="problems/medium/13x05.mps",
        sense=LpMaximize,
        expected_value=3120.5018,
    ),
    LinearProgrammingTest(
        filename="problems/medium/21x08.mps",
        sense=LpMinimize,
        expected_value=319.4278,
    ),
    LinearProgrammingTest(
        filename="problems/medium/34x15.mps",
        sense=LpMinimize,
        expected_value=264.0395,
    ),
    LinearProgrammingTest(
        filename="problems/medium/34x15.mps",
        sense=LpMaximize,
        expected_value=3_195.6684,
    ),
    LinearProgrammingTest(
        filename="problems/medium/28x21.mps",
        sense=LpMaximize,
        expected_value=673.5980,
    ),
    # LinearProgrammingTest(
    #     filename="problems/medium/47x45.mps",
    #     sense=LpMaximize,
    #     expected_value=,
    # ),
    # LinearProgrammingTest(
    #     filename="problems/medium/65x56.mps",
    #     sense=LpMaximize,
    #     expected_value=16192.0848,
    # ),
    # LinearProgrammingTest(
    #     filename="problems/medium/88x73.mps",
    #     sense=LpMaximize,
    #     expected_value=15_370.6017,
    # ),
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

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex(test_case):
    solver = GapDoubleSimplex(abs_eps=abs_eps, rel_eps=rel_eps)
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

