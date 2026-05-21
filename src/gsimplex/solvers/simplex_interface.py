from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, List
from pulp import (
    LpProblem, LpConstraint,
    LpMaximize, LpMinimize,
)
import numpy as np

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex
from gsimplex.constants import *

class ISimplex(ISolver, ABC):
    def __init__(self, 
                 max_iterations: Optional[int] = None,
                 abs_eps: Optional[float] = None,
                 rel_eps: Optional[float] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 ):
        """
        Initialize the simplex solver with given parameters.

        :param max_iterations: Maximum number of simplex iterations. If None, uses default.
        :type max_iterations: Optional[int]
        :param abs_eps: Absolute tolerance for feasibility and optimality checks. If None, uses default.
        :type abs_eps: Optional[float]
        :param rel_eps: Relative tolerance for numerical comparisons. If None, uses default.
        :type rel_eps: Optional[float]
        :param pivot_rule: Pivot rule used during the simplex iterations.
        :type pivot_rule: PivotRule
        """

        super().__init__(
            max_iterations=max_iterations,
            abs_eps=abs_eps,
            rel_eps=rel_eps,
        )

        self.pivot_rule = pivot_rule
    
    @abstractmethod
    def get_entering_constraint(self, 
                                v: "Vertex", 
                                d: Union[np.ndarray, List[float], None] = None,
                                ) -> Optional[LpConstraint]:
        """
        Select the entering constraint for the simplex iteration.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Optional moving direction vector.
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen entering constraint or None.
        :rtype: Optional[LpConstraint]
        """
        pass
    
    @abstractmethod
    def get_leaving_constraint(self, 
                               v: "Vertex", 
                               d: Union[np.ndarray, List[float], None] = None,
                               ) -> Optional[LpConstraint]:
        """
        Select the leaving constraint for the simplex iteration.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Optional moving direction vector.
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen leaving constraint or None.
        :rtype: Optional[LpConstraint]
        """
        pass

    @abstractmethod
    def get_moving_direction(self, v: "Vertex", constraint: LpConstraint) -> np.ndarray:
        """
        Compute the moving direction vector for the given constraint.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param constraint: The constraint to compute direction for.
        :type constraint: LpConstraint
        :return: The moving direction vector.
        :rtype: np.ndarray
        """
        pass
    
    @abstractmethod
    def get_starting_point(self, 
                           problem: LpProblem, 
                           ) -> Tuple[Optional["Vertex"], int]:
        """
        Find a starting point (vertex) for the simplex algorithm.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :return: A tuple of the starting vertex and iteration count.
        :rtype: Tuple[Optional[Vertex], int]
        """
        pass

    @abstractmethod
    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Union["Vertex", List[LpConstraint], List[str], None] = None,
                 **kwargs):
        """
        Solve the maximization problem using the simplex method.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis.
        :type start_basis: Union[Vertex, List[LpConstraint], List[str], None]
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        pass

    def minimize(self, 
                 problem: LpProblem, 
                 start_basis: Union["Vertex", List[LpConstraint], List[str], None] = None,
                 **kwargs):
        """
        Solve a minimization problem by converting it to a maximization problem.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis or vertex.
        :type start_basis: Union[Vertex, List[LpConstraint], List[str], None]
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        
        assert problem.sense == LpMinimize, "Tried to minimize a maximization problem!"
        
        if problem.objective is not None:
            problem.objective = -problem.objective
        problem.sense = LpMaximize

        try:
            self.maximize(problem=problem, 
                        start_basis=start_basis,
                        **kwargs
                        )
        finally:
            if problem.objective is not None:
                problem.objective = -problem.objective
            problem.sense = LpMinimize