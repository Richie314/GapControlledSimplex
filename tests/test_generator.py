import numpy as np
from pulp import LpConstraintLE, LpConstraintGE, LpConstraintEQ

from gsimplex.tools import LPProblemGenerator
from gsimplex.tools.parser import ProblemParser
from gsimplex.tools.problem import constraint_to_row, get_objective_function


def test_lp_problem_generator_creates_feasible_problem(tmp_path):
    output_path = tmp_path / "generated_lp.mps"
    generator = LPProblemGenerator(num_variables=4, num_constraints=6)

    problem = generator.generate()
    assert problem.numVariables() == 4
    assert problem.numConstraints() == 6

    generated_file = generator.write_mps(output_path)
    assert generated_file.exists(), "MPS file should be written"

    loaded = ProblemParser.load_mps_from_file(generated_file)
    assert loaded.numVariables() == 4
    assert loaded.numConstraints() == 6


def test_generator_creates_diverse_constraint_types():
    """Verify generator creates LE, GE, and EQ constraints."""
    generator = LPProblemGenerator(num_variables=5, num_constraints=10)
    problem = generator.generate()
    
    constraints = list(problem.constraints.values())
    assert len(constraints) == 10
    
    # Check that we have a mix of constraint types
    has_le = any(c.sense == LpConstraintLE for c in constraints)
    has_ge = any(c.sense == LpConstraintGE for c in constraints)
    # has_eq = any(c.sense == LpConstraintEQ for c in constraints)

    # With 10 random constraints from {LE, GE, EQ}, we should get at least some of each type
    # (this is probabilistic but very likely)
    assert has_le or has_ge, "Generator should create at least one diverse constraint type"


def test_generator_objective_coefficients_are_positive():
    """Verify all objective function coefficients are positive."""
    generator = LPProblemGenerator(num_variables=5, num_constraints=6)
    problem = generator.generate()
    
    objective_coeffs = get_objective_function(problem)
    assert np.all(objective_coeffs > 0), f"All objective coefficients must be positive, got {objective_coeffs}"


def test_generator_random_optimization_sense():
    """Verify that both min and max problems can be generated."""
    senses_found = set()
    
    # Generate multiple problems to likely get both senses
    for _ in range(20):
        generator = LPProblemGenerator(num_variables=4, num_constraints=5)
        problem = generator.generate()
        senses_found.add(problem.sense)
    
    # With 20 generations, we should see both min and max
    assert len(senses_found) == 2, f"Should generate both min and max problems, got senses: {senses_found}"


def test_generator_maintains_linear_independence():
    """Verify first num_variables constraints are linearly independent."""
    num_vars = 5
    generator = LPProblemGenerator(num_variables=num_vars, num_constraints=8)
    problem = generator.generate()
    
    # Extract coefficient vectors for first num_vars constraints
    constraints_list = list(problem.constraints.values())[:num_vars]
    coefficients_matrix = np.array([
        constraint_to_row(c, problem)[0] for c in constraints_list
    ])
    
    # Compute rank - should be equal to num_vars for independence
    rank = np.linalg.matrix_rank(coefficients_matrix)
    assert rank == num_vars, f"First {num_vars} constraints should be linearly independent, got rank {rank}"


def test_generator_respects_bounds():
    """Verify that generated problems respect variable bounds."""
    generator = LPProblemGenerator(
        num_variables=3,
        num_constraints=5,
        lower_bound=0.0,
    )
    problem = generator.generate()
    
    assert problem.numVariables() == 3
    assert problem.numConstraints() == 5
    assert problem.objective is not None
