from abc import ABC, abstractmethod
from typing import Optional, Tuple, Union, List
from pulp import LpProblem, LpConstraint
import numpy as np

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex
from gsimplex.constants import (
    PivotRule,
    DEFAULT_PIVOT_RULE,
)

class ISimplex(ISolver, ABC):
    def __init__(self, max_iterations: Optional[int] = None):
        if max_iterations is None:
            max_iterations = 1_000

        self.max_iterations: int = max_iterations
        assert self.max_iterations > 0, "Maximum number of iterations must be positive"

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