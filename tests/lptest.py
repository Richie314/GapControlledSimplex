import numpy as np
from typing import Union, List, Optional
from pulp import LpProblem, LpConstraint
from pulp.constants import LpSolutionOptimal, LpMaximize
from pathlib import Path

from gsimplex.vertex import Vertex
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.constants import (
    DEFAULT_ABS_TOLERANCE, 
    DEFAULT_REL_TOLERANCE,
    PivotRule, 
    DEFAULT_PIVOT_RULE,
)
from gsimplex.tools.parser import ProblemParser

class LinearProgrammingTest:
    def __init__(self, 
                 filename: Union[Path, str],
                 expected_solution: Optional[Union[np.ndarray, List[float]]] = None, 
                 expected_value: Optional[float] = None,
                 basis: Optional[Union[Vertex, List[LpConstraint], List[str]]] = None,
                 ):
        self.expected_solution = np.array(expected_solution) if expected_solution is not None else None
        self.expected_value = expected_value
        self.basis = basis

        filename = Path("tests") / filename
        assert filename.exists(), f"Problem {filename} not found!"

        self.problem: LpProblem = ProblemParser.load_mps_from_file(filename, sense=LpMaximize)
        assert self.problem.numConstraints() >= self.problem.numVariables()

        if self.basis is not None:
            assert self.problem.numVariables() == len(self.basis)

        if self.expected_solution is not None:
            assert self.problem.numVariables() == len(self.expected_solution)
            if self.expected_value is None:
                c = Vertex.get_objective_function(self.problem)
                self.expected_value = c @ self.expected_solution

        for constraint in list(self.problem.constraints.values()):
            assert constraint.name

    def test(self, solver: ISolver, use_start_basis: bool = True, pivot: PivotRule = DEFAULT_PIVOT_RULE):
        self.problem.solve(solver, 
                           start_basis=self.basis if use_start_basis else None, 
                           pivot_rule=pivot
                           )
        assert self.problem.status == LpSolutionOptimal, "Problem was not solved"

        assert self.problem.objective
        value = self.problem.objective.value()
        assert value is not None

        if self.expected_value is not None:
            slack = abs(value - self.expected_value)
            assert slack < DEFAULT_ABS_TOLERANCE, f"Too big solution gap: {slack:.4} = |{value} - {self.expected_value}|"
            
        if self.expected_solution is not None:
            for i in range(self.problem.numVariables()):
                x_Val = self.problem.variables()[i].varValue

                assert x_Val is not None
                slack = abs(x_Val - self.expected_solution[i])
                assert slack <= 2*DEFAULT_ABS_TOLERANCE, f"Too big solution gap: {slack:.4} = |{x_Val} - {self.expected_solution[i]}|"

