import argparse
import pulp
from pathlib import Path

from gsimplex.problem import Problem
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapSimplex

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

    solver: ISolver = solvers[args.solver]()

    problem_path = Path(args.problem)
    if not problem_path.exists():
        raise FileNotFoundError(f"Problem file not found: {problem_path.absolute()}")
        
    
    variables, problem = pulp.LpProblem.fromMPS(str(problem_path))

    print(f"{variables=}")
    print(f"{problem=}")

if __name__ == "__main__":
    __main()