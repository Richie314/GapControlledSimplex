from pulp import LpProblem, LpConstraint, LpVariable
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

        return y_B
    
    @staticmethod
    def __get_constraint_sense(constraint: LpConstraint, 
                               convert_eq_to: int = LpConstraintLE,
                               ) -> int:
        sense = constraint.sense
        if sense == LpConstraintEQ:
            sense = convert_eq_to
        
        if sense != LpConstraintLE and sense != LpConstraintGE:
            raise ValueError(f"Unsupported constraint sense: {constraint.sense}")
        
        return sense
    
    @staticmethod
    def constraint_to_row(constraint: LpConstraint, 
                          problem: LpProblem, 
                          convert_eq_to: int = LpConstraintLE,
                          ) -> np.ndarray:
        """
        Convert a constraint to a numpy array of coefficients corresponding to the given variables.
        """

        sense = ConstraintSet.__get_constraint_sense(constraint, convert_eq_to)
        return -sense * np.array([constraint.get(var, 0) for var in problem.variables()])
    
    @staticmethod
    def constraint_to_linear_term(constraint: LpConstraint, 
                                  convert_eq_to: int = LpConstraintLE,
                                  ) -> float:
        """
        Extract the linear term from a constraint in the form Ax <= b.
        """

        """
        Pulp memorizes data in the form Ax + constant <=> 0
        Hence b is
            * -constant if <=
            *  constant if >=
            * any of the above if == (treated as convert_eq_to says)
        """
        sense = ConstraintSet.__get_constraint_sense(constraint, convert_eq_to)
        
        """
        if sense == LpConstraintLE:
            return -constraint.constant
        else:
            return constraint.constant
        """
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
        assert len(self) == self.n, f"Basis must have same number of constraints as problem dimension: {len(self)} ≠ {self.n}"

        self.problem = problem

        self.__x: Optional[np.ndarray] = None
        self.__y: Optional[np.ndarray] = None

    def _set_primal_vars(self, x: Union[np.ndarray, List[float]]) -> np.ndarray:
        
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
        Primal point corresponding to this basis.
        """

        if self.__x is not None:
            return self.__x
        
        x = self._compute_primal_point(self.problem)
        return self._set_primal_vars(x)
    

    def _set_dual_vars(self, y_B: Union[np.ndarray, List[float]]) -> np.ndarray:
        assert len(y_B) == self.problem.numVariables()

        self.__y =  np.zeros(self.problem.numConstraints())
        for i, y_i in enumerate(y_B):
            constraint = self[i]
            self.__y[self.global_index(constraint)] = y_i

        return self.__y
    
    @property
    def y(self) -> np.ndarray:
        """
        Dual point corresponding to this basis.
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
            s += f'{c} → {c.value():.5}\n'
        return s
