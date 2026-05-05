from abc import ABC, abstractmethod
from typing import Optional, Tuple
from pulp import LpProblem

from gsimplex.solvers.solver_interface import ISolver
from gsimplex.vertex import Vertex

class ISimplex(ISolver, ABC):
    @abstractmethod
    def get_feasible_vertex(self, problem: LpProblem) -> Optional[Tuple[Vertex, int]]:
        pass

    @abstractmethod
    def make_feasible(self, vertex: Vertex) -> Optional[Vertex]:
        pass