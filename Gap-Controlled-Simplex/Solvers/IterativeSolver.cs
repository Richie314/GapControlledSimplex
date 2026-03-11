namespace Gap_Controlled_Simplex.Solvers;

public abstract class IterativeSolver : ISolver
{
    public int? MaxIterations = null;

    protected void checkIterationCount(int iterations)
    {
        if (MaxIterations.HasValue && iterations > MaxIterations.Value)
            throw new Exception(
                $"Iteration limit ({MaxIterations.Value}) exceeded: {iterations}."
            );
    }

    public abstract Solution? Maximize(Problem p, int[]? startingBasis);
}