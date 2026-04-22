from abc import ABC
from typing import Optional, Tuple

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex

class ISimplex(ISolver, ABC):
    def get_feasible_vertex(self, problem: Problem) -> Optional[Tuple[Vertex, int]]:
        pass

    def make_feasible(self, vertex: Vertex) -> Optional[Vertex]:
        pass