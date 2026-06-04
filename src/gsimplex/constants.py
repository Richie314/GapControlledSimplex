from typing import Literal

DEFAULT_ABS_TOLERANCE = 1.0e-10
'''Default tolerance to use in comparisons between real numbers'''

DEFAULT_REL_TOLERANCE = 1.0e-7
'''Default relative tolerance to use for real number comparisons'''

PivotRule = Literal["dantzig", "bland"]
'''Type of pivonting strategy. Can either be `dantzig` (default, faster) or `bland` (strict anti-cycling)'''

DEFAULT_PIVOT_RULE = "dantzig"
'''Default PivotRule strategy: `dantzig`'''

PivotType = Literal["primal", "dual"]
'''Type of pivoting algorithm. Can be either `primal` (row based) or `dual` (column based)'''

DEFAULT_MAX_ITERATIONS = 1_000
'''Default value for the maximum number of iterations'''

DEFAULT_ABS_GAP = DEFAULT_ABS_TOLERANCE
'''Default value for the absolute gap between primal and dual point'''

DEFAULT_REL_GAP = DEFAULT_REL_TOLERANCE
'''Default value for the relative gap between primal and dual point'''