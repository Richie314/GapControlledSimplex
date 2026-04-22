import bz2
import gzip
import zipfile
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from gsimplex.benchmarks.netlib import NetlibMpsExtractor

class Extractor:
    @staticmethod
    def is_compressed(filepath: str) -> bool:
        path = Path(filepath)
        return path.suffix.lower() in ['.bz2', '.gz', '.zip', '.mps.netlib', '.netlib']
    
    @staticmethod
    def extract_to_stream(filepath: str) -> BinaryIO:
        path = Path(filepath)
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
            elif suffix in ['.mps.netlib', '.netlib']:
                
                extractor = NetlibMpsExtractor()
                return extractor.convert(f)
            
            # Not compressed, return file stream
            return open(filepath, 'rb')