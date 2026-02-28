using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex.Tests;

public class LinearProgrammingTest
{
    public Problem p;

    public int[]? startingPrimalBasis;

    public Vector<double> expectedSolution;

    public LinearProgrammingTest(
        double[] expected, 
        int[]? B, 
        
        double[] c, 
        params double[][] Ab
    ) {
        Assert.Equal(c.Length, expected.Length);

        if (B is not null)
            Assert.Equal(B.Length, c.Length);

        p = new Problem(c, Ab).EnforcePositivity();
        Assert.True(p.Constraints >= p.Dimension, "Problem must have more constraints than variables");

        startingPrimalBasis = B;
        expectedSolution = Vector<double>.Build.DenseOfArray(expected);
    }

    public void Test(ISolver solver, bool useStartingBasis = true)
    {
        var result = solver.Maximize(p, useStartingBasis ? startingPrimalBasis : null);
        Assert.NotNull(result);

        Assert.True(result.IsOptimalPoint(), "Returned value not recognized as optimal");

        var expectedValue = p.Eval(expectedSolution);
        Assert.Equal(0.0, (result.PrimalValue - expectedValue) / expectedValue, 5.0e-3);
    }
}