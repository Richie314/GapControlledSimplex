from typing import Optional, List, Union
from pulp import (
    LpProblem, LpConstraint,
    LpMaximize, LpStatusOptimal,
)
import numpy as np

from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.vertex import Vertex
from gsimplex.tools.problem import get_different_constraints
from gsimplex.exception import *
from gsimplex.constants import *

class MutualPrimalDualSimplex(PrimalSimplex, DualSimplex):
    """
    Mutual Primal-Dual Simplex algorithm first proposed by
    Michel L. Balinsky and Ralph E. Gomory in 1963.
    """

    
    def __get_initial_point(self, 
                            problem: LpProblem, 
                            given: Optional[Union[List[LpConstraint], Vertex, List[str]]],
                            ) -> "Vertex":
        """
        Initialize a dual-feasible starting point.

        :param problem: The LP problem.
        :type problem: LpProblem
        :param given: Optional starting basis.
        :type given: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :return: A - not necessarily feasible - vertex.
        :rtype: Vertex
        :raises UnFeasibleProblemException: If no point is found.
        """
        if given is None:
            given = get_different_constraints(problem)
            given = Vertex(problem, *given)

        if given is None:
            raise UnFeasibleProblemException(
                "Could not find a proper set of initial constraints to form a basis"
            )

        if not isinstance(given, Vertex):
            given = Vertex(
                problem, 
                *[problem.constraints[name] if isinstance(name, str) else name for name in given]
            )

        return given
    
    def get_pivot_type(self, 
                       primal_slacks: Union[List[float], np.ndarray], 
                       dual_infeas: Union[List[float], np.ndarray],
                       ) -> "PivotType":
        """
        Calculates a score based on the current infeasibilities and decides
        if a `primal` pivot is appropriate of if a `dual` one is.
        """

        score = sum([abs(p) for p in primal_slacks] + [-abs(d) for d in dual_infeas])

        return "primal" if score < 0 else "dual"


    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 **kwargs
                 ):
        """
        Solve a maximization problem using the gap-controlled double simplex method.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis for the primal point.
        :type start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            # If no starting point was already provided,
            # grab a set of constraints, not necesseraly feasible
            current = self.__get_initial_point(problem, given=start_basis)

            for _ in range(self.max_iterations):
                primal_infeas = current.primal_infeasible_constraints(eps=self.abs_tol)
                dual_infeas = current.dual_infeasible_contraints(eps=self.abs_tol)

                # Check optimality
                if len(primal_infeas) == 0 and len(dual_infeas) == 0:
                    problem.status = LpStatusOptimal
                    return        

                # The choice on the type of pivot is performed via
                # the current infeasibilities (both primal and dual)
                pivot_type = self.get_pivot_type(
                    [p[1] for p in primal_infeas],
                    [d[1] for d in dual_infeas]
                )

                if pivot_type == "primal":
                    PrimalSimplex._single_iteration(self, current)
                else:
                    DualSimplex._single_iteration(self, current)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )


        except GsimplexException as e:
            problem.status = e.status