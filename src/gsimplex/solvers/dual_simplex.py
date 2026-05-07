from typing import Optional, Tuple, List, Union
from pulp import LpProblem, LpConstraint
from pulp.constants import LpStatusOptimal
import numpy as np

from gsimplex.solvers.simplex_interface import ISimplex, PivotRule, DEFAULT_PIVOT_RULE
from gsimplex.vertex import Vertex, DEFAULT_ABS_TOLERANCE
from gsimplex.exception import (
    UnboundedProblemException,
    UnFeasibleProblemException,
    InvalidBasisException,
    IterationLimitReachedException,
    GsimplexException,
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

        for i, global_i in enumerate(v.indices):

            den = d @ v.W[:, i]
            if den > -DEFAULT_ABS_TOLERANCE:
                continue

            ratio = v.y[global_i] / den
            candidates.append((v[i], ratio))

        if len(candidates) == 0:
            return None

        return min(candidates, key=lambda x: x[1])[0]

    def get_entering_bland(self, 
                          v: Vertex, 
                          d: Optional[Union[np.ndarray, List[float]]] = None,
                          ) -> Optional[LpConstraint]:
        """
        Smallest index among violated constraints.
        """

        violations = v.primal_infeasible_contraints()
        if len(violations) == 0:
            return None

        return violations[0][0]
    
    def get_entering_dantzig(self, 
                            v: Vertex, 
                            d: Optional[Union[np.ndarray, List[float]]] = None,
                            ) -> Optional[LpConstraint]:
        """
        Pick most violated primal constraint (most negative slack).
        """

        violations = v.primal_infeasible_contraints()
        if len(violations) == 0:
            return None

        # Most negative residual
        entering, _ = min(violations, key=lambda x: abs(x[1]))
        return entering

    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        """
        Dual simplex direction:
        corresponds to column of W associated with leaving constraint.
        """
        
        return Vertex.constraint_to_row(constraint, v.problem)


    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs):

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

    def phase_one_solve(self, vertex: Vertex) -> Tuple[Vertex, int]:

        iterations = 0
        while iterations < self.max_iterations:
            dual_infeas = vertex.dual_infeasible_contraints()
            if len(dual_infeas) == 0:
                break # No infeasible constraints ==> vertex is feasible

            # Exiting constraint (Bland rule): grab the first infeasible constraint
            leaving, _ = dual_infeas[0]

            # d = A_B^-1 @ Ap
            d = -vertex.W @ Vertex.constraint_to_row(leaving, vertex.problem)

            # Entering constraint: Bland rule only
            entering: Optional[LpConstraint] = None
            for constraint in vertex.non_basis:
                pivot = d @ Vertex.constraint_to_row(constraint, vertex.problem)
                if pivot <= -DEFAULT_ABS_TOLERANCE:
                    entering = constraint
                    break

            if entering is None:
                raise UnboundedProblemException

            vertex.swap(entering, leaving)
            iterations += 1

        return vertex, iterations
        

    def get_starting_point(self, problem: LpProblem) -> Tuple[Optional[Vertex], int]:

        n = problem.numVariables()
    
        constraints = list(problem.constraints.values())
        initial_point = Vertex(problem, *constraints[:n])
        try:
            return self.phase_one_solve(initial_point)
        except GsimplexException:
            return None, 0