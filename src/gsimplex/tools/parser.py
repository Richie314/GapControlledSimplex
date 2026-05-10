from pulp import LpProblem
from pulp.constants import LpMaximize, LpMinimize
import tempfile
from pathlib import Path
from typing import BinaryIO

from gsimplex.tools.extractor import Extractor

class ProblemParser:

    @staticmethod
    def __load_mps_file(file_path: str|Path, sense: int) -> LpProblem:
        """
        Load an MPS file into an LpProblem object.

        :param file_path: Path to the MPS file.
        :type file_path: str|Path
        :param sense: Optimization sense (minimize or maximize).
        :type sense: int
        :return: The loaded linear programming problem.
        :rtype: LpProblem
        """
        _, problem = LpProblem.fromMPS(str(file_path), sense=sense)
        return problem

    @staticmethod
    def load_mps_from_file(file_path: str|Path, sense: int = LpMinimize) -> LpProblem:
        """
        Load an MPS problem from a file path, handling compressed archives transparently.

        :param file_path: Path to the MPS file or compressed archive.
        :type file_path: str|Path
        :param sense: Optimization sense (minimize or maximize).
        :type sense: int
        :return: The loaded linear programming problem.
        :rtype: LpProblem
        """

        # Raise exception if file does not exist
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # If it's not compressed, we can load it directly
        if not Extractor.is_compressed(file_path):
            return ProblemParser.__load_mps_file(file_path, sense)

        # File must be uncompressed first
        with Extractor.extract_to_stream(file_path) as file_stream:
            return ProblemParser.load_mps_from_stream(file_stream, sense)
        
    @staticmethod
    def load_mps_from_stream(file_stream: BinaryIO, sense: int = LpMinimize) -> LpProblem:
        """
        Load an MPS problem from a binary stream.

        :param file_stream: Stream containing the MPS problem data.
        :type file_stream: BinaryIO
        :param sense: Optimization sense (minimize or maximize).
        :type sense: int
        :return: The loaded linear programming problem.
        :rtype: LpProblem
        """

        # Save stream to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mps") as tmp_file:
            tmp_file.write(file_stream.read())
            tmp_file_path = tmp_file.name
        
        try:
            # Load the problem from the temporary file
            problem = ProblemParser.__load_mps_file(tmp_file_path, sense)
        finally:
            Path(tmp_file_path).unlink()  # Clean up the temporary file
        
        return problem

