namespace Gap_Controlled_Simplex;

public class CrissCross : ISolver
{
    public Vertex? Maximize(Problem problem, int[]? B = null)
    {
        var allIndices = Enumerable.Range(0, problem.Dimension).ToArray();
        B ??= allIndices;

        while (true)
        {
            var v = new Vertex(problem, B);
            var r_p = v.primalResiduals();
            var r_d = v.dualResiduals();

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

            var dualLeaving = r_d.Find(r_i => r_i != 0.0);
            if (dualLeaving is not null)
            {
                throw new NotImplementedException();
                /*
                int entringRow = ??

                B = B.Where(i => i != dualLeaving.Item1).Append(enteringRow).ToArray();
                continue;
                */
            }

            return v;
        }
    }

}