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

    async def download_async(self, 
                             url: str, 
                             filename: str, 
                             cached_filename: Optional[str] = None,
                             ) -> Optional[str]:
        
        # Make sure the benchmark directory exists
        self._benchmark_dir.mkdir(parents=True, exist_ok=True)

        if not cached_filename:
            cached_filename = filename

        filepath = self._benchmark_dir / filename
        cached_filepath = self._benchmark_dir / cached_filename
        
        # If already downloaded, return it
        if cached_filepath.exists():
            if not self._quiet:
                print(f"Using cached: {cached_filename}")
            return str(cached_filepath)
        
        if not self._quiet:
            print(f"Downloading: {url}...")
        filepath.parent.mkdir(parents=True, exist_ok=True)
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

    async def download_many_async(self, 
                                  files: List[Tuple[str, str, str, Optional[str]]], 
                                  post_process=None,
                                  ) -> Dict[str, str]:
        tasks = [self.download_async(url, filename, cached_filename) for url, problem_name, filename, cached_filename in files]
        results = await asyncio.gather(*tasks)
        
        problem_files = {}
        for (url, problem_name, filename, cached_filename), path in zip(files, results):
            if path:
                if post_process is not None:
                    path = post_process(path)
                problem_files[problem_name] = path
        
        return problem_files

