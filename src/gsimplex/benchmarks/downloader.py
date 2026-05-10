import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class Downloader:
    """
    Asynchronous file downloader for benchmark datasets.
    """

    def __init__(self, benchmark_dir: Optional[str] = None, quiet: bool = False):
        """
        Initialize the downloader.

        :param benchmark_dir: Directory where benchmark files are stored.
        :type benchmark_dir: Optional[str]
        :param quiet: If True, suppress download progress output.
        :type quiet: bool
        """
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
        """
        Download a single benchmark file asynchronously.

        :param url: The URL to download from.
        :type url: str
        :param filename: The filename to save in the benchmark directory.
        :type filename: str
        :param cached_filename: Optional cached filename to reuse if the file already exists.
        :type cached_filename: Optional[str]
        :return: The path to the downloaded or cached file, or None on failure.
        :rtype: Optional[str]
        """
        
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
        """
        Download multiple benchmark files asynchronously.

        :param files: A list of tuples (url, problem_name, filename, cached_filename).
        :type files: List[Tuple[str, str, str, Optional[str]]]
        :param post_process: Optional callback to process each downloaded file path.
        :type post_process: Optional[callable]
        :return: A mapping from problem name to downloaded file path.
        :rtype: Dict[str, str]
        """
        tasks = [self.download_async(url, filename, cached_filename) for url, problem_name, filename, cached_filename in files]
        results = await asyncio.gather(*tasks)
        
        problem_files = {}
        for (url, problem_name, filename, cached_filename), path in zip(files, results):
            if path:
                if post_process is not None:
                    path = post_process(path)
                problem_files[problem_name] = path
        
        return problem_files

