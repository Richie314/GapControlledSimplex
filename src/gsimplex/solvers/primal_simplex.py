import numpy as np
from typing import Optional, Tuple, List

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solution import Solution

class PrimalSimplex(IterativeSolver, ISimplex):
    @staticmethod
    def iteration(vertex: Vertex) -> Optional[Vertex]:
        if not vertex.is_primal_feasible():
            return None

        # Leaving index (Bland rule)
        dual_infeas = vertex.dual_infeasible_values()
        if not dual_infeas:
            return vertex  # Optimal

        h, _ = dual_infeas[0]

        # Wh is the h-th column of -A_B^-1
        h_idx = np.where(vertex.basis == h)[0][0]
        Wh = vertex.W[:, h_idx]

        # Entering index (Bland rule)
        non_basis = vertex.non_basis
        ratios = []
        for i in non_basis:
            den = vertex.problem.A[i] @ Wh
            if den > Vertex.ABSOLUTE_TOLERANCE:
                num = vertex.problem.b[i] - vertex.problem.A[i] @ vertex.x
                ratios.append((i, num / den))

        if not ratios:
            return None  # Unbounded

        ratios.sort(key=lambda x: x[1])
        k, _ = ratios[0]

        new_basis = np.setdiff1d(vertex.basis, [h])
        new_basis = np.append(new_basis, k)

        return Vertex(vertex.problem, new_basis)

    def get_starting_point(self, problem: Problem, given_basis: Optional[List[int]] = None) -> Tuple[Optional[Vertex], int]:
        if given_basis is not None:
            return Vertex(problem, given_basis), 0

        feasible = self.get_feasible_vertex(problem)
        if feasible is None:
            return None, 0
        return feasible

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
        while not v.is_primal_feasible():
            infeas = v.primal_infeasible_rows()
            if not infeas:
                break
            k, _ = min(infeas, key=lambda x: x[1])

            Ak = v.problem.A[k]

            # Leaving index (Bland rule)
            h = -1
            for i in v.basis:
                idx = np.where(v.basis == i)[0][0]
                if Ak @ v.W[:, idx] < 0:
                    h = i
                    break
            if h == -1:
                return None

            new_basis = np.setdiff1d(v.basis, [h])
            new_basis = np.append(new_basis, k)
            v = Vertex(v.problem, new_basis)

        return v

    def get_feasible_vertex(self, problem: Problem) -> Optional[Tuple[Vertex, int]]:
        n = problem.dimension
        m = problem.constraints

        initial_basis = np.arange(n)
        initial_vertex = Vertex(problem, initial_basis)

        if initial_vertex.is_primal_feasible():
            return initial_vertex, 0

        # Auxiliary problem
        rp = initial_vertex.primal_residuals()
        V = initial_vertex.non_basis[rp[initial_vertex.non_basis] < 0]

        # Number of auxiliary variables
        k = len(V)

        # Build matrix of the auxiliary problem
        aux_A = np.zeros((m + k, n + k))
        aux_A[:m, :n] = problem.A
        aux_A[m:, n:] = -np.eye(k)
        for idx, i in enumerate(V):
            aux_A[i, n + idx] = -1

        aux_b = np.concatenate([problem.b, np.zeros(k)])
        aux_c = np.concatenate([np.zeros(n), -np.ones(k)])

        aux_problem = Problem(aux_c, aux_A, aux_b)

        aux_solution = self.maximize(aux_problem, initial_vertex.basis.tolist() + V.tolist())
        if aux_solution is None or not aux_solution.point.is_optimal_point() or aux_solution.point.primal_value() < 0:
            return None

        new_basis = aux_solution.basis[:n]
        new_vertex = Vertex(problem, new_basis)
        if not new_vertex.is_primal_feasible():
            raise ValueError("Auxiliary problem failed")

        return new_vertex, aux_solution.iteration_count