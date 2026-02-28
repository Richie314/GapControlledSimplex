using MathNet.Numerics;
using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class Vertex
{
    public readonly Problem Problem;

    public readonly int[] Basis;

    public readonly Vector<double> x;

    public readonly Vector<double> y;

    public readonly Matrix<double> A_B;

    public readonly Vector<double> b_B;

    /// <summary>
    /// W = - A_B^-1
    /// </summary>
    public readonly Matrix<double> W;

    public Vertex(Problem p, IEnumerable<int> B)
    {
        Problem = p;
        Basis = B.OrderBy(i => i).ToArray();

        A_B = getA_B(A, Basis);
        b_B = getb_B(b, Basis);

        W = -A_B.Inverse();

        // A_B x = b_B
        x = A_B.Solve(b_B); // x = -W * b_B;

        y = Vector<double>.Build.Dense(p.Constraints, 0);

        // y_B = c^T A_B^-1
        // y_B A_B = c^T
        // var yb = Problem.c * A_B.Inverse();
        var yb = A_B.Transpose().Solve(Problem.c);
        for (int i = 0; i < Basis.Length; i++)
            y[Basis[i]] = yb[i];
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

    private static Vector<double> getb_B(Vector<double> b, int[] Basis)
    {
        int n = Basis.Length;

        var b_B = Vector<double>.Build.Dense(n, 0);

        for (int i = 0; i < n; i++)
            b_B[i] = b[Basis[i]];

        return b_B;
    }

    public int[] NonBasis
    {
        get => Enumerable
            .Range(0, Problem.Constraints)
            .Except(Basis)
            .ToArray();
    }

    public Vector<double> primalResiduals()
    {
        Vector<double> r = Problem.b - Problem.A * x;
        r.MapInplace(r_i => Math.Min(0, r_i));
        return r;
    }

    public bool IsPrimalFeasible(
        double absTol = 1e-10, 
        double relTol = 1e-9
    ) {
        double maxViolation = Math.Abs(primalResiduals().AbsoluteMaximum());
        double scale = Problem.b.AbsoluteMaximum();

        return maxViolation <= absTol + relTol * scale;
    }

    public bool IsPrimalDegenerate(
        double absTol = 1e-10, 
        double relTol = 1e-9
    ) {
        double scale = Problem.b.AbsoluteMaximum();

        return 
            primalResiduals()
            .Count(r_i => Math.Abs(r_i) <= absTol + relTol * scale)
            > Problem.Dimension;
    }

    public Vector<double> dualResiduals() =>
        Problem.c - Problem.A.TransposeThisAndMultiply(y);

    public bool IsDualFeasible(
        double absTol = 1e-10, 
        double relTol = 1e-9
    ) {
        if (!y.All(y_i => y_i >= 0.0))
            return false;

        double maxViolation = Math.Abs(dualResiduals().AbsoluteMaximum());
        double scale = Problem.c.AbsoluteMaximum();

        return maxViolation <= absTol + relTol * scale;
    }

    public bool IsDualDegenerate(
        double absTol = 1e-10, 
        double relTol = 1e-9
    ) {
        double scale = Problem.c.AbsoluteMaximum();
        return y
            .Count(y_i => y_i < absTol + relTol * scale)
            > Problem.Dimension;
    }


    public bool IsOptimalPoint(
        double absTol = 1e-10, 
        double relTol = 1e-9
    ) => 
        IsPrimalFeasible(absTol, relTol) && IsDualFeasible(absTol, relTol);


    private double calculatePrimalValue()
    {
        if (!IsPrimalFeasible())
            throw new InvalidOperationException("Vertex is not primal feasible.");
        return Problem.Eval(x);
    }
    public double PrimalValue
    {
        get => calculatePrimalValue();
    }

    private double calculateDualValue()
    {
        if (!IsDualFeasible())
            throw new InvalidOperationException("Vertex is not dual feasible.");
        return Problem.b * y;
    }
    public double DualValue
    {
        get => calculateDualValue();
    }
}