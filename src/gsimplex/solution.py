from dataclasses import dataclass

from gsimplex.vertex import Vertex

@dataclass
class Solution:
    point: Vertex
    iteration_count: int
    initial_iterations: int = 0

    @property
    def problem(self):
        return self.point.problem

    @property
    def basis(self):
        return self.point.basis

    @property
    def x(self):
        return self.point.x

    @property
    def y(self):
        return self.point.y