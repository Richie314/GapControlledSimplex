using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class DualSimplex : ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsDualFeasible())
            return null;
        
        if (v.IsPrimalFeasible()) // Ax <= b
        {
            // Optimal value
            return v;
        }

        // Entering index
        int k = v.NonBasis.First(i => v.b[i] < v.A.Row(i) * v.x);
        var Ak = v.A.Row(k);

        var W = (-1) * v.A_B.Inverse();
        
        // Leaving index
        int h = int.MaxValue;
        double t = double.PositiveInfinity;
        foreach (int i in v.Basis)
        {
            var Ak_Wi = Ak * W.Column(v.Basis.IndexOf(i));
            if (Ak_Wi >= 0.0)
                continue;

            var t_i = -v.y[i] / Ak_Wi;
            
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

        var newBasis = v.Basis
            .Where(i => i != h)
            .Append(k);
        return new Vertex(v.Problem, newBasis);
    }


    public Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        Vertex? current = 
            StartBasis is not null ? 
            new(p, StartBasis) : 
            GetFeasibleVertex(p);

        for (; current is not null; current = Iteration(current))
        {
            if (current.IsOptimalPoint())
                return current;
        }

        return null;
    }

    public Vertex? GetFeasibleVertex(Problem p)
    {
        Vertex v = new(p, Enumerable.Range(0, p.Dimension));

        while (!v.IsDualFeasible())
        {

            // Direzione dual simplex
            // Wh = h-th column of -A_B^{-1}
            int h = v.Basis.First(i => v.y[i] < 0.0);
            var Wh = -v.A_B.Inverse().Column(v.Basis.IndexOf(h));

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