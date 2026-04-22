from typing import Optional, Tuple, List

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solution import Solution

class GapSimplex(IterativeSolver, ISimplex):
    def __init__(self):
        super().__init__()
        self._primal_simplex = PrimalSimplex()
        self._dual_simplex = DualSimplex()

    def maximize(self, problem: Problem, start_basis: Optional[List[int]] = None) -> Optional[Solution]:
        primal_vertex, initial_primal = self.get_starting_point(problem, start_basis)
        dual_vertex, initial_dual = self._dual_simplex.get_starting_point(problem)

        if (primal_vertex is None or not primal_vertex.is_primal_feasible() or
            dual_vertex is None or not dual_vertex.is_dual_feasible()):
            return None

        primal_iterations = 0
        dual_iterations = 0

        while (not primal_vertex.is_optimal_point() and self._check_iteration_count(primal_iterations) and
               not dual_vertex.is_optimal_point() and self._check_iteration_count(dual_iterations)):

            gap, rel_gap, dual_val, primal_val = Vertex.gap(dual_vertex, primal_vertex)

            print(f"Gap: {gap} = {dual_val} - {primal_val}")
            if rel_gap is not None:
                print(f"Relative gap: {rel_gap}")

            if primal_vertex.is_primal_degenerate():
                new_primal = self._primal_simplex.make_feasible(dual_vertex)
                if new_primal is not None and new_primal.primal_value() > primal_val:
                    primal_vertex = new_primal

            if dual_vertex.is_dual_degenerate():
                new_dual = self._dual_simplex.make_feasible(primal_vertex)
                if new_dual is not None and new_dual.dual_value() < dual_val:
                    dual_vertex = new_dual

            primal_vertex = PrimalSimplex.iteration(primal_vertex)
            if primal_vertex is None or primal_vertex.is_optimal_point():
                break
            primal_iterations += 1

            dual_vertex = DualSimplex.iteration(dual_vertex)
            if dual_vertex is None or dual_vertex.is_optimal_point():
                break
            dual_iterations += 1

        if primal_vertex is None or dual_vertex is None:
            return None

        optimal_point = primal_vertex if primal_vertex.is_optimal_point() else dual_vertex
        return Solution(
            point=optimal_point,
            iteration_count=max(primal_iterations, dual_iterations),
            initial_iterations=initial_primal + initial_dual
        )

    def get_feasible_vertex(self, problem: Problem) -> Optional[Tuple[Vertex, int]]:
        return self._primal_simplex.get_feasible_vertex(problem)

    def get_starting_point(self, problem: Problem, given_basis: Optional[List[int]] = None) -> Tuple[Optional[Vertex], int]:
        return self._primal_simplex.get_starting_point(problem, given_basis)

    def make_feasible(self, vertex: Vertex) -> Optional[Vertex]:
        raise NotImplementedError()