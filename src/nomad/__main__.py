import requests
import zipfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class NOMADAction(str, Enum):
    search = "search"
    download = "download"
    search_and_download = "search_and_download"


class EntryRange(BaseModel):
    start: int = Field(..., ge=1, description="Starting entry number (1-based)")
    end: int = Field(..., ge=1, description="Ending entry number (1-based)")
    
    @field_validator('end')
    @classmethod
    def end_must_be_greater_than_start(cls, v, info):
        if info.data.get('start') and v < info.data['start']:
            raise ValueError('end must be greater than or equal to start')
        return v
    
    @property
    def limit(self) -> int:
        return self.end - self.start + 1
    
    @property
    def page_offset(self) -> int:
        return (self.start - 1) // self.limit


class NOMADEntry(BaseModel):
    entry_id: str = Field(..., description="NOMAD entry ID")
    upload_id: Optional[str] = Field(None, description="NOMAD upload ID")
    formula: Optional[str] = Field(None, description="Chemical formula")
    program_name: Optional[str] = Field(None, description="Computational program used (VASP, Gaussian, etc.)")
    program_version: Optional[str] = Field(None, description="Version of the computational program")


def _parse_date_to_timestamp(date_str: str, end_of_day: bool = False) -> Optional[int]:
    """Parse date string to Unix timestamp in milliseconds.
    
    Args:
        date_str: Date string in various formats
        end_of_day: If True and date is date-only, set to end of day (23:59:59)
    
    Returns:
        Unix timestamp in milliseconds, or None if parsing fails
    """
    try:
        # Try "MM/DD/YYYY HH:MM" format first
        parsed_date = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
    except ValueError:
        try:
            # Try ISO format
            parsed_date = datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # Try date only
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                if end_of_day:
                    parsed_date = parsed_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                return None
    
    # Convert to Unix timestamp in milliseconds
    return int(parsed_date.timestamp() * 1000)


mcp = FastMCP("NOMAD Central Materials Database")


@mcp.tool()
def search_nomad_entries(
    formula: Optional[str] = None,
    program_name: Optional[str] = None,
    start: int = 1,
    end: int = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
) -> List[NOMADEntry]:
    """Search NOMAD database for materials entries.
    
    Args:
        formula: Chemical formula (e.g., "Si2O4", "C6H6")
        program_name: Computational program (e.g., "Gaussian", "ORCA")
        start: Starting entry number (1-based, default: 1)
        end: Ending entry number (1-based, default: 10)
        date_from: Start date for upload time filter (ISO format: "2024-01-01")
        date_to: End date for upload time filter (ISO format: "2024-12-31")
    
    Returns:
        List of NOMADEntry objects matching the search criteria
    """
    base_url = "https://nomad-lab.eu/prod/v1/api/v1/entries/query"
    
    # Create entry range from start/end parameters
    entry_range = EntryRange(start=start, end=end)
    
    # Build query parameters
    query_body = {
        "owner": "visible",
        "query": {},
        "aggregations": {},
        "pagination": {
            "order_by": "upload_create_time",
            "order": "desc",
            "page_size": entry_range.limit,
            "page_offset": entry_range.page_offset
        },
        "required": {
            "exclude": [
                "quantities",
                "sections",
                "files"
            ]
        }
    }
    
    # Add search filters
    if formula:
        query_body["query"]["results.material.chemical_formula_reduced:any"] = [formula]
    if program_name:
        query_body["query"]["results.method.simulation.program_name:any"] = [program_name]
    
    # Add date filters - NOMAD expects Unix timestamps in milliseconds
    date_filter = {}
    
    if date_from:
        timestamp_ms = _parse_date_to_timestamp(date_from)
        if timestamp_ms is None:
            raise ValueError(f"Invalid date_from format: '{date_from}'. Supported formats: 'MM/DD/YYYY HH:MM', '2024-01-01T10:30:00', '2024-01-01'")
        date_filter["gte"] = timestamp_ms
    
    if date_to:
        timestamp_ms = _parse_date_to_timestamp(date_to, end_of_day=True)
        if timestamp_ms is None:
            raise ValueError(f"Invalid date_to format: '{date_to}'. Supported formats: 'MM/DD/YYYY HH:MM', '2024-12-31T23:59:59', '2024-12-31'")
        date_filter["lte"] = timestamp_ms
    
    # Add the date filter to query if any dates were provided
    if date_filter:
        query_body["query"]["upload_create_time"] = date_filter
    
    try:
        response = requests.post(base_url, json=query_body, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        entries = []
        for item in data.get("data", []):
            entry = NOMADEntry(
                entry_id=item.get("entry_id", ""),
                upload_id=item.get("upload_id"),
                formula=item.get("results", {}).get("material", {}).get("chemical_formula_reduced"),
                program_name=item.get("results", {}).get("method", {}).get("simulation", {}).get("program_name"),
                program_version=item.get("results", {}).get("method", {}).get("simulation", {}).get("program_version"),
            )
            entries.append(entry)
        
        return entries
        
    except requests.RequestException as e:
        raise Exception(f"Failed to query NOMAD API: {str(e)}")


@mcp.tool()
def get_nomad_raw_files(entry_id: str) -> str:
    """Download and extract NOMAD raw files to .data directory.
    
    Args:
        entry_id: NOMAD entry ID
    
    Returns:
        Path to extracted files directory
    """
    
    # Create entry-specific directory
    data_dir = Path(".data") / entry_id
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if files already downloaded
    if any(data_dir.iterdir()):
        return str(data_dir)
    
    # Download raw files as zip
    url = f"https://nomad-lab.eu/prod/v1/api/v1/entries/{entry_id}/raw"
    zip_path = data_dir / f"{entry_id}_raw.zip"
    
    try:
        response = requests.get(url, timeout=120, stream=True)
        response.raise_for_status()
        
        # Save zip file
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract zip
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        
        # Remove zip file
        zip_path.unlink()
        
        return str(data_dir)
        
    except requests.RequestException as e:
        raise Exception(f"Failed to download NOMAD raw files for {entry_id}: {str(e)}")
    except zipfile.BadZipFile as e:
        raise Exception(f"Failed to extract NOMAD raw files for {entry_id}: {str(e)}")


@mcp.tool()
def get_nomad_archive(entry_id: str, section: Optional[str] = None) -> Dict[str, Any]:
    """Download NOMAD archive data for detailed computational results.
    
    Args:
        entry_id: NOMAD entry ID
        section: Optional section to retrieve (e.g., "run", "workflow", "results")
    
    Returns:
        Archive data as dictionary
    """
    url = f"https://nomad-lab.eu/prod/v1/api/v1/entries/{entry_id}/archive"
    
    params = {}
    if section:
        params["required"] = section
    
    try:
        response = requests.get(url, params=params, timeout=60)
        response.raise_for_status()
        return response.json()
        
    except requests.RequestException as e:
        raise Exception(f"Failed to download NOMAD archive for {entry_id}: {str(e)}")


@mcp.prompt()
def nomad_materials_prompt(
    search_query: str,
    action: NOMADAction = NOMADAction.search,
    max_entries: int = 5
) -> str:
    """Generate a prompt for NOMAD materials database interactions.
    
    Args:
        search_query: Description of materials/compounds to search for
        action: Action to perform (search, download, or search_and_download)
        max_entries: Maximum number of entries to process (default: 5)
    
    Returns:
        Formatted prompt string for NOMAD operations
    """
    
    if action == NOMADAction.search:
        return f"""Search the NOMAD materials database for: {search_query}

Use `search_nomad_entries` with appropriate parameters to find up to {max_entries} relevant computational entries. Focus on:
- Chemical formula matching
- Computational method information  
- Program versions and metadata
- Recent high-quality calculations

Return a list of NOMADEntry objects with detailed metadata."""
    
    elif action == NOMADAction.download:
        return f"""Download raw computational files from NOMAD for: {search_query}

Assuming you have specific entry IDs, use `get_nomad_raw_files` to download the raw computational files to the .data directory. The files will be extracted and ready for parsing with other tools like cclib or custom_gaussian."""
    
    else:  # search_and_download
        return f"""Search and download materials data from NOMAD for: {search_query}

1. First use `search_nomad_entries` to find up to {max_entries} relevant entries
2. Then use `get_nomad_raw_files` to download the raw files for promising entries
3. Files will be available in .data/[entry_id]/ for further analysis
4. Consider using parsing tools (cclib, custom_gaussian) on the downloaded files

This comprehensive workflow provides both metadata and raw computational data for analysis."""


if __name__ == "__main__":
    mcp.run()
