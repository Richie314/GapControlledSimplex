namespace Gap_Controlled_Simplex.Solvers;

public abstract class IterativeSolver : ISolver
{
    public int? MaxIterations = null;

    protected bool checkIterationCount(int iterations)
        => !MaxIterations.HasValue || iterations <= MaxIterations.Value;

    public abstract Solution? Maximize(in Problem p, int[]? startingBasis);


    public abstract (Vertex? v, int initialIterations) 
        GetStartingPoint(in Problem p, int[]? givenBasis = null);
}