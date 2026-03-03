using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex.Tests;

public class LinearProgrammingTest
{
    public Problem P;

    public int[]? StartingPrimalBasis;

    public Vector<double>? ExpectedSolution;
    public double? ExpectedValue;

    public LinearProgrammingTest(
        double[]? expected, 
        int[]? B, 
        
        double[] c, 
        params double[][] Ab
    ) {
        if (expected is not null)
            Assert.Equal(c.Length, expected.Length);

        if (B is not null)
            Assert.Equal(c.Length, B.Length);

        P = new Problem(c, Ab).EnforcePositivity();
        Assert.True(P.Constraints >= P.Dimension, "Problem must have more constraints than variables");

        StartingPrimalBasis = B;

        if (expected is not null)
        {
            ExpectedSolution = Vector<double>.Build.DenseOfArray(expected);
            ExpectedValue = P.Eval(ExpectedSolution);
        }
    }

    public void Test(ISolver solver, bool useStartingBasis = true)
    {
        var result = solver.Maximize(P, useStartingBasis ? StartingPrimalBasis : null);
        Assert.NotNull(result);

        Assert.True(result.IsOptimalPoint(), "Returned value not recognized as optimal");

        if (ExpectedValue is not null)
            Assert.Equal(0.0, (result.PrimalValue - ExpectedValue.Value) / ExpectedValue.Value, 5.0e-3);
    }
}