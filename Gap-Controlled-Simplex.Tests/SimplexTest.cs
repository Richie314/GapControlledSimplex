namespace Gap_Controlled_Simplex.Tests;

public class SimplexTest
{
    private static void DoTest(
        ISimplex solver,
        double[] expected, 
        int[]? B, 
        
        double[] c, 
        params double[][] Ab
    ) {
        parseContraints(Ab, out var A, out var b);
        Assert.Equal(A.GetLength(0), b.Length);
        Assert.Equal(A.GetLength(1), c.Length);
        Assert.Equal(c.Length, expected.Length);

        if (B is not null)
            Assert.Equal(B.Length, c.Length);

        var p = new Problem(c, A, b).EnforcePositivity();
        Assert.True(p.Constraints >= p.Dimension, "Problem must have more constraints than variables");

        var result = solver.Maximize(p, B);
        Assert.NotNull(result);

        Assert.True(result.IsOptimalPoint, "Returned value not recognized as optimal");
        Assert.Equal(0.0, result.Gap, 1.0e-9);

        var expectedValue = p.Eval(expected);
        Assert.Equal(0.0, (result.PrimalValue - expectedValue) / expectedValue, 5.0e-3);
    }

    [Theory]
    [InlineData(data: [
        new double [] { 320.0/39, 268.0/39 },
        new int[] { 4, 5 },

        new double [] {  8.0, 12.0 }, 
        new double [] {  0.7,  1.0, 15.0 },
        new double [] {  2.5,  4.0, 48.0 },
        new double [] {  4.0,  2.5, 50.0 },
        new double [] {  1.5, 1.25, 25.0 },
        new double [] { -1.0,  0.0, -6.0 },
        new double [] {  0.0, -1.0, -6.0 },
    ])]
    [InlineData(data: [
        new double [] { 5000.0/11, 2500.0/11, 5000.0/11 },
        new int[] { 0, 3, 4 },

        new double [] {  4.0,  5.0,  2.0 }, 
        new double [] {  0.0,  0.6,  0.8, 500.0 },
        new double [] { -1.0,  2.0,  0.0,   0.0 },
        new double [] {  1.0,  0.0, -1.0,   0.0 },
    ])]
    [InlineData(data: [
        new double [] { 7, 3, 59.0/12 },
        new int[] { 3, 6, 7 },

        new double [] {  6.0,  20.0, 15.0 }, 
        new double [] { -1.0,   0.0,  0.0, -7.0 },
        new double [] {  0.0,   1.0,  0.0,  3.0 },
        new double [] {  0.2,   0.5,  0.4,  6.0 },
        new double [] {  0.3,  0.65,  0.6,  7.0 },
        new double [] { 0.12,  0.45,  0.2,  7.0 },
    ])]
    [InlineData(data: [
        new double [] { 350.0/23, 1090.0/23 },
        new int[] { 1, 3 },

        new double [] { 250,  300 }, 
        new double [] { 1.9,  1.5, 100.0 },
        new double [] { 0.5,  1.0,  55.0 },
        new double [] { 1.0, -0.5,   0.0 },
    ])]
    [InlineData(data: [
        new double [] { 650.0/29, 1300.0/29, 1800.0/29 },
        new int[] { 1, 5, 6 },

        new double [] { 100.0, 80.0, 60.0 }, 
        new double [] {   6.0,  5.0,  4.0, 1000.0 },
        new double [] {   4.0,  2.0, 10.0,  800.0 },
        new double [] {   4.0,  5.0,  3.0,  500.0 },
        new double [] {   2.0, -1.0,  0.0,    0.0 },
        new double [] {  -0.4,  0.6, -0.4,    0.0 },
    ])]
    [InlineData(data: [
        new double [] { 20.0/21, 3250.0/21, 470.0/21 },
        new int[] { 3, 4, 5 },

        new double [] { 14.0, 20.0, 16.0 }, 
        new double [] {  1.0,  3.0,  2.0, 510.0 },
        new double [] {  1.0,  2.0,  4.0, 400.0 },
        new double [] {  3.0,  1.0,  1.0, 180.0 },
    ])]
    [InlineData(data: [
        new double [] { 1000.0/3, 2000.0/3 },
        new int[] { 0, 4 },

        new double [] { 1200, 1500 }, 
        new double [] {  1.5,  1.5,  1500 },
        new double [] {  0.8,  1.0,  2000 },
        new double [] {  1.0,  2.2,  1800 },
    ])]
    public void PrimalMax(
        double[] expected, 
        int[]? B, 
        double[] c, 
        params double[][] Ab
    ) {
        var solver = new PrimalSimplex();

        // Test both with and without starting feasible basis
        DoTest(solver, expected, B, c, Ab);
        DoTest(solver, expected, null, c, Ab);
    }

    
    [Theory]
    [InlineData(data: [
        new double [] { 320.0/39, 268.0/39 },
        //new int[] { 4, 5 },

        new double [] {  8.0, 12.0 }, 
        new double [] {  0.7,  1.0, 15.0 },
        new double [] {  2.5,  4.0, 48.0 },
        new double [] {  4.0,  2.5, 50.0 },
        new double [] {  1.5, 1.25, 25.0 },
        new double [] { -1.0,  0.0, -6.0 },
        new double [] {  0.0, -1.0, -6.0 },
    ])]
    [InlineData(data: [
        new double [] { 5000.0/11, 2500.0/11, 5000.0/11 },
        //new int[] { 0, 3, 4 },

        new double [] {  4.0,  5.0,  2.0 }, 
        new double [] {  0.0,  0.6,  0.8, 500.0 },
        new double [] { -1.0,  2.0,  0.0,   0.0 },
        new double [] {  1.0,  0.0, -1.0,   0.0 },
    ])]
    [InlineData(data: [
        new double [] { 7, 3, 59.0/12 },
        //new int[] { 3, 6, 7 },

        new double [] {  6.0,  20.0, 15.0 }, 
        new double [] { -1.0,   0.0,  0.0, -7.0 },
        new double [] {  0.0,   1.0,  0.0,  3.0 },
        new double [] {  0.2,   0.5,  0.4,  6.0 },
        new double [] {  0.3,  0.65,  0.6,  7.0 },
        new double [] { 0.12,  0.45,  0.2,  7.0 },
    ])]
    [InlineData(data: [
        new double [] { 350.0/23, 1090.0/23 },
        //new int[] { 1, 3 },

        new double [] { 250,  300 }, 
        new double [] { 1.9,  1.5, 100.0 },
        new double [] { 0.5,  1.0,  55.0 },
        new double [] { 1.0, -0.5,   0.0 },
    ])]
    [InlineData(data: [
        new double [] { 650.0/29, 1300.0/29, 1800.0/29 },
        //new int[] { 1, 5, 6 },

        new double [] { 100.0, 80.0, 60.0 }, 
        new double [] {   6.0,  5.0,  4.0, 1000.0 },
        new double [] {   4.0,  2.0, 10.0,  800.0 },
        new double [] {   4.0,  5.0,  3.0,  500.0 },
        new double [] {   2.0, -1.0,  0.0,    0.0 },
        new double [] {  -0.4,  0.6, -0.4,    0.0 },
    ])]
    [InlineData(data: [
        new double [] { 20.0/21, 3250.0/21, 470.0/21 },
        //new int[] { 3, 4, 5 },

        new double [] { 14.0, 20.0, 16.0 }, 
        new double [] {  1.0,  3.0,  2.0, 510.0 },
        new double [] {  1.0,  2.0,  4.0, 400.0 },
        new double [] {  3.0,  1.0,  1.0, 180.0 },
    ])]
    [InlineData(data: [
        new double [] { 1000.0/3, 2000.0/3 },
        //new int[] { 0, 4 },

        new double [] { 1200, 1500 }, 
        new double [] {  1.5,  1.5,  1500 },
        new double [] {  0.8,  1.0,  2000 },
        new double [] {  1.0,  2.2,  1800 },
    ])]
    public void DualMax(
        double[] expected, 
        //int[]? B, 
        double[] c, 
        params double[][] Ab
    ) {
        var solver = new DualSimplex();
        DoTest(solver, expected, null, c, Ab);
    }

    private static void parseContraints(
        double[][] Ab,
        out double[,] A,
        out double[] b
    ) {
        int rows = Ab.Length;
        int cols = Ab[0].Length - 1;

        A = new double[rows, cols];
        b = new double[rows];

        for (int i = 0; i < rows; i++)
        {
            for (int j = 0; j < cols; j++)
                A[i, j] = Ab[i][j];

            b[i] = Ab[i][cols];
        }
    }
}
