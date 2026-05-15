from pulp.constants import (
    LpStatusNotSolved, 
    LpStatusUnbounded, 
    LpStatusInfeasible,
)

class GsimplexException(Exception):
    """
    Base exception class for gsimplex solver errors.
    """
    def __init__(self, *args: object):
        self.status = LpStatusNotSolved
        super().__init__(*args)
    
    def __str__(self) -> str:
        return '\n'.join(str(a) for a in self.args)
    

class UnboundedProblemException(GsimplexException):
    """
    Exception raised when the linear programming problem is unbounded.
    """
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusUnbounded

class UnFeasibleProblemException(GsimplexException):
    """
    Exception raised when the linear programming problem is infeasible.
    """
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusInfeasible

class InvalidBasisException(GsimplexException):
    """
    Exception raised when an invalid basis is encountered during solving.
    """
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusNotSolved

class IterationLimitReachedException(GsimplexException):
    """
    Exception raised when the maximum number of iterations is reached without convergence.
    """
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusNotSolved