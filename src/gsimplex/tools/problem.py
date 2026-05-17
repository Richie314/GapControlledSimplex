import math
import numpy as np
from typing import Union, List, Tuple
from pulp import (
    LpProblem, LpVariable, LpConstraint,
    LpConstraintEQ, LpConstraintGE, LpConstraintLE,
)

from gsimplex.tools.algebra import rows_are_same
from gsimplex.exception import UnFeasibleProblemException

def constraint_sense(c: LpConstraint, convert_eq_to: int = LpConstraintLE) -> int:
    """
    Extracts the sense from a `LpConstraint`.

    :param c: The constraint to extract the sense from.
    :type c: LpConstraint
    :param convert_eq_to: How to treat equality constraints when converting them.
    :type convert_eq_to: int
    :return: Either `pulp.LpConstraintGE` or `pulp.LpConstraintLE`.
    :rtype: int
    """

    sense = c.sense
    if sense == LpConstraintEQ:
        sense = convert_eq_to
    
    if sense != LpConstraintLE and sense != LpConstraintGE:
        raise ValueError(f"Unsupported constraint sense: {c.sense}")
    
    return sense

def constraint_to_row(c: LpConstraint, 
                      lp: Union[LpProblem, List[LpVariable]], 
                      convert_eq_to: int = LpConstraintLE,
                      ) -> Tuple[np.ndarray, float]:
    """
    Convert a constraint to a numpy array of coefficients corresponding to the given variables.

    :param c: The constraint to convert.
    :type c: LpConstraint
    :param lp: The linear programming problem containing the variables.
    :type lp: LpProblem
    :param convert_eq_to: How to treat equality constraints when converting them.
    :type convert_eq_to: int
    :return: A numpy vector of coefficients corresponding to problem variables.
    :rtype: np.ndarray
    """

    variables = lp.variables() if isinstance(lp, LpProblem) else lp

    sense = constraint_sense(c, convert_eq_to)
    
    """
    Pulp memorizes data in the form Ax + constant <=> 0
    Hence b is
        * -constant if <=
        *  constant if >=
        * any of the above if == (treated as convert_eq_to says)
    """

    Ai = -sense * np.array([c.get(var, 0) for var in variables])
    bi = sense * c.constant
    return (Ai, bi)


def get_objective_function(lp: LpProblem) -> np.ndarray:
    """
    Extract the objective function coefficients from the problem.

    :param lp: The linear programming problem containing the objective.
    :type lp: LpProblem
    :return: The objective coefficients vector aligned with problem variables.
    :rtype: np.ndarray
    """

    if lp.objective is None:
        return np.array([0] * lp.numVariables())

    return np.array([lp.objective.get(var, 0) for var in lp.variables()])

def clone_problem(lp: LpProblem) -> LpProblem:
    """
    Create a deep copy of a linear programming problem.

    :param lp: The original LP problem to clone.
    :type lp: LpProblem
    :return: A new LP problem instance with copied variables, objective, and constraints.
    :rtype: LpProblem
    """
    
    assert lp.objective

    lp2 = LpProblem(name=f"Copy_of_{lp.name}", sense=lp.sense)
    vars = [LpVariable(name=f"{x.name}_copy", 
                        lowBound=x.lowBound,
                        upBound=x.upBound,
                        cat=x.cat,
                        ) for x in lp.variables()]
    
    # Copy the objective function
    lp2 += get_objective_function(lp) @ vars + lp.objective.constant

    # Copy the constraints
    for c in lp.constraints.values():
        Ai, bi = constraint_to_row(c, lp)

        if c.sense == LpConstraintEQ:
            lp2 += Ai @ vars == bi
        #elif c.sense == LpConstraintGE:
        #    lp2 += -Ai @ vars >= -bi
        else:
            lp2 += Ai @ vars <= bi

    return lp2

def get_different_constraints(problem: LpProblem) -> List[LpConstraint]:

    n = problem.numVariables()
    m = problem.numConstraints()
    assert m >= n, f"Problem has more variables ({n=}) than constraints ({m=})."

    constraints = list(problem.constraints.values())
    if n == m:
        return constraints

    l: List[LpConstraint] = []

    def _check_if_already_present(c: LpConstraint) -> bool:
        Ai, _ = constraint_to_row(c, problem)
        for c2 in l:
            Aj, _ = constraint_to_row(c2, problem)
            if rows_are_same(Ai, Aj):
                return True
        return False

    # First run: filter equality constraints first
    for c in constraints:
        if c.sense != LpConstraintEQ:
            continue

        if not _check_if_already_present(c):
            l.append(c)
            if len(l) == n:
                return l

    # Second run: consider inequalities only
    for c in constraints:
        if c.sense == LpConstraintEQ:
            continue

        if not _check_if_already_present(c):
            l.append(c)
            if len(l) == n:
                return l

    raise UnFeasibleProblemException(
        "A linear indipendent constraint set cannot be formed for this problem"
    )

def add_variable_constraints(lp: LpProblem) -> bool:
    n = lp.numVariables()

    if n <= lp.numConstraints():
        return True
    
    for var in list(lp.variables()):
        if var.lowBound is not None and math.isfinite(var.lowBound):
            lb = var.lowBound

            constraint = LpConstraint(var >= lb)
            constraint.sense = LpConstraintGE
            constraint.name = f"_LB_{var.name}"
            
            Ai, _ = constraint_to_row(constraint, lp)
            insert = True
            for c in lp.constraints.values():
                Aj, _ = constraint_to_row(c, lp)
                if rows_are_same(Ai, Aj):
                    insert = False
                    break
            
            if insert:
                lp += constraint
        
        if var.upBound is not None and math.isfinite(var.upBound):
            ub = var.upBound

            constraint = LpConstraint(var <= ub)
            constraint.sense = LpConstraintLE
            constraint.name = f"_UB_{var.name}"

            Ai, _ = constraint_to_row(constraint, lp)
            insert = True
            for c in lp.constraints.values():
                Aj, _ = constraint_to_row(c, lp)
                if rows_are_same(Ai, Aj):
                    insert = False
                    break
            
            if insert:
                lp += constraint

    return n <= lp.numConstraints()