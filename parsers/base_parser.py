from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any


class BaseCSVParser(ABC):
    """Abstract base class that all CSV parsers must inherit from.

    Ensures consistent error handling and output structure across all data
    vendors.
    """

    def __init__(self, file_path_or_buffer):
        self.file_input = file_path_or_buffer
        self.df = None

    def load_csv(self) -> bool:
        """Loads the uploaded CSV into a pandas DataFrame."""
        try:
            # Handle potential encoding variances (UTF-8, UTF-16, Latin-1)
            try:
                self.df = pd.read_csv(self.file_input, encoding="utf-8")
            except UnicodeDecodeError:
                self.df = pd.read_csv(self.file_input, encoding="latin1")

            # Clean column names (lowercase, strip whitespace)
            self.df.columns = self.df.columns.str.strip().str.lower()
            return True
        except Exception as e:
            print(f"Error loading CSV: {str(e)}")
            return False

    @abstractmethod
    def parse(self) -> Dict[str, Any]:
        """Must be implemented by each specific vendor parser.

        Should return a standardized dictionary matching the audit schema.
        """
        pass
