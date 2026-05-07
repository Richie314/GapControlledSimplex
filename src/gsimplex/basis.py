from pulp import LpProblem, LpConstraint
from pulp.constants import LpConstraintEQ, LpConstraintLE, LpConstraintGE
from typing import List, Tuple, Optional, Union
import numpy as np


class ConstraintSet(List[LpConstraint]):
    """
    A set of linear constraints for a linear programming problem.
    """

    def __init__(self, *constraints: LpConstraint):
        super().__init__(constraints)

    def _compute_system(self, problem: LpProblem) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute the system of equations defined by the constraints in this set.
        """

        a_B = np.array([ConstraintSet.constraint_to_row(constraint, problem) for constraint in self])
        b_B = np.array([ConstraintSet.constraint_to_linear_term(constraint) for constraint in self])
        return a_B, b_B

    def _compute_primal_point(self, problem: LpProblem) -> np.ndarray:
        """
        Compute the vertex corresponding to this basis by solving the system
        of equations defined by the constraints.

        Solves A_B x = b_B
        """

        n = problem.numVariables()
        assert len(self) >= n, "Not enough constraints to form a square matrix"

        a_B, b_B = self._compute_system(problem)
        return np.linalg.solve(a_B, b_B)
    
    def _build_Y(self, 
                  y_B: Union[np.ndarray, List[float]], 
                  constraints: Union[List[LpConstraint], LpProblem]):
        if isinstance(constraints, LpProblem):
            constraints = list(constraints.constraints.values())

        if not isinstance(y_B, np.ndarray):
            y_B = np.array([yi for yi in y_B])

        y = np.zeros(len(constraints))
        for i, constraint in enumerate(constraints):
            if constraint in self:
                y[i] = y_B.item(self.index(constraint))
        return y

    def _compute_dual_point(self, problem: LpProblem) -> np.ndarray:
        """
        Compute the dual vertex corresponding to this basis by solving the system
        of equations defined by the constraints.

        Solves y_B^T A_B = c^T <==> A_B^T y_B = c
        """

        n = problem.numVariables()
        assert len(self) >= n, "Not enough constraints to form a square matrix"

        m = problem.numConstraints()
        assert len(self) <= m, "Too many constraints in basis"

        assert problem.objective, "Problem must have an objective function"
        c = np.array([problem.objective.get(var, 0) for var in problem.variables()])

        a_B, _ = self._compute_system(problem)
        y_B = np.linalg.solve(a_B.T, c)

        return self._build_Y(y_B, problem)
    
    @staticmethod
    def __get_sense_multiplier(constraint: LpConstraint, convert_eq_to: int = LpConstraintLE) -> int:
        sense = constraint.sense
        if sense == LpConstraintEQ:
            sense = convert_eq_to
        
        if sense != LpConstraintLE and sense != LpConstraintGE:
            raise ValueError(f"Unsupported constraint sense: {constraint.sense}")
        
        return sense
    
    @staticmethod
    def constraint_to_row(constraint: LpConstraint, 
                          problem: LpProblem, 
                          convert_eq_to: int = LpConstraintLE
                          ) -> np.ndarray:
        """
        Convert a constraint to a numpy array of coefficients corresponding to the given variables.
        """

        sense = ConstraintSet.__get_sense_multiplier(constraint, convert_eq_to)
        return -sense * np.array([constraint.get(var, 0) for var in problem.variables()])
    
    @staticmethod
    def constraint_to_linear_term(constraint: LpConstraint, 
                                  convert_eq_to: int = LpConstraintLE
                                  ) -> float:
        """
        Extract the linear term from a constraint.
        """

        sense = ConstraintSet.__get_sense_multiplier(constraint, convert_eq_to)
        return sense * constraint.constant
    

class Basis(ConstraintSet):
    """
    A basis for a linear programming problem, represented as a set of constraints.
    """

    def __init__(self, problem: LpProblem, *constraints: LpConstraint):
        super().__init__(*constraints)

        assert problem.objective, "Problem must have an objective function"

        self.n = problem.numVariables()
        assert self.n > 0, "Problem must have at least one variable"
        assert len(self) == self.n, f"Basis must have same number of constraints as problem dimension: {len(self)} != {self.n}"

        self.problem = problem
        self.variables = self.problem.variables().copy()

        self._x: Optional[Union[np.ndarray, List[float]]] = None
        self._y: Optional[Union[np.ndarray, List[float]]] = None

    def update_variables(self):
        for i, var in enumerate(self.problem.variables()):
            var.varValue = self.x[i]

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
        return self.all_constraints.index(constraint)

    @property
    def non_basis(self) -> ConstraintSet:
        """
        Return the set of constraints that are not in the basis.
        """

        return ConstraintSet(*[constraint for constraint in self.problem.constraints.values() 
                               if constraint not in self])
    
    @property
    def x(self) -> np.ndarray:
        """
        Primal point corresponding to this basis.
        """

        if self._x is None:
            self._x = self._compute_primal_point(self.problem)
            self.update_variables()

        if not isinstance(self._x, np.ndarray):
            self._x = np.array(self._x)
        return self._x
    
    @property
    def y(self) -> np.ndarray:
        """
        Dual point corresponding to this basis.
        """

        if self._y is None:
            self._y = self._compute_dual_point(self.problem)

        if not isinstance(self._y, np.ndarray):
            self._y = np.array(self._y)
        return self._y
    
    def __str__(self) -> str:
        s  = f'x = {self.x}\n'
        s += f'y = {self.y}\n'
        for c in self:
            s += f'{c} -> {c.value():.5}\n'
        return s

    def swap(self, entering: LpConstraint, leaving: LpConstraint):

        assert entering != leaving, "Cannot swap a constraint with itself!"
        assert entering not in self, "Entering constraint must not be in Basis yet"

        assert leaving in self, "Leaving constraint must be in basis"
        leaving_index = self.index(leaving)

        # Preserve overall order
        self[leaving_index] = entering

        return self