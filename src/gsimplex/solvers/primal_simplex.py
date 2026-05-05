from typing import Optional, Tuple, List, Union
from pulp import (
    LpProblem, LpConstraint, LpVariable, 
    LpConstraintEQ, LpConstraintLE, LpConstraintGE,
    LpMinimize, LpStatusNotSolved,
)
from pulp.constants import LpStatusOptimal

from gsimplex.solvers.iterative_solver import IterativeSolver
from gsimplex.solvers.simplex_interface import ISimplex
from gsimplex.vertex import Vertex, DEFAULT_ABS_TOLERANCE
from gsimplex.exception import (
    UnboundedProblemException,
    UnFeasibleProblemException,
    GsimplexException,
    InvalidBasisException,
)

class PrimalSimplex(IterativeSolver, ISimplex):
    @staticmethod
    def iteration(vertex: Vertex) -> Vertex:
        if not vertex.is_primal_feasible():
            raise InvalidBasisException

        # Leaving index (Bland rule)
        dual_infeas = vertex.dual_infeasible_values()
        if len(dual_infeas) == 0:
            return vertex  # Optimal

        h, _ = dual_infeas[0]
        h_idx = vertex.index(h)
        Wh = vertex.W[:, h_idx]
        print(f"{h=}, {Wh=}")

        ratios: List[Tuple[LpConstraint, float]] = []
        for constraint in vertex.non_basis:
            Ai = Vertex.constraint_to_row(constraint, vertex.problem)
            slack = Vertex.slack(constraint)

            den = Ai @ Wh
            if den > DEFAULT_ABS_TOLERANCE:
                ratios.append((constraint, slack / den))

        if len(ratios) == 0:
            raise UnboundedProblemException

        ratios.sort(key=lambda x: (x[1], x[0].name), reverse=False)
        k, _ = ratios[0]
        print(f"{k=}")

        return vertex.swap(k, h)

    def get_starting_point(self, problem: LpProblem) -> Tuple[Optional[Vertex], int]:

        try:
            return self.get_feasible_vertex(problem)
        except GsimplexException:
            return None, 0

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex]] = None
                 ):

        iterations = 0
        try:
            if start_basis is None:
                start_basis, iterations = self.get_starting_point(problem)

            if start_basis is None:
                raise UnFeasibleProblemException
            
            if not isinstance(start_basis, Vertex):
                start_basis = Vertex(problem, *start_basis)
        
            current = start_basis
            while True:
                if current.is_optimal_point():
                    problem.status = LpStatusOptimal
                    return
                
                self._check_iteration_count(iterations)
                
                print(f"{current.x=}")
                current = self.iteration(current)
                iterations += 1

        except GsimplexException as e:
            print(e)
            problem.status = e.status

    def make_feasible(self, vertex: Vertex) -> Tuple[Vertex, int]:

        iterations = 0
        while True:

            infeas = vertex.primal_infeasible_rows()
            if len(infeas) == 0:
                break

            self._check_iteration_count(iterations)

            k, _ = min(infeas, key=lambda x: x[1])
            Ak = Vertex.constraint_to_row(k, vertex.problem)

            # Leaving index (Bland rule)
            h = None
            for constraint in vertex:
                idx = vertex.index(constraint)
                if Ak @ vertex.W[:, idx] < 0:
                    h = constraint
                    break

            if h is None:
                raise UnboundedProblemException

            vertex.swap(k, h)
            iterations += 1

        return vertex, iterations
    
    def get_auxiliary_problem(self, original: LpProblem) -> Tuple[LpProblem, Vertex]:
        n = original.numVariables()

        initial_basis = list(original.constraints.values())[:n]
        initial_vertex = Vertex(original, *initial_basis)

        if initial_vertex.is_primal_feasible():
            return original, initial_vertex

        # Auxiliary problem
        rp = initial_vertex.primal_residuals()
        V = [constraint for constraint in initial_vertex.non_basis
             if rp[initial_vertex.global_index(constraint)] < 0]

        # Number of auxiliary variables
        k = len(V)

        # Build variables for the auxiliary problem
        aux_vars = [LpVariable(f"aux_{i}", lowBound=0) for i in range(k)]
        for i, constraint in enumerate(V):
            j = initial_vertex.global_index(constraint)
            aux_vars[i].setInitialValue(-rp[j])

        # Build the auxiliary problem
        aux_problem = LpProblem(f"Auxiliary_for_{original.name}", LpMinimize)
        aux_problem.setObjective(sum(aux_vars))

        for constraint in original.constraints.values():
            j = V.index(constraint) if constraint in V else None
            if j is None:
                copy = constraint.copy()
                if constraint in initial_basis:
                    copy.name = f"_B_{constraint.name}"
                else:
                    copy.name = f"_U_{constraint.name}"

                aux_problem += copy
                continue

            variable: LpVariable = aux_vars[j]
            new_constraint_sub = None
            new_constraint_add = None
            
            if constraint.sense == LpConstraintLE or constraint.sense == LpConstraintEQ:
                # Ai @ x - s <= bi || Ai @ x - s == bi
                new_constraint_sub = constraint.copy()
                new_constraint_sub.name = f"_VS_{constraint.name}"
                new_constraint_sub.subInPlace(variable)

            if constraint.sense == LpConstraintGE or constraint.sense == LpConstraintEQ:
                # Ai @ x + s >= bi || Ai @ x + s == bi
                new_constraint_add = constraint.copy()
                new_constraint_add.name = f"_VA_{constraint.name}"
                new_constraint_add.addInPlace(variable)

            if new_constraint_sub:
                aux_problem += new_constraint_sub
            if new_constraint_add:                
                aux_problem += new_constraint_add

        # Build a knwon initial vertex for the auxiliary problem
        aux_vertex = Vertex(
            aux_problem,
            *[c for c in aux_problem.constraints.values() 
              if c.name and (c.name.startswith("_VS_") or c.name.startswith("_VA_") or c.name.startswith("_B_"))]
        )

        return aux_problem, aux_vertex

    def get_feasible_vertex(self, problem: LpProblem) -> Tuple[Vertex, int]:
        n = problem.numVariables()

        aux_problem, aux_vertex = self.get_auxiliary_problem(problem)
        if aux_problem == problem:
            return aux_vertex, 0

        aux_problem.solve(solver=self, start_basis=aux_vertex)
        if aux_problem.status != LpStatusOptimal:
            raise UnFeasibleProblemException # Auxiliary problem unfeasible or unbounded
        
        assert aux_problem.objective is not None
        aux_value = aux_problem.objective.value()
        if aux_value is None or aux_value > DEFAULT_ABS_TOLERANCE:
            raise UnboundedProblemException # Slack variables should be zero at optimality

        aux_solution = Vertex.from_problem_state(aux_problem)
        assert len(aux_solution) >= n
 
        feasible_solution_constraints = [
            c for c in problem.constraints.values()
            if aux_solution.has_named_constraints([
                f"_B_{c.name}", 
                f"_U_{c.name}", 
                f"_VS_{c.name}", 
                f"_VA_{c.name}",
            ])
        ]
        assert len(feasible_solution_constraints) == n, "Selected constraint count mismatch"

        feasible_solution = Vertex(problem, *feasible_solution_constraints)
        return feasible_solution, 0