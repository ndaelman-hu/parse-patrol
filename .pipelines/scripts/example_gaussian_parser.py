import sys
import os

# Dynamically add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from typing import Any, Dict
from src.custom_gaussian.__main__ import gauss_parse_file_to_model

def parse_gaussian_files(directory: str):
    """
    Parse Gaussian files in the specified directory.

    Args:
        directory (str): Path to the directory containing Gaussian files.

    Returns:
        Dict[str, Any]: Parsed data for each file.
    """
    results = {}

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        
        try:
            if filename.endswith(".chk"):
                print(f"Skipping unsupported file: {filename}. Convert to .fchk first.")
                continue

            print(f"Parsing file: {filename}")
            parsed_data = gauss_parse_file_to_model(filepath)
            results[filename] = parsed_data

        except Exception as e:
            print(f"Error parsing file {filename}: {e}")

    return results

if __name__ == "__main__":
    directory = ".pipelines/data/gaussian"
    parsed_results = parse_gaussian_files(directory)

    # Save results to a log file
    with open(".pipelines/scripts/gaussian_parsing_results.log", "w") as log_file:
        for filename, data in parsed_results.items():
            log_file.write(f"File: {filename}\n")
            log_file.write(f"Data: {data}\n\n")

    print("Parsing complete. Results saved to .pipelines/scripts/gaussian_parsing_results.log")
