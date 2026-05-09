import numpy as np
from typing import List, Tuple, Optional
from pulp import LpProblem, LpConstraint
from pulp.constants import LpConstraintEQ

from gsimplex.basis import Basis
from gsimplex.constants import DEFAULT_ABS_TOLERANCE

class Vertex(Basis):
    """
    Vertex (basis solution) for a primal or dual linear programming polyhedron.
    """

    def __init__(self, problem: LpProblem, *constraints: LpConstraint):
        super().__init__(problem, *constraints)

        a_B, b_B = self._compute_system(problem)
        self.W = -np.linalg.inv(a_B)

        x = -self.W @ b_B
        self._set_primal_vars(x)

    @staticmethod
    def from_problem_state(p: LpProblem, eps: float = DEFAULT_ABS_TOLERANCE) -> "Vertex":
        assert eps >= 0, "Eps must be >= 0"

        active_constraints = [c for c in list(p.constraints.values()) if abs(Vertex.slack(c)) < 2*eps]
        return Vertex(p, *active_constraints)
    
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

        """
        Retrieved value can mean different things depending on the type of constraint
        * value =  Ai * x - bi <= 0 --> bi - Ai * x = -value
        * value = -Ai * x + bi >= 0 --> bi - Ai * x =  value
        * value =  Ai * x - bi == 0 --> bi - Ai * x = -value
        """

        if constraint.sense == LpConstraintEQ:
            return -value

        return constraint.sense * value
    
    @property
    def primal_value(self) -> float:

        assert self.problem.objective, "Problem must have an objective function"
        return self.problem.objective.valueOrDefault()

    def primal_residuals(self) -> np.ndarray:
        s = [Vertex.slack(c) for c in self.all_constraints]
        return np.minimum(s, 0)
    
    def primal_infeasible_constraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        r = self.primal_residuals()
        return [(c, r[i]) for i, c in enumerate(self.all_constraints) if r[i] < -eps]

    def is_primal_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        return len(self.primal_infeasible_constraints(eps)) == 0

    @property
    def dual_value(self) -> float:
        s = 0
        for i, constraint in enumerate(self.all_constraints):
            if constraint in self:
                s += self.y[i] * constraint.constant
        return s
    
    def dual_infeasible_contraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        return [(c, self.y[i]) for i, c in enumerate(self.all_constraints) if self.y[i] < -eps]
    
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
        A_B = self._compute_system(self.problem)[0]
        s += f'Ab = {A_B}\n'
        s += f'W  = {self.W}\n'
        s += f'Ab @ W = {A_B @ self.W}'
        return s
    
    @staticmethod
    def __build_W(problem: LpProblem,
                   W: np.ndarray,  
                   i: int,
                   new: LpConstraint,
                   old: LpConstraint
                   ) -> np.ndarray:
        """
        Builds a new matrix W s.t. A_B @ W == -I, given the current W and the variation in A_B.

        This function takes O(n^2) time using the Sherman-Morrison formula for the update of an inverse matrix.
        See https://en.wikipedia.org/wiki/Sherman%E2%80%93Morrison_formula
        """
        

        n = W.shape[0]
        A_Inv = -W

        # Compute the variation in the i-th row of A_B
        new_vec = Vertex.constraint_to_row(new, problem)
        old_vec = Vertex.constraint_to_row(old, problem)

        # Variation in the i-th row
        v = new_vec - old_vec

        # u = e_i
        u = np.zeros(n)
        u[i] = 1.0

        # Compute denominator
        Au = A_Inv @ u
        denom = 1.0 + v @ Au

        if np.isclose(denom, 0.0, atol=DEFAULT_ABS_TOLERANCE):
            raise np.linalg.LinAlgError(
                "Updated matrix is singular or nearly singular (denominator ≈ 0)."
            )

        # Build rank-1 correction matrix
        outer = np.outer(Au, v @ A_Inv)

        A_new_inv = A_Inv - outer / denom

        return -A_new_inv
        
    
    def swap(self, entering: LpConstraint, leaving: LpConstraint|str):

        if not isinstance(leaving, LpConstraint):
            leaving_candidates = [x for x in self if x.name == leaving]
            if len(leaving_candidates) == 0:
                raise Exception(f'No candidate is found for leaving constraint with name "{leaving}"')
            leaving = leaving_candidates[0]

        assert entering != leaving, "Cannot swap a constraint with itself!"
        assert entering not in self, "Entering constraint must not be in Basis yet"

        assert leaving in self, "Leaving constraint must be in basis"
        leaving_index = self.index(leaving)

        # Preserve overall order
        self[leaving_index] = entering

        # self.__build_W() will update W in a way eqivalent to the following but in O(n^2) instead of O(n^3)
        # self.W = -np.linalg.inv(self._compute_system(self.problem)[0])
        self.W = self.__build_W(self.problem, self.W, leaving_index, entering, leaving)

        # A_B x = b_B <==> x = -W b_B
        b_B = np.array([Vertex.constraint_to_linear_term(constraint) for constraint in self])
        x = -self.W @ b_B
        self._set_primal_vars(x)

        # y_B^T A_B = c^T <==> y_B^T = -c^T * W
        assert self.problem.objective, "Problem must have an objective function"
        c = Vertex.get_objective_function(self.problem)
        y_B = -c.T @ self.W
        self._set_dual_vars(y_B)

        return self