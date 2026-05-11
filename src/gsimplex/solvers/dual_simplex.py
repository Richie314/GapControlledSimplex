from typing import Optional, Tuple, List, Union
from pulp import LpProblem, LpConstraint
from pulp.constants import LpStatusOptimal, LpMinimize, LpMaximize
import numpy as np

from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.vertex import Vertex
from gsimplex.exception import (
    UnboundedProblemException,
    UnFeasibleProblemException,
    InvalidBasisException,
    IterationLimitReachedException,
    GsimplexException,
)
from gsimplex.constants import PivotRule, DEFAULT_PIVOT_RULE

class DualSimplex(ISimplex):
    """
    Dual simplex solver implementation.
    """

    def get_leaving_bland(self, 
                           v: Vertex,
                           d: Optional[Union[np.ndarray, List[float]]] = None,
                           ) -> Optional[LpConstraint]:
        """
        Select the leaving constraint using Bland's dual ratio rule.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector (not used by Bland rule).
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen leaving constraint or None when no valid candidate exists.
        :rtype: Optional[LpConstraint]
        """

        return self.get_leaving_dantzig(v, d)

    def get_leaving_dantzig(self, 
                             v: Vertex,
                             d: Optional[Union[np.ndarray, List[float]]] = None,
                             ) -> Optional[LpConstraint]:
        """
        Select the leaving constraint by minimizing the dual ratio.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector used to compute ratios.
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen leaving constraint or None when no valid candidate exists.
        :rtype: Optional[LpConstraint]
        """

        assert d is not None, "Direction Ak must be provided"
        candidates: List[Tuple[LpConstraint, float]] = []

        for i, c in enumerate(v):
            den = d @ v.W[:, i]
            if den > self.abs_tol:
                continue

            ratio = -v.y[v.global_index(c)] / den
            candidates.append((c, ratio))

        if len(candidates) == 0:
            return None

        leaving, _ = min(candidates, key=lambda x: x[1])
        return leaving

    def get_entering_bland(self, 
                          v: Vertex, 
                          d: Optional[Union[np.ndarray, List[float]]] = None,
                          ) -> Optional[LpConstraint]:
        """
        Select the entering constraint using Bland's primal violation order.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector (not used in this rule).
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen entering constraint or None when none are violated.
        :rtype: Optional[LpConstraint]
        """

        violations = v.primal_infeasible_constraints(eps=self.abs_tol)
        if len(violations) == 0:
            return None

        entering, _ = violations[0]
        return entering
    
    def get_entering_dantzig(self, 
                            v: Vertex, 
                            d: Optional[Union[np.ndarray, List[float]]] = None,
                            ) -> Optional[LpConstraint]:
        """
        Select the entering constraint by choosing the most violated primal constraint.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector (not used by this selection rule).
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen entering constraint or None when no violations exist.
        :rtype: Optional[LpConstraint]
        """

        violations = v.primal_infeasible_constraints(eps=self.abs_tol)
        if len(violations) == 0:
            return None

        # Most negative residual
        entering, _ = max(violations, key=lambda x: x[1])
        return entering

    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        """
        Compute the dual simplex moving direction for a constraint.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param constraint: The constraint used to compute the direction.
        :type constraint: LpConstraint
        :return: The moving direction vector for the dual simplex step.
        :rtype: np.ndarray
        """
        
        Ak = Vertex.constraint_to_row(constraint, v.problem)
        return Ak


    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs):
        """
        Solve a maximization problem using the dual simplex method.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis or vertex.
        :type start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :param pivot_rule: Pivot rule used to choose entering and leaving constraints.
        :type pivot_rule: PivotRule
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            initial_iterations = 0
            if start_basis is None:
                start_basis, initial_iterations = self.get_starting_point(problem)

            if start_basis is None:
                raise UnFeasibleProblemException(
                    "Could not find a starting, dual-feasible, basis"
                )
            
            if not isinstance(start_basis, Vertex):
                start_basis = Vertex(
                    problem, 
                    *[problem.constraints[name] if isinstance(name, str) else name for name in start_basis]
                )
        
            if not start_basis.is_dual_feasible(eps=self.abs_tol):
                raise UnFeasibleProblemException(
                    f"#{initial_iterations} Starting point isn't dual-feasible",
                )

            current = start_basis
            for i in range(initial_iterations, self.max_iterations):
                if not current.is_dual_feasible(eps=self.abs_tol):
                    raise InvalidBasisException(
                        f"#{i} Current point isn't dual-feasible",
                    )
                
                if current.is_primal_feasible(eps=self.abs_tol):
                    problem.status = LpStatusOptimal
                    return
                
                # Choose entering constraint
                entering = self.get_entering_constraint(current, pivot_rule=pivot_rule)
                assert entering is not None
            
                # Calculate the direction
                direction = self.get_moving_direction(current, entering)

                # Choose leaving constraint
                leaving = self.get_leaving_constraint(current, d=direction, pivot_rule=pivot_rule)
                if leaving is None:
                    raise UnFeasibleProblemException(
                        f"#{i} Dual simplex detected infeasibility",
                    )

                current.swap(entering, leaving)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )

        except GsimplexException as e:
            # print(e)
            problem.status = e.status

    
    def minimize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs
                 ):
        """
        Solve a minimization problem by converting it to a maximization problem for dual simplex.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis or vertex.
        :type start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]]
        :param pivot_rule: Pivot rule used during the solve.
        :type pivot_rule: PivotRule
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        
        assert problem.sense == LpMinimize, "Tried to minimize a maximization problem!"
        assert problem.objective

        problem.setObjective(-problem.objective)
        problem.sense = LpMaximize

        self.maximize(problem=problem, 
                      start_basis=start_basis,
                      pivot_rule=pivot_rule,
                      **kwargs)
        
        problem.setObjective(-problem.objective)
        problem.sense = LpMinimize

    def phase_one_solve(self, 
                        v: Vertex, 
                        pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                        ) -> Tuple[Vertex, int]:
        """
        Perform Phase I iterations to obtain a dual-feasible starting vertex.

        :param v: Initial vertex for the Phase I solve.
        :type v: Vertex
        :param pivot_rule: Pivot rule used during Phase I.
        :type pivot_rule: PivotRule
        :return: A tuple with a dual-feasible vertex and the number of iterations used.
        :rtype: Tuple[Vertex, int]
        """

        for it in range(self.max_iterations):
            dual_infeas = v.dual_infeasible_contraints(eps=self.abs_tol)
            if len(dual_infeas) == 0:
                # No infeasible constraints ==> vertex is dual-feasible
                return v, it

            if pivot_rule == 'bland':
                leaving, _ = dual_infeas[0]
            else:
                leaving, _ = max(dual_infeas, key=lambda x: abs(x[1]))
            assert leaving in v, "Leaving index must be in vertex"

            if pivot_rule == 'bland':
                d = v.W[:, v.index(leaving)]
            else:
                # A_B @ d = Ap --> d = A_B^-1 @ Ap = -W @ Ap 
                d = -v.W @ Vertex.constraint_to_row(leaving, v.problem)

            entering: Optional[LpConstraint] = None
            if pivot_rule == 'bland':
                ratios: List[Tuple[LpConstraint, float]] = []
                for c in v.non_basis:
                    Ai = Vertex.constraint_to_row(c, v.problem)
                    slack = Vertex.slack(c)

                    den = float(Ai @ d)
                    if den > self.abs_tol:
                        ratios.append((c, slack / den))

                if len(ratios) > 0:
                    entering, _ = min(ratios, key=lambda x: x[1])
            else:
                for constraint in v.non_basis:
                    pivot = d @ Vertex.constraint_to_row(constraint, v.problem)
                    if pivot < -self.abs_tol:
                        entering = constraint
                        break

            if entering is None:
                raise UnboundedProblemException(
                    "Phase I dual-problem is unbounded",
                )
                
            v.swap(entering, leaving)

        raise IterationLimitReachedException(
            f"Max iterations ({self.max_iterations}) reached for Phase I problem"
        )
        

    def get_starting_point(self, 
                           problem: LpProblem,
                           pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                           ) -> Tuple[Optional[Vertex], int]:
        """
        Find a starting point for the dual simplex solver.

        :param problem: The LP problem to initialize.
        :type problem: LpProblem
        :param pivot_rule: Pivot rule used for the starting point search.
        :type pivot_rule: PivotRule
        :return: A dual-feasible starting vertex and the iteration count, or (None, 0).
        :rtype: Tuple[Optional[Vertex], int]
        """

        n = problem.numVariables()
    
        constraints = list(problem.constraints.values())
        initial_point = Vertex(problem, *constraints[:n])
        try:
            return self.phase_one_solve(initial_point, pivot_rule=pivot_rule)
        except GsimplexException as e:
            # print(e)
            return None, 0