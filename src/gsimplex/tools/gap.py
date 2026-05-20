import numpy as np
from typing import Tuple, Union, Optional
from pulp import LpProblem

from gsimplex.vertex import Vertex
from gsimplex.constants import DEFAULT_ABS_TOLERANCE
from gsimplex.tools.problem import get_objective_function


def gap_ub(dual: Union["Vertex", np.ndarray, float],
           lp: Optional[LpProblem] = None,
           eps: float = DEFAULT_ABS_TOLERANCE,
           ) -> float:
    """
    Computes the dual value associated with a vertex.

    :param dual: The dual vertex for the problem or the dual value itself.
    :type dual: Union[Vertex, np.ndarray, float]
    :param eps: Tolerance used for feasibility assertions.
    :type eps: float
    :return: The dual value.
    :rtype: float
    """

    if isinstance(dual, float):
        return dual
    
    if isinstance(dual, Vertex):
        assert dual.is_dual_feasible(eps), "Dual vertex is not feasible"
        dual = dual.y

    # Manually compute dual value
    assert isinstance(dual, np.ndarray)
    assert lp is not None, "Reference LP not provided."
    assert len(dual) == lp.numConstraints(), f"Given dual-vector dimension mismatch. Expected {lp.numConstraints()}."


    s = 0
    for i, constraint in enumerate(lp.constraints.values()):
        s += dual[i] * constraint.constant
    return s


def gap_lb(primal: Union["Vertex", np.ndarray, float],
           lp: Optional[LpProblem] = None,
           eps: float = DEFAULT_ABS_TOLERANCE,
           ) -> float:
    """
    Computes the primal value of a vertex

    :param primal: The primal vertex for the same problem or the primal value itself.
    :type primal: Union[Vertex, np.ndarray, float]
    :param eps: Tolerance used for feasibility assertions.
    :type eps: float
    :return: The primal value.
    :rtype: float
    """

    if isinstance(primal, float):
        return primal
    
    if isinstance(primal, Vertex):
        assert primal.is_primal_feasible(eps), "Primal vertex is not feasible"
        return primal.primal_value

    # Manually compute primal value
    assert isinstance(primal, np.ndarray)
    assert lp is not None, "Reference LP not provided."
    assert len(primal) == lp.numVariables(), f"Given primal-vector dimension mismatch. Expected {lp.numVariables()}."

    c = get_objective_function(lp)

    return float(c.T @ primal)

def gap(dual: Union["Vertex", np.ndarray, float], 
        primal: Union["Vertex", np.ndarray, float],
        eps: float = DEFAULT_ABS_TOLERANCE,
        ) -> Tuple[float, float, float, float]:
    """
    Compute the optimality gap between a dual and a primal vertex.

    :param dual: The dual vertex for the problem or the dual value itself.
    :type dual: Union[Vertex, np.ndarray, float]
    :param primal: The primal vertex for the same problem or the primal value itself.
    :type primal: Union[Vertex, np.ndarray, float]
    :param eps: Tolerance used for feasibility assertions.
    :type eps: float
    :return: A tuple of (gap, relative gap, dual value, primal value).
    :rtype: Tuple[float, float, float, float]
    """
    
    lp: Optional[LpProblem] = primal.problem if isinstance(primal, Vertex) else (
                                dual.problem if isinstance(dual, Vertex) else
                                None)

    dual_val = gap_ub(dual, lp, eps)
    primal_val = gap_lb(primal, lp, eps)

    gap = abs(dual_val - primal_val)
    rel_gap = gap / (abs(primal_val) + 1)

    return gap, rel_gap, dual_val, primal_val