from abc import ABC, abstractmethod
from typing import Optional, Tuple

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.problem import Problem
from gsimplex.vertex import Vertex

class ISimplex(ISolver, ABC):
    @abstractmethod
    def get_feasible_vertex(self, problem: Problem) -> Optional[Tuple[Vertex, int]]:
        pass

    @abstractmethod
    def make_feasible(self, vertex: Vertex) -> Optional[Vertex]:
        pass