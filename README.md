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

- `pulp` compatible solver backend
- Gap-controlled primal/dual simplex algorithms
- Easy installation from PyPI or source
- Built-in benchmark downloader for Plato and Netlib test sets

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
It downloads the Plato and Netlib benchmark sets into a local directory, so you can test the solver on real LP problems.

By default, benchmark files are saved under the `benchmark/` directory in the current working directory. Plato files are stored in `benchmark/plato/`, and Netlib files are stored in `benchmark/netlib/`.

### Download all benchmarks

```bash
gsimplex-download-benchmarks
```

### Download only one benchmark set

```bash
gsimplex-download-benchmarks --plato True --netlib False
# or
gsimplex-download-benchmarks --plato False --netlib True
```

> Note: the CLI uses boolean flags for `--plato` and `--netlib`, so set the one you want to disable to `False`.

### Change the destination directory

```bash
gsimplex-download-benchmarks --dir benchmark
```

### Quiet mode

```bash
gsimplex-download-benchmarks --quiet
```

If you installed the package editable with `pip install -e .`, the command will be available immediately.
