namespace Gap_Controlled_Simplex.Solvers;

public interface ISolver
{
    public Solution? Maximize(in Problem problem, int[]? B = null);
    
    public Solution? Minimize(in Problem p, int[]? StartBasis = null)
    {
        var invertedProblem = new Problem(
            -p.c,
            p.A,
            p.b
        );

        var result = Maximize(invertedProblem, StartBasis);
        if (result is null)
            return null;

        // Change reference problem back to original
        return new Solution()
        {
            Point = new Vertex(p, result.Basis),
            IterationCount = result.IterationCount,
        };
    }
}