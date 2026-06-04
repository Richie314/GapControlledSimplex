#!/usr/bin/env python3

import argparse
from pulp import (
    LpMaximize, LpMinimize, 
    LpStatusOptimal, LpStatus,
    LpSenses, LpConstraintSenses,
)

from gsimplex.solvers import *
from gsimplex.tools.parser import ProblemParser
from gsimplex.tools.problem import constraint_to_row
from gsimplex.constants import DEFAULT_ABS_TOLERANCE

def main():
    """
    Command-line entry point for the gsimplex solver.

    :return: Exit code for the program.
    :rtype: int
    """

    solvers = {
        'psimplex': PrimalSimplex,
        'dsimplex': DualSimplex,
        'gsimplex': GapDoubleSimplex,
        'msimplex': MutualGapSimplex
    }

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode')
    parser.add_argument('--problem', type=str, required=True, help='Path to the problem to solve')
    parser.add_argument('--sense', type=str, choices=['minimize', 'maximize'], default='minimize', help='Optimization sense')
    parser.add_argument('--solver', default='gsimplex', type=str, choices=solvers.keys(), 
                        help='Algorithm to use to solve the problem')
    args = parser.parse_args()

    sense = LpMinimize if args.sense == 'minimize' else LpMaximize

    problem = ProblemParser.load_mps_from_file(args.problem, sense=sense)
    solver: ISimplex = solvers[args.solver]()
    
    print(f"Loaded problem from {args.problem} with sense {LpSenses[sense]} and {len(problem.variables())} variables.")
    print(f"Solving problem with {args.solver}...")

    problem.solve(solver)

    print(f"Status: {LpStatus[problem.status]}")
    print()

    if problem.objective is not None:
        print(f"Objective c^T x: {problem.objective.value()}")
        print()

    print("Variable values:")
    for var in problem.variables():
        print(f"{var.name}: {var.value()}")
    print()

    print("Constraint slacks:")
    for name, c in problem.constraints.items():
        _, _, slack = constraint_to_row(c, problem)
        emoji = "⚠️" if slack is None or slack < -DEFAULT_ABS_TOLERANCE else "✅"
        print(f"{emoji} {name} ({LpConstraintSenses[c.sense]}): {slack}")
    print()

    return 0 if problem.status == LpStatusOptimal else 1

if __name__ == "__main__":
    from sys import exit
    exit(main())