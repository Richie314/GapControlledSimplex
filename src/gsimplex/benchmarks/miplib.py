import tempfile
import asyncio
import zipfile
from pathlib import Path
from typing import Union

from gsimplex.benchmarks.downloader import Downloader


class MipLibDownloader(Downloader):
    COLLECTION_URL = "https://miplib.zib.de/downloads/collection.zip"
    
    async def download_miplib_benchmarks_async(self) -> None:

        miplib_dir = self._benchmark_dir / "miplib"
        miplib_dir.mkdir(exist_ok=True, parents=True)

        with tempfile.NamedTemporaryFile(suffix="_miplib_collection.zip", delete=False) as tmp:
            tmp_path = tmp.name
    
        try:
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
        finally:
            tmp_path = Path(tmp_path)
            if tmp_path.exists():
                tmp_path.unlink()

                if not self._quiet:
                    print(f"✓ Temp file deleted: {tmp_path}")

    @staticmethod
    def _extract_collection(tmp_path: Union[Path, str], dest_dir: Path, quiet: bool = False) -> bool:
        
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