from abc import ABC, abstractmethod
from typing import Optional

from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solution import Solution

class ISolver(ABC):
    @abstractmethod
    def maximize(self, problem: Problem, start_basis: Optional[list[int]] = None) -> Optional[Solution]:
        pass

    def minimize(self, 
                 problem: Problem, 
                 start_basis: Optional[list[int]] = None
                 ) -> Optional[Solution]:
        
        inverted_problem = Problem(-problem.c, problem.A, problem.b)
        result = self.maximize(inverted_problem, start_basis)
        if result is None:
            return None
        
        # Change back to original problem
        return Solution(
            point=Vertex(problem, result.basis),
            iteration_count=result.iteration_count
        )