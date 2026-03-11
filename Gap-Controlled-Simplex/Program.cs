using Gap_Controlled_Simplex;
using Gap_Controlled_Simplex.Solvers;

var problem = new Problem(
    [ 4.0,  5.0,  2.0], 
    [ 0.0,  0.6,  0.8, 500.0],
    [-1.0,  2.0,  0.0,   0.0],
    [ 1.0,  0.0, -1.0,   0.0]
).EnforcePositivity();

void solveAndPrint(ISolver solver, int[]? B = null)
{
    Solution? solution = null;

    try
    {
        solution = solver.Maximize(problem, B);
    } catch (Exception ex)
    {
        Console.WriteLine(ex.Message);
        if (!string.IsNullOrWhiteSpace(ex.StackTrace))
            Console.WriteLine(ex.StackTrace);
        return;
    }

    if (solution is null)
    {
        Console.WriteLine("Problem is unbounded or infeasible");
        return;
    }

    Console.WriteLine($"x = [{string.Join("; ", solution.x)}]");
    Console.WriteLine($"y = [{string.Join("; ", solution.y)}]");

    try
    {
        Console.WriteLine($"c^T * x = {solution.Point.primalValue()}"); 
    } catch (Exception ex)
    {
        Console.WriteLine(ex.Message);
    }

    try
    {
        Console.WriteLine($"y^T * b = {solution.Point.dualValue()}");
    } catch (Exception ex)
    {
        Console.WriteLine(ex.Message);
    }
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
