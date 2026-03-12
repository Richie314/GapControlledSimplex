namespace Gap_Controlled_Simplex.Solvers;

public class DualSimplex : IterativeSolver, ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsDualFeasible())
            return null;
        
        if (v.IsPrimalFeasible()) // check Ax <= b
            return v; // Optimal value reached

        // Entering index (Bland rule)
        var (k, slack) = v
            .primalInfeasibleRows()
            .First();

        // Direction
        var Ak = v.A.Row(k);
        
        // Leaving index (Minimum ratio + Bland rule)
        var (h, tDenom) = v
            .Basis
            .Select(i => (i, den: Ak * v.W.Column(v.Basis.IndexOf(i))))
            .Where(pair => pair.den < -Vertex.AbsoluteTolerance)
            .OrderBy(pair => -v.y[pair.i] / pair.den)
            .FirstOrDefault(defaultValue: (-1, 0.0));

        if (h == -1)
            return null; // Unbounded problem

        var newBasis = v.Basis
            .Except([h])
            .Append(k);
        return new Vertex(v.Problem, newBasis);
    }


    public override Solution? Maximize(in Problem p, int[]? StartBasis = null)
    {
        var (current, initialIterations) = GetStartingPoint(p, StartBasis);

        for (int iterations = 0; 
            current is not null && checkIterationCount(iterations); 
            current = Iteration(current), iterations++
        ) {
            if (current.IsOptimalPoint())
            {
                return new Solution()
                {
                    Point = current,
                    IterationCount = iterations,
                    InitialIterations = initialIterations
                };
            }
        }

        return null;
    }

    public Vertex? MakeFeasible(in Vertex w)
    {
        Vertex v = w;
        int n = v.Problem.Dimension;

        while (!v.IsDualFeasible())
        {
            // Leaving index (Bland rule)
            var (p, dualSlack) = v
                .dualInfeasibleValues()
                .First();

            // Direction
            var d = -v.W * v.A.Row(p);
            
            // Entering index (Minimum coefficient + Bland rule)
            var (q, pivot) = v
                .NonBasis
                .Select(i => (i, v.A.Row(i) * d))
                .FirstOrDefault(
                    pair => pair.Item2 <= -Vertex.AbsoluteTolerance, 
                    defaultValue: (-1, 0.0)
                );
                
#if false
            // Enetering index (Largest pivot + Bland rule)
            var (q, pivot) = v
                .NonBasis
                .Select(i => (i, v.A.Row(i) * d))
                .Where(pair => pair.Item2 <= -Vertex.AbsoluteTolerance)
                .OrderBy(pair => Math.Abs(pair.Item2))
                .FirstOrDefault(defaultValue: (-1, 0.0));
#endif

            if (q == -1)
                throw new Exception("Unbounded problem");

            var newBasis = v.Basis
                .Except([p])
                .Append(q);

            v = new Vertex(v.Problem, newBasis);
        }
        
        return v;
    }

    public (Vertex, int)? GetFeasibleVertex(in Problem p)
    {
        // TODO: count dual initial iterations too
        var initialPoint = new Vertex(p, Enumerable.Range(0, p.Dimension));

        var dualFeasiblePoint = MakeFeasible(initialPoint);
        if (dualFeasiblePoint is null)
            return null;

        return (dualFeasiblePoint, 0);
    }

    public override (Vertex? v, int initialIterations) 
        GetStartingPoint(in Problem p, int[]? givenBasis = null)
    {
        if (givenBasis is not null)
            return (new(p, givenBasis), 0);

        var phaseOneSolution = GetFeasibleVertex(p);
        if (phaseOneSolution is null)
            return (null, 0);
        return phaseOneSolution.Value;
    }
}