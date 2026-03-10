namespace Gap_Controlled_Simplex.Solvers;

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

            if (primalVertex.IsPrimalDegenerate())
            {
                var newPrimalPoint = primalSimplex.MakeFeasible(dualVertex);
                if (newPrimalPoint is not null && 
                    newPrimalPoint.PrimalValue > primalVertex.PrimalValue
                )
                    primalVertex = newPrimalPoint;
            }

            if (dualVertex.IsDualDegenerate())
            {
                var newDualPoint = dualSimplex.MakeFeasible(primalVertex);
                if (newDualPoint is not null && 
                    newDualPoint.DualValue < dualVertex.DualValue
                )
                    dualVertex = newDualPoint;
            }

            primalVertex = PrimalSimplex.Iteration(primalVertex);
            if (primalVertex is null || primalVertex.IsOptimalPoint())
                return primalVertex;

            dualVertex = DualSimplex.Iteration(dualVertex);
            if (dualVertex is null || dualVertex.IsOptimalPoint())
                return dualVertex;
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

    public Vertex? MakeFeasible(Vertex v) =>
        throw new NotImplementedException();
}