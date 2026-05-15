from pulp import LpProblem, LpVariable
from pulp.constants import LpConstraintEQ, LpConstraintGE

from gsimplex.vertex import Vertex

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
    lp2 += Vertex.get_objective_function(lp) @ vars + lp.objective.constant

    # Copy the constraints
    for c in lp.constraints.values():
        Ai = Vertex.constraint_to_row(c, lp)
        bi = Vertex.constraint_to_linear_term(c)

        if c.sense == LpConstraintEQ:
            lp2 += Ai @ vars == bi
        #elif c.sense == LpConstraintGE:
        #    lp2 += -Ai @ vars >= -bi
        else:
            lp2 += Ai @ vars <= bi

    return lp2