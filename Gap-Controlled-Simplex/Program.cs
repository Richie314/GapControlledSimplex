using Gap_Controlled_Simplex;

var c = new double[] { 2, 1 };
var A = new double[,] {
    {  1,  0 },
    {  1,  1 },
    { -1.0,  0.0 },
    {  0.0, -1.0 },
};
var b = new double[] { 2, 3, 0, 0 };

var problem = new Problem(c, A, b);

void solveAndPrint(ISimplex solver, int[]? B = null)
{
    var solution = solver.Maximize(problem, B);

    if (solution is null)
    {
        Console.WriteLine("Problem is unbounded or infeasible");
        return;
    }

    Console.WriteLine($"x = [{string.Join("; ", solution.x)}]");
    Console.WriteLine($"y = [{string.Join("; ", solution.y)}]");
    Console.WriteLine($"c^T * x = {solution.PrimalValue}");
    Console.WriteLine($"y^T * b = {solution.DualValue}");
    Console.WriteLine($"gap = |V(D) - V(P)| = {solution.Gap}");
}

Console.WriteLine("=== Primal Simplex ===");
solveAndPrint(new PrimalSimplex(), B: [0, 1]);
Console.WriteLine();
Console.WriteLine();

Console.WriteLine("=== Dual Simplex ===");
solveAndPrint(new DualSimplex());