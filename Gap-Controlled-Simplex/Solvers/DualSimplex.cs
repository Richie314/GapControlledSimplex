using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex.Solvers;

public class DualSimplex : ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsDualFeasible())
            return null;
        
        if (v.IsPrimalFeasible()) // Ax <= b
        {
            // Optimal value
            return v;
        }

        // Entering index
        int k = v.NonBasis.First(i => v.b[i] < v.A.Row(i) * v.x);
        var Ak = v.A.Row(k);
        
        // Leaving index
        int h = int.MaxValue;
        double t = double.PositiveInfinity;
        foreach (int i in v.Basis)
        {
            var Ak_Wi = Ak * v.W.Column(v.Basis.IndexOf(i));
            if (Ak_Wi >= 0.0)
                continue;

            var t_i = -v.y[i] / Ak_Wi;
            
            if (t_i < t)
            {
                t = t_i;
                h = i;
            }
        }

        if (h == int.MaxValue)
        {
            // Unbounded problem
            return null;
        }

        var newBasis = v.Basis
            .Where(i => i != h)
            .Append(k);
        return new Vertex(v.Problem, newBasis);
    }


    public Vertex? Maximize(Problem p, int[]? StartBasis = null)
    {
        Vertex? current = 
            StartBasis is not null ? 
            new(p, StartBasis) : 
            GetFeasibleVertex(p);

        for (; current is not null; current = Iteration(current))
        {
            if (current.IsOptimalPoint())
                return current;
        }

        return null;
    }

    public Vertex? MakeFeasible(Vertex v)
    {
        int n = v.Problem.Dimension;

        while (!v.IsDualFeasible())
        {
            var p = v
                .dualInfeasibleValues()
                .First();

            var eP = Vector<double>.Build.Dense(n);
            eP[v.Basis.IndexOf(p.index)] = 1.0;
            var d = v.A_B.LU().Solve(eP);
            
            var q = v
                .NonBasis
                .Select(i => new { i, den = v.A.Row(i) * d })
                .Where(p => p.den <= -Vertex.AbsoluteTolerance)
                .OrderBy(p => Math.Abs(v.b[p.i] - v.A.Row(p.i).DotProduct(d)) / p.den)
                .FirstOrDefault(defaultValue: null);

            if (q is null)
                throw new Exception("Unbounded problem");

            var newBasis = v.Basis
                .Where(i => i != p.index)
                .Append(q.i);

            v = new Vertex(v.Problem, newBasis);
        }
        
        return v;
    }

    public Vertex? GetFeasibleVertex(Problem p) =>
        MakeFeasible(new Vertex(p, Enumerable.Range(0, p.Dimension)));

}