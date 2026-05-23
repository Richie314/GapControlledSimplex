# Gap controlled Simplex

[![Test and publish package](https://github.com/Richie314/GapControlledSimplex/actions/workflows/pypi.yml/badge.svg)](https://github.com/Richie314/GapControlledSimplex/actions/workflows/pypi.yml)
[![PyPI - Version](https://img.shields.io/pypi/v/gsimplex)](https://pypi.org/project/gsimplex/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gsimplex)](https://pypi.org/project/gsimplex/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gsimplex)](https://pypi.org/project/gsimplex/)
[![License](https://img.shields.io/pypi/l/gsimplex)](https://github.com/Richie314/GapControlledSimplex/blob/main/LICENSE)

`gsimplex` is a lightweight Python package that implements a simplex solver governed by the primal-dual gap.
It integrates directly with [pulp](https://coin-or.github.io/pulp/) and uses [numpy](https://numpy.org/) for its linear algebra routines.
The current release supports continuous linear programming problems; mixed-integer support may be added in a future version.

## Features

This package provides three main solver implementations in `gsimplex.solvers`:

- [`PrimalSimplex`](./src/gsimplex/solvers/primal_simplex.py)
  - Standard primal simplex algorithm.
  - Parameters:
    - `max_iterations`: maximum number of simplex iterations (default configured by package).
    - `abs_eps`: absolute tolerance used for feasibility and optimality checks.
    - `rel_eps`: relative tolerance for numerical comparisons.
    - `pivot_rule`: pivot selection strategy, typically `"dantzig"` by default; use `"bland"` to avoid cycling.

- [`DualSimplex`](./src/gsimplex/solvers/dual_simplex.py)
  - Dual simplex algorithm for problems with a dual-feasible starting basis.
  - Parameters:
    - `max_iterations`: maximum number of simplex iterations.
    - `abs_eps`: absolute tolerance for primal/dual feasibility checking.
    - `rel_eps`: relative tolerance for numerical comparisons.
    - `pivot_rule`: pivot selection strategy, with `"bland"` available for Bland's rule.

- [`GapDoubleSimplex`](./src/gsimplex/solvers/gap_simplex.py)
  - Combined primal/dual gap-controlled solver.
  - Runs primal and dual simplex iterations together and stops when the primal-dual gap is small enough.
  - Parameters:
    - `max_iterations`: maximum total iterations before giving up.
    - `abs_eps`: absolute tolerance for feasibility and basis checks.
    - `rel_eps`: relative tolerance for numerical comparisons.
    - `abs_gap`: absolute gap threshold for early termination.
    - `rel_gap`: relative gap threshold for early termination.
    - `pivot_rule`: pivot selection strategy for both primal and dual steps.

## Installation

Install from PyPI:

```bash
python -m pip install gsimplex
```

Install from source for local development:

```bash
git clone https://github.com/Richie314/GapControlledSimplex.git
cd GapControlledSimplex
python -m pip install -e .
python -m pip install -e .[dev]
```

Run the test suite with:

```bash
python -m pytest
```

## Usage
```python
from pulp import LpVariable, LpProblem, LpMaximize
from gsimplex.solvers import PrimalSimplex

x1 = LpVariable("x1", lowBound=0, upBound=1)
x2 = LpVariable("x2", lowBound=0, upBound=3)

problem = LpProblem("Problem", LpMaximize)
problem += x1 + x2
problem += x1 + x2 <= 2
problem += x1 <= 1
problem += x2 <= 3
problem += x1 >= 0
problem += x2 >= 0

solver = PrimalSimplex()
problem.solve(solver)

print("Optimal value:", problem.objective.value()) # 2.0
print("Solution:", [var.varValue for var in problem.variables()]) # [1.0, 1.0]
```

## Download benchmark problems

This package installs a command-line helper called `gsimplex-download-benchmarks`.
It can download [Plato](https://plato.asu.edu/ftp/lptestset/), [Netlib](https://www.netlib.org/lp/data/) and [MipLib](https://miplib.zib.de/index.html) benchmark sets into a local directory, so you can test the solver on real LP problems.

By default, benchmark files are saved under the `benchmark/` directory in the current working directory.
Plato files are stored in `benchmark/plato/`, Netlib files are stored in `benchmark/netlib/` and MipLib files are stored in `benchmark/miplib/`.

A script is provided to download the desired benchmarks.

```bash
# Will download only Plato benchmarks
gsimplex-download-benchmarks --plato

# Will download only Netlib benchmarks
gsimplex-download-benchmarks --netlib

# Will download both Plato and MipLib benchmarks
gsimplex-download-benchmarks --plato --miplib
```

### Change the destination directory

```bash
gsimplex-download-benchmarks --plato --dir benchmark
```

### Quiet mode

```bash
gsimplex-download-benchmarks --plato --quiet
```

If you installed the package editable with `pip install -e .`, the command will be available immediately.
