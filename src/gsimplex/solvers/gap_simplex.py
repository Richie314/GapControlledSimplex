from typing import Optional, Tuple, List, Union
from pulp import LpProblem, LpConstraint, LpVariable
from pulp.constants import LpMaximize, LpStatusOptimal

from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
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

class GapDoubleSimplex(PrimalSimplex, DualSimplex):
    def __init__(self):
        super().__init__()

    def __primal_init(self, 
                      problem: LpProblem, 
                      given: Optional[Union[List[LpConstraint], Vertex, List[str]]],
                      pivot_rule: PivotRule,
                      ) -> Tuple[Vertex, int]:
        it = 0
        if given is None:
            given, it = PrimalSimplex.get_starting_point(self, problem, pivot_rule)

        if given is None:
            raise UnFeasibleProblemException(
                "Could not find a *primal-feasible* starting point (basis)"
            )

        if not isinstance(given, Vertex):
            given = Vertex(
                problem, 
                *[problem.constraints[name] if isinstance(name, str) else name for name in given]
            )
    
        if not given.is_primal_feasible(self.abs_tol):
            raise UnFeasibleProblemException(
                f"#{it} Starting point isn't primal-feasible",
            )

        return given, it
    
    def __dual_init(self, 
                      problem: LpProblem, 
                      given: Optional[Union[List[LpConstraint], Vertex, List[str]]],
                      pivot_rule: PivotRule,
                      ) -> Tuple[Vertex, int]:
        it = 0
        if given is None:
            given, it = DualSimplex.get_starting_point(self, problem, pivot_rule)

        if given is None:
            raise UnFeasibleProblemException(
                "Could not find a *primal-feasible* starting point (basis)"
            )

        if not isinstance(given, Vertex):
            given = Vertex(
                problem, 
                *[problem.constraints[name] if isinstance(name, str) else name for name in given]
            )
    
        if not given.is_dual_feasible(eps=self.abs_tol):
            raise UnFeasibleProblemException(
                f"#{it} Starting point isn't primal-feasible",
            )

        return given, it

    def maximize(self, 
                 problem: LpProblem, 
                 start_basis: Optional[Union[List[LpConstraint], Vertex, List[str]]] = None,
                 pivot_rule: PivotRule = DEFAULT_PIVOT_RULE,
                 **kwargs
                 ):
        
        assert problem.sense == LpMaximize, "Tried to maximize a minimization problem!"

        try:
            initial_iterations = 0
            
            primal_point, primal_it = self.__primal_init(problem, given=start_basis, pivot_rule=pivot_rule)
            dual_point,   dual_it = self.__dual_init(problem, given=None, pivot_rule=pivot_rule)


        except GsimplexException as e:
            problem.status = e.status