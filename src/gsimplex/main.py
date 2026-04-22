from gsimplex.problem import Problem
from gsimplex.solvers.solver_interface import ISolver
from gsimplex.solvers.primal_simplex import PrimalSimplex
from gsimplex.solvers.dual_simplex import DualSimplex
from gsimplex.solvers.gap_simplex import GapSimplex

def solve_and_print(solver: ISolver, problem: Problem, B: list[int]|None = None):
    solution = None
    try:
        solution = solver.maximize(problem, B)
    except Exception as e:
        print(str(e))
        return

    if solution is None:
        print("Problem is unbounded or infeasible")
        return

    print(f"x = [{'; '.join(map(str, solution.x))}]")
    print(f"y = [{'; '.join(map(str, solution.y))}]")

    try:
        print(f"c^T * x = {solution.point.primal_value()}")
    except Exception as e:
        print(str(e))

    try:
        print(f"y^T * b = {solution.point.dual_value()}")
    except Exception as e:
        print(str(e))

def __main():
    problem = Problem.from_ab_rows(
        [4.0, 5.0, 2.0],
        [0.0, 0.6, 0.8, 500.0],
        [-1.0, 2.0, 0.0, 0.0],
        [1.0, 0.0, -1.0, 0.0]
    ).enforce_positivity()

    print("=== Primal Simplex ===")
    solve_and_print(PrimalSimplex(), problem, B=[0, 3, 4])
    print()
    print()

    print("=== Dual Simplex ===")
    solve_and_print(DualSimplex(), problem)
    print()
    print()

    print("=== Gap-Controlled Simplex ===")
    solve_and_print(GapSimplex(), problem, B=[0, 3, 4])

if __name__ == "__main__":
    __main()