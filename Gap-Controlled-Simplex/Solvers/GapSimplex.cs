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
            var (gap, relativeGap, dualValue, primalValue)
                = Vertex.Gap(dualVertex, primalVertex);
                
            if (relativeGap.HasValue)
                Console.WriteLine($"Relative gap: {relativeGap.Value}");
            Console.WriteLine($"Gap: {gap} = {dualValue} - {primalValue}");

            if (primalVertex.IsPrimalDegenerate())
            {
                var newPrimalPoint = primalSimplex.MakeFeasible(dualVertex);
                if (newPrimalPoint is not null && 
                    newPrimalPoint.primalValue() > primalValue
                )
                    primalVertex = newPrimalPoint;
            }

            if (dualVertex.IsDualDegenerate())
            {
                var newDualPoint = dualSimplex.MakeFeasible(primalVertex);
                if (newDualPoint is not null && 
                    newDualPoint.dualValue() < dualValue
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