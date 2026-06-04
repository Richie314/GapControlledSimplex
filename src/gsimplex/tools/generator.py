import argparse
from pathlib import Path
from typing import Optional, Union, List, Tuple
import os
import numpy as np
from pulp import (
    LpProblem, LpVariable, LpConstraint,
    LpConstraintLE, LpConstraintGE, LpConstraintEQ,
    LpMinimize, LpMaximize,
    lpDot, lpSum,
)

from gsimplex.constants import DEFAULT_ABS_TOLERANCE
from gsimplex.tools.problem import constraint_to_row

class LPProblemGenerator:
    """
    Generate feasible linear programs using FRaGenLP algorithm.
    See also doi 10.48550/arXiv.2105.10384 for more details.
    """

    def __init__(
        self,
        num_variables: int,
        num_constraints: int,
        lower_bound: float = 0.0,
        upper_bound: Optional[float] = None,
    ):
        assert num_variables > 0, "num_variables must be positive"
        assert num_constraints >= 0, "num_constraints must be a non-negative integer"

        # Problem dimension
        self.n = num_variables
        # Total number of constraints; m = 2*n + d
        self.m = 2*self.n + num_constraints
        # Additional constraints
        self.d = num_constraints

        # Bounds to variables
        if upper_bound is None:
            upper_bound = 20.0 * (lower_bound + 1.0)
        assert upper_bound > lower_bound, "upper_bound must be greater than lower_bound"
        
        self.lb = lower_bound
        self.ub = upper_bound

        # generate seed from system entropy for non-reproducible randomness
        seed = int.from_bytes(os.urandom(4), byteorder='big')
        self.rng = np.random.default_rng(seed)

    def _get_objective_function(self) -> Tuple[np.ndarray, float, float]:
        alpha = self.ub - self.lb
        theta = np.random.rand() * alpha/2
        rho = theta / 10.0

        objective_coeffs = theta * self.rng.uniform(1.0, 20.0, size=self.n)
        objective_coeffs = np.round(objective_coeffs, decimals=4)

        # Sort in descending order
        objective_coeffs.sort()
        objective_coeffs = objective_coeffs[::-1]
        
        return objective_coeffs, theta, rho

    def _get_variables(self) -> List[LpVariable]:
        variables = [
            LpVariable(
                name=f"x{i+1}",
                lowBound=self.lb,
                upBound=self.ub,
            )
            for i in range(self.n)
        ]
        return variables
    
    def _get_support_inequalities(self, 
                                  vars: List[LpVariable],
                                  add_bounds_as_constraints: bool = False,
                                  ) -> List[LpConstraint]:
        constraints = []

        if add_bounds_as_constraints:
            for var in vars:
                c = LpConstraint(var >= self.lb, name=f"{var.name}_LB")
                c.sense = LpConstraintGE
                constraints.append(c)

                c = LpConstraint(var <= self.ub, name=f"{var.name}_UB")
                c.sense = LpConstraintLE
                constraints.append(c)

        alpha = self.ub - self.lb
        guard = (self.n-1) * alpha + alpha/2 + self.n*self.lb
        c = LpConstraint(lpSum(vars) <= guard, name="GuardConstraint")
        c.sense = LpConstraintLE
        constraints.append(c)
        return constraints
    
    def _get_initial_feasible_point(self) -> np.ndarray:
        alpha = self.ub - self.lb
        return np.full(self.n, self.lb + alpha/2)
    
    @staticmethod
    def _similar(c1: LpConstraint, 
                 c2: LpConstraint, 
                 vars: List[LpVariable], 
                 lMax: float,
                 sMin: float,
                 ) -> bool:
        a1, b1, _ = constraint_to_row(c1, vars)
        a2, b2, _ = constraint_to_row(c2, vars)

        norm1 = float(np.linalg.norm(a1)) + DEFAULT_ABS_TOLERANCE
        norm2 = float(np.linalg.norm(a2)) + DEFAULT_ABS_TOLERANCE

        deltaA = float(np.linalg.norm(a1 / norm1 - a2 / norm2))
        deltaB = abs(b1 / norm1 - b2 / norm2)

        return deltaA < lMax and deltaB < sMin

    def generate(self, 
                 sense: Optional[int] = None,
                 add_bounds_as_constraints: bool = False,
                 ) -> LpProblem:
        """Create a feasible LP problem with diverse constraint types."""
        
        # Randomly choose optimization sense if not provided
        if sense is None:
            sense = self.rng.choice([LpMinimize, LpMaximize])
        assert sense in [LpMinimize, LpMaximize], "sense must be LpMinimize or LpMaximize"

        # Generate LpProblem instance and variables
        problem = LpProblem(
            name=f"GeneratedLP_{self.n}x{self.m}",
            sense=sense,
        )
        variables = self._get_variables()

        # Generate positive objective function coefficients
        objective_coeffs, theta, rho = self._get_objective_function()
        problem += lpDot(objective_coeffs, variables), "Objective"

        # Generate support inequalities (bounds to variables)
        constraints = self._get_support_inequalities(variables, add_bounds_as_constraints)

        # Build a feasible point in the interior of the bounds.
        h = self._get_initial_feasible_point()

        lMax = np.random.rand() * 0.6 + 0.1
        sMin = 1.0
        for i in range(self.d):
            while True: # Use a loop to handle retires
                Ai = self.rng.normal(0, 1, size=self.n)
                bi = float(Ai @ h + self.rng.uniform(1.0, 10.0))
                
                if Ai @ h < bi:
                    ci = LpConstraint(lpDot(Ai, variables) <= bi, name=f"ExtraConstraint_{i+1}")
                    ci.sense = LpConstraintLE
                else:
                    ci = LpConstraint(lpDot(Ai, variables) >= bi, name=f"ExtraConstraint_{i+1}")
                    ci.sense = LpConstraintGE

                # Check if the constraint is to close or too far to h
                distance = abs(Ai @ h - bi) / (np.linalg.norm(Ai) + DEFAULT_ABS_TOLERANCE)
                if distance > theta or distance < rho:
                    continue
                
                # Check if the new constraint is similar to any existing one
                if any(self._similar(ci, cj, variables, lMax, sMin) for cj in constraints):
                    continue

                constraints.append(ci)
                break
        
        for c in constraints:
            problem += c

        return problem

    def write_mps(self, output_path: Union[str, Path]) -> Path:
        """Write the generated LP in MPS format."""

        problem = self.generate()
        output_file = Path(output_path)
        problem.writeMPS(str(output_file))
        return output_file


def __main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a feasible LP problem and export it to MPS format. "
        "Optimization sense (min/max) and objective coefficients are chosen randomly."
    )
    parser.add_argument(
        "--variables",
        "-n",
        type=int,
        required=True,
        help="Number of variables in the generated LP.",
    )
    parser.add_argument(
        "--constraints",
        "-m",
        type=int,
        required=True,
        help="Number of constraints in the generated LP.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="generated_lp.mps",
        help="Output MPS file path.",
    )

    args = parser.parse_args()

    generator = LPProblemGenerator(
        num_variables=args.variables,
        num_constraints=args.constraints,
    )
    output_file = generator.write_mps(args.output)
    print(f"Generated feasible LP: {output_file}")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(__main())
