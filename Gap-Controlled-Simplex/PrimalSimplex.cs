namespace Gap_Controlled_Simplex;

public class PrimalSimplex : ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsPrimalFeasible)
            return null;

        // A_N*x has 0 component => degenerate point

        if (v.IsOptimalPoint) // y_b >= 0
        {
            // Optimal value
            return v;
        }

        var h = v.Basis.First(i => v.y[i] < 0.0);

        // Wh is the h-th column of -A_b_inv
        var Wh = (-1) * 
            v.A_B
            .Inverse()
            .Column(v.Basis.IndexOf(h));

        // Entering index
        int k = int.MaxValue;
        double t = double.PositiveInfinity;
        foreach (int i in v.NonBasis.Where(i => v.A.Row(i) * Wh > 0.0))
        {
            var t_i = (v.b[i] - v.A.Row(i) * v.x) / (v.A.Row(i) * Wh);
            
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

        var newBasis = v.Basis
            .Where(i => i != h)
            .Append(k);
        return new Vertex(v.Problem, newBasis);
    }

    public Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        StartBasis ??= [];

        for (Vertex? current = new(p, StartBasis); 
            current is not null; 
            current = Iteration(current)
        ) {
            if (current.IsOptimalPoint)
                return current;
        }

        // Unsolvable or unbounded problem
        return null;
    }
}