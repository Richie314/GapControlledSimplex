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
    """

    solvers = {
        'psimplex': (PrimalSimplex,    "Primal simplex"),
        'dsimplex': (DualSimplex,      "Dual simplex"),
        'gsimplex': (GapDoubleSimplex, "Gap-controlled double simplex"),
        'msimplex': (MutualGapSimplex, "Mutual gap simplex")
    }

    parser = argparse.ArgumentParser(description="")
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode')
    
    parser.add_argument('--problem', type=str, required=True, help='Path to the problem to solve')
    parser.add_argument('--sense', type=str, choices=['minimize', 'maximize'], default='minimize', help='Optimization sense')
    
    parser.add_argument('--solver', default='dsimplex', type=str, choices=solvers.keys(), 
                        help='Algorithm to use to solve the problem')
    parser.add_argument('--pivot-type', type=str, choices=['dantzig', 'bland'], default=None,
                        help='Pivot selection rule for the solver')
    
    parser.add_argument('--abs-tol', type=float, default=1.0e-7,
                        help='Absolute tolerance for feasibility/optimality checks')
    parser.add_argument('--rel-tol', type=float, default=1.0e-7,
                        help='Relative tolerance for numerical comparisons')
    parser.add_argument('--abs-gap', type=float, default=None,
                        help='Absolute gap threshold for gap-controlled solvers')
    parser.add_argument('--rel-gap', type=float, default=None,
                        help='Relative gap threshold for gap-controlled solvers')


    parser.add_argument('--ub', type=float, default=None,
                        help='Upper bound on objective value (for msimplex)')
    parser.add_argument('--lb', type=float, default=None,
                        help='Lower bound on objective value (for msimplex)')

    args = parser.parse_args()

    sense = LpMinimize if args.sense == 'minimize' else LpMaximize
    problem = ProblemParser.load_mps_from_file(args.problem, sense=sense)
    solver_kwargs = {
        'abs_eps': args.abs_tol,
        'rel_eps': args.rel_tol,
        'pivot_rule': args.pivot_type,
    }
    if args.solver in {'gsimplex', 'msimplex'}:
        solver_kwargs['abs_gap'] = args.abs_gap
        solver_kwargs['rel_gap'] = args.rel_gap

    solver = solvers[args.solver][0](**{k: v for k, v in solver_kwargs.items() if v is not None})
    solver_name = solvers[args.solver][1]

    print(f"Loaded problem from {args.problem} with sense {LpSenses[sense]} and {len(problem.variables())} variables.")
    print(f"Solving problem with {solver_name}...")

    # For msimplex, pass lb and ub bounds if provided
    solve_kwargs = {}
    if args.solver == 'msimplex':
        if args.ub is not None:
            solve_kwargs['ub'] = args.ub
        if args.lb is not None:
            solve_kwargs['lb'] = args.lb

    problem.solve(solver, **solve_kwargs)

    print(f"Status: {LpStatus[problem.status]}.")
    print(f"Time: {problem.solutionTime:.4} seconds.")
    print(f"CPU time: {problem.solutionCpuTime:.4} seconds.")
    print()

    if problem.objective is not None:
        print(f"Objective c^T x: {problem.objective.value()}")
        print()

    ret = 0 if problem.status == LpStatusOptimal else 1
    if args.quiet:
        return ret

    print("Variable values:")
    for var in problem.variables():
        print(f"{var.name}:\t\t{var.value()}")
    print()

    print("Constraint slacks:")
    for name, c in problem.constraints.items():
        _, _, slack = constraint_to_row(c, problem)
        emoji = "⚠️ " if slack is None or slack < -DEFAULT_ABS_TOLERANCE else "✅"
        print(f"{emoji} {name} ({LpConstraintSenses[c.sense]}):\t{slack}")
    print()

    return ret

if __name__ == "__main__":
    from sys import exit
    exit(main())