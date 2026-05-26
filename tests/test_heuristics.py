import pytest
from .test_simple import test_data

from gsimplex.solvers import DualSimplex

"""
=============================================================
          dual-feasible point from primal-feasible
=============================================================
"""

@pytest.mark.parametrize("test_case", test_data)
def test_primal_to_dual_dantzig(test_case):
    if test_case.basis is None:
        pytest.skip("Test case doesn't have a starting basis")

    simplex = DualSimplex(pivot_rule='dantzig')

    v, _ = simplex.phase_one_solve(test_case._get_problem(), test_case.basis)
    assert v is not None
    assert v.is_dual_feasible()

@pytest.mark.parametrize("test_case", test_data)
def test_primal_to_dual_bland(test_case):
    if test_case.basis is None:
        pytest.skip("Test case doesn't have a starting basis")

    simplex = DualSimplex(pivot_rule='bland')

    v, _ = simplex.phase_one_solve(test_case._get_problem(), test_case.basis)
    assert v is not None
    assert v.is_dual_feasible()