import requests
import zipfile
from pathlib import Path
from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class NOMADEntry(BaseModel):
    entry_id: str = Field(..., description="NOMAD entry ID")
    upload_id: Optional[str] = Field(None, description="NOMAD upload ID")
    formula: Optional[str] = Field(None, description="Chemical formula")
    program_name: Optional[str] = Field(None, description="Computational program used (VASP, Gaussian, etc.)")
    program_version: Optional[str] = Field(None, description="Version of the computational program")


mcp = FastMCP("NOMAD Central Materials Database")


@mcp.tool()
def search_nomad_entries(
    formula: Optional[str] = None,
    program_name: Optional[str] = None,
    limit: int = 10
) -> List[NOMADEntry]:
    """Search NOMAD database for materials entries.
    
    Args:
        formula: Chemical formula (e.g., "Si2O4", "C6H6")
        program_name: Computational program (e.g., "Gaussian", "ORCA")
        limit: Maximum number of entries to return (default: 10)
    
    Returns:
        List of NOMADEntry objects matching the search criteria
    """
    base_url = "https://nomad-lab.eu/prod/v1/api/v1/entries/query"
    
    # Build query parameters
    query_body = {
        "owner": "visible",
        "query": {},
        "aggregations": {},
        "pagination": {
            "order_by": "upload_create_time",
            "order": "desc",
            "page_size": limit
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


@mcp.resource("nomad://{entry_id}")
def get_nomad_raw_files(entry_id: str) -> str:
    """Download and extract NOMAD raw files to .data directory.
    
    URI format: nomad://entry_id
    
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


if __name__ == "__main__":
    mcp.run()
