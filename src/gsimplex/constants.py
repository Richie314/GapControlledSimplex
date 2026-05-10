from typing import Literal

DEFAULT_ABS_TOLERANCE = 1.0e-10
'''Default tolerance to use in comparisons between real numbers'''

DEFAULT_REL_TOLERANCE = 1.0e-4
'''Default relative tolerance to use for real number comparisons'''

PivotRule = Literal["dantzig", "bland"]
'''Type of pivonting strategy. Can either be `dantzig` (default, faster) or `bland` (strict anti-cycling)'''

DEFAULT_PIVOT_RULE = "dantzig"
'''Default PivotRule strategy: `dantzig`'''