#!/usr/bin/env python3

import asyncio
import sys
import argparse
from typing import Dict, List, Optional

from gsimplex.benchmarks.downloader import Downloader


class PlatoDownloader(Downloader):
    BASE_URL = "https://plato.asu.edu/ftp/lptestset/"
    
    async def download_plato_benchmarks_async(self, problem_names: List[str]) -> Dict[str, str]:
        files = [
            (f"{self.BASE_URL}{name}.mps.bz2", name, f"plato/{name}.mps.bz2")
            for name in problem_names
            if name.strip()
        ]
        return await self.download_many_async(files)
    
    def get_problem_file(self, problem: str) -> Optional[str]:
        path = self._benchmark_dir / "plato" / f"{problem}.mps.bz2"
        if path.exists():
            return str(path)
        return None

async def download_plato_benchmarks(dir: Optional[str] = None, quiet: bool = False) -> bool:
    downloader = PlatoDownloader(benchmark_dir=dir, quiet=quiet)
    
    # All Plato problems (flattened)
    problem_names = [
        "Dual2_5000", "L2CTA3D", "Primal2_1000", "a2864", "bharat",
        "brazil3", "chromaticindex1024-7", "datt256_lp", "dlr1", "dlr2",
        "ex10", "fhnw-binschedule1", "graph40-40", "irish-electricity",
        "neos-3025225", "neos-5052403-cygnet", "neos-5251015",
        "physiciansched3-3", "qap15", "rmine15", "s82", "s100", "s250r10",
        "savsched1", "scpm1", "set-cover-model", "square41",
        "supportcase10", "supportcase19", "thk_48", "thk_63",
        "tpl-tub-ws1617", "woodlands09"
    ]
    
    if not quiet:
        print(f"Downloading {len(problem_names)} Plato problems...")
    results = await downloader.download_plato_benchmarks_async(problem_names)
    if not quiet:
        print(f"Downloaded {len(results)} problems successfully")

    return len(results) == len(problem_names)

def main():
    parser = argparse.ArgumentParser(description="Download Plato benchmarks")
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode')
    parser.add_argument('--dir', type=str, default='benchmark/plato', help='Directory to save benchmarks')
    args = parser.parse_args()

    esit = asyncio.run(download_plato_benchmarks(quiet=args.quiet, dir=args.dir))
    return 0 if esit else 1

if __name__ == "__main__":
    sys.exit(main())