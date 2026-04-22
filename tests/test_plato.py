import pytest
import asyncio
from scripts.downloader import PlatoDownloader
from scripts.mps_parser import MpsParser
from solvers.dual_simplex import DualSimplex

plato_problems = [
    ["Dual2_5000"], ["L2CTA3D"], ["Primal2_1000"], ["a2864"], ["bharat"],
    ["brazil3"], ["chromaticindex1024-7"], ["datt256_lp"], ["dlr1", "dlr2"],
    ["ex10"], ["fhnw-binschedule1"], ["graph40-40"], ["irish-electricity"],
    ["neos-3025225", "neos-5052403-cygnet", "neos-5251015"],
    ["physiciansched3-3"], ["qap15"], ["rmine15"], ["s82", "s100", "s250r10"],
    ["savsched1"], ["scpm1"], ["set-cover-model"], ["square41"],
    ["supportcase10", "supportcase19"], ["thk_48", "thk_63"],
    ["tpl-tub-ws1617"], ["woodlands09"]
]

@pytest.mark.asyncio
@pytest.mark.parametrize("problem_names", plato_problems)
async def test_download_plato(problem_names):
    downloader = PlatoDownloader()
    results = await downloader.download_plato_benchmarks_async(problem_names)
    
    assert len(results) == len(problem_names)
    for problem, filepath in results.items():
        assert filepath is not None

@pytest.mark.parametrize("problem_name", ["ex10"])
def test_solve_plato_problem(problem_name):
    downloader = PlatoDownloader()
    filepath = downloader.get_problem_file(problem_name)
    assert filepath is not None
    
    parser = MpsParser()
    parser.parse_file(filepath)
    problem = parser.to_problem()
    
    solver = DualSimplex()
    result = solver.maximize(problem)
    assert result is not None</content>
<parameter name="filePath">c:\Users\Richie\OneDrive\Documenti\UniPI\Tesi Triennale\tests\test_plato.py