namespace Gap_Controlled_Simplex;

public interface ISolver
{
    public Vertex? Maximize(Problem problem, int[]? B = null);
    
    public Vertex? Minimize(Problem p, int[]? StartBasis = null)
    {
        var invertedProblem = new Problem(
            p.c * -1.0,
            p.A,
            p.b
        );

        var result = Maximize(invertedProblem, StartBasis);
        if (result is null || !result.IsOptimalPoint())
            return null;

        // Change reference problem back to original
        return new Vertex(p, result.Basis);
    }
}