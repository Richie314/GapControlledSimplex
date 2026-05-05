import pytest
from .test_linear_programming import LinearProgrammingTest
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapSimplex


'''
    LinearProgrammingTest(
        filename="demo/2.mps",
        expected_solution=[7, 3, 59.0/12],
        # basis=[3, 6, 7],
    ),
    LinearProgrammingTest(
        filename="demo/4.mps",
        expected_solution=[1000.0/3, 2000.0/3],
        # basis=[0, 4],
    ),
'''

test_data = [
    LinearProgrammingTest(
        filename="demo/1.mps",
        expected_solution=[5000.0/11, 2500.0/11, 5000.0/11],
        # basis=[0, 3, 4],
    ),
    LinearProgrammingTest(
        filename="demo/3.mps",
        expected_solution=[650.0/29, 1300.0/29, 1800.0/29],
        # basis=[1, 5, 6],
    ),
    LinearProgrammingTest(
        filename="demo/5.mps",
        expected_solution=[350.0/23, 1090.0/23],
        # basis=[1, 3],
    ),
    LinearProgrammingTest(
        filename="demo/6.mps",
        expected_solution=[320.0/39, 268.0/39],
        # basis=[4, 5],
    ),
    LinearProgrammingTest(
        filename="demo/7.mps",
        expected_solution=[20.0/21, 3250.0/21, 470.0/21],
        # basis=[3, 4, 5],
    ),
]


@pytest.mark.parametrize("test_case", test_data)
def test_dual_simplex(test_case):
    solver = DualSimplex()
    test_case.test(solver)

'''
@pytest.mark.parametrize("test_case", test_data)
def test_primal_simplex(test_case):
    solver = PrimalSimplex()
    test_case.test(solver)

@pytest.mark.parametrize("test_case", test_data)
def test_gap_simplex(test_case):
    solver = GapSimplex()
    test_case.test(solver)
'''