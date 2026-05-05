from pulp.constants import (
    LpStatusNotSolved, LpStatusOptimal, 
    LpStatusUnbounded, LpStatusInfeasible,
    LpStatusUndefined
)

class GsimplexException(Exception):
    def __init__(self, *args: object):
        self.status = LpStatusNotSolved
        super().__init__(*args)
    

class UnboundedProblemException(GsimplexException):
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusUnbounded

class UnFeasibleProblemException(GsimplexException):
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusInfeasible

class InvalidBasisException(GsimplexException):
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusNotSolved

