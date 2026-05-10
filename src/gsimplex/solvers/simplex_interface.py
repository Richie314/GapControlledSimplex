from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, List
from pulp import LpProblem, LpConstraint
import numpy as np

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex
from gsimplex.constants import (
    PivotRule,
    DEFAULT_PIVOT_RULE,
    DEFAULT_ABS_TOLERANCE,
    DEFAULT_REL_TOLERANCE,
    DEFAULT_MAX_ITERATIONS,
)

class ISimplex(ISolver, ABC):
    def __init__(self, 
                 max_iterations: Optional[int] = None,
                 abs_eps: Optional[float] = None,
                 rel_eps: Optional[float] = None,
                 ):

        self.max_iterations = max_iterations if max_iterations else DEFAULT_MAX_ITERATIONS
        assert self.max_iterations > 0, f"Maximum number of iterations must be positive. {self.max_iterations} given."

        self.abs_tol = abs_eps if abs_eps else DEFAULT_ABS_TOLERANCE
        assert self.abs_tol >= 0, f"Absolute ε must be >= 0. {self.abs_tol:.5} given."

        self.rel_tol = rel_eps if rel_eps else DEFAULT_REL_TOLERANCE
        assert self.rel_tol >= 0, f"Relative ε must be >= 0. {self.abs_tol:.5} given."

    @abstractmethod
    def get_entering_dantzig(self, 
                             v: Vertex, 
                             d: Optional[Union[np.ndarray, List[float]]] = None,
                             ) -> Optional[LpConstraint]:
        pass
    
    @abstractmethod
    def get_entering_bland(self, 
                           v: Vertex, 
                           d: Optional[Union[np.ndarray, List[float]]] = None,
                           ) -> Optional[LpConstraint]:
        pass
    
    def get_entering_constraint(self, 
                                v: Vertex, 
                                d: Optional[Union[np.ndarray, List[float]]] = None,
                                pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                                ) -> Optional[LpConstraint]:
        return self.get_entering_bland(v, d) if pivot_rule == "bland" else self.get_entering_dantzig(v, d)

    @abstractmethod
    def get_leaving_dantzig(self, 
                            v: Vertex, 
                            d: Optional[Union[np.ndarray, List[float]]] = None,
                            ) -> Optional[LpConstraint]:
        pass
    
    @abstractmethod
    def get_leaving_bland(self, 
                          v: Vertex, 
                          d: Optional[Union[np.ndarray, List[float]]] = None,
                          ) -> Optional[LpConstraint]:
        pass
    
    def get_leaving_constraint(self, 
                               v: Vertex, 
                               d: Optional[Union[np.ndarray, List[float]]] = None,
                               pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                               ) -> Optional[LpConstraint]:
        return self.get_leaving_bland(v, d) if pivot_rule == "bland" else self.get_leaving_dantzig(v, d)

    
    @abstractmethod
    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        pass
    
    @abstractmethod
    def get_starting_point(self, 
                           problem: LpProblem, 
                           pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                           ) -> Tuple[Optional[Vertex], int]:
        pass

    @abstractmethod
    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs):
        pass

    @abstractmethod
    def minimize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs):
        pass