import bz2
import gzip
import zipfile
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

class Extractor:
    @staticmethod
    def is_compressed(filepath: str|Path) -> bool:
        path = Path(filepath)
        return path.suffix.lower() in ['.bz2', '.gz', '.zip']
    
    @staticmethod
    def extract_to_stream(filepath: str|Path) -> BinaryIO:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        
        with open(filepath, 'rb') as f:
            if suffix == '.bz2':
                return BytesIO(bz2.decompress(f.read()))
            elif suffix == '.gz':
                return BytesIO(gzip.decompress(f.read()))
            elif suffix == '.zip':
                # For simplicity, assume single file in zip
                with zipfile.ZipFile(f) as zf:
                    names = zf.namelist()
                    if names:
                        return BytesIO(zf.read(names[0]))
                    else:
                        raise ValueError("Empty zip file")
            
            # Not compressed, return file stream
            return open(filepath, 'rb')