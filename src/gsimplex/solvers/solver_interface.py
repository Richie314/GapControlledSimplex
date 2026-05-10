from abc import ABC, abstractmethod
from typing import Optional, List
from pulp import (
    LpSolver, LpProblem,
    LpMinimize, LpMaximize,
)
    
class ISolver(LpSolver, ABC):
    def __init__(self, 
                 options: Optional[List] = None, 
                 *args, 
                 **kwargs
                 ):
        super().__init__(mip=False, 
                         options=options, 
                         *args,
                         **kwargs
                         )
        
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

    @abstractmethod
    def minimize(self, problem: LpProblem, **kwargs):
        pass