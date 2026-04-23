import numpy as np
from typing import List, Iterable, Tuple, Optional
from gsimplex.problem import Problem

class Vertex:
    """
    Vertex (basis solution) for a primal or dual linear programming polyhedron.
    """


    ABSOLUTE_TOLERANCE = 1e-10
    RELATIVE_TOLERANCE = 1e-9

    def __init__(self, problem: Problem, basis: Iterable[int]):
        self.problem = problem
        self.basis = np.array(sorted(set(basis)), dtype=int)

        if len(self.basis) != problem.dimension:
            raise ValueError("Basis must have same size as problem dimension")

        A_B = problem.A[self.basis, :]
        b_B = problem.b[self.basis]

        self.W = -np.linalg.inv(A_B)

        # A_B x = b_B
        self.x = np.linalg.solve(A_B, b_B)

        # y_B = c^T A_B^-1
        self.y_B = np.linalg.solve(A_B.T, problem.c)

    @property
    def non_basis(self) -> np.ndarray:
        return np.setdiff1d(np.arange(self.problem.constraints), self.basis)

    @property
    def y(self) -> np.ndarray:
        y_full = np.zeros(self.problem.constraints)
        y_full[self.basis] = self.y_B
        return y_full

    def primal_residuals(self) -> np.ndarray:
        r = self.problem.b - self.problem.A @ self.x
        return np.minimum(r, 0)

    def is_primal_feasible(self, abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> bool:
        return len(self.primal_infeasible_rows(abs_tol, rel_tol)) == 0

    def primal_infeasible_rows(self, abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> List[Tuple[int, float]]:
        scale = np.max(np.abs(self.problem.b))
        slack = self.primal_residuals()
        return [(i, slack[i]) for i in range(self.problem.constraints)
                if abs(slack[i]) > abs_tol + rel_tol * scale]

    def is_primal_degenerate(self, abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> bool:
        scale = np.max(np.abs(self.problem.b))
        residuals = self.primal_residuals()
        return np.sum(np.abs(residuals) <= abs_tol + rel_tol * scale) > self.problem.dimension

    def dual_infeasible_values(self, abs_tol: float = ABSOLUTE_TOLERANCE) -> List[Tuple[int, float]]:
        return [(self.basis[i], abs(self.y_B[i])) for i in range(len(self.y_B)) if self.y_B[i] < -abs_tol]

    def is_dual_feasible(self, abs_tol: float = ABSOLUTE_TOLERANCE) -> bool:
        return len(self.dual_infeasible_values(abs_tol)) == 0

    def is_dual_degenerate(self, abs_tol: float = ABSOLUTE_TOLERANCE) -> np.bool:
        return np.any(np.abs(self.y_B) < abs_tol)

    def is_optimal_point(self, abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> bool:
        return self.is_primal_feasible(abs_tol, rel_tol) and self.is_dual_feasible(abs_tol)

    def primal_value(self, abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> float:
        if not self.is_primal_feasible(abs_tol, rel_tol):
            raise ValueError("Point is not primal feasible")
        
        return self.problem.c @ self.x

    def dual_value(self, abs_tol: float = ABSOLUTE_TOLERANCE) -> float:
        if not self.is_dual_feasible(abs_tol):
            raise ValueError("Point is not dual feasible")
        
        return self.y_B @ self.problem.b[self.basis]

    @staticmethod
    def gap(dual_vertex: 'Vertex', primal_vertex: 'Vertex',
            abs_tol: float = ABSOLUTE_TOLERANCE, rel_tol: float = RELATIVE_TOLERANCE) -> Tuple[float, Optional[float], float, float]:
        if dual_vertex.problem is not primal_vertex.problem:
            raise ValueError("Vertices from different problems")

        dual_val = dual_vertex.dual_value(abs_tol)
        primal_val = primal_vertex.primal_value(abs_tol, rel_tol)

        gap = dual_val - primal_val
        rel_gap = gap / primal_val if abs(primal_val) > abs_tol else None

        return gap, rel_gap, dual_val, primal_val