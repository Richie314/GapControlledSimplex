import math
import numpy as np
from typing import Union, List, Tuple, Optional
from pulp import (
    LpProblem, LpVariable, LpConstraint,
    LpConstraintEQ, LpConstraintGE, LpConstraintLE,
    lpDot,
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
                      ) -> Tuple[np.ndarray, float, Optional[float]]:
    """
    Convert a constraint to a numpy array of coefficients corresponding to the given variables.
    Constraint are mathematically modeled with the form Ai @ x <= bi.

    :param c: The constraint to convert.
    :type c: LpConstraint
    :param lp: The linear programming problem containing the variables.
    :type lp: LpProblem
    :param convert_eq_to: How to treat equality constraints when converting them.
    :type convert_eq_to: int
    :return: A tuple of the form (Ai, bi, slack = bi - Ai @ x). The slack can be None if a variale is None
    :rtype: Tuple[np.ndarray, float, Optional[float]]
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

    slack = None
    value = c.value()
    if value is not None:
        """
        Retrieved value can mean different things depending on the type of constraint
        * value =  Ai * x - bi <= 0 --> bi - Ai * x = -value
        * value = -Ai * x + bi >= 0 --> bi - Ai * x =  value
        * value =  Ai * x - bi == 0 --> bi - Ai * x = -value
        """

        if c.sense == LpConstraintEQ:
            slack = -value
        else:
            slack = c.sense * value

    return (Ai, bi, slack)


def get_objective_function(lp: LpProblem) -> np.ndarray:
    """
    Extract the objective function coefficients from the problem.

    :param lp: The linear programming problem containing the objective.
    :type lp: LpProblem
    :return: The objective coefficients vector aligned with problem variables.
    :rtype: np.ndarray
    """

    if lp.objective is None:
        return np.zeros(lp.numVariables(), dtype=float)

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
    obj = get_objective_function(lp)
    lp2 += lpDot(obj, vars) + lp.objective.constant

    # Copy the constraints
    for c in lp.constraints.values():
        Ai, bi, slack = constraint_to_row(c, lp)

        if c.sense == LpConstraintEQ:
            lp2 += lpDot(Ai, vars) == bi, c.name
        elif c.sense == LpConstraintGE:
            lp2 += lpDot(-Ai, vars) >= -bi, c.name
        else:
            lp2 += lpDot(Ai, vars) <= bi, c.name

    return lp2

def get_different_constraints(problem: LpProblem, shuffle_constraints: bool = False) -> List[LpConstraint]:

    n = problem.numVariables()
    m = problem.numConstraints()
    assert m >= n, f"Problem has more variables ({n=}) than constraints ({m=})."

    constraints = list(problem.constraints.values())
    
    if shuffle_constraints:
        idx = np.arange(len(constraints))
        np.random.shuffle(idx)
        constraints = [constraints[i] for i in idx]

    if n == m:
        return constraints

    l: List[LpConstraint] = []

    def _check_if_already_present(c: LpConstraint) -> bool:
        Ai, bi, slacki = constraint_to_row(c, problem)
        for c2 in l:
            Aj, bj, slackj = constraint_to_row(c2, problem)
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
            
            Ai, bi, slacki = constraint_to_row(constraint, lp)
            insert = True
            for c in lp.constraints.values():
                Aj, bj, slackj = constraint_to_row(c, lp)
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

            Ai, bi, slacki = constraint_to_row(constraint, lp)
            insert = True
            for c in lp.constraints.values():
                Aj, bj, slackj = constraint_to_row(c, lp)
                if rows_are_same(Ai, Aj):
                    insert = False
                    break
            
            if insert:
                lp += constraint

    return n <= lp.numConstraints()