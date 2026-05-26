import argparse
from pathlib import Path
from typing import Optional, Union
import os
import numpy as np
from pulp import (
    LpProblem, LpVariable, 
    LpMinimize, LpMaximize, 
    LpConstraintLE, LpConstraintGE, LpConstraintEQ,
    lpDot, 
)

from gsimplex.constants import DEFAULT_ABS_TOLERANCE

class LPProblemGenerator:
    """
    Generate feasible linear programs using FRaGenLP algorithm.
    See also doi 10.48550/arXiv.2105.10384 for more details.
    
    Algorithm:
    1. Choose random feasible point x_0 ∈ [lower_bound, upper_bound]
    2. Generate m random constraint rows (first n linearly independent)
    3. Compute RHS: b_i = A[i] · x_0 + slack_i (slack_i > 0)
    4. This guarantees Ax_0 <= b (x_0 is feasible for all constraint types)
    5. Mix LE (Ax <= b), GE (Ax >= b where b < Ax_0), and EQ (Ax = Ax_0) constraints
    """

    def __init__(
        self,
        num_variables: int,
        num_constraints: int,
        lower_bound: float = 0.0,
        upper_bound: Optional[float] = None,
    ):
        assert num_variables > 0, "num_variables must be positive"
        assert num_constraints >= num_variables, "num_constraints must be positive and greater or equal to num_variables"

        self.num_variables = num_variables
        self.num_constraints = num_constraints
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        # Auto-generate seed from system entropy for non-reproducible randomness
        auto_seed = int.from_bytes(os.urandom(4), byteorder='big')
        self.rng = np.random.default_rng(auto_seed)
        self._constraint_coefficients: list[np.ndarray] = []

    def _is_linearly_independent(self, new_coeffs: np.ndarray, tolerance: float = 100 * DEFAULT_ABS_TOLERANCE) -> bool:
        """
        Check if a constraint coefficient vector is linearly independent from existing ones.
        Uses QR decomposition rank test for numerical stability.
        
        :param new_coeffs: Coefficient vector for the new constraint.
        :param tolerance: Numerical tolerance for rank computation.
        :return: True if the new constraint is independent from existing ones.
        """
        if not self._constraint_coefficients:
            return True
        
        # Build matrix from existing coefficients
        existing_matrix = np.array(self._constraint_coefficients)
        
        # Add new coefficients
        test_matrix = np.vstack([existing_matrix, new_coeffs])
        
        # Compute rank using SVD (more numerically stable than QR)
        _, singular_values, _ = np.linalg.svd(test_matrix)
        rank = np.sum(singular_values > tolerance)
        
        # If rank increased, the new constraint is independent
        return rank == len(self._constraint_coefficients) + 1

    def generate(self) -> LpProblem:
        """Create a feasible LP problem with diverse constraint types."""
        self._constraint_coefficients = []
        
        # Randomly choose optimization sense
        sense = self.rng.choice([LpMinimize, LpMaximize])
        
        problem = LpProblem(
            name=f"GeneratedLP_{self.num_variables}x{self.num_constraints}",
            sense=sense,
        )

        variables = [
            LpVariable(
                name=f"x{i+1}",
                lowBound=self.lower_bound,
                upBound=self.upper_bound,
            )
            for i in range(self.num_variables)
        ]

        # Build a feasible point in the interior of the bounds.
        if self.upper_bound is None:
            x0 = self.rng.uniform(
                max(self.lower_bound + 0.1, 0.1),
                max(self.lower_bound + 5.0, 5.0),
                size=self.num_variables,
            )
        else:
            x0 = self.rng.uniform(
                self.lower_bound,
                self.upper_bound,
                size=self.num_variables,
            )

        # Generate positive objective function coefficients
        objective_coeffs = self.rng.uniform(1.0, 10.0, size=self.num_variables)
        problem += lpDot(objective_coeffs, variables), "Objective"

        # Constraint types distribution
        constraint_types = [
            LpConstraintLE, LpConstraintGE
        ] * 4 + [LpConstraintEQ]  # More LE/GE than EQ
        added_constraints = 0
        attempts = 0
        # Allow more attempts if we have more constraints than variables
        max_attempts = max(200, self.num_constraints * 30)
        # Enforce strict independence only up to num_variables constraints
        strict_independence_count = min(self.num_variables, self.num_constraints)

        while added_constraints < self.num_constraints and attempts < max_attempts:
            attempts += 1
            # Generate random constraint coefficients using normal distribution
            coefficients = self.rng.normal(0, 1, size=self.num_variables)
            
            # Ensure non-zero coefficient vector
            if np.linalg.norm(coefficients) < DEFAULT_ABS_TOLERANCE:
                coefficients = self.rng.uniform(-1, 1, size=self.num_variables)
            
            # Normalize for numerical stability
            coefficients = coefficients / (np.linalg.norm(coefficients) + DEFAULT_ABS_TOLERANCE)

            # Check linear independence only for the first num_variables constraints
            if added_constraints < strict_independence_count:
                if not self._is_linearly_independent(coefficients):
                    continue
            
            self._constraint_coefficients.append(coefficients.copy())

            # Choose random constraint type
            constraint_type = self.rng.choice(constraint_types)
            
            # CRITICAL: Set appropriate RHS based on constraint type
            # to guarantee x_0 is feasible
            slack = self.rng.uniform(1.0, 10.0)
            rhs_le = float(coefficients @ x0 + slack)  # Ax_0 + slack > Ax_0
            rhs_ge = float(coefficients @ x0 - slack)  # Ax_0 - slack < Ax_0
            rhs_eq = float(coefficients @ x0)          # Exact value
            
            constraint_index = added_constraints + 1

            # Add constraint based on type
            if constraint_type == LpConstraintLE:
                # Ax <= b where b = Ax_0 + slack > Ax_0
                problem += lpDot(coefficients, variables) <= rhs_le, f"C{constraint_index}_LE"
            elif constraint_type == LpConstraintGE:
                # Ax >= b where b = Ax_0 - slack < Ax_0
                problem += lpDot(coefficients, variables) >= rhs_ge, f"C{constraint_index}_GE"
            else:  # EQ
                # Ax = b where b = Ax_0 exactly
                problem += lpDot(coefficients, variables) == rhs_eq, f"C{constraint_index}_EQ"

            added_constraints += 1

        if added_constraints < self.num_constraints:
            raise RuntimeError(
                f"Could not generate {self.num_constraints} constraints "
                f"after {max_attempts} attempts. Only {added_constraints} were generated."
            )

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
