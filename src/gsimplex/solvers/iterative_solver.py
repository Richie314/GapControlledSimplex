from abc import ABC, abstractmethod
from typing import Optional, Tuple

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex

class IterativeSolver(ISolver, ABC):
    def __init__(self):
        self.max_iterations: Optional[int] = None

    def _check_iteration_count(self, iterations: int) -> bool:
        return self.max_iterations is None or iterations <= self.max_iterations

    @abstractmethod
    def get_starting_point(self, 
                           problem: Problem, 
                           given_basis: Optional[list[int]] = None
                           ) -> Tuple[Optional[Vertex], int]:
        pass