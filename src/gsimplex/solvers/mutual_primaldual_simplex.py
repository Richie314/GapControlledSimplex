from typing import Optional, List, Union, Tuple
from pulp import (
    LpProblem, LpConstraint,
    LpMaximize, LpStatusOptimal,
)
import numpy as np

from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapDoubleSimplex
from gsimplex.vertex import Vertex
from gsimplex.tools.problem import get_different_constraints
from gsimplex.tools.gap import vertex_gap, gap_max, gap_min
from gsimplex.exception import *
from gsimplex.constants import *

class MutualPrimalDualSimplex(PrimalSimplex, DualSimplex):
    """
    Mutual Primal-Dual Simplex algorithm first proposed by
    Michel L. Balinsky and Ralph E. Gomory in 1963.
    """

    
    def get_starting_point(self, 
                           problem: LpProblem,
                           ) -> Tuple[Optional["Vertex"], int]:
        """
        Initialize a non-feasible starting point.

        :param problem: The LP problem.
        :type problem: LpProblem
        :return: A - not necessarily feasible - vertex.
        :rtype: Tuple[Optional[Vertex], int]
        """

        constraints = get_different_constraints(problem)
        return Vertex(problem, *constraints), 0
    
    
    def _get_initial_point(self, 
                           problem: LpProblem, 
                           given: Union["Vertex", List[LpConstraint], List[str], None],
                           ) -> "Vertex":
        """
        Initialize a non-feasible starting point.

        :param problem: The LP problem.
        :type problem: LpProblem
        :param given: Optional starting basis.
        :type given: Union[Vertex, List[LpConstraint], List[str], None]
        :return: A - not necessarily feasible - vertex.
        :rtype: Vertex
        """

        if given is None:
            given, _ = self.get_starting_point(problem)
        
        assert given is not None

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

    def _conditional_iteration(self,
                               primal_infeas: List[Tuple[LpConstraint, float]], 
                               dual_infeas: List[Tuple[LpConstraint, float]],
                               current: "Vertex",
                               ):
        
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

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Union["Vertex", List[LpConstraint], List[str], None] = None,
                 **kwargs
                 ):
        """
        Solve a maximization problem using the gap-controlled double simplex method.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis for the primal point.
        :type start_basis: Union[Vertex, List[LpConstraint], List[str], None]
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            # If no starting point was already provided,
            # grab a set of constraints, not necesseraly feasible
            current = self._get_initial_point(problem, given=start_basis)

            for _ in range(self.max_iterations):
                primal_infeas = current.primal_infeasible_constraints(eps=self.abs_tol)
                dual_infeas = current.dual_infeasible_contraints(eps=self.abs_tol)

                # Check optimality
                if len(primal_infeas) == 0 and len(dual_infeas) == 0:
                    problem.status = LpStatusOptimal
                    return        

                self._conditional_iteration(primal_infeas, dual_infeas, current)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )


        except GsimplexException as e:
            problem.status = e.status

class MutualGapSimplex(MutualPrimalDualSimplex, GapDoubleSimplex):
    """
    
    """
    


    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Union[Vertex, List[LpConstraint], List[str], None] = None,
                 lb: Union[np.ndarray, float, List[float], None] = None,
                 ub: Union[np.ndarray, float, List[float], None] = None,
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
            current = self._get_initial_point(problem, given=start_basis)

            gap = float('+inf')
            rel_gap = float('+inf')

            for _ in range(self.max_iterations):
                primal_infeas = current.primal_infeasible_constraints(eps=self.abs_tol)
                dual_infeas = current.dual_infeasible_contraints(eps=self.abs_tol)

                is_primal_feasible = len(primal_infeas) == 0
                is_dual_feasible = len(dual_infeas) == 0

                # Check optimality
                if is_primal_feasible and is_dual_feasible:
                    problem.status = LpStatusOptimal
                    return
                
                if is_primal_feasible:
                    """
                    Point has reached primal feasibility (but not optimality).
                    From now on, only primal pivots will be executed.
                    The ub will not change, but the lb will slightly increase
                    Reducing the gap until optimality.
                    """
                    new_lb = gap_max(lb, current.x, eps=self.abs_tol, lp=current.problem)
                    lb = new_lb.x if isinstance(new_lb, Vertex) else new_lb

                if is_dual_feasible:
                    """
                    Point has reached dual feasibility (but not optimality).
                    From now on, only dual pivots will be executed.
                    The lb will not change, but the ub will slightly decrease
                    Reducing the gap until optimality.
                    """
                    new_ub = gap_min(ub, current.y, eps=self.abs_tol, lp=current.problem)
                    ub = new_ub.y if isinstance(new_ub, Vertex) else new_ub

                if lb is not None and ub is not None:
                    gap, rel_gap, _, _ = vertex_gap(ub, lb, lp=current.problem, eps=self.abs_tol)

                if gap < self.abs_gap or rel_gap < self.rel_gap:

                    assert lb is not None
                    assert ub is not None

                    if isinstance(lb, np.ndarray) or isinstance(lb, List):
                        for i, xi in enumerate(problem.variables()):
                            xi.varValue = lb[i]

                        problem.status = LpStatusOptimal
                        return
                
                self._conditional_iteration(primal_infeas, dual_infeas, current)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )


        except GsimplexException as e:
            problem.status = e.status