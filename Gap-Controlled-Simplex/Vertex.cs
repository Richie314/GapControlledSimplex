using MathNet.Numerics;
using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class Vertex
{
    public const double AbsoluteTolerance = 1.0e-10;
    public const double RelativeTolerance = 1.0e-9;


    public readonly Problem Problem;

    public readonly int[] Basis;

    public readonly Vector<double> x;

    public readonly Vector<double> y_B;

    public readonly Matrix<double> A_B;

    /// <summary>
    /// W = - A_B^-1
    /// </summary>
    public readonly Matrix<double> W;

    public Vertex(Problem p, IEnumerable<int> B)
    {
        Problem = p;
        Basis = B.OrderBy(i => i).ToArray();

        A_B = getA_B(A, Basis);
        var b_B = Vector<double>.Build.DenseOfIndexed(
            Basis.Length,
            Enumerable
                .Range(0, Basis.Length)
                .Select(i => (i, b[Basis[i]]))
        );

        W = -A_B.Inverse();

        // A_B x = b_B
        x = A_B.Solve(b_B); // x = -W * b_B;

        // y_B = c^T A_B^-1
        // y_B A_B = c^T
        y_B = A_B.Transpose().Solve(Problem.c);
    }

    public Matrix<double> A { get => Problem.A; }

    public Vector<double> b { get => Problem.b; }

    private static Matrix<double> getA_B(Matrix<double> A, int[] Basis)
    {
        int n = A.ColumnCount;

        if (n != Basis.Length)
            throw new InvalidParameterException();

        var A_B = Matrix<double>.Build.Dense(n, n, 0);

        for (int i = 0; i < n; i++)
            A_B.SetRow(i, A.Row(Basis[i]));

        return A_B;
    }

    public IEnumerable<int> NonBasis
    {
        get => Enumerable
            .Range(0, Problem.Constraints)
            .Except(Basis);
    }

    public Vector<double> y
    {
        get => Vector<double>.Build.DenseOfIndexed(
            Problem.Constraints,
            Enumerable
                .Range(0, Problem.Dimension)
                .Select(i => (Basis[i], y_B[i]))
        );
    }


    public Vector<double> primalResiduals()
    {
        Vector<double> r = Problem.b - Problem.A * x;
        r.MapInplace(r_i => Math.Min(0, r_i));
        return r;
    }

    public bool IsPrimalFeasible(
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) => !primalInfeasibleRows(absTol, relTol).Any();

    public IEnumerable<(int index, double slack)> primalInfeasibleRows(
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) {
        double scale = Problem.b.AbsoluteMaximum();
        var slack = primalResiduals();

        return Enumerable
            .Range(0, Problem.Constraints)
            .Select(i => (i, slack: slack[i]))
            .Where(p => Math.Abs(p.slack) > absTol + relTol * scale);
    }

    public bool IsPrimalDegenerate(
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) {
        double scale = Problem.b.AbsoluteMaximum();

        return 
            primalResiduals()
            .Count(r_i => Math.Abs(r_i) <= absTol + relTol * scale)
            > Problem.Dimension;
    }

    public IEnumerable<(int index, double slack)> 
    dualInfeasibleValues(double absTol = AbsoluteTolerance)
        => y_B
            .EnumerateIndexed()
            .Where(p => p.Item2 < -absTol)
            .Select(p => (index: Basis[p.Item1], slack: Math.Abs(p.Item2)));


    public bool IsDualFeasible(double absTol = AbsoluteTolerance) 
        => !dualInfeasibleValues(absTol).Any();

    public bool IsDualDegenerate(double absTol = AbsoluteTolerance) 
        => y_B.Any(y_i => Math.Abs(y_i) < absTol);


    public bool IsOptimalPoint(
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) => 
        IsPrimalFeasible(absTol, relTol) && IsDualFeasible(absTol);


    public double primalValue(
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) {
        if (!IsPrimalFeasible(absTol, relTol))
            throw new InvalidOperationException(
                "Point is not primal feasible, " +
                "hence the primal objective function c^T * x cannot be evaluated."
            );

        return Problem.c * x;
    }

    public double dualValue(double absTol = AbsoluteTolerance)
    {
        if (!IsDualFeasible(absTol))
            throw new InvalidOperationException(
                "Point is not dual feasible, hence the dual objective function b^T * y cannot be evaluated."
            );

        // return Problem.b * y;
        
        // Since y_N = 0, z = b_B * y_B
        return Enumerable
            .Range(0, Problem.Dimension)
            .Sum(i => y_B[i] * b[Basis[i]]);
    }

    public static (double gap, double? relativeGap, double dualValue, double primalValue) 
    Gap(Vertex dualVertex, 
        Vertex primalVertex,
        double absTol = AbsoluteTolerance, 
        double relTol = RelativeTolerance
    ) {
        if (dualVertex.Problem != primalVertex.Problem)
            throw new InvalidOperationException(
                "Given vertices are based on different problems!"
            );

        double dualValue = dualVertex.dualValue(absTol);
        double primalValue = primalVertex.primalValue(absTol, relTol);

        double gap = dualValue - primalValue;
        double? relativeGap = Math.Abs(primalValue) > absTol ? (gap / primalValue) : null;

        return (
            gap,
            relativeGap,
            dualValue,
            primalValue
        );
    }
}