import pulp as pl
import tempfile
from pathlib import Path
from typing import BinaryIO

from gsimplex.tools.extractor import Extractor

class ProblemParser:

    @staticmethod
    def __load_mps_file(file_path: str|Path) -> pl.LpProblem:
        _, problem = pl.LpProblem.fromMPS(str(file_path))
        return problem

    @staticmethod
    def load_mps_from_file(file_path: str|Path) -> pl.LpProblem:

        # Raise exception if file does not exist
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # If it's not compressed, we can load it directly
        if not Extractor.is_compressed(file_path):
            return ProblemParser.__load_mps_file(file_path)

        # File must be uncompressed first
        with Extractor.extract_to_stream(file_path) as file_stream:
            return ProblemParser.load_mps_from_stream(file_stream)
        
    @staticmethod
    def load_mps_from_stream(file_stream: BinaryIO) -> pl.LpProblem:

        # Save stream to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mps") as tmp_file:
            tmp_file.write(file_stream.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Load the problem from the temporary file
            problem = ProblemParser.__load_mps_file(tmp_file_path)
        finally:
            Path(tmp_file_path).unlink()  # Clean up the temporary file
        
        return problem

