from typing import Optional, Tuple, List, Union
from pulp import (
    LpProblem, LpConstraint,
    LpMaximize, LpStatusOptimal,
)

from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.vertex import Vertex
from gsimplex.exception import *
from gsimplex.constants import *
from gsimplex.tools.problem import get_different_constraints


class CrissCross(PrimalSimplex, DualSimplex):
    """
    A true criss-cross style solver that can start from a point which is
    both primal and dual infeasible and pivot until optimality is reached.
    """

    def get_starting_point(self, problem: LpProblem) -> Tuple[Optional[Vertex], int]:
        """
        Construct a starting vertex using the first `n` constraints.
        This is compatible with the other solvers and provides a basis
        even when the initial point is infeasible.
        """

        initial_constraints = get_different_constraints(problem)
        initial_point = Vertex(problem, *initial_constraints)
        return initial_point, 0

    def maximize(self,
                 problem: LpProblem,
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 **kwargs):
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            if start_basis is None:
                current, it0 = self.get_starting_point(problem)
            else:
                it0 = 0
                if isinstance(start_basis, Vertex):
                    current = start_basis
                else:
                    current = Vertex(
                        problem,
                        *[problem.constraints[name] if isinstance(name, str) else name for name in start_basis]
                    )

            if current is None:
                raise UnFeasibleProblemException(
                    "Could not build an initial basis for CrissCross",
                )

            for i in range(it0, self.max_iterations):
                primal_violations = current.primal_infeasible_constraints(eps=self.abs_tol)
                dual_violations = current.dual_infeasible_contraints(eps=self.abs_tol)

                primal_feas = len(primal_violations) == 0
                dual_feas = len(dual_violations) == 0

                if primal_feas and dual_feas:
                    # Point is both primal and dual feasible, hence optimal
                    problem.status = LpStatusOptimal
                    return
                
                if primal_feas and not dual_feas:
                    # Point is only primal-feasible: only primal-simplex can be safely applied
                    PrimalSimplex._single_iteration(self, current)
                    continue

                if not primal_feas and dual_feas:
                    # Point is only dual-feasible: only dual-simplex can be safely applied
                    DualSimplex._single_iteration(self, current)
                    continue

                raise UnFeasibleProblemException(
                    "Current point is neither primal nor dual feasible"
                )

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )

        except GsimplexException as e:
            problem.status = e.status
