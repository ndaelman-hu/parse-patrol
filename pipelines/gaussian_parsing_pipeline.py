"""
Parsing Pipeline for Gaussian Files

This script defines a modular pipeline for parsing Gaussian files and extracting key chemical properties.
"""

from typing import List, Dict, Any
from mcp.server.fastmcp import FastMCP
from src.cclib.__main__ import cclib_parse_file_to_model  # comment by CE: Agent wants to import modules like this which does not work, will still leave the fil here for now
from src.custom_gaussian.__main__ import gauss_parse_file_to_model
from src.iodata_parser.__main__ import iodata_parse_file_to_model
from src.nomad.__main__ import search_nomad_entries, get_nomad_raw_files, get_nomad_archive

# Define supported file extensions and their corresponding parsers
SUPPORTED_PARSERS = {
    ".log": cclib_parse_file_to_model,
    ".out": cclib_parse_file_to_model,
    ".chk": gauss_parse_file_to_model,
    ".gjf": gauss_parse_file_to_model,
    ".com": gauss_parse_file_to_model,
    ".fchk": gauss_parse_file_to_model,
}

def parse_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a given file and extract key chemical properties.

    Args:
        file_path (str): Path to the file to be parsed.

    Returns:
        Dict[str, Any]: Parsed data as a dictionary.

    Raises:
        ValueError: If the file type is unsupported.
    """
    # Determine the file extension
    file_extension = file_path.split(".")[-1].lower()

    # Check if the file extension is supported
    if file_extension not in SUPPORTED_PARSERS:
        raise ValueError(f"Unsupported file type: {file_extension}")

    # Select the appropriate parser
    parser = SUPPORTED_PARSERS[file_extension]

    # Parse the file
    try:
        parsed_data = parser(file_path)
        return parsed_data.dict()  # Convert Pydantic model to dictionary
    except Exception as e:
        raise RuntimeError(f"Error parsing file {file_path}: {e}")

def summarize_properties(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Summarize key chemical properties from parsed data.

    Args:
        parsed_data (Dict[str, Any]): Parsed data as a dictionary.

    Returns:
        Dict[str, Any]: Summary of key chemical properties.
    """
    summary = {
        "molecular_geometry": parsed_data.get("atomcoords"),
        "energies": parsed_data.get("scfenergies"),
        "vibrational_frequencies": parsed_data.get("vibfreqs"),
        "thermochemistry": parsed_data.get("thermo"),
    }
    return summary

def main(file_paths: List[str]):
    """
    Main function to execute the parsing pipeline.

    Args:
        file_paths (List[str]): List of file paths to be parsed.
    """
    for file_path in file_paths:
        try:
            # Parse the file
            parsed_data = parse_file(file_path)

            # Summarize the properties
            summary = summarize_properties(parsed_data)

            # Print the summary
            print(f"Summary for {file_path}:")
            print(summary)
        except Exception as e:
            print(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    # Example usage
    example_files = [
        "test_files/gaussian/frequency.chk",
        "test_files/gaussian/frequency.gjf",
        "test_files/gaussian/FREQUENCY.LOG",
    ]
    main(example_files)
