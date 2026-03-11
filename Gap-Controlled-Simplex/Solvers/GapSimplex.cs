namespace Gap_Controlled_Simplex.Solvers;

public class GapSimplex : IterativeSolver, ISimplex
{
    public override Solution? Maximize(Problem p, int[]? StartBasis = null)
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

        int primalIterations = 0, dualIterations = 0;
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
                break;
            primalIterations++;
            checkIterationCount(primalIterations);

            dualVertex = DualSimplex.Iteration(dualVertex);
            if (dualVertex is null || dualVertex.IsOptimalPoint())
                break;
            dualIterations++;
            checkIterationCount(dualIterations);
        }

        if (primalVertex is null || dualVertex is null)
            return null;

        return new Solution()
        {
            Point = primalVertex.IsOptimalPoint() ? primalVertex : dualVertex,
            IterationCount = primalIterations
        };
    }

    public Vertex? GetFeasibleVertex(Problem p) =>
        new PrimalSimplex().GetFeasibleVertex(p);

    public Vertex? MakeFeasible(Vertex v) =>
        throw new NotImplementedException();
}