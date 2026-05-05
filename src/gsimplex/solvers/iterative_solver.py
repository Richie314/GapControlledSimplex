from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Union
from pulp import LpProblem, LpConstraint

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex

class IterativeSolver(ISolver, ABC):
    def __init__(self):
        self.max_iterations: Optional[int] = None

    def _check_iteration_count(self, iterations: int) -> bool:
        return self.max_iterations is None or iterations <= self.max_iterations

    @abstractmethod
    def get_starting_point(self, 
                           problem: LpProblem, 
                           given_basis: Optional[Union[List[LpConstraint], Vertex]] = None
                           ) -> Tuple[Optional[Vertex], int]:
        pass