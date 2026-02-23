namespace Gap_Controlled_Simplex;

public class PrimalSimplex
{
    public static Vertex? Minimize(Problem p, int[]? StartBasis = null)
    {
        var invertedProblem = new Problem(
            p.c * -1,
            p.A,
            p.b
        );

        var result = Maximize(invertedProblem, StartBasis);
        if (result is null)
            return result;

        // Change reference problem back to original
        result.Problem = p;
        return result;
    }

    public static Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        StartBasis ??= [];
        Vertex current = new(p, StartBasis);

        while (true)
        {
            if (!current.IsPrimalFeasible)
                return null;

            // A_N*x has 0 component => degenerate point

            if (current.IsOptimalPoint) // y_b >= 0
            {
                // Optimal value
                return current;
            }

            var h = current.Basis.First(i => current.y[i] < 0.0);

            // Wh is the h-th column of -A_b_inv
            var Wh = (-1) * current
                .activeConstraintsMatrix()
                .Inverse()
                .Column(current.Basis.IndexOf(h));

            // Entering index
            int k = int.MaxValue;
            double t = double.PositiveInfinity;
            foreach (int i in current.NonBasis.Where(i => p.A.Row(i) * Wh > 0.0))
            {
                var t_i = (p.b[i] - p.A.Row(i) * current.x) / (p.A.Row(i) * Wh);
                
                if (t_i < t)
                {
                    t = t_i;
                    k = i;
                }
            }

            if (k == int.MaxValue)
            {
                // Unbounded problem
                return null;
            }

            var newBasis = current.Basis
                .Where(i => i != h)
                .Append(k);
            current = new Vertex(p, newBasis);
        }
    }
}