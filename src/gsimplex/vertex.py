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
        """
        Initialize a vertex from the given basis constraints.

        :param problem: The linear programming problem associated with the vertex.
        :type problem: LpProblem
        :param constraints: The basic constraints defining the vertex.
        :type constraints: LpConstraint
        """
        super().__init__(problem, *constraints)

        a_B, b_B = self._compute_system(problem)
        self.W = -np.linalg.inv(a_B)

        x = -self.W @ b_B
        self._set_primal_vars(x)

    @staticmethod
    def from_problem_state(p: LpProblem, eps: float = DEFAULT_ABS_TOLERANCE) -> "Vertex":
        """
        Build a vertex from the current state of a linear problem.

        :param p: The linear programming problem whose active constraints define the vertex.
        :type p: LpProblem
        :param eps: Tolerance for determining whether a constraint is active.
        :type eps: float
        :return: A vertex representing the current basis-active solution.
        :rtype: Vertex
        """
        assert eps >= 0, "Eps must be >= 0"

        active_constraints = [c for c in list(p.constraints.values()) if abs(Vertex.slack(c)) < 2*eps]
        return Vertex(p, *active_constraints)
    
    def has_named_constraints(self, names: List[str]) -> bool:
        """
        Check whether this vertex contains any of the requested constraint names.

        :param names: A list of constraint names to search for.
        :type names: List[str]
        :return: True if the vertex includes at least one named constraint.
        :rtype: bool
        """
        for c in self:
            if c.name in names:
                return True
            
        return False

    @staticmethod
    def slack(constraint: LpConstraint) -> float:
        """
        Compute the slack of a constraint, defined as b_i - A_i x.

        :param constraint: The constraint for which to compute slack.
        :type constraint: LpConstraint
        :return: The slack value for the constraint.
        :rtype: float
        """

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
        """
        Get the objective value of the current primal vertex.

        :return: The primal objective value.
        :rtype: float
        """

        assert self.problem.objective, "Problem must have an objective function"
        return self.problem.objective.valueOrDefault()

    def primal_residuals(self) -> np.ndarray:
        """
        Compute the primal residuals for all constraints.

        :return: An array of primal residual values truncated at zero.
        :rtype: np.ndarray
        """
        s = [Vertex.slack(c) for c in self.all_constraints]
        return np.minimum(s, 0)
    
    def primal_infeasible_constraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        """
        Return the list of constraints that violate primal feasibility.

        :param eps: Tolerance used for feasibility checking.
        :type eps: float
        :return: A list of (constraint, residual) pairs for infeasible constraints.
        :rtype: List[Tuple[LpConstraint, float]]
        """
        r = self.primal_residuals()
        return [(c, r[i]) for i, c in enumerate(self.all_constraints) if r[i] < -eps]

    def is_primal_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        """
        Determine whether the vertex is primal feasible.

        :param eps: Tolerance used for feasibility checking.
        :type eps: float
        :return: True if no constraints violate primal feasibility.
        :rtype: bool
        """
        return len(self.primal_infeasible_constraints(eps)) == 0

    @property
    def dual_value(self) -> float:
        """
        Compute the objective value of the current dual vertex.

        :return: The dual objective value.
        :rtype: float
        """
        s = 0
        for i, constraint in enumerate(self.all_constraints):
            if constraint in self:
                s += self.y[i] * constraint.constant
        return s
    
    def dual_infeasible_contraints(self, eps: float = DEFAULT_ABS_TOLERANCE) -> List[Tuple[LpConstraint, float]]:
        """
        Return the list of constraints that violate dual feasibility.

        :param eps: Tolerance used for dual feasibility checking.
        :type eps: float
        :return: A list of (constraint, reduced cost) pairs for infeasible constraints.
        :rtype: List[Tuple[LpConstraint, float]]
        """
        return [(c, self.y[i]) for i, c in enumerate(self.all_constraints) if self.y[i] < -eps]
    
    def is_dual_feasible(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        """
        Determine whether the vertex is dual feasible.

        :param eps: Tolerance used for dual feasibility checking.
        :type eps: float
        :return: True if no constraints violate dual feasibility.
        :rtype: bool
        """
        return len(self.dual_infeasible_contraints(eps)) == 0
    
    def is_optimal_point(self, eps: float = DEFAULT_ABS_TOLERANCE) -> bool:
        """
        Check whether the vertex is both primal and dual feasible.

        :param eps: Tolerance used for feasibility checking.
        :type eps: float
        :return: True if the vertex is optimal within tolerance.
        :rtype: bool
        """
        return self.is_primal_feasible(eps) and self.is_dual_feasible(eps)


    @staticmethod
    def gap(dual_vertex: 'Vertex', 
            primal_vertex: 'Vertex',
            eps: float = DEFAULT_ABS_TOLERANCE
            ) -> Tuple[float, Optional[float], float, float]:
        """
        Compute the optimality gap between a dual and a primal vertex.

        :param dual_vertex: The dual vertex for the problem.
        :type dual_vertex: Vertex
        :param primal_vertex: The primal vertex for the same problem.
        :type primal_vertex: Vertex
        :param eps: Tolerance used for feasibility assertions.
        :type eps: float
        :return: A tuple of (gap, relative gap, dual value, primal value).
        :rtype: Tuple[float, Optional[float], float, float]
        """
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
        s += f'Ab = {self._compute_system(self.problem)[0]}\n'
        s += f'W  = {self.W}\n'
        # s += f'Ab @ W = {A_B @ self.W}'
        return s
    
    @staticmethod
    def __build_W(problem: LpProblem,
                   W: np.ndarray,  
                   i: int,
                   new: LpConstraint,
                   old: LpConstraint
                   ) -> np.ndarray:
        """
        Update the inverse basis matrix using a rank-1 Sherman-Morrison correction.

        :param problem: The linear problem defining the constraint system.
        :type problem: LpProblem
        :param W: The current inverse basis matrix.
        :type W: np.ndarray
        :param i: The index of the row being swapped.
        :type i: int
        :param new: The entering constraint.
        :type new: LpConstraint
        :param old: The leaving constraint.
        :type old: LpConstraint
        :return: The updated inverse basis matrix.
        :rtype: np.ndarray
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
        """
        Replace one basic constraint with another and update the vertex.

        :param entering: The constraint entering the basis.
        :type entering: LpConstraint
        :param leaving: The constraint leaving the basis, or its name.
        :type leaving: LpConstraint | str
        :return: The updated basis vertex.
        :rtype: Vertex
        """

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