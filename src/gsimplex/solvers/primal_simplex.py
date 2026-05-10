from typing import Optional, Tuple, List, Union
from pulp import LpProblem, LpConstraint, LpVariable
from pulp.constants import ( 
    LpConstraintEQ, LpConstraintLE, LpConstraintGE,
    LpMinimize, LpMaximize, LpStatusOptimal,
)
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


class PrimalSimplex(ISimplex):

    def get_entering_bland(self, 
                           v: Vertex, 
                           d: Optional[Union[np.ndarray, List[float]]] = None,
                           ) -> Optional[LpConstraint]:
        return self.get_entering_dantzig(v, d)

    def get_entering_dantzig(self, 
                             v: Vertex,
                             d: Optional[Union[np.ndarray, List[float]]] = None,
                             ) -> Optional[LpConstraint]:
        assert d is not None

        ratios: List[Tuple[LpConstraint, float]] = []
        for c in v.non_basis:
            Ai = Vertex.constraint_to_row(c, v.problem)
            slack = Vertex.slack(c)

            den = float(Ai @ d)
            if den > self.abs_tol:
                ratios.append((c, slack / den))

        if len(ratios) == 0:
            return None
        
        return min(ratios, key=lambda x: x[1])[0]

    def get_leaving_bland(self, 
                          v: Vertex, 
                          d: Optional[Union[np.ndarray, List[float]]] = None,
                          ) -> Optional[LpConstraint]:
        """
        Bland tie-breaking on minimum ratio.
        """

        dual_infeas = v.dual_infeasible_contraints(eps=self.abs_tol)
        if len(dual_infeas) == 0:
            return None
        
        leaving, _ = dual_infeas[0]
        return leaving
    
    def get_leaving_dantzig(self, 
                            v: Vertex, d: Optional[Union[np.ndarray, List[float]]] = None,
                            ) -> Optional[LpConstraint]:
        """
        Standard minimum ratio test.
        """

        dual_infeas = v.dual_infeasible_contraints(eps=self.abs_tol)
        if len(dual_infeas) == 0:
            return None
        
        leaving, _ = max(dual_infeas, key=lambda x: abs(x[1]))
        return leaving

    def get_moving_direction(self, v: Vertex, constraint: LpConstraint) -> np.ndarray:
        h = v.index(constraint)
        return v.W[:, h]

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs
                 ):
        
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            initial_iterations = 0
            if start_basis is None:
                start_basis, initial_iterations = self.get_starting_point(problem, pivot_rule)

            if start_basis is None:
                raise UnFeasibleProblemException(
                    "Could not find a *primal-feasible* starting point (basis)",
                )

            if not isinstance(start_basis, Vertex):
                start_basis = Vertex(
                    problem, 
                    *[problem.constraints[name] if isinstance(name, str) else name for name in start_basis]
                )
        
            if not start_basis.is_primal_feasible(eps=self.abs_tol):
                raise UnFeasibleProblemException(
                    f"#{initial_iterations} Starting point isn't primal-feasible",
                )
            
            current = start_basis
            for i in range(initial_iterations, self.max_iterations):
                if not current.is_primal_feasible(eps=self.abs_tol):
                    raise InvalidBasisException(
                        f"#{i} Current point isn't primal-feasible",
                    )
                
                if current.is_optimal_point(eps=self.abs_tol):
                    problem.status = LpStatusOptimal
                    return
                
                # Choose leaving constraint
                leaving = self.get_leaving_constraint(current, pivot_rule=pivot_rule)
                assert leaving is not None
            
                # Calculate the direction
                direction = self.get_moving_direction(current, leaving)

                # Choose entering constraint
                entering = self.get_entering_constraint(current, d=direction, pivot_rule=pivot_rule)
                if entering is None:
                    raise UnboundedProblemException(
                        f"#{i} Problem is unbounded (no entering constraint)"
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

    def get_auxiliary_problem(self, original: LpProblem) -> Tuple[LpProblem, Vertex]:
        n = original.numVariables()

        initial_basis = list(original.constraints.values())[:n]
        initial_vertex = Vertex(original, *initial_basis)

        infeas = initial_vertex.primal_infeasible_constraints(eps=self.abs_tol)
        if len(infeas) == 0:
            return original, initial_vertex # Already feasible point

        # Auxiliary problem
        V: List[LpConstraint] = [i[0] for i in infeas]

        # Build variables for the auxiliary problem
        k = len(infeas)
        aux_vars = [LpVariable(f"aux_{n + i + 1}") for i in range(k)]

        # Build the auxiliary problem
        aux_problem = LpProblem(f"Auxiliary_for_{original.name}", LpMinimize)
        aux_problem.setObjective(sum(aux_vars))

        for constraint in initial_vertex.all_constraints:
            j = V.index(constraint) if constraint in V else None
            if j is None:
                copy = constraint.copy()
                if constraint in initial_basis:
                    copy.name = f"_B_{constraint.name}"
                else:
                    copy.name = f"_U_{constraint.name}"

                aux_problem += copy
                continue

            constraints_to_add : List[LpConstraint] = []

            # s >= 0
            var: LpVariable = aux_vars[j]
            var.setInitialValue(-infeas[j][1])
            var.lowBound = 0
            var_bound = LpConstraint(var >= 0, sense=LpConstraintGE)
            constraints_to_add.append(var_bound)
            
            if constraint.sense == LpConstraintLE or constraint.sense == LpConstraintEQ:
                # Ai @ x - s <= bi || Ai @ x - s == bi
                slack = constraint.copy()
                slack.name = f"_VS_{constraint.name}"
                slack.subInPlace(var)
                constraints_to_add.append(slack)

            if constraint.sense == LpConstraintGE:
                # Ai @ x + s >= bi

                slack = constraint.copy()
                slack.name = f"_VA_{constraint.name}"
                slack.addInPlace(var)
                constraints_to_add.append(slack)

            for c in constraints_to_add:
                aux_problem += c

        # Build a knwon initial vertex for the auxiliary problem
        aux_vertex = Vertex(
            aux_problem,
            *[c for c in aux_problem.constraints.values() 
              if c.name and (c.name.startswith("_VS_") or c.name.startswith("_VA_") or c.name.startswith("_B_"))]
        )

        return aux_problem, aux_vertex

    def get_feasible_vertex(self, problem: LpProblem, pivot_rule: PivotRule) -> Tuple[Vertex, int]:
        n = problem.numVariables()

        aux_problem, aux_vertex = self.get_auxiliary_problem(problem)
        if aux_problem == problem:
            return aux_vertex, 0

        aux_problem.solve(solver=self, start_basis=aux_vertex, pivot_rule=pivot_rule)
        if aux_problem.status != LpStatusOptimal:
            raise UnFeasibleProblemException(
                "Auxiliary problem unfeasible or unbounded"
            )
        
        assert aux_problem.objective is not None
        aux_value = aux_problem.objective.value()
        if aux_value is None or aux_value > self.abs_tol * n:
            raise UnboundedProblemException(
                f"Auxiliary (phase I) problem was not solved: " + 
                f"slack variables should be zero at optimality ({aux_value:.4} instead)"
            )

        aux_solution = Vertex.from_problem_state(aux_problem)
 
        feasible_solution_constraints = [
            c for c in problem.constraints.values()
            if aux_solution.has_named_constraints([
                f"_B_{c.name}", 
              # f"_U_{c.name}", 
                f"_VS_{c.name}", 
                f"_VA_{c.name}",
            ])
        ]
        feas_cons_tot = len(feasible_solution_constraints)
        assert feas_cons_tot == n, f"Selected constraint count mismatch: {feas_cons_tot} != {n}"

        feasible_solution = Vertex(problem, *feasible_solution_constraints)
        return feasible_solution, 0
    
    
    def get_starting_point(self, 
                           problem: LpProblem,
                           pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                           ) -> Tuple[Optional[Vertex], int]:

        try:
            return self.get_feasible_vertex(problem, pivot_rule=pivot_rule)
        except GsimplexException as e:
            # print(e)
            return None, 0