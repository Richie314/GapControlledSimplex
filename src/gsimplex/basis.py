from pulp import (
    LpProblem, LpConstraint, LpVariable,
    LpConstraintEQ, LpConstraintLE, LpConstraintGE,
)
from typing import List, Tuple, Optional, Union
import numpy as np

from gsimplex.tools.algebra import rows_are_same
from gsimplex.tools.problem import constraint_to_row, get_objective_function
from gsimplex.exception import UnFeasibleProblemException

class ConstraintSet(List[LpConstraint]):
    """
    A set of linear constraints for a linear programming problem.
    """

    def __init__(self, *constraints: LpConstraint):
        super().__init__(constraints)

    def _compute_system(self, problem: LpProblem) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the system of equations defined by the constraints in this set.

        :param problem: The linear programming problem that defines the variables.
        :type problem: LpProblem
        :return: A tuple containing the constraint coefficient matrix and right-hand side vector.
        :rtype: Tuple[np.ndarray, np.ndarray]
        """

        a_B = np.array([constraint_to_row(constraint, problem)[0] for constraint in self])
        b_B = np.array([constraint_to_row(constraint, problem)[1] for constraint in self])
        return a_B, b_B

    def _compute_primal_point(self, problem: LpProblem) -> np.ndarray:
        """
        Compute the primal point *x* corresponding to this basis by solving the basis system (A_B x = b_B).

        :param problem: The linear programming problem used to determine the active variables.
        :type problem: LpProblem
        :return: The primal solution vector associated with the current basis.
        :rtype: np.ndarray
        """

        n = problem.numVariables()
        assert len(self) >= n, "Not enough constraints to form a square matrix"

        a_B, b_B = self._compute_system(problem)
        return np.linalg.solve(a_B, b_B)

    def _compute_dual_point(self, problem: LpProblem) -> np.ndarray:
        """
        Compute the dual point *y* corresponding to this basis by solving the dual system.

        :param problem: The linear programming problem whose objective determines the dual solution.
        :type problem: LpProblem
        :return: The dual solution values for the basic constraints.
        :rtype: np.ndarray
        """

        n = problem.numVariables()
        assert len(self) == n, f"Constraint number mismatch: {len(self)} != {n}"

        m = problem.numConstraints()
        assert len(self) <= m, "Too many constraints in basis"

        c = get_objective_function(problem)
        assert len(c) == n

        a_B, _ = self._compute_system(problem)
        y_B = np.linalg.solve(a_B.T, c)

        return y_B
    
    
    def has_named_constraints(self, names: List[str]) -> bool:
        """
        Check whether this vertex contains any of the requested constraint names.

        :param names: A list of constraint names to search for.
        :type names: List[str]
        :return: True if the vertex includes at least one named constraint.
        :rtype: bool
        """
        for c in self:
            if c.name is not None and c.name in names:
                return True
            
        return False
    

class Basis(ConstraintSet):
    """
    A basis for a linear programming problem, represented as a set of constraints.
    """

    def __init__(self, problem: LpProblem, *constraints: LpConstraint):
        """
        Initialize a basis with the specified constraints for a linear problem.

        :param problem: The linear programming problem for this basis.
        :type problem: LpProblem
        :param constraints: The active basis constraints.
        :type constraints: LpConstraint
        """

        super().__init__(*constraints)

        assert problem.objective, "Problem must have an objective function"

        self.n = problem.numVariables()
        assert self.n > 0, "Problem must have at least one variable"
        assert len(self) == self.n, f"Basis must have same number of constraints as problem dimension: {len(self)} ≠ {self.n}"

        self.problem = problem

        self.__x: Optional[np.ndarray] = None
        self.__y: Optional[np.ndarray] = None

    def _set_primal_vars(self, x: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Store and assign the primal solution values to problem variables.

        :param x: The primal solution values for all problem variables.
        :type x: Union[np.ndarray, List[float]]
        :return: The stored primal solution as a NumPy array.
        :rtype: np.ndarray
        """

        if not isinstance(x, np.ndarray):
            x = np.array(x)

        assert len(x) == self.problem.numVariables()

        self.__x = x
        for i, var in enumerate(self.variables):
            var.varValue = self.__x[i]

        return self.__x
    
    @property
    def x(self) -> np.ndarray:
        """
        Get the primal point corresponding to this basis.

        :return: The primal solution vector for the basis.
        :rtype: np.ndarray
        """

        if self.__x is not None:
            return self.__x
        
        x = self._compute_primal_point(self.problem)
        return self._set_primal_vars(x)
    

    def _set_dual_vars(self, y_B: Union[np.ndarray, List[float]]) -> np.ndarray:
        """
        Store the dual solution values and map them into the full constraint vector.

        :param y_B: The dual values for the basic constraints.
        :type y_B: Union[np.ndarray, List[float]]
        :return: The full dual solution vector mapped to all problem constraints.
        :rtype: np.ndarray
        """

        assert len(y_B) == self.problem.numVariables()

        self.__y =  np.zeros(self.problem.numConstraints())
        for i, y_i in enumerate(y_B):
            constraint = self[i]
            self.__y[self.global_index(constraint)] = y_i

        return self.__y
    
    @property
    def y(self) -> np.ndarray:
        """
        Get the dual point corresponding to this basis.

        :return: The dual solution vector for all problem constraints.
        :rtype: np.ndarray
        """

        if self.__y is not None:
            return self.__y
        
        y_B = self._compute_dual_point(self.problem)
        return self._set_dual_vars(y_B)

    @property
    def variables(self) -> List[LpVariable]:
        return self.problem.variables()

    @property
    def indices(self) -> List[int]:
        return [self.global_index(c) for c in self]

    @property
    def non_basis_indices(self) -> List[int]:
        return [self.global_index(c) for c in self.non_basis]
    
    @property
    def all_constraints(self) -> List[LpConstraint]:
        return list(self.problem.constraints.values())

    def global_index(self, constraint: LpConstraint) -> int:
        """
        Return the global index of a constraint in the original problem ordering.

        :param constraint: The constraint whose index is requested.
        :type constraint: LpConstraint
        :return: The zero-based index of the constraint in the problem.
        :rtype: int
        """

        return self.all_constraints.index(constraint)

    @property
    def non_basis(self) -> ConstraintSet:
        """
        Return the set of constraints that are not in the basis.
        """

        return ConstraintSet(*[c for c in self.all_constraints if c not in self])
    
    
    def __str__(self) -> str:
        s  = f'x = {self.x}\n'
        s += f'y = {self.y}\n'
        for c in self:
            s += f'{c}\t→ {c.value():.4}\n'
        return s
