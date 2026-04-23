#!/usr/bin/env python3

import asyncio
import sys
import argparse
from typing import Dict, List, Optional, Tuple
from pathlib import Path

from gsimplex.benchmarks.downloader import Downloader
from gsimplex.benchmarks.netlib_emps import expand_mps

class NetLibDownloader(Downloader):
    BASE_URL = "https://www.netlib.org/lp/data/"
    
    async def download_netlib_benchmarks_async(self, problem_names: List[str]) -> Dict[str, str]:
        files: List[Tuple[str, str, str, Optional[str]]] = [
            (f"{self.BASE_URL}{name}", name, f"netlib/{name}.mps.netlib", f"netlib/{name}.mps")
            for name in problem_names
            if name.strip()
        ]
        return await self.download_many_async(files, post_process=NetLibDownloader.post_process_download)
    
    @staticmethod
    def post_process_download(netlib_mps_file: str|Path) -> str:
        downloaded_file = Path(netlib_mps_file)
        if not downloaded_file.exists():
            raise FileNotFoundError(f"Downloaded file path mismatch: {downloaded_file} not found!")
        
        download_dir = downloaded_file.parent
        target_file = download_dir / downloaded_file.name.removesuffix('.netlib')

        expand_mps(str(downloaded_file), str(target_file))
        downloaded_file.unlink()

        assert target_file.exists()
        return str(target_file)
  
async def download_netlib_benchmarks(dir: Optional[str] = None, quiet: bool = False) -> bool:
    downloader = NetLibDownloader(benchmark_dir=dir, quiet=quiet)
    
    # All Netlib problems
    problem_names = [
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
    
    if not quiet:
        print(f"Downloading {len(problem_names)} Netlib problems...")
    results = await downloader.download_netlib_benchmarks_async(problem_names)
    if not quiet:
        print(f"Downloaded {len(results)} problems successfully")

    return len(results) == len(problem_names)

def main():
    parser = argparse.ArgumentParser(description="Download Netlib benchmarks")
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode')
    parser.add_argument('--dir', type=str, default=None, help='Directory to save benchmarks')
    args = parser.parse_args()

    esit = asyncio.run(download_netlib_benchmarks(quiet=args.quiet, dir=args.dir))
    return 0 if esit else 1

if __name__ == "__main__":
    sys.exit(main())