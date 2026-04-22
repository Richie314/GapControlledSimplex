import pytest
from .test_linear_programming import LinearProgrammingTest
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapSimplex

test_data = [
    LinearProgrammingTest(
        [5000.0/11, 2500.0/11, 5000.0/11],
        [0, 3, 4],
        [4.0, 5.0, 2.0],
        [0.0, 0.6, 0.8, 500.0],
        [-1.0, 2.0, 0.0, 0.0],
        [1.0, 0.0, -1.0, 0.0]
    ),
    LinearProgrammingTest(
        [320.0/39, 268.0/39],
        [4, 5],
        [8.0, 12.0],
        [0.7, 1.0, 15.0],
        [2.5, 4.0, 48.0],
        [4.0, 2.5, 50.0],
        [1.5, 1.25, 25.0],
        [-1.0, 0.0, -6.0],
        [0.0, -1.0, -6.0]
    ),
    LinearProgrammingTest(
        [7, 3, 59.0/12],
        [3, 6, 7],
        [6.0, 20.0, 15.0],
        [-1.0, 0.0, 0.0, -7.0],
        [0.0, 1.0, 0.0, 3.0],
        [0.2, 0.5, 0.4, 6.0],
        [0.3, 0.65, 0.6, 7.0],
        [0.12, 0.45, 0.2, 7.0]
    ),
    LinearProgrammingTest(
        [350.0/23, 1090.0/23],
        [1, 3],
        [250, 300],
        [1.9, 1.5, 100.0],
        [0.5, 1.0, 55.0],
        [1.0, -0.5, 0.0]
    ),
    LinearProgrammingTest(
        [650.0/29, 1300.0/29, 1800.0/29],
        [1, 5, 6],
        [100.0, 80.0, 60.0],
        [6.0, 5.0, 4.0, 1000.0],
        [4.0, 2.0, 10.0, 800.0],
        [4.0, 5.0, 3.0, 500.0],
        [2.0, -1.0, 0.0, 0.0],
        [-0.4, 0.6, -0.4, 0.0]
    ),
    LinearProgrammingTest(
        [20.0/21, 3250.0/21, 470.0/21],
        [3, 4, 5],
        [14.0, 20.0, 16.0],
        [1.0, 3.0, 2.0, 510.0],
        [1.0, 2.0, 4.0, 400.0],
        [3.0, 1.0, 1.0, 180.0]
    ),
    LinearProgrammingTest(
        [1000.0/3, 2000.0/3],
        [0, 4],
        [1200, 1500],
        [1.5, 1.5, 1500],
        [0.8, 1.0, 2000],
        [1.0, 2.2, 1800]
    ),
]

@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex(test_case):
    solver = PrimalSimplex()
    test_case.test(solver, use_starting_basis=True)
    test_case.test(solver, use_starting_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex(test_case):
    solver = DualSimplex()
    test_case.test(solver, use_starting_basis=False)

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex(test_case):
    solver = GapSimplex()
    test_case.test(solver, use_starting_basis=True)
    test_case.test(solver, use_starting_basis=False)