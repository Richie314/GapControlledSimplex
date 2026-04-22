import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class Downloader:
    def __init__(self, benchmark_dir: Optional[str] = None, quiet: bool = False):
        self._quiet = quiet
        if benchmark_dir is None:
            self._benchmark_dir = Path.cwd() / "benchmark"
        else:
            self._benchmark_dir = Path(benchmark_dir)

    async def download_async(self, url: str, filename: str) -> Optional[str]:
        
        # Make sure the benchmark directory exists
        self._benchmark_dir.mkdir(parents=True, exist_ok=True)
        filepath = self._benchmark_dir / filename
        
        # If already downloaded, return it
        if filepath.exists():
            if not self._quiet:
                print(f"Using cached: {filename}")
            return str(filepath)
        
        if not self._quiet:
            print(f"Downloading: {url}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if not response.ok:
                        if not self._quiet:
                            print(f"Failed to download {filename}: HTTP {response.status}")
                        return None
                    
                    content = await response.read()
                    with open(filepath, 'wb') as f:
                        f.write(content)
                    
                    return str(filepath)
        except Exception as e:
            if not self._quiet:
                print(f"Failed to download {url}: {e}")
            if filepath.exists():
                try:
                    filepath.unlink()
                except:
                    pass
            return None

    async def download_many_async(self, files: List[Tuple[str, str, str]]) -> Dict[str, str]:
        tasks = [self.download_async(url, filename) for url, _, filename in files]
        results = await asyncio.gather(*tasks)
        
        problem_files = {}
        for (url, problem_name, filename), path in zip(files, results):
            if path:
                problem_files[problem_name] = path
        
        return problem_files

