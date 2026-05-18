from typing import Optional, Tuple, List, Union
from pulp import ( 
    LpProblem, LpConstraint, LpVariable,
    LpConstraintEQ, LpConstraintLE, LpConstraintGE,
    LpMinimize, LpMaximize, LpStatusOptimal,
    lpSum,
)
import numpy as np

from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.vertex import Vertex
from gsimplex.exception import *
from gsimplex.tools.problem import constraint_to_row, get_different_constraints


class PrimalSimplex(ISimplex):
    """
    Primal simplex solver implementation.
    """

    def get_entering_constraint(self, 
                                v: Vertex, 
                                d: Optional[Union[np.ndarray, List[float]]] = None,
                                ) -> Optional[LpConstraint]:
        """
        Select the entering constraint by Dantzig's rule.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector, required.
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen entering constraint or None when no valid entering constraint exists.
        :rtype: Optional[LpConstraint]
        """

        assert d is not None

        ratios: List[Tuple[LpConstraint, float]] = []
        for c in v.non_basis:
            Ai, bi, slack = constraint_to_row(c, v.problem)
            assert slack is not None

            den = float(Ai @ d)
            if den > self.abs_tol:
                ratios.append((c, slack / den))

        if len(ratios) == 0:
            return None
        
        entering, _ = min(ratios, key=lambda x: x[1])
        return entering

    def get_leaving_constraint(self, 
                               v: Vertex, 
                               d: Optional[Union[np.ndarray, List[float]]] = None,
                               ) -> Optional[LpConstraint]:
        """
        Select the leaving constraint using the Dantzig's maximum dual-infeasibility rule
        or Bland's lesser constraint's name rule.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param d: Current moving direction vector (not used directly here).
        :type d: Optional[Union[np.ndarray, List[float]]]
        :return: The chosen leaving constraint or None when no dual infeasibility exists.
        :rtype: Optional[LpConstraint]
        """

        dual_infeas = v.dual_infeasible_contraints(eps=self.abs_tol)
        if len(dual_infeas) == 0:
            return None
        
        if self.pivot_rule == "bland": 
            leaving, _ = dual_infeas[0]
        else:
            leaving, _ = max(dual_infeas, key=lambda x: abs(x[1]))

        return leaving

    def get_moving_direction(self, v: "Vertex", constraint: LpConstraint) -> np.ndarray:
        """
        Compute the moving direction for a candidate leaving constraint.

        :param v: Current vertex representing the basis.
        :type v: Vertex
        :param constraint: The leaving constraint used to compute direction.
        :type constraint: LpConstraint
        :return: The moving direction vector corresponding to the leaving constraint.
        :rtype: np.ndarray
        """

        h = v.index(constraint)
        return v.W[:, h]
    
    def _single_iteration(self, point: "Vertex") -> "Vertex":

        # Choose leaving constraint
        leaving = PrimalSimplex.get_leaving_constraint(self, point)
        assert leaving is not None
    
        # Calculate the direction
        direction = PrimalSimplex.get_moving_direction(self, point, leaving)

        # Choose entering constraint
        entering = PrimalSimplex.get_entering_constraint(self, point, d=direction)
        if entering is None:
            raise UnboundedProblemException(
                f"Problem is unbounded (no entering constraint)"
            )

        return point.swap(entering, leaving)

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 **kwargs
                 ):
        """
        Solve a maximization problem using the primal simplex method.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param start_basis: Optional starting basis or vertex.
        :type start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]]
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
                
                self._single_iteration(current)

            raise IterationLimitReachedException(
                f"Max iterations ({self.max_iterations}) reached"
            )

        except GsimplexException as e:
            # print(e)
            problem.status = e.status

    def get_auxiliary_problem(self, original: LpProblem) -> Tuple[LpProblem, Vertex]:
        """
        Construct an auxiliary LP problem and initial vertex for Phase I.

        :param original: The original LP problem requiring a feasible basis.
        :type original: LpProblem
        :return: A tuple with the auxiliary problem and its initial feasible vertex.
        :rtype: Tuple[LpProblem, Vertex]
        """
        n = original.numVariables()

        initial_basis = get_different_constraints(original)
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
        aux_problem = LpProblem(f"Auxiliary_for_{original.name}", sense=LpMinimize)
        aux_problem.setObjective(lpSum(aux_vars))

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

    def get_feasible_vertex(self, problem: LpProblem) -> Tuple[Vertex, int]:
        """
        Compute a primal feasible basis vertex for the given problem.

        :param problem: The LP problem to make feasible.
        :type problem: LpProblem
        :return: A tuple containing a feasible vertex and the iteration count.
        :rtype: Tuple[Vertex, int]
        """
        n = problem.numVariables()

        aux_problem, aux_vertex = self.get_auxiliary_problem(problem)
        if aux_problem == problem:
            return aux_vertex, 0

        aux_problem.solve(solver=self, start_basis=aux_vertex)
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
                           ) -> Tuple[Optional["Vertex"], int]:
        """
        Find a starting basis for the primal simplex solver.

        :param problem: The LP problem to initialize.
        :type problem: LpProblem
        :return: A possibly feasible starting vertex and the iteration count.
        :rtype: Tuple[Optional[Vertex], int]
        """

        try:
            return self.get_feasible_vertex(problem)
        except GsimplexException as e:
            # print(e)
            return None, 0
        
    def _nearest_primal_vertex(self, v: "Vertex") -> bool:
        while True:

            unfeasible_contraints = v.primal_infeasible_constraints(eps=self.abs_tol)
            if len(unfeasible_contraints) == 0:
                return True # Point is primal feasible
            
            # Same as entering constraint in Dual Simplex
            if self.pivot_rule == "bland":
                # First infeasible constraint
                entering, _ = unfeasible_contraints[0] 
            else:
                # Least infeasible contraint
                entering, _ = max(unfeasible_contraints, key=lambda x: x[1])

                
            if self.pivot_rule == "bland":
                d = v.W[:, v.index(entering)]
            else:
                # A_B @ d = Ap --> d = A_B^-1 @ Ap = -W @ Ap 
                Ap, bp, slackp = constraint_to_row(entering, v.problem)
                d = -v.W @ Ap

            leaving: Optional[LpConstraint] = None
            if self.pivot_rule == 'bland':
                ratios: List[Tuple[LpConstraint, float]] = []
                for c in v.non_basis:
                    Ai, bi, slack = constraint_to_row(c, v.problem)
                    assert slack is not None

                    den = float(Ai @ d)
                    if den > self.abs_tol:
                        ratios.append((c, slack / den))

                if len(ratios) > 0:
                    leaving, _ = min(ratios, key=lambda x: x[1])
            else:
                for constraint in v.non_basis:
                    Ak, bk, slackk = constraint_to_row(constraint, v.problem)
                    pivot = d @ Ak
                    if pivot < -self.abs_tol:
                        leaving = constraint
                        break

            if leaving is None:
                raise UnboundedProblemException(
                    "Phase I dual-problem is unbounded",
                )
                
            v.swap(entering, leaving)