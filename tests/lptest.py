import numpy as np
from typing import Union, List, Optional
from pulp import (
    LpProblem, LpConstraint,
    LpSolutionOptimal, LpMaximize,
)
from pathlib import Path

from gsimplex.vertex import Vertex
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.constants import (
    DEFAULT_ABS_TOLERANCE, 
    DEFAULT_REL_TOLERANCE,
)
from gsimplex.tools import ProblemParser, get_objective_function

class LinearProgrammingTest:
    def __init__(self, 
                 filename: Union[Path, str],
                 expected_solution: Optional[Union[np.ndarray, List[float]]] = None, 
                 expected_value: Optional[float] = None,
                 basis: Optional[Union[Vertex, List[LpConstraint], List[str]]] = None,
                 sense: int = LpMaximize,
                 ):
        self.expected_solution = np.array(expected_solution) if expected_solution is not None else None
        self.expected_value = expected_value
        self.basis = basis

        filename = Path("tests") / filename
        assert filename.exists(), f"Problem {filename} not found!"

        self.problem: LpProblem = ProblemParser.load_mps_from_file(filename, sense=sense)


        if self.basis is not None:
            assert self.problem.numVariables() == len(self.basis)

        if self.expected_solution is not None:
            assert self.problem.numVariables() == len(self.expected_solution)
            if self.expected_value is None:
                obj = get_objective_function(self.problem)
                self.expected_value = obj @ self.expected_solution

        for constraint in list(self.problem.constraints.values()):
            assert constraint.name

    def test(self, solver: ISolver, use_start_basis: bool = True):
        self.problem.solve(solver, 
                           start_basis=self.basis if use_start_basis else None, 
                           )
        assert self.problem.status == LpSolutionOptimal, "Problem was not solved"

        assert self.problem.objective
        value = self.problem.objective.value()
        assert value is not None

        optimal_basis = Vertex.from_problem_state(self.problem)
        assert len(optimal_basis) == self.problem.numVariables()
        optimal_basis = Vertex(self.problem, *optimal_basis)
        assert optimal_basis.is_primal_feasible(), f"Final point is not primal-feasible. {optimal_basis}"
        assert optimal_basis.is_dual_feasible(), f"Final point is not dual-feasible. {optimal_basis}"

        if self.expected_value is not None:
            slack = abs(value - self.expected_value)
            assert slack < DEFAULT_ABS_TOLERANCE, f"Too big distance to known optimal value: {slack:.4} = |{value} - {self.expected_value}|. {optimal_basis}"
            
        if self.expected_solution is not None:
            for i in range(self.problem.numVariables()):
                x_Val = self.problem.variables()[i].varValue

                assert x_Val is not None
                slack = abs(x_Val - self.expected_solution[i])
                assert slack <= 2*DEFAULT_ABS_TOLERANCE, f"Too distance in optimal point: {slack:.4} = |{x_Val} - {self.expected_solution[i]}| {optimal_basis}"

