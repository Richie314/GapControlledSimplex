using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public record Solution
{
    public required Vertex Point;

    public Problem Problem { get => Point.Problem; }

    public int[] Basis { get => Point.Basis; }

    public Vector<double> x { get => Point.x; }

    public Vector<double> y { get => Point.y; }


    public required int IterationCount;
    public int InitialIterations = 0;

}