from abc import ABC, abstractmethod
from typing import Optional, List
from pulp import (
    LpSolver, LpProblem,
    LpMinimize, LpMaximize,
)

from gsimplex.constants import *
    
class ISolver(LpSolver, ABC):
    def __init__(self, 
                 options: Optional[List] = None,
                 
                 max_iterations: Optional[int] = None,
                 abs_eps: Optional[float] = None,
                 rel_eps: Optional[float] = None,

                 *args, 
                 **kwargs
                 ):
        super().__init__(mip=False, 
                         options=options, 
                         *args,
                         **kwargs
                         )
        
        
        self.max_iterations = max_iterations if max_iterations else DEFAULT_MAX_ITERATIONS
        assert self.max_iterations > 0, f"Maximum number of iterations must be positive. {self.max_iterations} given."

        self.abs_tol = abs_eps if abs_eps else DEFAULT_ABS_TOLERANCE
        assert self.abs_tol >= 0, f"Absolute ε must be >= 0. {self.abs_tol:.5} given."

        self.rel_tol = rel_eps if rel_eps else DEFAULT_REL_TOLERANCE
        assert self.rel_tol >= 0, f"Relative ε must be >= 0. {self.abs_tol:.5} given."
        
    def available(self):
        """
        Check whether the solver implementation is available.

        :return: True when the solver can be executed.
        :rtype: bool
        """
        return True
    
    def actualSolve(self, lp: LpProblem, **kwargs):
        """
        Solve a linear programming problem using the solver implementation.

        :param lp: The linear programming problem to solve.
        :type lp: LpProblem
        :param kwargs: Additional solver-specific options.
        :type kwargs: dict
        :return: The problem status after solving.
        """
        
        assert not lp.isMIP(), "MIP problems are not supported"
        
        if lp.sense == LpMinimize:
            self.minimize(lp, **kwargs)
        elif lp.sense == LpMaximize:
            self.maximize(lp, **kwargs)

        return lp.status


    @abstractmethod
    def maximize(self, problem: LpProblem, **kwargs):
        pass

    def minimize(self, problem: LpProblem, **kwargs):
        """
        Solve a minimization problem by converting it to a maximization problem.

        :param problem: The LP problem to solve.
        :type problem: LpProblem
        :param kwargs: Additional solver options.
        :type kwargs: dict
        """
        
        assert problem.sense == LpMinimize, "Tried to minimize a maximization problem!"
        
        if problem.objective is not None:
            problem.objective = -problem.objective
        problem.sense = LpMaximize

        self.maximize(problem=problem, **kwargs)
        
        if problem.objective is not None:
            problem.objective = -problem.objective
        problem.sense = LpMinimize