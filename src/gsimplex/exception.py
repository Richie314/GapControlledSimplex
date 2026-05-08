from pulp.constants import LpStatusNotSolved, LpStatusUnbounded, LpStatusInfeasible

class GsimplexException(Exception):
    def __init__(self, *args: object):
        self.status = LpStatusNotSolved
        super().__init__(*args)
    
    def __str__(self) -> str:
        return '\n'.join(str(a) for a in self.args)
    

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

class IterationLimitReachedException(GsimplexException):
    def __init__(self, *args: object):
        super().__init__(*args)
        self.status = LpStatusNotSolved