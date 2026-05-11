from typing import Dict, List, Optional, Tuple

from gsimplex.benchmarks.downloader import Downloader


class PlatoDownloader(Downloader):
    BASE_URL = "https://plato.asu.edu/ftp/lptestset/"
    
    async def download_plato_benchmarks_async(self, problem_names: List[str]) -> Dict[str, str]:
        files: List[Tuple[str, str, str, Optional[str]]] = [
            (f"{self.BASE_URL}{name}.mps.bz2", name, f"plato/{name}.mps.bz2", None)
            for name in problem_names
            if name.strip()
        ]
        return await self.download_many_async(files)
