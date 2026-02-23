using MathNet.Numerics;
using MathNet.Numerics.LinearAlgebra;


namespace Gap_Controlled_Simplex;

public class Problem
{
    /// <summary>
    /// Polyhedron matrix (Ax <= b)
    /// </summary>
    public Matrix<double> A;

    /// <summary>
    /// Polyhedron vector (Ax <= b form)
    /// </summary>
    public Vector<double> b;

    /// <summary>
    /// Linear constraints (max { c^T x } form)
    /// </summary>
    public Vector<double> c;

    public int Dimension
    {
        get => A.ColumnCount;
    }

    public int Constraints
    {
        get => A.RowCount;
    }

    public Problem(Vector<double> c, Matrix<double> A, Vector<double> b)
    {
        this.c = c;
        this.A = A;
        this.b = b;

        if (c.Count != A.ColumnCount)
        {
            throw new InvalidParameterException();
        }

        if (A.RowCount != b.Count)
        {
            throw new InvalidParameterException();
        }
    }

    public Problem(double[] c, double[,] A, double[] b) :
        this(
            Vector<double>.Build.DenseOfArray(c),
            Matrix<double>.Build.DenseOfArray(A),
            Vector<double>.Build.DenseOfArray(b)
        ) { }

    public Problem EnforcePositivity()
    {
        var I = -1 * Matrix<double>.Build.DenseIdentity(Dimension, Dimension);
        var newB = Vector<double>.Build.Dense(Constraints + Dimension, 0.0);
        newB.SetSubVector(0, Constraints, b);
        
        return new Problem(
            c, 
            A.Stack(I), 
            newB
        );
    }

    public double Eval(Vector<double> x)
    {
        return c * x;
    }

    public double Eval(double[] x)
    {
        var v = Vector<double>.Build.DenseOfArray(x);
        return Eval(v);
    }
}
