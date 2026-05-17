import numpy as np

from gsimplex.constants import DEFAULT_ABS_TOLERANCE

def rows_are_same(l: np.ndarray, 
                  r: np.ndarray, 
                  ) -> bool:
    if len(l) != len(r):
        return False
    
    norm = np.linalg.vector_norm(l)

    if norm < DEFAULT_ABS_TOLERANCE:
        norm2 = float(np.linalg.vector_norm(r))
        return norm2 < DEFAULT_ABS_TOLERANCE
    
    return np.array_equal(l / norm, r / norm) or np.array_equal(l / norm, -r / norm)
