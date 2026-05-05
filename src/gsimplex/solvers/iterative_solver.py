from abc import ABC, abstractmethod
from typing import Optional, Tuple
from pulp import LpProblem

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex
from gsimplex.exception import IterationLimitReachedException

class IterativeSolver(ISolver, ABC):
    def __init__(self):
        self.max_iterations: Optional[int] = None

    def _check_iteration_count(self, iterations: int):
        if self.max_iterations is not None and iterations > self.max_iterations:
            raise IterationLimitReachedException

    @abstractmethod
    def get_starting_point(self, problem: LpProblem) -> Tuple[Optional[Vertex], int]:
        pass