using MathNet.Numerics.LinearAlgebra;

namespace Gap_Controlled_Simplex.Solvers;

public class PrimalSimplex : IterativeSolver, ISimplex
{
    public static Vertex? Iteration(Vertex v)
    {
        if (!v.IsPrimalFeasible())
            return null;

        // Leaving index (Bland rule)
        var (h, dualSlack) = v
            .dualInfeasibleValues()
            .FirstOrDefault(defaultValue: (-1, 0.0));
        if (h == -1)
            return v; // y_b >= 0. Optimal value

        // Wh is the h-th column of -A_B^-1
        var Wh = v.W.Column(v.Basis.IndexOf(h));

        // Entering index (Bland rule)
        var (k, enteringDen) = v
            .NonBasis
            .Select(i => (i, den: v.A.Row(i) * Wh ))
            .Where(p => p.den > Vertex.AbsoluteTolerance)
            .OrderBy(p => (v.b[p.i] - v.A.Row(p.i) * v.x) / p.den)
            .FirstOrDefault(defaultValue: (-1, 0.0));

        if (k == -1)
            return null; // Unbounded problem

        var newBasis = v.Basis
            .Except([h])
            .Append(k);
        return new Vertex(v.Problem, newBasis);
    }

    public override (Vertex?, int) GetStartingPoint(in Problem p, int[]? StartBasis = null)
    {
        if (StartBasis is not null)
            return (new(p, StartBasis), 0);

        var auxiliaryPoint = GetFeasibleVertex(p);
        if (auxiliaryPoint is null)
            return (null, 0);
        return auxiliaryPoint.Value;
    }

    public override Solution? Maximize(in Problem p, int[]? StartBasis = null)
    {
        var (current, initialIterations) = GetStartingPoint(p, StartBasis);

        for (int iterations = 0; 
             current is not null && checkIterationCount(iterations); 
             current = Iteration(current), iterations++
        ) {
            if (current.IsOptimalPoint())
            {
                return new Solution()
                {
                    Point = current,
                    IterationCount = iterations,
                    InitialIterations = initialIterations
                };
            }
        }

        // Unsolvable or unbounded problem
        return null;
    }

    public Vertex? MakeFeasible(in Vertex w)
    {
        Vertex v = w;
        while (!v.IsPrimalFeasible())
        {
            // Entering index (Largest infeasibility)
            var (k, primalSlack) = v
                .primalInfeasibleRows()
                .MinBy(row => row.slack);

            // Direction
            var Ak = v.A.Row(k);

            // Leaving index (Bland rule)
            int h = v
                .Basis
                .FirstOrDefault(
                    i => Ak * v.W.Column(v.Basis.IndexOf(i)) < 0.0, 
                    -1
                );
            if (h == -1)
                return null;

            var newBasis = v.Basis
                .Except([h])
                .Append(k);

            v = new Vertex(v.Problem, newBasis);
        }

        return v;
    }

    public (Vertex v, int iterations)? GetFeasibleVertex(in Problem p)
    {
        int n = p.Dimension, 
            m = p.Constraints;

        var A = p.A;
        var b = p.b;

        var initialRandomBasis = Enumerable.Range(0, n).ToArray();
        var initialVertex = new Vertex(p, initialRandomBasis);

        if (initialVertex.IsPrimalFeasible())
            return (initialVertex, 0);

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
            m + additionalVariables, 
            n + additionalVariables, 
            (i, j) =>
            {
                if (i < m && j < n)
                    return A[i, j];
                
                if (i >= m && j >= n)
                    if (i - m == j - n)
                        return -1.0;

                if (V.Contains(i) && j >= n)
                    if (V.IndexOf(i) == j - n)
                        return -1.0;
                
                return 0.0;
            }
        );
        var auxVector = Vector<double>.Build.Dense(
            p.Constraints + additionalVariables, 
            i => i < m ? b[i] : 0.0
        ); 
        var auxCost = Vector<double>.Build.Dense(
            p.Dimension + additionalVariables, 
            i => i >= n ? -1.0 : 0.0
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
            !auxSolution.Point.IsOptimalPoint() || 
            auxSolution.Point.primalValue() < 0.0
        ) // Check if the simplex failed for the aux problem
            return null;

        var newVertex = new Vertex(p, auxSolution.Basis.Take(p.Dimension).ToArray());
        if (!newVertex.IsPrimalFeasible())
            throw new DataMisalignedException(
                "The auxiliary problem should have returned a primal feasible vertex " +
                "for the original problem"
            );
        return (newVertex, auxSolution.IterationCount);
    }
}