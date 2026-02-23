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

var solution = DualSimplex.Maximize(problem);

if (solution is null)
    Console.WriteLine("null");
else
{
    Console.WriteLine($"c*x = {solution.PrimalValue}");
    Console.WriteLine($"x = [{string.Join("; ", solution.x)}]");
    Console.WriteLine($"y = [{string.Join("; ", solution.y)}]");
    Console.WriteLine($"gap = {solution.Gap}");
}