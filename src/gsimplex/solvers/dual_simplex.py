import numpy as np
from typing import Optional, Tuple, List

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solution import Solution

class DualSimplex(IterativeSolver, ISimplex):
    @staticmethod
    def iteration(vertex: Vertex) -> Optional[Vertex]:
        if not vertex.is_dual_feasible():
            return None

        if vertex.is_primal_feasible():
            return vertex  # Optimal

        # Entering index (Bland rule)
        infeas = vertex.primal_infeasible_rows()
        if not infeas:
            return vertex
        k, _ = infeas[0]

        Ak = vertex.problem.A[k]

        # Leaving index (Minimum ratio + Bland rule)
        ratios = []
        for i in vertex.basis:
            idx = np.where(vertex.basis == i)[0][0]
            den = Ak @ vertex.W[:, idx]
            if den < -Vertex.ABSOLUTE_TOLERANCE:
                ratios.append((i, -vertex.y[i] / den))

        if not ratios:
            return None  # Unbounded

        ratios.sort(key=lambda x: x[1])
        h, _ = ratios[0]

        new_basis = np.setdiff1d(vertex.basis, [h])
        new_basis = np.append(new_basis, k)

        return Vertex(vertex.problem, new_basis)

    def maximize(self, problem: Problem, start_basis: Optional[List[int]] = None) -> Optional[Solution]:
        current, initial_iterations = self.get_starting_point(problem, start_basis)

        iterations = 0
        while current is not None and self._check_iteration_count(iterations):
            if current.is_optimal_point():
                return Solution(
                    point=current,
                    iteration_count=iterations,
                    initial_iterations=initial_iterations
                )
            current = self.iteration(current)
            iterations += 1

        return None

    def make_feasible(self, vertex: Vertex) -> Optional[Vertex]:
        v = vertex
        while not v.is_dual_feasible():
            dual_infeas = v.dual_infeasible_values()
            if not dual_infeas:
                break
            p, _ = dual_infeas[0]

            d = -v.W @ v.problem.A[p]

            # Entering index
            min_pivot = float('inf')
            q = -1
            for i in v.non_basis:
                pivot = v.problem.A[i] @ d
                if pivot <= -Vertex.ABSOLUTE_TOLERANCE and abs(pivot) < min_pivot:
                    min_pivot = abs(pivot)
                    q = i

            if q == -1:
                raise ValueError("Unbounded problem")

            new_basis = np.setdiff1d(v.basis, [p])
            new_basis = np.append(new_basis, q)
            v = Vertex(v.problem, new_basis)

        return v

    def get_feasible_vertex(self, problem: Problem) -> Optional[Tuple[Vertex, int]]:
        initial_point = Vertex(problem, np.arange(problem.dimension))
        dual_feasible = self.make_feasible(initial_point)
        if dual_feasible is None:
            return None
        return dual_feasible, 0

    def get_starting_point(self, problem: Problem, given_basis: Optional[List[int]] = None) -> Tuple[Optional[Vertex], int]:
        if given_basis is not None:
            return Vertex(problem, given_basis), 0

        phase_one = self.get_feasible_vertex(problem)
        if phase_one is None:
            return None, 0
        return phase_one