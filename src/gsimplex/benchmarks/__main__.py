#!/usr/bin/env python3

from typing import Optional
import argparse
import asyncio
import sys

from gsimplex.benchmarks.plato import PlatoDownloader
from gsimplex.benchmarks.netlib import NetLibDownloader

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
    parser = argparse.ArgumentParser(description="Download Plato or Netlib benchmarks")
    parser.add_argument('--quiet', action='store_true', help='Run in quiet mode')
    parser.add_argument('--dir', type=str, default=None, help='Directory to save benchmarks')
    parser.add_argument('--plato', type=bool, default=True, help="Download plato benchmarks")
    parser.add_argument('--netlib', type=bool, default=True, help="Download plato benchmarks")
    
    args = parser.parse_args()

    assert args.plato or args.netlib, "You must download at least one of the benchmarks"

    if args.plato:
        esit_plato = asyncio.run(download_plato_benchmarks(quiet=args.quiet, dir=args.dir))
    else:
        esit_plato = True

    
    if args.netlib:
        esit_netlib = asyncio.run(download_netlib_benchmarks(quiet=args.quiet, dir=args.dir))
    else:
        esit_netlib = True

    return 0 if esit_plato and esit_netlib else 1

if __name__ == "__main__":
    sys.exit(main())
