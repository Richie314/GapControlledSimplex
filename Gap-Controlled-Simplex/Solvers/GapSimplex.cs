namespace Gap_Controlled_Simplex.Solvers;

public class GapSimplex : IterativeSolver, ISimplex
{
    private PrimalSimplex _primalSimplex = new();
    private DualSimplex _dualSimplex = new();

    public override Solution? Maximize(in Problem p, int[]? StartBasis = null)
    {
        var (primalVertex, initialPrimalIterations) = GetStartingPoint(p, StartBasis);
        var (dualVertex, initialDualIterations) = _dualSimplex.GetStartingPoint(p);

        if (primalVertex is null || 
            !primalVertex.IsPrimalFeasible() ||
            dualVertex is null ||
            !dualVertex.IsDualFeasible()
        )
            return null;

        int primalIterations = 0, dualIterations = 0;
        while (
            !primalVertex.IsOptimalPoint() && 
            checkIterationCount(primalIterations) &&
            !dualVertex.IsOptimalPoint() &&
            checkIterationCount(dualIterations)
        ) {
            var (gap, relativeGap, dualValue, primalValue)
                = Vertex.Gap(dualVertex, primalVertex);
                
            if (relativeGap.HasValue)
                Console.WriteLine($"Relative gap: {relativeGap.Value}");
            Console.WriteLine($"Gap: {gap} = {dualValue} - {primalValue}");

            if (primalVertex.IsPrimalDegenerate())
            {
                var newPrimalPoint = _primalSimplex.MakeFeasible(dualVertex);
                if (newPrimalPoint is not null && 
                    newPrimalPoint.primalValue() > primalValue
                )
                    primalVertex = newPrimalPoint;
            }

            if (dualVertex.IsDualDegenerate())
            {
                var newDualPoint = _dualSimplex.MakeFeasible(primalVertex);
                if (newDualPoint is not null && 
                    newDualPoint.dualValue() < dualValue
                )
                    dualVertex = newDualPoint;
            }

            primalVertex = PrimalSimplex.Iteration(primalVertex);
            if (primalVertex is null || primalVertex.IsOptimalPoint())
                break;
            primalIterations++;

            dualVertex = DualSimplex.Iteration(dualVertex);
            if (dualVertex is null || dualVertex.IsOptimalPoint())
                break;
            dualIterations++;
        }

        if (primalVertex is null || dualVertex is null)
            return null;

        return new Solution()
        {
            Point = primalVertex.IsOptimalPoint() ? primalVertex : dualVertex,
            IterationCount = primalIterations,
            InitialIterations = initialPrimalIterations + initialDualIterations
        };
    }

    public (Vertex v, int iterations)? GetFeasibleVertex(in Problem p) 
        => _primalSimplex.GetFeasibleVertex(p);

    public override (Vertex?, int) GetStartingPoint(in Problem p, int[]? B = null)
        => _primalSimplex.GetStartingPoint(p, B);

    public Vertex? MakeFeasible(in Vertex v) =>
        throw new NotImplementedException();
}