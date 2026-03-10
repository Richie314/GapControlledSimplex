namespace Gap_Controlled_Simplex.Solvers;

public interface ISimplex : ISolver
{
    public Vertex? GetFeasibleVertex(Problem p);
    public Vertex? MakeFeasible(Vertex v);
}