from typing import Optional, Tuple, Union, List
from pulp import (
    LpProblem, LpConstraint,
    LpStatusOptimal,
)

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.vertex import Vertex, DEFAULT_ABS_TOLERANCE
from gsimplex.exception import (
    UnboundedProblemException,
    UnFeasibleProblemException,
    InvalidBasisException,
    GsimplexException,
)

class DualSimplex(IterativeSolver, ISimplex):
    def __init__(self, max_iterations: Optional[int] = 1_000):
        super().__init__()
        self.max_iterations = max_iterations

    @staticmethod
    def iteration(vertex: Vertex) -> Vertex:
        if not vertex.is_dual_feasible():
            raise InvalidBasisException

        infeas = vertex.primal_infeasible_rows()
        if len(infeas) == 0:
            return vertex  # Optimal
        
        # Entering constraint (Bland rule): grab the first infeasible constraint
        infeas.sort(key=lambda x: x[0].name if x[0].name else "")
        k, _ = infeas[0]
        Ak = Vertex.constraint_to_row(k, vertex.problem)

        # Leaving constraint (Minimum ratio + Bland rule)
        ratios: List[Tuple[LpConstraint, float]] = []
        for constraint in vertex:
            idx = vertex.index(constraint)
            den = Ak @ vertex.W[:, idx]
            if den < -DEFAULT_ABS_TOLERANCE:
                ratios.append((constraint, -vertex.y[vertex.global_index(constraint)] / den))

        if len(ratios) == 0:
            raise UnboundedProblemException

        ratios.sort(key=lambda x: (x[1], x[0].name))
        h, _ = ratios[0]

        return vertex.swap(k, h)

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex]] = None
                 ):
        iterations = 0
        try:
            if start_basis is None:
                start_basis, iterations = self.get_starting_point(problem)

            if start_basis is None:
                raise UnFeasibleProblemException
            
            if not isinstance(start_basis, Vertex):
                start_basis = Vertex(problem=problem, *start_basis)

            current = start_basis
            while True:
                
                if current.is_optimal_point():
                    problem.status = LpStatusOptimal
                    return
                
                self._check_iteration_count(iterations)
                
                print(f"{current.x=}")
                current = self.iteration(current)
                iterations += 1

        except GsimplexException as e:
            problem.status = e.status

    def make_feasible(self, vertex: Vertex) -> Tuple[Vertex, int]:

        iterations = 0
        while True:
            dual_infeas = vertex.dual_infeasible_values()
            if len(dual_infeas) == 0:
                break # No infeasible constraints ==> vertex is feasible

            self._check_iteration_count(iterations)

            # Exiting constraint (Bland rule): grab the first infeasible constraint
            dual_infeas.sort(key=lambda x: x[0].name if x[0].name else "")
            p, _ = dual_infeas[0]
            d = -vertex.W @ Vertex.constraint_to_row(p, vertex.problem)

            # Entering constraint
            min_pivot = float('inf')
            q = None
            for constraint in vertex.non_basis:
                pivot = Vertex.constraint_to_row(constraint, vertex.problem) @ d
                if pivot <= -DEFAULT_ABS_TOLERANCE and abs(pivot) < min_pivot:
                    min_pivot = abs(pivot)
                    q = constraint

            if q is None:
                raise UnboundedProblemException

            vertex.swap(entering=q, exiting=p)
            iterations += 1

        return vertex, iterations

    def get_feasible_vertex(self, problem: LpProblem) -> Tuple[Vertex, int]:
        n = problem.numVariables()
        
        constraints = list(problem.constraints.values())
        initial_point = Vertex(problem, *constraints[:n])

        return self.make_feasible(initial_point)
        

    def get_starting_point(self, problem: LpProblem) -> Tuple[Optional[Vertex], int]:

        try:
            return self.get_feasible_vertex(problem)
        except GsimplexException:
            return None, 0