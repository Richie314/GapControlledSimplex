namespace Gap_Controlled_Simplex;

public class GapSimplex : ISimplex
{
    public Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        var primalSimplex = new PrimalSimplex();
        var dualSimplex = new DualSimplex();

        var primalVertex = 
            StartBasis is not null ? 
            new Vertex(p, StartBasis) : 
            primalSimplex.GetFeasibleVertex(p);
        var dualVertex = dualSimplex.GetFeasibleVertex(p);

        if (primalVertex is null || 
            !primalVertex.IsPrimalFeasible() ||
            dualVertex is null ||
            !dualVertex.IsDualFeasible()
        )
            return null;

        while (!primalVertex.IsOptimalPoint() && !dualVertex.IsOptimalPoint())
        {
            double gap = dualVertex.DualValue - primalVertex.PrimalValue;
            if (primalVertex.PrimalValue != 0.0)
            {
                double relativeGap = Math.Abs(gap / primalVertex.PrimalValue);
                Console.WriteLine($"Relative gap: {relativeGap}");
            }
            Console.WriteLine($"Gap: {gap} = {dualVertex.DualValue} - {primalVertex.PrimalValue}");



            // A
            primalVertex = PrimalSimplex.Iteration(primalVertex);
            if (primalVertex is null)
                return null;

            // B
            dualVertex = DualSimplex.Iteration(dualVertex);
            if (dualVertex is null)
                return null;

            //dualVertex = makeDualFeasible(p, primalVertex);
            //primalVertex = makePrimalFeasible(p, dualVertex);
        }

        if (primalVertex.IsOptimalPoint())
        {
            Console.WriteLine("Optimal primal vertex found");
            return primalVertex;
        }

        Console.WriteLine("Optimal dual vertex found");
        return dualVertex;
    }

    public Vertex? GetFeasibleVertex(Problem p) =>
        new PrimalSimplex().GetFeasibleVertex(p);

    private static Vertex? makePrimalFeasible(Problem p, Vertex v)
    {
        while (!v.IsPrimalFeasible())
        {
            // Calculate primal residuals
            var rp = v.primalResiduals();

            // Leaving index: remove the "most primal-infeasible" index from the basis
            int h = v.Basis.MaxBy(i => Math.Abs(rp[i]));

            // Entering index
            int k = -1;
            double t = 0;
            foreach (int j in v.NonBasis)
            {
                
            }

            var newBasis = v.Basis
                .Where(i => i != h)
                .Append(k);

            v = new Vertex(p, newBasis);
        }

        return v;
    }

    private static Vertex? makeDualFeasible(Problem p, Vertex v)
    {
        while (!v.IsDualFeasible())
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
}