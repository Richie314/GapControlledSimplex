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
            throw new InvalidParameterException();

        if (A.RowCount != b.Count)
            throw new InvalidParameterException();
    }

    public Problem(double[] c, double[,] A, double[] b) :
        this(
            Vector<double>.Build.DenseOfArray(c),
            Matrix<double>.Build.DenseOfArray(A),
            Vector<double>.Build.DenseOfArray(b)
        ) { }

    public Problem(double[] c, params double[][] Ab) :
        this(
            Vector<double>.Build.DenseOfArray(c),
            Matrix<double>.Build.DenseOfRows(Ab.Select(row => row.Take(row.Length - 1))),
            Vector<double>.Build.DenseOfArray(Ab.Select(row => row.Last()).ToArray())
        ) { }

    public Problem EnforcePositivity()
    {
        var I = Matrix<double>.Build.DenseIdentity(Dimension);
        var newB = Vector<double>.Build.Dense(Constraints + Dimension, 0.0);
        newB.SetSubVector(0, Constraints, b);
        
        return new Problem(
            c, 
            A.Stack(-1.0 * I), 
            newB
        );
    }
}
