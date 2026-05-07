import pytest
from .lptest import LinearProgrammingTest
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
#from gsimplex.solvers.gap_simplex import GapSimplex


test_data = [
    LinearProgrammingTest(
        filename="demo/1.mps",
        expected_solution=[5000.0/11, 2500.0/11, 5000.0/11],
        basis=["_C1", "_C4", "_C5"],
    ),
    LinearProgrammingTest(
        filename="demo/2.mps",
        expected_solution=[7, 3, 59.0/12],
        basis=["_C4", "_C5", "_C6"],
    ),
    LinearProgrammingTest(
        filename="demo/3.mps",
        expected_solution=[650.0/29, 1300.0/29, 1800.0/29],
        basis=["_C2", "_C6", "_C7"],
    ),
    LinearProgrammingTest(
        filename="demo/4.mps",
        expected_solution=[1000.0/3, 2000.0/3],
        basis=["_C1", "_C5"],
    ),
    LinearProgrammingTest(
        filename="demo/5.mps",
        expected_solution=[350.0/23, 1090.0/23],
        basis=["_C2", "_C4"],
    ),
    LinearProgrammingTest(
        filename="demo/6.mps",
        expected_solution=[320.0/39, 268.0/39],
        basis=["_C5", "_C6"],
    ),
    LinearProgrammingTest(
        filename="demo/7.mps",
        expected_solution=[20.0/21, 3250.0/21, 470.0/21],
        basis=["_C4", "_C5", "_C6"],
    ),
]

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex(test_case):
    solver = PrimalSimplex()
    test_case.test(solver, pivot='dantzig')

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex(test_case):
    solver = DualSimplex(max_iterations=20)
    test_case.test(solver, use_start_basis=False, pivot='bland')

'''
@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex(test_case):
    solver = PrimalSimplex()
    test_case.test(solver, pivot='bland')

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex(test_case):
    solver = DualSimplex(max_iterations=20)
    test_case.test(solver, use_start_basis=False, pivot='bland')

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex(test_case):
    solver = GapSimplex()
    test_case.test(solver)
'''