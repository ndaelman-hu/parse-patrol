"""
Pipeline for parsing and summarizing key chemical properties from computational chemistry files.
"""

import os
from src.cclib.__main__ import cclib_parse_file_to_model
from src.custom_gaussian.__main__ import gauss_parse_file_to_model
from src.nomad.__main__ import search_nomad_entries, get_nomad_raw_files, get_nomad_archive

def parse_and_summarize(file_paths):
    """
    Parse and summarize key chemical properties from the given files.

    Args:
        file_paths (list): List of file paths to parse.

    Returns:
        dict: Summary of key chemical properties.
    """
    summary = {}

    for file_path in file_paths:
        if file_path.endswith(".log") or file_path.endswith(".out"):
            # Use Gaussian parser
            parsed_data = gauss_parse_file_to_model(file_path)
        elif file_path.endswith(".chk") or file_path.endswith(".gjf"):
            # Use cclib parser
            parsed_data = cclib_parse_file_to_model(file_path)
        else:
            # Use NOMAD tools for other file types
            entry_id = search_nomad_entries(formula="", program_name="", start=1, end=1)[0].entry_id
            raw_files_path = get_nomad_raw_files(entry_id)
            parsed_data = get_nomad_archive(entry_id)

        # Summarize key properties
        summary[file_path] = {
            "Molecular Geometry": parsed_data.get("atomcoords", "N/A"),
            "SCF Energies": parsed_data.get("scfenergies", "N/A"),
            "Vibrational Frequencies": parsed_data.get("vibfreqs", "N/A"),
            "Thermochemistry": {
                "ZPVE": parsed_data.get("zpve", "N/A"),
                "Thermal Energies": parsed_data.get("sum_electronic_and_thermal_energies", "N/A"),
                "Free Energies": parsed_data.get("sum_electronic_and_thermal_free_energies", "N/A"),
            },
        }

    return summary

if __name__ == "__main__":
    # Example usage
    test_files = [
        "test_files/gaussian/FREQUENCY.LOG",
        "test_files/gaussian/frequency.chk",
        "test_files/gaussian/frequency.gjf",
    ]
    results = parse_and_summarize(test_files)
    for file, data in results.items():
        print(f"Summary for {file}:")
        for key, value in data.items():
            print(f"  {key}: {value}")
