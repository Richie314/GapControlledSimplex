import numpy as np

from gsimplex.constants import DEFAULT_ABS_TOLERANCE, DEFAULT_REL_TOLERANCE

def rows_are_same(l: np.ndarray, 
                  r: np.ndarray,
                  eps: float = DEFAULT_REL_TOLERANCE
                  ) -> bool:
    if len(l) != len(r):
        return False
    
    normL = np.linalg.vector_norm(l)
    normR = np.linalg.vector_norm(r)

    if normL < DEFAULT_ABS_TOLERANCE and normR < DEFAULT_ABS_TOLERANCE:
        # Both are effectively zero, so we consider them the same
        return True
    
    if normL < DEFAULT_ABS_TOLERANCE or normR < DEFAULT_ABS_TOLERANCE:
        # One is zero and the other is not, so they can't be the same
        return False
    
    return np.allclose(l / normL, r / normR, rtol=eps) or np.allclose(l / normL, -r / normR, rtol=eps)
