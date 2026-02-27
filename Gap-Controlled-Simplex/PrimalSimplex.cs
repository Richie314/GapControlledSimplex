using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex;

public class PrimalSimplex : ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsPrimalFeasible())
            return null;

        // A_N*x has 0 component => degenerate point

        if (v.IsDualFeasible()) // y_b >= 0
        {
            // Optimal value
            return v;
        }

        var h = v.Basis.First(i => v.y[i] < 0.0);

        // Wh is the h-th column of -A_b_inv
        var Wh = (-1) * 
            v.A_B
            .Inverse()
            .Column(v.Basis.IndexOf(h));

        // Entering index
        int k = int.MaxValue;
        double t = double.PositiveInfinity;
        foreach (int i in v.NonBasis.Where(i => v.A.Row(i) * Wh > 0.0))
        {
            var t_i = (v.b[i] - v.A.Row(i) * v.x) / (v.A.Row(i) * Wh);
            
            if (t_i < t)
            {
                t = t_i;
                k = i;
            }
        }

        if (k == int.MaxValue)
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

        // Unsolvable or unbounded problem
        return null;
    }

    public Vertex? GetFeasibleVertex(Problem p)
    {
        var initialRandomBasis = Enumerable.Range(0, p.Dimension).ToArray();
        var initialVertex = new Vertex(p, initialRandomBasis);

        if (initialVertex.IsPrimalFeasible())
            return initialVertex;

        // Create the auxiliary problem and solve it for a feasible vertex
        // Let's consider an initial B s.t. 
        // A_B x = b_B
        // V = { i in N : A_i x > b_i }
        // U = { i in N : A_i x <= b_i }

        // max -sum { e_i }
        // A_B,U x <= b_B,U
        // A_V   x <= b_V
        // x >= 0, e >= 0

        var rp = initialVertex.primalResiduals();
        var V = initialVertex.NonBasis.Where(i => rp[i] < 0.0).ToArray();

        int additionalVariables = V.Length;

        var auxMatrix = Matrix<double>.Build.Dense(
            p.Constraints + additionalVariables, 
            p.Dimension + additionalVariables, 
            (i, j) =>
            {
                if (i < p.Constraints && j < p.Dimension)
                    return p.A[i, j];
                
                if (i >= p.Constraints && j >= p.Dimension)
                    if (i - p.Constraints == j - p.Dimension)
                        return -1.0;

                if (V.Contains(i) && j >= p.Dimension)
                    if (V.IndexOf(i) == j - p.Dimension)
                        return -1.0;
                
                return 0.0;
            }
        );
        var auxVector = Vector<double>.Build.Dense(
            p.Constraints + additionalVariables, 
            i => i < p.Constraints ? p.b[i] : 0.0
        ); 
        var auxCost = Vector<double>.Build.Dense(
            p.Dimension + additionalVariables, 
            i => i >= p.Dimension ? -1.0 : 0.0
        );

        var auxProblem = new Problem(auxCost, auxMatrix, auxVector);

        // Now let's solve the aux problem, for which we already have a feasible vertex:
        // the one with basis B U V, which corresponds to the matrix
        // A_B,V = [ A_B 0; A_V -I ]
        // and the vector b_B,V = [ b_B; b_V ]

        // If this custom crafted problem has no solution or a negative value,
        // then the original problem is infeasible.
        // Otherwise, we can extract a feasible (not optimal) vertex for the original problem

        var auxSolution = Maximize(
            auxProblem, 
            initialVertex.Basis.Concat(V).ToArray()
        );
        if (auxSolution is null || 
            !auxSolution.IsOptimalPoint() || 
            auxSolution.PrimalValue < 0.0
        ) // Check if the simplex failed for the aux problem
            return null;

        var newVertex = new Vertex(p, auxSolution.Basis.Take(p.Dimension).ToArray());
        if (!newVertex.IsPrimalFeasible())
            throw new DataMisalignedException(
                "The auxiliary problem should have returned a primal feasible vertex " +
                "for the original problem"
            );
        return newVertex;
    }
}