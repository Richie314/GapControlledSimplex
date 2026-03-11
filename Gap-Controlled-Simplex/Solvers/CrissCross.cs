namespace Gap_Controlled_Simplex.Solvers;

public class CrissCross : IterativeSolver
{
    public override Solution? Maximize(Problem problem, int[]? B = null)
    {
        var allIndices = Enumerable.Range(0, problem.Dimension).ToArray();
        B ??= allIndices;

        while (true)
        {
            var v = new Vertex(problem, B);
            var r_p = v.primalResiduals();

            var primalLeaving = r_p.Find(r_i => r_i < 0);
            if (primalLeaving is not null)
            {
                throw new NotImplementedException();
                /*
                int enteringRow = ?

                B = B.Where(i => i != primalLeaving.Item1).Append(enteringRow).ToArray();
                continue;
                */
            }


            throw new NotImplementedException();
        }
    }

}