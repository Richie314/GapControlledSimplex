import tempfile
import asyncio
import zipfile
import aiofiles
import json
from pathlib import Path
from typing import Union

from gsimplex.benchmarks.downloader import Downloader


class MipLibDownloader(Downloader):
    COLLECTION_URL = "https://miplib.zib.de/downloads/collection.zip"
    SOLUTIONS_URL =  "https://miplib.zib.de/downloads/miplib2017-v36.solu"
    
    async def download_miplib_benchmarks_async(self) -> None:
        """
        Asynchronously download and extract the MIPLIB benchmark collection.
        """

        miplib_dir = self._benchmark_dir / "miplib"
        miplib_dir.mkdir(exist_ok=True, parents=True)

        with tempfile.NamedTemporaryFile(suffix="_miplib_collection.zip", delete=False) as tmp:
            tmp_path = tmp.name
    
        try:
            await self.download_solutions()
            
            result = await self.download_async(self.COLLECTION_URL, tmp_path, cached_filename="collection.zip")
            assert result is not None, "Problem collection zip file download failed"
            file = Path(result[0])
            print("Saved collection", file)

            # Extraction is CPU-bound / I-O bound but not async-friendly,
            # so we run it in a thread pool to keep the event loop responsive.
            loop = asyncio.get_running_loop()
            zip_esit = await loop.run_in_executor(None, self._extract_collection, file, miplib_dir, self._quiet)
    
            if not self._quiet:
                if zip_esit:
                    print("Extraction complete.")
                else:
                    print("Extraction failed.")
            
            if not zip_esit:
                return
            
        except Exception as e:
            if not self._quiet:
                print(e)
        finally:
            tmp_path = Path(tmp_path)
            if tmp_path.exists():
                tmp_path.unlink()

                if not self._quiet:
                    print(f"✓ Temp file deleted: {tmp_path}")

    @staticmethod
    def _extract_collection(tmp_path: Union[Path, str], dest_dir: Path, quiet: bool = False) -> bool:
        """
        Extract the MIPLIB collection zip file to the destination directory.

        :param tmp_path: Path to the zip file.
        :type tmp_path: Union[Path, str]
        :param dest_dir: Destination directory for extraction.
        :type dest_dir: Path
        :param quiet: If True, suppress progress messages.
        :type quiet: bool
        :return: True if extraction succeeded, False otherwise.
        :rtype: bool
        """
        
        if not quiet:
            print(f"Extracting to: {dest_dir}")

        tmp_path = Path(tmp_path)

        try:
            assert tmp_path.exists()

            with zipfile.ZipFile(tmp_path, "r") as zf:
                members = zf.infolist()
                total = len(members)
                for i, member in enumerate(members, 1):
                    zf.extract(member, dest_dir)
                    
                    if not quiet:
                        print(f"\r  Extracted {i}/{total} files", end="", flush=True)
            if not quiet:
                print()
            return True
        except Exception as e:
            if not quiet:
                print(e)
            return False
        
    async def download_solutions(self) -> bool:
        """
        Download and parse the MIPLIB solutions file.

        :return: True if download and parsing succeeded, False otherwise.
        :rtype: bool
        """
        miplib_dir = self._benchmark_dir / "miplib"
        soltions_file = miplib_dir / 'solutions.solu'
        otuput_file = miplib_dir / 'solutions.json'

        result = await self.download_async(self.SOLUTIONS_URL, str(soltions_file), cached_filename="miplib/solutions.json")
        if result is None:
            return False
        
        try:
            async with aiofiles.open(result[0], 'r') as f:
                content = await f.read()
                opt = self.parse_solu(content)

            json_str = json.dumps(opt)
            async with aiofiles.open(otuput_file, 'w') as f:
                otuput_file.write_text(json_str)

            return True
        except:
            return False

    @staticmethod
    def parse_solu(content: str) -> dict[str, float]:
        """
        Parse the MIPLIB solutions file content into a dictionary.

        :param content: The content of the solutions file.
        :type content: str
        :return: A dictionary mapping problem names to optimal values.
        :rtype: dict[str, float]
        """
        optimal: dict[str, float] = {}
    
        for line in content.splitlines():
            line = line.strip()
            if not line or not line.startswith("=opt="):
                continue
    
            parts = line.split()
            # parts[0] == "=opt=", parts[1] == problem name, parts[2] == value
            if len(parts) < 3:
                continue
    
            _, name, raw_value = parts[0], parts[1], parts[2]
            try:
                value = float(raw_value)
            except ValueError:
                continue
    
            optimal[name] = value
    
        return optimal