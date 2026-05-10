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
from gsimplex.constants import (
    DEFAULT_ABS_TOLERANCE,
    DEFAULT_REL_TOLERANCE,
    PivotRule,
    DEFAULT_PIVOT_RULE,
)


class DualSimplex(ISimplex):

    def get_leaving_bland(self, 
                           v: Vertex,
                           d: Optional[Union[np.ndarray, List[float]]] = None,
                           ) -> Optional[LpConstraint]:
        """
        Bland version of dual ratio test.
        """

        return self.get_leaving_dantzig(v, d)

    def get_leaving_dantzig(self, 
                             v: Vertex,
                             d: Optional[Union[np.ndarray, List[float]]] = None,
                             ) -> Optional[LpConstraint]:
        """
        Choose entering constraint minimizing ratio:
            y_j / a_rj   with a_rj < 0
        """

        assert d is not None, "Direction Ak must be provided"
        candidates: List[Tuple[LpConstraint, float]] = []

        for i, c in enumerate(v):
            den = d @ v.W[:, i]
            if den > DEFAULT_ABS_TOLERANCE:
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
        Smallest index among violated constraints.
        """

        violations = v.primal_infeasible_constraints()
        if len(violations) == 0:
            return None

        entering, _ = violations[0]
        return entering
    
    def get_entering_dantzig(self, 
                            v: Vertex, 
                            d: Optional[Union[np.ndarray, List[float]]] = None,
                            ) -> Optional[LpConstraint]:
        """
        Pick least violated primal constraint (least negative slack != 0).
        """

        violations = v.primal_infeasible_constraints()
        if len(violations) == 0:
            return None

        # Most negative residual
        entering, _ = max(violations, key=lambda x: x[1])
        return entering

    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        """
        Dual simplex direction:
        corresponds to column of W associated with leaving constraint.
        """
        
        Ak = Vertex.constraint_to_row(constraint, v.problem)
        return Ak


    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs):
        
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
        
            if not start_basis.is_dual_feasible():
                raise UnFeasibleProblemException(
                    f"#{initial_iterations} Starting point isn't dual-feasible",
                    str(start_basis),
                )

            current = start_basis
            for i in range(initial_iterations, self.max_iterations):
                if not current.is_dual_feasible():
                    raise InvalidBasisException(
                        f"#{i} Current point isn't dual-feasible",
                        str(current),
                    )
                
                if current.is_optimal_point():
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
                        problem,
                    )

                print(f"Replacing \"{leaving}\" with \"{entering}\"")
                current.swap(entering, leaving)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )

        except GsimplexException as e:
            print(e)
            problem.status = e.status

    
    def minimize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs
                 ):
        
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

        for it in range(self.max_iterations):
            dual_infeas = v.dual_infeasible_contraints()
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
                    if den > DEFAULT_ABS_TOLERANCE:
                        ratios.append((c, slack / den))

                if len(ratios) > 0:
                    entering, _ = min(ratios, key=lambda x: x[1])
            else:
                for constraint in v.non_basis:
                    pivot = d @ Vertex.constraint_to_row(constraint, v.problem)
                    if pivot < -DEFAULT_ABS_TOLERANCE:
                        entering = constraint
                        break

            if entering is None:
                raise UnboundedProblemException(
                    "Phase I dual-problem is unbounded",
                    v,
                    d,
                    leaving,
                )
                
            v.swap(entering, leaving)

        raise IterationLimitReachedException(
            f"Max iterations ({self.max_iterations}) reached for Phase I problem"
        )
        

    def get_starting_point(self, 
                           problem: LpProblem,
                           pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                           ) -> Tuple[Optional[Vertex], int]:

        n = problem.numVariables()
    
        constraints = list(problem.constraints.values())
        initial_point = Vertex(problem, *constraints[:n])
        try:
            return self.phase_one_solve(initial_point, pivot_rule=pivot_rule)
        except GsimplexException as e:
            print(e)
            return None, 0