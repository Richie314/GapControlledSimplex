from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, List
from pulp import LpProblem, LpConstraint
from pulp.constants import LpMaximize, LpMinimize
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

        :param pivot_rule: Pivot rule used during the simplex iterations.
        :type pivot_rule: PivotRule
        """

        self.max_iterations = max_iterations if max_iterations else DEFAULT_MAX_ITERATIONS
        assert self.max_iterations > 0, f"Maximum number of iterations must be positive. {self.max_iterations} given."

        self.abs_tol = abs_eps if abs_eps else DEFAULT_ABS_TOLERANCE
        assert self.abs_tol >= 0, f"Absolute ε must be >= 0. {self.abs_tol:.5} given."

        self.rel_tol = rel_eps if rel_eps else DEFAULT_REL_TOLERANCE
        assert self.rel_tol >= 0, f"Relative ε must be >= 0. {self.abs_tol:.5} given."

        self.pivot_rule = pivot_rule
    
    @abstractmethod
    def get_entering_constraint(self, 
                                v: Vertex, 
                                d: Optional[Union[np.ndarray, List[float]]] = None,
                                ) -> Optional[LpConstraint]:
        pass
    
    @abstractmethod
    def get_leaving_constraint(self, 
                               v: Vertex, 
                               d: Optional[Union[np.ndarray, List[float]]] = None,
                               ) -> Optional[LpConstraint]:
        pass

    @abstractmethod
    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_starting_point(self, 
                           problem: LpProblem, 
                           ) -> Tuple[Optional[Vertex], int]:
        pass

    @abstractmethod
    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 **kwargs):
        pass

    def minimize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 **kwargs):
        """
        Solve a minimization problem by converting it to a maximization problem.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis or vertex.
        :type start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        
        assert problem.sense == LpMinimize, "Tried to minimize a maximization problem!"
        assert problem.objective

        problem.setObjective(-problem.objective)
        problem.sense = LpMaximize

        self.maximize(problem=problem, 
                      start_basis=start_basis,
                      **kwargs
                      )
        
        problem.setObjective(-problem.objective)
        problem.sense = LpMinimize