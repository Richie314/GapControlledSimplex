import argparse
import sys

from gsimplex.problem import Problem
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapSimplex
from gsimplex.tools.parser import ProblemParser

def __main():
    solvers = {
        'gsimplex' : GapSimplex,
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