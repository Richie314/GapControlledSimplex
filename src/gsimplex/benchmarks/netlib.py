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
    def post_process_download(netlib_mps_file: str|Path) -> Optional[str]:
        downloaded_file = Path(netlib_mps_file)
        if not downloaded_file.exists():
            raise FileNotFoundError(f"Downloaded file path mismatch: {downloaded_file} not found!")
        
        download_dir = downloaded_file.parent
        target_file = download_dir / downloaded_file.name.removesuffix('.netlib')

        try:
            expand_mps(str(downloaded_file), str(target_file))
            assert target_file.exists()
            return str(target_file)
        except Exception as e:
            print(e)
            return None
        finally:
            downloaded_file.unlink()
