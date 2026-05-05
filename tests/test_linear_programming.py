import numpy as np
from typing import Union, List, Optional
from pulp import LpProblem, LpConstraint
from pulp.constants import LpSolutionOptimal
from pathlib import Path

from gsimplex.vertex import Vertex, DEFAULT_ABS_TOLERANCE
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.tools.parser import ProblemParser

class LinearProgrammingTest:
    def __init__(self, 
                 filename: Union[Path, str],
                 expected_solution: Optional[Union[np.ndarray, List[float]]] = None, 
                 expected_value: Optional[float] = None,
                 basis: Optional[Union[Vertex, List[LpConstraint]]] = None
                 ):
        self.expected_solution = np.array(expected_solution) if expected_solution is not None else None
        self.expected_value = expected_value
        self.basis = basis

        filename = Path("tests") / filename
        assert filename.exists(), f"Problem {filename} not found!"

        self.problem: LpProblem = ProblemParser.load_mps_from_file(filename)
        assert self.problem.numConstraints() >= self.problem.numVariables()

        if self.basis is not None:
            assert self.problem.numVariables() == len(self.basis)

        if self.expected_solution is not None:
            assert self.problem.numVariables() == len(self.expected_solution)
            #if self.expected_value is None:
            #    self.expected_value = self.problem.c @ self.expected_solution

    def test(self, solver: ISolver):
        self.problem.solve(solver, start_basis=self.basis)
        assert self.problem.status == LpSolutionOptimal

        assert self.problem.objective
        value = self.problem.objective.value()
        assert value is not None

        if self.expected_value is not None:
            assert abs(value - self.expected_value) < DEFAULT_ABS_TOLERANCE
