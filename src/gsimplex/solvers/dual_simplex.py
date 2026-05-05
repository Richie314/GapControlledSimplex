from typing import Optional, Tuple, Union, List
from pulp import (
    LpProblem, LpConstraint,
    LpStatusNotSolved, LpStatusOptimal, 
    LpStatusUnbounded, LpStatusInfeasible,
)

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.vertex import Vertex, DEFAULT_ABS_TOLERANCE
from gsimplex.exception import (
    UnboundedProblemException,
    UnFeasibleProblemException,
    GsimplexException,
)

class DualSimplex(IterativeSolver, ISimplex):
    @staticmethod
    def iteration(vertex: Vertex) -> Vertex:
        if not vertex.is_dual_feasible():
            raise UnFeasibleProblemException

        infeas = vertex.primal_infeasible_rows()
        if len(infeas) == 0:
            return vertex  # Optimal
        
        # Entering constraint (Bland rule): grab the first infeasible constraint
        k, _ = infeas[0]
        Ak = Vertex.constraint_to_row(k, vertex.problem)

        # Leaving constraint (Minimum ratio + Bland rule)
        ratios = []
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
            
            current, _ = self.get_starting_point(problem, start_basis)
            if current is None:
                raise UnFeasibleProblemException


            while self._check_iteration_count(iterations):
                if current.is_optimal_point():
                    problem.status = LpStatusOptimal
                    return
                
                print(f"{current.x=}")
                current = self.iteration(current)
                iterations += 1

        except GsimplexException as e:
            problem.status = e.status

    def make_feasible(self, vertex: Vertex) -> Vertex:
        v = vertex
        while True:
            dual_infeas = v.dual_infeasible_values()
            if len(dual_infeas) == 0:
                break

            p, _ = dual_infeas[0]
            d = -v.W @ Vertex.constraint_to_row(p, vertex.problem)

            # Entering index
            min_pivot = float('inf')
            q = None
            for constraint in v.non_basis:
                pivot = Vertex.constraint_to_row(constraint, vertex.problem) @ d
                if pivot <= -DEFAULT_ABS_TOLERANCE and abs(pivot) < min_pivot:
                    min_pivot = abs(pivot)
                    q = constraint

            if q is None:
                raise UnboundedProblemException(vertex.problem)

            v = v.swap(q, p)

        return v

    def get_feasible_vertex(self, problem: LpProblem) -> Optional[Tuple[Vertex, int]]:
        
        constraints = list(problem.constraints.values())
        initial_point = Vertex(problem, *constraints[:problem.numVariables()])

        try:
            dual_feasible = self.make_feasible(initial_point)
            return dual_feasible, 0
        except GsimplexException:
            return None
        

    def get_starting_point(self, 
                           problem: LpProblem, 
                           given_basis: Optional[Union[List[LpConstraint], Vertex]] = None
                           ) -> Tuple[Optional[Vertex], int]:
        if given_basis is not None:
            if isinstance(given_basis, Vertex):
                return given_basis, 0
            return Vertex(problem, *given_basis), 0

        phase_one = self.get_feasible_vertex(problem)
        if phase_one is None:
            return None, 0
        return phase_one