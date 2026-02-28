namespace Gap_Controlled_Simplex;

public interface ISimplex : ISolver
{
    public Vertex? GetFeasibleVertex(Problem p);
    public Vertex? MakeFeasible(Vertex v);
}