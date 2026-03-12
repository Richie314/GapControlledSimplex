namespace Gap_Controlled_Simplex.Solvers;

public interface ISimplex : ISolver
{
    public (Vertex v, int iterations)? GetFeasibleVertex(in Problem p);
    public Vertex? MakeFeasible(in Vertex v);
}