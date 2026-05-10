import argparse
import sys

from gsimplex.solvers import (
    ISolver,
    PrimalSimplex,
    DualSimplex,
    GapDoubleSimplex,
)
from gsimplex.tools.parser import ProblemParser

def __main():
    """
    Command-line entry point for the gsimplex solver.

    :return: Exit code for the program.
    :rtype: int
    """
    solvers = {
        'gsimplex' : GapDoubleSimplex,
        'psimplex': PrimalSimplex,
        'dsimplex': DualSimplex,
    }

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--quiet', action='store_true', 
                        help='Run in quiet mode')
    parser.add_argument('--problem', type=str, required=True, 
                        help='Name of the problem to solve or path to it')
    parser.add_argument('--solver', default='gsimplex', type=str, choices=solvers.keys(), 
                        help='Algorithm to use to solve the problem')
    args = parser.parse_args()


    problem = ProblemParser.load_mps_from_file(args.problem)
    print(f"{problem=}")

    solver: ISolver = solvers[args.solver]()
    print(f"{solver=}")

    return 0

if __name__ == "__main__":
    sys.exit(__main())