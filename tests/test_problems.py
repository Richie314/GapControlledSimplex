import pytest
from pulp import getSolver

from .test_simple import test_data as simple_data
from .test_medium import test_data as medium_data

@pytest.mark.parametrize("test_case", simple_data)
def test_cbc_simple(test_case):
    cbc = getSolver('PULP_CBC_CMD')
    test_case.test_library(cbc, eps=5.0e-4)

@pytest.mark.parametrize("test_case", simple_data)
def test_gurobi_simple(test_case):
    gurobi = getSolver('GUROBI')
    test_case.test_library(gurobi)

@pytest.mark.parametrize("test_case", simple_data)
def test_cplex_simple(test_case):
    cplex = getSolver('CPLEX_PY')
    test_case.test_library(cplex)