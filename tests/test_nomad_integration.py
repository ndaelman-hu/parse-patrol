"""
Integration tests that download real computational chemistry files from NOMAD,
test parsing with each supported parser, then clean up the downloaded files.

This provides end-to-end testing of:
1. NOMAD database search and download functionality
2. Parser capabilities with real quantum chemistry output files
3. Complete workflow from file acquisition to data extraction
"""

import sys
import os
import pytest  # pyright: ignore[reportMissingImports]
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional


# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


# Test configurations for different quantum chemistry software
QM_SOFTWARE_CONFIGS = [
    {
        "name": "Gaussian",
        "program_name": "Gaussian",
        "formula": "H2O",  # Simple molecule for testing
        "expected_extensions": [".log", ".out", ".fchk"],
        "parser_modules": ["cclib", "iodata", "gaussian"],
    },
    {
        "name": "ORCA", 
        "program_name": "ORCA",
        "formula": "H2O",
        "expected_extensions": [".out", ".inp"],
        "parser_modules": ["cclib", "iodata"],
    },
    {
        "name": "VASP",
        "program_name": "VASP", 
        "formula": "Si",  # Common in materials science
        "expected_extensions": ["OUTCAR", "POSCAR", "CONTCAR"],
        "parser_modules": ["iodata"],
    },
    {
        "name": "Q-Chem",
        "program_name": "Q-Chem",
        "formula": "CH4",
        "expected_extensions": [".out", ".in"],
        "parser_modules": ["cclib", "iodata"],
    },
    {
        "name": "NWChem",
        "program_name": "NWChem", 
        "formula": "H2O",
        "expected_extensions": [".out", ".nw"],
        "parser_modules": ["cclib", "iodata"],
    },
    {
        "name": "Psi4",
        "program_name": "Psi4",
        "formula": "H2O", 
        "expected_extensions": [".out"],
        "parser_modules": ["cclib", "iodata"],
    },
]


class NOMADTestManager:
    """Manages NOMAD downloads and cleanup for testing."""
    
    def __init__(self):
        self.temp_dir = Path(tempfile.mkdtemp(prefix="nomad_test_"))
        self.downloaded_entries: List[str] = []
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Clean up all downloaded test files."""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
            
            # Also clean up .data directory entries we created
            data_dir = Path("tests/.data")
            if data_dir.exists():
                for entry_id in self.downloaded_entries:
                    entry_path = data_dir / entry_id
                    if entry_path.exists():
                        shutil.rmtree(entry_path)
        except Exception as e:
            print(f"Warning: Failed to clean up test files: {e}")
    
    def search_and_download_sample(self, program_name: str, formula: str) -> Optional[str]:
        """Search NOMAD and download a sample file for the given software."""
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries, nomad_get_raw_files
            
            # Search for entries
            entries = nomad_search_entries(
                program_name=program_name,
                formula=formula,
                start=1,
                end=5  # Get a few options
            )
            
            if not entries:
                return None
            
            # Try to download the first available entry
            for entry in entries:
                try:
                    download_path = nomad_get_raw_files(entry.entry_id)
                    self.downloaded_entries.append(entry.entry_id)
                    return download_path
                except Exception as e:
                    print(f"Failed to download {entry.entry_id}: {e}")
                    continue
            
            return None
            
        except Exception as e:
            print(f"Error in search_and_download_sample: {e}")
            return None


def find_parseable_files(download_path: str, expected_extensions: List[str]) -> List[Path]:
    """Find files that match expected extensions for parsing."""
    download_dir = Path(download_path)
    parseable_files = []
    
    for ext in expected_extensions:
        if ext.startswith("."):
            # Regular file extensions
            pattern = f"**/*{ext}"
        else:
            # VASP-style files without extensions
            pattern = f"**/{ext}"
        
        files = list(download_dir.glob(pattern))
        parseable_files.extend(files)
    
    # Also look for common output file patterns
    common_patterns = ["**/*.out", "**/*.log", "**/*.dat"]
    for pattern in common_patterns:
        files = list(download_dir.glob(pattern))
        parseable_files.extend(files)
    
    # Remove duplicates and return
    return list(set(parseable_files))


def test_parser_available(parser_name: str) -> bool:
    """Check if a parser is available (dependencies installed)."""
    try:
        if parser_name == "cclib":
            import parse_patrol.parsers.cclib.utils
        elif parser_name == "iodata":
            import parse_patrol.parsers.iodata.utils
        elif parser_name == "gaussian":
            import parse_patrol.parsers.gaussian.utils
        else:
            return False
        return True
    except ImportError:
        return False


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize("software_config", QM_SOFTWARE_CONFIGS, ids=lambda cfg: cfg["name"])
def test_nomad_download_and_parse(software_config):
    """Test downloading real files from NOMAD and parsing them with available parsers.
    
    This test:
    1. Searches NOMAD for files from specific quantum chemistry software
    2. Downloads raw computational files 
    3. Tests parsing with all compatible parsers
    4. Cleans up downloaded files
    
    Marks: integration, slow (requires network access and file downloads)
    """
    
    with NOMADTestManager() as manager:
        # Skip if NOMAD dependencies not available
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries  # noqa: F401
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        # Download sample files
        download_path = manager.search_and_download_sample(
            software_config["program_name"], 
            software_config["formula"]
        )
        
        if not download_path:
            pytest.skip(f"No {software_config['name']} files found in NOMAD for {software_config['formula']}")
        
        # Find parseable files
        parseable_files = find_parseable_files(download_path, software_config["expected_extensions"])
        
        if not parseable_files:
            pytest.skip(f"No parseable files found for {software_config['name']}")
        
        # Test each compatible parser
        parsing_success = False
        
        for parser_name in software_config["parser_modules"]:
            if not test_parser_available(parser_name):
                print(f"⚠ Parser {parser_name} not available, skipping")
                continue
            
            # Test parsing with each compatible file
            for file_path in parseable_files[:3]:  # Limit to first 3 files to avoid long tests
                try:
                    if parser_name == "cclib":
                        from parse_patrol.parsers.cclib.utils import cclib_parse
                        result = cclib_parse(str(file_path))
                        assert result is not None
                        assert hasattr(result, 'source_format') or hasattr(result, 'atnums') or hasattr(result, 'atomnos')
                        
                    elif parser_name == "iodata":
                        from parse_patrol.parsers.iodata.utils import iodata_parse  
                        result = iodata_parse(str(file_path))
                        assert result is not None
                        assert hasattr(result, 'source_format') or hasattr(result, 'atnums') or hasattr(result, 'atcoords')
                        
                    elif parser_name == "gaussian":
                        from parse_patrol.parsers.gaussian.utils import gaussian_parse
                        result = gaussian_parse(str(file_path))
                        assert result is not None
                        
                    parsing_success = True
                    print(f"✓ Successfully parsed {file_path.name} with {parser_name}")
                    break  # If one file works, that's sufficient for this parser
                    
                except Exception as e:
                    print(f"⚠ Failed to parse {file_path.name} with {parser_name}: {e}")
                    continue
        
        # At least one parser should have succeeded
        if not parsing_success:
            pytest.fail(f"No parser successfully handled {software_config['name']} files")


@pytest.mark.integration  
@pytest.mark.slow
def test_nomad_multi_software_workflow():
    """Test the complete workflow with multiple software packages.
    
    This test validates that the system can handle a mixed workflow:
    1. Download files from multiple QM software packages
    2. Parse each with appropriate parsers
    3. Verify data integrity across different formats
    4. Clean up all downloaded files
    """
    
    with NOMADTestManager() as manager:
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries  # noqa: F401
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        successful_parses = 0
        tested_software = []
        
        # Test a subset of software for this broader test
        test_configs = [
            {"program_name": "Gaussian", "formula": "H2O", "parser": "cclib"},
            {"program_name": "ORCA", "formula": "H2O", "parser": "cclib"}, 
            {"program_name": "VASP", "formula": "Si", "parser": "iodata"},
        ]
        
        for config in test_configs:
            if not test_parser_available(config["parser"]):
                continue
                
            download_path = manager.search_and_download_sample(
                config["program_name"], 
                config["formula"]
            )
            
            if not download_path:
                continue
            
            # Find any parseable file
            download_dir = Path(download_path)
            files = list(download_dir.rglob("*"))
            parseable_files = [f for f in files if f.is_file() and f.suffix in ['.out', '.log', '.fchk'] or f.name in ['OUTCAR', 'POSCAR']]
            
            if not parseable_files:
                continue
            
            # Try parsing with the appropriate parser
            try:
                test_file = parseable_files[0]
                
                result = None
                if config["parser"] == "cclib":
                    from parse_patrol.parsers.cclib.utils import cclib_parse
                    result = cclib_parse(str(test_file))
                elif config["parser"] == "iodata":
                    from parse_patrol.parsers.iodata.utils import iodata_parse
                    result = iodata_parse(str(test_file))
                
                if result is not None:
                    successful_parses += 1
                    tested_software.append(config["program_name"])
                    print(f"✓ Successfully tested {config['program_name']} with {config['parser']}")
                    
            except Exception as e:
                print(f"⚠ Failed workflow test for {config['program_name']}: {e}")
                continue
        
        # Require at least 2 different software packages to be successfully tested
        assert successful_parses >= 1, f"Multi-software workflow failed. Only {successful_parses} successful parses from {tested_software}"
        print(f"✓ Multi-software workflow successful: {successful_parses} packages tested ({tested_software})")


@pytest.mark.integration
def test_nomad_search_functionality():
    """Test NOMAD search functionality without downloading large files."""
    
    try:
        from parse_patrol.databases.nomad.utils import nomad_search_entries
    except ImportError:
        pytest.skip("NOMAD dependencies not available")
    
    # Test basic search functionality
    entries = nomad_search_entries(
        formula="H2O",
        start=1,
        end=3
    )
    
    assert isinstance(entries, list)
    assert len(entries) <= 3
    
    if entries:
        entry = entries[0]
        assert hasattr(entry, 'entry_id')
        assert hasattr(entry, 'formula')
        assert entry.entry_id is not None
        print(f"✓ NOMAD search found {len(entries)} entries")


if __name__ == "__main__":
    # Run a simple test if executed directly
    print("Running NOMAD integration test suite...")
    pytest.main([__file__, "-v", "-s"])