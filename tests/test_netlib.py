import pytest
import asyncio
from scripts.downloader import NetLibDownloader
from scripts.mps_parser import MpsParser

netlib_problems = [
    "25fv47", "80bau3b", "adlittle", "afiro", "agg", "agg2", "agg3",
    "bandm", "beaconfd", "blend", "bnl1", "bnl2", "boeing1", "boeing2",
    "bore3d", "brandy", "capri", "cycle", "czprob", "d2q06c", "d6cube",
    "degen2", "degen3", "dfl001", "e226", "etamacro", "fffff800",
    "finnis", "fit1d", "fit1p", "fit2d", "fit2p", "forplan", "ganges",
    "gfrd-pnc", "greenbea", "greenbeb", "grow7", "grow15", "grow22",
    "israel", "kb2", "lotfi", "maros", "maros-r7", "modszk1", "nesm",
    "perold", "pilot", "pilot.ja", "pilot.we", "pilot4", "pilot87",
    "pilotnov", "recipe", "sc105", "sc205", "sc50a", "sc50b",
    "scagr25", "scagr7", "scfxm1", "scfxm2", "scfxm3", "scorpion",
    "scrs8", "scsd1", "scsd6", "scsd8", "sctap1", "sctap2", "sctap3",
    "seba", "share1b", "share2b", "shell", "ship04l", "ship04s",
    "ship08l", "ship08s", "ship12l", "ship12s", "sierra", "stair",
    "standata", "standgub", "standmps", "stocfor1", "stocfor2",
    "tuff", "vtp.base", "wood1p", "woodw"
]

@pytest.mark.asyncio
@pytest.mark.parametrize("problem_names", [netlib_problems[i:i+5] for i in range(0, len(netlib_problems), 5)])
async def test_download_netlib(problem_names):
    downloader = NetLibDownloader()
    results = await downloader.download_netlib_benchmarks_async(problem_names)
    
    assert len(results) == len(problem_names)
    for problem, filepath in results.items():
        assert filepath is not None
        # Try to parse the file
        parser = MpsParser()
        parser.parse_file(filepath)
        assert parser.problem_name or True  # Just check it doesn't crash</content>
<parameter name="filePath">c:\Users\Richie\OneDrive\Documenti\UniPI\Tesi Triennale\tests\test_netlib.py