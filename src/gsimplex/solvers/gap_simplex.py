from typing import Optional, Tuple, List, Union
from pulp import (
    LpProblem, LpConstraint,
    LpMaximize, LpStatusOptimal,
)

from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.vertex import Vertex
from gsimplex.tools.problem import clone_problem
from gsimplex.exception import *
from gsimplex.constants import *

class GapDoubleSimplex(PrimalSimplex, DualSimplex):
    def __init__(self, 
                 max_iterations: Optional[int] = None,
                 abs_eps: Optional[float] = None,
                 rel_eps: Optional[float] = None,
                 abs_gap: Optional[float] = None,
                 rel_gap: Optional[float] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 ):
        """
        Initialize the gap-controlled double simplex solver.

        :param max_iterations: Maximum number of iterations. If None, uses default.
        :type max_iterations: Optional[int]
        :param abs_eps: Absolute tolerance for feasibility checks. If None, uses default.
        :type abs_eps: Optional[float]
        :param rel_eps: Relative tolerance for numerical comparisons. If None, uses default.
        :type rel_eps: Optional[float]
        :param abs_gap: Absolute gap threshold for early termination. If None, uses default.
        :type abs_gap: Optional[float]
        :param rel_gap: Relative gap threshold for early termination. If None, uses default.
        :type rel_gap: Optional[float]
        :param pivot_rule: Pivot rule for simplex iterations.
        :type pivot_rule: PivotRule
        """
        super().__init__(max_iterations, abs_eps, rel_eps, pivot_rule)

        self.abs_gap = abs_gap if abs_gap else DEFAULT_ABS_GAP
        assert self.abs_gap >= 0, f"Absolute gap must be >= 0. {self.abs_gap:.5} given."

        self.rel_gap = rel_gap if rel_gap else DEFAULT_REL_GAP
        assert self.rel_gap >= 0, f"Relative gap must be >= 0. {self.rel_gap:.5} given."


    def __primal_init(self, 
                      problem: LpProblem, 
                      given: Optional[Union[List[LpConstraint], Vertex, List[str]]],
                      ) -> Tuple["Vertex", int]:
        """
        Initialize a primal-feasible starting point.

        :param problem: The LP problem.
        :type problem: LpProblem
        :param given: Optional starting basis.
        :type given: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :return: A primal-feasible vertex and iteration count.
        :rtype: Tuple[Vertex, int]
        :raises UnFeasibleProblemException: If no primal-feasible point is found.
        """
        it = 0
        if given is None:
            given, it = PrimalSimplex.get_starting_point(self, problem)

        if given is None:
            raise UnFeasibleProblemException(
                "Could not find a *primal-feasible* starting point (basis)"
            )

        if not isinstance(given, Vertex):
            given = Vertex(
                problem, 
                *[problem.constraints[name] if isinstance(name, str) else name for name in given]
            )
    
        if not given.is_primal_feasible(self.abs_tol):
            raise UnFeasibleProblemException(
                f"#{it} Starting point isn't primal-feasible",
            )

        return given, it
    
    def __dual_init(self, 
                      problem: LpProblem, 
                      given: Optional[Union[List[LpConstraint], Vertex, List[str]]],
                      ) -> Tuple["Vertex", int]:
        """
        Initialize a dual-feasible starting point.

        :param problem: The LP problem.
        :type problem: LpProblem
        :param given: Optional starting basis.
        :type given: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :return: A dual-feasible vertex and iteration count.
        :rtype: Tuple[Vertex, int]
        :raises UnFeasibleProblemException: If no dual-feasible point is found.
        """
        it = 0
        if given is None:
            given, it = DualSimplex.get_starting_point(self, problem)

        if given is None:
            raise UnFeasibleProblemException(
                "Could not find a *dual-feasible* starting point (basis)"
            )

        if not isinstance(given, Vertex):
            given = Vertex(
                problem, 
                *[problem.constraints[name] if isinstance(name, str) else name for name in given]
            )
    
        if not given.is_dual_feasible(eps=self.abs_tol):
            raise UnFeasibleProblemException(
                f"#{it} Starting point isn't dual-feasible",
            )

        return given, it

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

        dual_problem = clone_problem(problem)

        try:
            primal_point, primal_it = self.__primal_init(problem, given=start_basis)
            dual_point,   dual_it = self.__dual_init(dual_problem, given=None)

            for it in range(max(primal_it, dual_it), self.max_iterations):
                if not primal_point.is_primal_feasible(eps=self.abs_tol):
                    raise InvalidBasisException(
                        f"#{it} Primal point has lost primal-feasibility.",
                    )
                
                if primal_point.is_dual_feasible(eps=self.abs_tol):
                    # Primal point has reached optimality
                    problem.status = LpStatusOptimal
                    return
                
                if not dual_point.is_dual_feasible(eps=self.abs_tol):
                    raise InvalidBasisException(
                        f"#{it} Dual point has lost dual-feasibility",
                    )
                
                if dual_point.is_primal_feasible(eps=self.abs_tol):
                    # Dual point has reached optimality
                    problem.status = LpStatusOptimal
                    
                    # Since dual_point operates on the copy of the main problem
                    # we need to copy the values here from the Vertex to the problem
                    for i, var in enumerate(problem.variables()):
                        var.varValue = dual_point.x[i]
                    
                    return
                
                gap, rel_gap, primal_value, dual_value = Vertex.gap(dual_point, primal_point, self.abs_tol)
                if gap < self.abs_gap or rel_gap < self.rel_gap:
                    # Optimality was not reached, but we are close enough
                    problem.status = LpStatusOptimal
                    return

                PrimalSimplex._single_iteration(self, primal_point)
                DualSimplex._single_iteration(self, dual_point)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )


        except GsimplexException as e:
            problem.status = e.status