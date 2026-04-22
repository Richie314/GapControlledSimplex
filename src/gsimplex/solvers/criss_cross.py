from typing import Optional, Tuple, List

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solution import Solution

class CrissCross(IterativeSolver):
    def get_starting_point(self, problem: Problem, given_basis: Optional[List[int]] = None) -> Tuple[Optional[Vertex], int]:
        raise NotImplementedError()

    def maximize(self, problem: Problem, start_basis: Optional[List[int]] = None) -> Optional[Solution]:
        raise NotImplementedError()