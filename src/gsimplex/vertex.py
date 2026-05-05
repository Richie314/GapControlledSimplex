import numpy as np
from typing import List, Tuple, Optional
from pulp import LpProblem, LpConstraint
from pulp.constants import (
    LpConstraintEQ, LpConstraintLE, LpConstraintGE,
)

from gsimplex.basis import Basis

DEFAULT_ABS_TOLERANCE = 1e-10

class Vertex(Basis):
    """
    Vertex (basis solution) for a primal or dual linear programming polyhedron.
    """

    def __init__(self, problem: LpProblem, *constraints: LpConstraint):
        super().__init__(problem, *constraints)

        a_B, _ = self._compute_system(problem)
        self.W = -np.linalg.inv(a_B)
        self.x

    @staticmethod
    def slack(constraint: LpConstraint) -> float:
        """Given the constraint Ai, returns bi - Ai*x"""

        value = constraint.value()
        assert value is not None, "Constraint value is None, cannot compute slack"

        if constraint.sense == LpConstraintEQ:
            return -abs(value)
        if constraint.sense == LpConstraintLE:
            return -value
        if constraint.sense == LpConstraintGE:
            return value
        
        raise Exception
    
    @property
    def primal_value(self) -> float:

        assert self.problem.objective, "Problem must have an objective function"
        return self.problem.objective.valueOrDefault()
    
    def is_primal_degenerate(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        r = self.primal_residuals()
        return len(r[r >= -eps]) > self.n

    def primal_slacks(self) -> np.ndarray:
        return np.array([Vertex.slack(constraint) for constraint in self.problem.constraints.values()])

    def primal_residuals(self) -> np.ndarray:
        s = self.primal_slacks()
        # print(f"{s=}")
        return np.minimum(s, 0)
    
    def primal_infeasible_contraints(self, 
                                     eps: float = DEFAULT_ABS_TOLERANCE
                                     ) -> List[Tuple[LpConstraint, float]]:
        r = self.primal_residuals()
        return [(constraint, r[i]) for i, constraint in enumerate(self.problem.constraints.values())
                if r[i] < -eps]

    def primal_infeasible_rows(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        r = self.primal_residuals()
        return [(constraint, r[i]) for i, constraint in enumerate(self.problem.constraints.values()) 
                if r[i] < -eps]

    def dual_infeasible_values(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        return self.dual_infeasible_contraints(eps)

    def is_primal_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        r = self.primal_residuals()
        # print(f"{r=}")
        return bool(np.all(r >= -eps))

    @property
    def dual_value(self) -> float:
        s = 0
        for i, constraint in enumerate(self.problem.constraints.values()):
            if constraint in self:
                s += self.y[i] * constraint.constant
        return s
    
    def is_dual_degenerate(self) -> np.bool:
        return np.count_nonzero(self.y) < self.n
    
    def dual_infeasible_contraints(self, 
                                   eps: float = DEFAULT_ABS_TOLERANCE
                                   ) -> List[Tuple[LpConstraint, float]]:
        return [(constraint, self.y[i]) for i, constraint in enumerate(self.problem.constraints.values())
                if constraint in self and self.y[i] < -eps]
    
    def is_dual_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        return bool(np.all(self.y >= -eps))
    
    def is_optimal_point(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        return self.is_primal_feasible(eps) and self.is_dual_feasible(eps)


    @staticmethod
    def gap(dual_vertex: 'Vertex', 
            primal_vertex: 'Vertex',
            eps: float = DEFAULT_ABS_TOLERANCE
            ) -> Tuple[float, Optional[float], float, float]:
        
        if dual_vertex.problem is not primal_vertex.problem:
            raise ValueError("Vertices from different problems")

        assert primal_vertex.is_primal_feasible(eps), "Primal vertex is not feasible"
        assert dual_vertex.is_dual_feasible(eps), "Dual vertex is not feasible"

        dual_val = dual_vertex.dual_value
        primal_val = primal_vertex.primal_value

        gap = dual_val - primal_val
        rel_gap = gap / primal_val if abs(primal_val) > eps else None

        return gap, rel_gap, dual_val, primal_val
    
    def __sub__(self, other: 'Vertex') -> Tuple[float, Optional[float], float, float]:
        return Vertex.gap(self, other)
    
    @staticmethod
    def __build_W(problem: LpProblem,
                   W: np.ndarray,  
                   r_index: int,
                   r_new: LpConstraint,
                   r_old: LpConstraint
                   ) -> np.ndarray:
    
        # Compute the variation in the i-th row of A_B
        delta = Vertex.constraint_to_row(r_new - r_old, problem)

        # Grab the i-th column of W and compute delta^T @ W
        col_i = W[:, r_index]
        deltaT_W = delta @ W

        # 1 + delta^T @ W @ e_i
        denom = 1.0 + deltaT_W[r_index]

        if np.isclose(denom, 0, atol=DEFAULT_ABS_TOLERANCE):
            raise ValueError("Updated matrix is singular (denominator ≈ 0).")

        # Outer product: col_i @ deltaT_W; Nx1 * 1xN => NxN
        W_diff = np.outer(col_i, deltaT_W) / denom

        return W - W_diff
    
    def swap(self, entering: LpConstraint, exiting: LpConstraint|str):

        if not isinstance(exiting, LpConstraint):
            exiting_candidates = [x for x in self if x.name == exiting]
            if len(exiting_candidates) == 0:
                raise Exception(f'No candidate is found for exiting constraint with name "{exiting}"')
            exiting = exiting_candidates[0]

        super().swap(entering, exiting)

        index = self.index(entering)
        self.W = self.__build_W(self.problem, self.W, index, entering, exiting)

        # A_B x = b_B <==> x = -W b_B
        b_B = np.array([Vertex.constraint_to_linear_term(constraint) for constraint in self])
        self._x = -self.W @ b_B
        self.update_variables()

        # y_B^T A_B = c^T <==> y = -W^T * c
        assert self.problem.objective, "Problem must have an objective function"
        c = np.array([self.problem.objective.get(var, 0) for var in self.problem.variables()])
        y_B = -self.W.transpose() @ c
        self._y = self._build_Y(y_B, self.problem)

        return self