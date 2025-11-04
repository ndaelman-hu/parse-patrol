"""
Integration tests for the NOMAD database interface.

Tests the NOMAD search and download functionality without testing parsers.
Parsers should be tested separately in their own unit tests.
"""

import pytest
import shutil
from pathlib import Path
import sys
import os

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class TestNOMADInterface:
    """Test suite for NOMAD database interface functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_test_data_dir(self, tmp_path):
        """Setup temporary directory for test downloads."""
        self.test_data_dir = tmp_path / "test_data"
        self.test_data_dir.mkdir()
    
    @pytest.mark.integration
    @pytest.mark.parametrize("search_params,expected_behavior", [
        # Basic search
        (
            {"formula": "H2O", "start": 1, "end": 3},
            {"max_results": 3, "validate_entry": True}
        ),
        # Program filter
        (
            {"program_name": "Gaussian", "formula": "H2O", "start": 1, "end": 2},
            {"max_results": 2, "validate_program": "Gaussian"}
        ),
        # Date filter
        (
            {"formula": "H2O", "date_from": "2023-01-01", "date_to": "2024-12-31", "start": 1, "end": 2},
            {"max_results": 2, "validate_entry": True}
        ),
        (
            {"formula": "UnlikelyFormula123", "program_name": "NonexistentProgram", "start": 1, "end": 3},
            {"max_results": 3, "validate_no_match": True}
        ),
        # Formula type testing
        (
            {"formula": "H2O", "formula_type": "reduced", "start": 1, "end": 2},
            {"max_results": 2, "validate_entry": True, "formula_type": "reduced"}
        ),
        (
            {"formula": "H2O", "formula_type": "hill", "start": 1, "end": 2},
            {"max_results": 2, "validate_entry": True, "formula_type": "hill"}
        ),
    ])
    def test_nomad_search_functionality(self, search_params: dict, expected_behavior: dict):
        """Test NOMAD search with various parameters and filters."""
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries, FormulaType
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        # Convert string formula_type to enum if present
        if "formula_type" in search_params:
            formula_type_str = search_params["formula_type"]
            search_params["formula_type"] = FormulaType(f"chemical_formula_{formula_type_str}")
        
        entries = nomad_search_entries(**search_params)
        
        # Basic validation
        assert isinstance(entries, list)
        assert len(entries) <= expected_behavior["max_results"]
        
        # Validate entries if found
        if expected_behavior.get("validate_entry", False):
            if entries:
                entry = entries[0]
                assert hasattr(entry, 'entry_id')
                assert hasattr(entry, 'formula')
                assert hasattr(entry, 'formula_type')
                assert entry.entry_id is not None
                
                # Validate formula_type field matches expected type
                if "formula_type" in expected_behavior:
                    expected_type = expected_behavior["formula_type"]
                    assert entry.formula_type.name == expected_type
                    
            if (program := expected_behavior.get("validate_program")):
                for entry in entries:
                    if entry.program_name:
                        assert program in entry.program_name
        elif expected_behavior.get("validate_no_match", False):
            # For unlikely formulas, we expect either no results or results that don't match
            for entry in entries:
                if entry.formula:
                    assert "UnlikelyFormula123" not in entry.formula
                if entry.program_name:
                    assert "NonexistentProgram" not in entry.program_name
    
    @pytest.mark.parametrize("entry_id", [
        "ak2gQ6tnIAe9GIOPlYaZBKPI7AZW",
    ])
    @pytest.mark.integration
    @pytest.mark.slow
    def test_nomad_download_functionality(self, entry_id):
        """Test NOMAD file download functionality."""
        try:
            from parse_patrol.databases.nomad.utils import nomad_get_raw_files
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        try:
            # Test download with custom data root
            download_path = nomad_get_raw_files(entry_id, data_root=str(self.test_data_dir))
            
            # Verify download path exists
            assert Path(download_path).exists()
            assert entry_id in download_path
            
            # Verify some files were downloaded
            download_dir = Path(download_path)
            files = list(download_dir.rglob("*"))
            assert len(files) > 0
            
        finally:
            # Cleanup
            if hasattr(self, 'test_data_dir') and self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir)
    
    @pytest.mark.parametrize("formula_type_name", [
        "reduced",
        "hill", 
        "anonymous",
        "descriptive"
    ])
    @pytest.mark.integration
    def test_formula_type_field_validation(self, formula_type_name: str):
        """Test that NOMADEntry.formula_type field is correctly populated."""
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries, FormulaType
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        # Test that all formula types are valid enum values
        formula_type = FormulaType(f"chemical_formula_{formula_type_name}")
        assert formula_type.name == formula_type_name
        
        # Test search with each formula type
        entries = nomad_search_entries(
            formula="H2O",
            formula_type=formula_type,
            start=1,
            end=2
        )
        
        # Basic validation - should be able to search with any formula type
        assert isinstance(entries, list)
        assert len(entries) <= 2
        
        # Validate formula_type field is correctly set in returned entries
        for entry in entries:
            assert hasattr(entry, 'formula_type')
            assert entry.formula_type == formula_type
            assert entry.formula_type.name == formula_type_name
    
    @pytest.mark.parametrize("start, end, reference", [
        (1, 10, True),  # Valid range
        (5, 5, True),  # Edge case: start == end
        (10, 5, False),  # Invalid range: end < start
    ])
    def test_entry_range_model(self, start: int, end: int, reference: bool):
        """Test EntryRange model validation."""
        from parse_patrol.databases.nomad.utils import EntryRange
        
        # Test valid range
        if reference:
            range_obj = EntryRange(start=start, end=end)
            assert range_obj.limit == end - start + 1
        else:
            with pytest.raises(ValueError):
                EntryRange(start=start, end=end)
    
    @pytest.mark.parametrize("date, reference", [
        ("2024-01-01", True),
        ("01/01/2024 10:30", True),
        ("2024-01-01T10:30:00", True),
        ("invalid-date", False),
    ])
    def test_date_parsing_utility(self, date: str, reference: bool):
        """Test date parsing utility functions."""
        from parse_patrol.databases.nomad.utils import _parse_date_to_timestamp
        
        # Test various date formats
        timestamp = _parse_date_to_timestamp(date)
        if reference:
            assert timestamp is not None
            assert isinstance(timestamp, int)
        else:
            assert timestamp is None

    @pytest.mark.parametrize("start, end", [(1, 2)])
    @pytest.mark.integration
    def test_nomad_search_pagination(self, start: int, end: int):
        """Test NOMAD search pagination parameters."""
        try:
            from parse_patrol.databases.nomad.utils import nomad_search_entries
        except ImportError:
            pytest.skip("NOMAD dependencies not available")
        
        entries_page1 = nomad_search_entries(
            formula="H2O",
            start=start,
            end=end
        )
        
        entries_page2 = nomad_search_entries(
            formula="H2O", 
            start=end + 1,
            end=2 * end
        )
        
        if len(entries_page1) > 0 and len(entries_page2) > 0:
            assert entries_page1[0].entry_id != entries_page2[0].entry_id
