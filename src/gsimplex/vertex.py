import numpy as np
from typing import List, Tuple, Optional
from pulp import LpProblem, LpConstraint
from pulp.constants import LpConstraintEQ

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
    def from_problem_state(p: LpProblem, eps: float = DEFAULT_ABS_TOLERANCE) -> "Vertex":
        assert eps >= 0, "Eps must be >= 0"

        return Vertex(p,
                      *[c for c in list(p.constraints.values())
                        if abs(Vertex.slack(c)) < 2*eps])
    
    def has_named_constraints(self, names: List[str]) -> bool:
        for c in self:
            if c.name in names:
                return True
            
        return False

    @staticmethod
    def slack(constraint: LpConstraint) -> float:
        """Given the constraint Ai, returns bi - Ai*x"""

        value = constraint.value()
        assert value is not None, "Constraint value is None, cannot compute slack"

        if constraint.sense == LpConstraintEQ:
            return -abs(value)
        return constraint.sense * value
    
    @property
    def primal_value(self) -> float:

        assert self.problem.objective, "Problem must have an objective function"
        return self.problem.objective.valueOrDefault()
    
    def is_primal_degenerate(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        r = self.primal_residuals()
        return len(r[r >= -eps]) > self.n

    def primal_slacks(self) -> np.ndarray:
        return np.array([Vertex.slack(constraint) for constraint in self.all_constraints])

    def primal_residuals(self) -> np.ndarray:
        s = self.primal_slacks()
        return np.minimum(s, 0)
    
    def primal_infeasible_contraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        r = self.primal_residuals()
        return [(constraint, r[i]) for i, constraint in enumerate(self.all_constraints)
                if r[i] < -eps]

    def is_primal_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        return len(self.primal_infeasible_contraints(eps)) == 0

    @property
    def dual_value(self) -> float:
        s = 0
        for i, constraint in enumerate(self.problem.constraints.values()):
            if constraint in self:
                s += self.y[i] * constraint.constant
        return s
    
    def is_dual_degenerate(self) -> np.bool:
        return np.count_nonzero(self.y) < self.n
    
    def dual_infeasible_contraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        return [(constraint, self.y[i]) for i, constraint in enumerate(self.problem.constraints.values())
                if constraint in self and self.y[i] < -eps]
    
    def is_dual_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        return len(self.dual_infeasible_contraints(eps)) == 0
    
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
    
    def __str__(self) -> str:
        s = super().__str__()
        s += f'\nW = {self.W}'
        return s
    
    @staticmethod
    def __build_W(problem: LpProblem,
                   W: np.ndarray,  
                   r_index: int,
                   r_new: LpConstraint,
                   r_old: LpConstraint
                   ) -> np.ndarray:
    
        # Compute the variation in the i-th row of A_B
        delta = Vertex.constraint_to_row(r_new - r_old, problem)

        # Grab the i-th column of A_B^-1 and compute delta^T @ W
        col_i = -W[:, r_index]
        deltaT_W = delta @ -W

        # 1 + delta^T @ W @ e_i
        denom = 1.0 + deltaT_W[r_index]

        if np.isclose(denom, 0, atol=DEFAULT_ABS_TOLERANCE):
            raise ValueError("Updated matrix is singular (denominator ≈ 0).")

        # Outer product: col_i @ deltaT_W; Nx1 * 1xN => NxN
        A_Inv = -W - np.outer(col_i, deltaT_W) / denom
        return -A_Inv
    
    def swap(self, entering: LpConstraint, leaving: LpConstraint|str):

        if not isinstance(leaving, LpConstraint):
            leaving_candidates = [x for x in self if x.name == leaving]
            if len(leaving_candidates) == 0:
                raise Exception(f'No candidate is found for leaving constraint with name "{leaving}"')
            leaving = leaving_candidates[0]

        super().swap(entering, leaving)

        index = self.index(entering)
        self.W = self.__build_W(self.problem, self.W, index, entering, leaving)

        # A_B x = b <==> x = -W b
        b = np.array([Vertex.constraint_to_linear_term(constraint) for constraint in self])
        self._x = -self.W @ b
        self.update_variables()

        # y_B^T A_B = c^T <==> y_B^T = -c^T * W
        assert self.problem.objective, "Problem must have an objective function"
        c = np.array([self.problem.objective.get(var, 0) for var in self.problem.variables()])
        y_B = -c.T @ self.W
        self._y = self._build_Y(y_B, self.problem)

        return self