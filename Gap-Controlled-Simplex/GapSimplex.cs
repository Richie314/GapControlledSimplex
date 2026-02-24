namespace Gap_Controlled_Simplex;

public class GapSimplex : ISimplex
{
    public Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        throw new NotImplementedException();
    }

    private static Vertex? makeDualFeasible(Problem p, Vertex v)
    {
        while (!v.IsDualFeasible)
        {
            // Dual residuals c^T - y^T A
            var rc = v.dualResiduals();

            // Entering index
            int k = v.NonBasis.MaxBy(i => rc[i]);

            // Primal direction
            var d = v.A_B.Inverse() * p.A.Row(k);

            // Leaving index
            int h = int.MaxValue;
            double t = double.PositiveInfinity;
            foreach (int i in v.Basis)
            {
                if (d[i] <= 0.0)
                    continue;

                var t_i = (p.b[i] - p.A.Row(i) * v.x) / d[i];
                
                if (t_i < t)
                {
                    t = t_i;
                    h = i;
                }
            }

            if (h == int.MaxValue)
                return null;
            
            var newBasis = v.Basis
                .Where(i => i != h)
                .Append(k);
            
            v = new Vertex(p, newBasis);
        }

        return v;
    } 

    private static Vertex makePrimalFeasible(Problem p, Vertex v)
    {
        while (!v.IsPrimalFeasible)
        {
        }

        return v;
    }
}