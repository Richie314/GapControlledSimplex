from gsimplex.problem import Problem
from gsimplex.vertex import Vertex
from gsimplex.solvers.solver_interface import ISolver

class LinearProgrammingTest:
    def __init__(self, expected, B, c, *ab_rows):
        self.expected = np.array(expected) if expected is not None else None
        self.B = B
        self.c = c
        self.ab_rows = ab_rows

        if self.expected is not None:
            assert len(c) == len(self.expected)

        if self.B is not None:
            assert len(c) == len(self.B)

        self.problem = Problem.from_ab_rows(c, *ab_rows).enforce_positivity()
        assert self.problem.constraints >= self.problem.dimension

        if self.expected is not None:
            self.expected_solution = np.array(expected)
            self.expected_value = self.problem.c @ self.expected_solution

    def test(self, solver: ISolver, use_starting_basis: bool = True):
        result = solver.maximize(self.problem, self.B if use_starting_basis else None)
        assert result is not None

        gap, relative_gap, dual_value, primal_value = Vertex.gap(result.point, result.point)

        assert abs(primal_value - dual_value) < Vertex.ABSOLUTE_TOLERANCE * 10
        assert abs(gap) < Vertex.ABSOLUTE_TOLERANCE * 10

        if relative_gap is not None:
            assert abs(relative_gap) < Vertex.RELATIVE_TOLERANCE * 10

        assert result.point.is_optimal_point()

        if self.expected is not None:
            if abs(self.expected_value) > Vertex.ABSOLUTE_TOLERANCE:
                relative_error = (primal_value - self.expected_value) / self.expected_value
                assert abs(relative_error) < 5e-3
            else:
                assert abs(primal_value - self.expected_value) < Vertex.ABSOLUTE_TOLERANCE * 10