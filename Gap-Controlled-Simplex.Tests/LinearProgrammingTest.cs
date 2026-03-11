using MathNet.Numerics.LinearAlgebra;
using Gap_Controlled_Simplex.Solvers;

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
            ExpectedValue = P.c * ExpectedSolution;
        }
    }

    public void Test(ISolver solver, bool useStartingBasis = true)
    {
        var result = solver.Maximize(P, useStartingBasis ? StartingPrimalBasis : null);
        Assert.NotNull(result);

        var (gap, relativeGap, dualValue, primalValue) = Vertex.Gap(result.Point, result.Point);

        Assert.Equal(primalValue, dualValue, Vertex.AbsoluteTolerance * 10);
        Assert.Equal(0.0, gap, Vertex.AbsoluteTolerance * 10);

        if (relativeGap.HasValue)
            Assert.Equal(0.0, relativeGap.Value, Vertex.RelativeTolerance * 10);

        Assert.True(result.Point.IsOptimalPoint(), "Returned value not recognized as optimal");

        if (ExpectedValue is not null)
        {
            if (Math.Abs(ExpectedValue.Value) > Vertex.AbsoluteTolerance)
            {
                // Can safely divide by ExpectedValue.Value
                double relativeError = (primalValue - ExpectedValue.Value) / ExpectedValue.Value;
                Assert.Equal(0.0, relativeError, 5.0e-3);
            } else
            {
                // ExpectedValue.Value is near zero
                Assert.Equal(primalValue, ExpectedValue.Value, Vertex.AbsoluteTolerance * 10);
            }
        }
    }
}