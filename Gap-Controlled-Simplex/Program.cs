using Gap_Controlled_Simplex;

var problem = new Problem(
    [ 4.0,  5.0,  2.0], 
    [ 0.0,  0.6,  0.8, 500.0],
    [-1.0,  2.0,  0.0,   0.0],
    [ 1.0,  0.0, -1.0,   0.0]
).EnforcePositivity();

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

    if (!solution.IsPrimalFeasible())
        Console.WriteLine("Warning: solution is not primal feasible");
    else
        Console.WriteLine($"c^T * x = {solution.PrimalValue}");

    if (!solution.IsDualFeasible())
        Console.WriteLine("Warning: solution is not dual feasible");
    else
        Console.WriteLine($"y^T * b = {solution.DualValue}");
}


Console.WriteLine("=== Primal Simplex ===");
solveAndPrint(new PrimalSimplex(), B: [0, 3, 4]);
Console.WriteLine();
Console.WriteLine();

Console.WriteLine("=== Dual Simplex ===");
solveAndPrint(new DualSimplex());
Console.WriteLine();
Console.WriteLine();


Console.WriteLine("=== Gap-Controlled Simplex ===");
solveAndPrint(new GapSimplex(), B: [0, 3, 4]);
