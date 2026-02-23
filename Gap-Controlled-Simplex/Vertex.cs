using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class Vertex
{
    public Problem Problem;

    public readonly int[] Basis;

    public readonly Vector<double> x;

    public readonly Vector<double> y;

    public Vertex(Problem p, IEnumerable<int> B)
    {
        Problem = p;
        Basis = B.OrderBy(i => i).ToArray();

        var A_B = activeConstraintsMatrix();
        var b_B = activeConstraintsVector();

        x = A_B.Inverse() * b_B;

        y = Vector<double>.Build.Dense(p.Constraints, 0);

        // y_B = c^T A_B^-1
        var yb = Problem.c * A_B.Inverse();
        for (int i = 0; i < Basis.Length; i++)
            y[Basis[i]] = yb[i];
    }

    public Matrix<double> activeConstraintsMatrix()
    {
        var A_B = Matrix<double>.Build.Dense(Problem.Dimension, Problem.Dimension, 0);

        for (int i = 0; i < Problem.Dimension; i++)
            A_B.SetRow(i, Problem.A.Row(Basis[i]));

        return A_B;
    }

    public Vector<double> activeConstraintsVector()
    {
        var b_B = Vector<double>.Build.Dense(Problem.Dimension, 0);

        for (int i = 0; i < Problem.Dimension; i++)
            b_B[i] = Problem.b[Basis[i]];

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

    private bool checkPrimalFeasibility(double absTol = 1e-10, double relTol = 1e-9)
    {
        double maxViolation = Math.Abs(primalResiduals().AbsoluteMaximum());
        double scale = Problem.b.AbsoluteMaximum();

        return maxViolation <= absTol + relTol * scale;
    }

    private bool checkDualFeasibility(double absTol = 1e-10, double relTol = 1e-9)
    {
        if (!y.All(y_i => y_i >= 0.0))
            return false;

        double maxViolation = Math.Abs(dualResiduals().AbsoluteMaximum());
        double scale = Problem.c.AbsoluteMaximum();

        return maxViolation <= absTol + relTol * scale;
    }

    public Vector<double> dualResiduals()
    {
        return Problem.c - Problem.A.TransposeThisAndMultiply(y);
    }

    public bool IsPrimalFeasible
    {
        get => checkPrimalFeasibility();
    }
    public bool IsDualFeasible
    {
        get => checkDualFeasibility();
    }

    public bool IsOptimalPoint
    {
        get => IsPrimalFeasible && IsDualFeasible;
    }




    public double PrimalValue
    {
        get => Problem.Eval(x);
    }

    public double DualValue
    {
        get => Problem.b * y;
    }

    public double Gap
    {
        get => Math.Abs(DualValue - PrimalValue);
    }

}