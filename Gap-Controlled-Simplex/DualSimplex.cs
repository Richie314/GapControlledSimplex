using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class DualSimplex
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
        Vertex current = 
            StartBasis is not null ? 
            new(p, StartBasis) : 
            getStartingBasis(p);

        while (current.IsDualFeasible)
        {
            if (current.IsOptimalPoint) // Ax <= b
            {
                // Optimal value
                return current;
            }

            // Entering index
            int k = current.NonBasis.First(i => p.b[i] < p.A.Row(i) * current.x);
            var Ak = p.A.Row(k);

            var W = (-1) * current
                .activeConstraintsMatrix()
                .Inverse();

            // Leaving index
            int h = int.MaxValue;
            double t = double.PositiveInfinity;
            foreach (int i in current.Basis)
            {
                var Ak_Wi = Ak * W.Column(current.Basis.IndexOf(i));
                if (Ak_Wi >= 0.0)
                    continue;

                var t_i = -current.y[i] / Ak_Wi;
                
                if (t_i < t)
                {
                    t = t_i;
                    h = i;
                }
            }

            if (h == int.MaxValue)
            {
                // Unbounded problem
                return null;
            }

            var newBasis = current.Basis
                .Where(i => i != h)
                .Append(k);
            current = new Vertex(p, newBasis);
        }

        return null;
    }

    private static Vertex getStartingBasis(Problem p)
    {
        Vertex v = new(p, Enumerable.Range(0, p.Dimension));

        while (!v.IsDualFeasible)
        {

            // Direzione dual simplex
            // W_h = -B^{-1} e_h
            int h = v.Basis.First(i => v.y[i] < 0.0);
            var eh = Vector<double>.Build.Dense(p.Dimension, 0.0);
            eh[h] = 1.0;

            var Wh = -v.activeConstraintsMatrix().Inverse() * eh;

            // Ratio test duale
            int entering = -1;
            double tMin = double.PositiveInfinity;

            foreach (int i in v.NonBasis)
            {
                double denom = p.A.Row(i) * Wh;

                if (denom <= 0.0)
                    continue;
                
                double t = (p.b[i] - p.A.Row(i) * v.x) / denom;

                if (t < tMin)
                {
                    tMin = t;
                    entering = i;
                }
            }

            // Nessun vincolo blocca → problema mal posto
            if (entering == -1)
            {
                throw new Exception("Unbounded problem");
            }

            // Pivot: sostituisci vincolo h
            var newBasis = v.Basis
                .Where(i => i != h)
                .Append(entering);

            v = new Vertex(p, newBasis);
        }
        
        return v;
    }
}