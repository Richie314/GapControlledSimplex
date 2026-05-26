import numpy as np
from typing import Union, List, Optional
from pulp import (
    LpProblem, LpConstraint, LpSolver,
    LpSolutionOptimal, LpMaximize,
    getSolver,
)
from pathlib import Path

from gsimplex.vertex import Vertex
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.tools import ProblemParser, get_objective_function, clone_problem
from gsimplex.constants import DEFAULT_ABS_TOLERANCE

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

        self.__problem: LpProblem = ProblemParser.load_mps_from_file(filename, sense=sense)


        if self.basis is not None:
            assert self.__problem.numVariables() == len(self.basis)

        if self.expected_solution is not None:
            assert self.__problem.numVariables() == len(self.expected_solution)
            if self.expected_value is None:
                obj = get_objective_function(self.__problem)
                self.expected_value = float(obj @ self.expected_solution)

        for constraint in list(self.__problem.constraints.values()):
            assert constraint.name

    def _get_problem(self) -> LpProblem:
        return clone_problem(self.__problem)

    def _check_result(self,  p: LpProblem, eps: float) -> float:
        assert p.status == LpSolutionOptimal

        n = p.numVariables()

        assert p.objective
        value = p.objective.value()
        assert value is not None

        optimal_basis = Vertex.from_problem_state(p, eps)
        optimal_basis = Vertex(p, *optimal_basis[:n])
        assert optimal_basis.is_primal_feasible(eps), f"Final point is not primal-feasible. {optimal_basis}"
        assert optimal_basis.is_dual_feasible(eps), f"Final point is not dual-feasible. {optimal_basis}"

        if self.expected_value is not None:
            slack = abs(value - self.expected_value)
            assert slack < eps, f"Too big distance to known optimal value: {slack:.4} = |{value} - {self.expected_value}|. {optimal_basis}"
            
        if self.expected_solution is not None:
            for i, var in enumerate(p.variables()):
                x_Val = var.varValue

                assert x_Val is not None
                slack = abs(x_Val - self.expected_solution[i])
                assert slack <= 2*eps, f"Too distance in optimal point: {slack:.4} = |{x_Val} - {self.expected_solution[i]}| {optimal_basis}"
        
        return value


    def test(self, solver: ISolver, use_start_basis: bool = True):
        p = self._get_problem()
        p.solve(solver, start_basis=self.basis if use_start_basis else None)
        return self._check_result(eps=solver.abs_tol, p=p)

    def test_library(self, solver: Optional[LpSolver] = None, eps: float = DEFAULT_ABS_TOLERANCE):
        p = self._get_problem()

        if solver is None:
            solver = getSolver('GUROBI')

        p.solve(solver)
        return self._check_result(eps=eps, p=p)
    
    def test_with_optimal_detection(self, solver: ISolver, use_start_basis: bool = True):
        p = self._get_problem()

        # If we don't have an expected value, try to get it from the library solver
        if self.expected_value is None:
            gurobi = getSolver('GUROBI')
            p.solve(gurobi)
            assert p.status == LpSolutionOptimal, "Library solver did not find an optimal solution."

            c = get_objective_function(p)
            self.expected_value = float(c @ [v.varValue for v in p.variables()])

        p.solve(solver, start_basis=self.basis if use_start_basis else None)
        return self._check_result(eps=solver.abs_tol, p=p)
