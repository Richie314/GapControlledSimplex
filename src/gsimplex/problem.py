import numpy as np
from typing import List, Union

class Problem:
    """
    Linear programming problem in the form max { c^T x } subject to Ax <= b, x >= 0
    """
    
    def __init__(self, 
                 c: Union[List[float], np.ndarray], 
                 A: Union[List[List[float]], np.ndarray], 
                 b: Union[List[float], np.ndarray]
                 ):
        self.c = np.array(c, dtype=float)
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)

        if self.c.shape[0] != self.A.shape[1]:
            raise ValueError("c must have same length as A columns")

        if self.A.shape[0] != self.b.shape[0]:
            raise ValueError("A rows must match b length")

    @property
    def dimension(self) -> int:
        return self.A.shape[1]

    @property
    def constraints(self) -> int:
        return self.A.shape[0]

    @classmethod
    def from_arrays(cls, c: List[float], A: List[List[float]], b: List[float]) -> 'Problem':
        return cls(c, A, b)

    @classmethod
    def from_ab_rows(cls, c: List[float], *ab_rows: List[float]) -> 'Problem':
        A = [row[:-1] for row in ab_rows]
        b = [row[-1] for row in ab_rows]
        return cls(c, A, b)

    def enforce_positivity(self) -> 'Problem':
        I = np.eye(self.dimension)
        new_b = np.concatenate([self.b, np.zeros(self.dimension)])
        new_A = np.vstack([self.A, -I])
        return Problem(self.c, new_A, new_b)