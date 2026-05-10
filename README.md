# Gap controlled Simplex

[![Test and publish package](https://github.com/Richie314/GapControlledSimplex/actions/workflows/pypi.yml/badge.svg)](https://github.com/Richie314/GapControlledSimplex/actions/workflows/pypi.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/gsimplex)](https://pypi.org/project/gsimplex/)

`gsimplex` is a python implementation of a linear programming problem solver controlled by the primal-dual gap.
It is provided as a solver to use in conjunction with the [pulp](https://coin-or.github.io/pulp/) library and is backed by [numpy](https://numpy.org/) for linear algebra.
Right now, the solver only supporst continuous variables, but support for also integer and boolean ones will hopefully come in the future.

## Installation

You can install the package via [PyPi](https://pypi.org/project/gsimplex/)
```bash
pip install gsimplex
```

It is also possible to install via this repo
```bash
git clone https://github.com/Richie314/GapControlledSimplex.git
cd GapControlledSimplex
pip install -e .
```

After that, you can run a few basic tests using [PyTest](https://docs.pytest.org/en/stable/) (`pip install pytest`)
```bash
pytest
```

## Usage
```python
from pulp import LpVariable, LpProblem, LpMaximize
from pulp.constants import LpSolutionOptimal
from gsimplex.solvers import PrimalSimplex

x1 = LpVariable("x1", lowBound=0, upBound=1)
x2 = LpVariable("x2", lowBound=0, upBound=3)

problem = LpProblem("Problem", LpMaximize)
problem += x1 + x2
problem += x1 + x2 <=2
problem += x1 <= 1
problem += x2 <= 3
problem += x1 >= 0
problem += x2 >= 0

solver = PrimalSimplex()
problem.solve(solver)

print("Optimal solution: ", problem.objective.value())
print("Optimal vector: ", list(problem.variables()))
```

## Download test problems
