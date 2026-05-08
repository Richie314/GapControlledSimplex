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
        """True if the solver is available"""
        return True
    
    def actualSolve(self, lp: LpProblem, **kwargs):
        """Solve a well formulated lp problem"""
        
        assert not lp.isMIP(), "MIP problems are not supported"
        assert lp.objective is not None, "Objective function must be defined"
        
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