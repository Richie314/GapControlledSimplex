import pytest
from pulp import LpMinimize

from .lptest import LinearProgrammingTest
from gsimplex.solvers import (
    PrimalSimplex,
    DualSimplex,
    GapDoubleSimplex,
    MutualPrimalDualSimplex,
    MutualGapSimplex,
)


test_data = [
    LinearProgrammingTest(
        filename="problems/simple/01.mps",
        expected_solution=[5000.0/11, 2500.0/11, 5000.0/11],
        basis=["_C1", "_C4", "_C5"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/02.mps",
        expected_solution=[7, 3, 59.0/12],
        basis=["_C4", "_C5", "_C6"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/03.mps",
        expected_solution=[650.0/29, 1300.0/29, 1800.0/29],
        basis=["_C2", "_C6", "_C7"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/04.mps",
        expected_value=1_500,
        basis=["_C1", "_C5"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/05.mps",
        expected_solution=[350.0/23, 1090.0/23],
        basis=["_C2", "_C4"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/06.mps",
        expected_solution=[320.0/39, 268.0/39],
        basis=["_C5", "_C6"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/07.mps",
        expected_solution=[20.0/21, 3250.0/21, 470.0/21],
        basis=["_C4", "_C5", "_C6"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/08.mps",
        sense=LpMinimize,
        expected_value=11.0, # Problem has infinite solutions (two vertices)
        basis=["_C2", "_C3"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/09.mps",
        sense=LpMinimize,
        expected_solution=[90/7, 130/7],
        basis=["_C1", "_C4"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/10.mps",
        expected_solution=[87.5, 412.5, 2225.0/6, 1375.0/6],
        basis=["_C1", "_C2", "_C7", "_C9"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/11.mps",
        expected_solution=[23.125, 28.125],
        basis=["_C1", "_C5"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/12.mps",
        basis=["_C2", "_C5"],
    ),
    LinearProgrammingTest(
        filename="problems/simple/13.mps",
        expected_solution=[5300/43, 400/43],
        basis=["_C1", "_C5"],
    ),
]

"""
=============================================================
                      Primal Simplex
=============================================================
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
=============================================================
                    Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex_dantzig(test_case):
    solver = DualSimplex(max_iterations=20, pivot_rule="dantzig")
    test_case.test(solver, use_start_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex_bland(test_case):
    solver = DualSimplex(max_iterations=20, pivot_rule="bland")
    test_case.test(solver, use_start_basis=False)


"""
=============================================================
                  Gap-controlled Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_dantzig(test_case):
    solver = GapDoubleSimplex(pivot_rule="dantzig")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex_bland(test_case):
    solver = GapDoubleSimplex(pivot_rule="bland")
    test_case.test(solver)

"""
=============================================================
                 Mutual Primal-Dual Simplex
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_dantzig(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="dantzig")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_bland(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="bland")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_phase_I_dantzig(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="dantzig")
    test_case.test(solver, use_start_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_primaldual_simplex_phase_I_bland(test_case):
    solver = MutualPrimalDualSimplex(pivot_rule="bland")
    test_case.test(solver, use_start_basis=False)



@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_dantzig(test_case):
    solver = MutualGapSimplex(pivot_rule="dantzig")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_bland(test_case):
    solver = MutualGapSimplex(pivot_rule="bland")
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_phase_I_dantzig(test_case):
    solver = MutualGapSimplex(pivot_rule="dantzig")
    test_case.test(solver, use_start_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_mutual_gap_simplex_phase_I_bland(test_case):
    solver = MutualGapSimplex(pivot_rule="bland")
    test_case.test(solver, use_start_basis=False)

