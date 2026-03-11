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

        Assert.True(result.IsOptimalPoint(), "Returned value not recognized as optimal");

        double p = result.primalValue(), 
               d = result.dualValue();

        Assert.Equal(p, d, Vertex.AbsoluteTolerance);

        if (ExpectedValue is not null)
        {
            if (Math.Abs(ExpectedValue.Value) > Vertex.AbsoluteTolerance)
            {
                // Can safely divide by ExpectedValue.Value
                double relativeGap = (p - ExpectedValue.Value) / ExpectedValue.Value;
                Assert.Equal(0.0, relativeGap, 5.0e-3);
            } else
            {
                // ExpectedValue.Value is near zero
                Assert.Equal(p, ExpectedValue.Value, Vertex.AbsoluteTolerance * 10);
            }
        }
    }
}