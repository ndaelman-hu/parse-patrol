import asyncio
from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger
from typing import Optional, Dict, List, Any
from .utils import (
    NOMADEntry,
    NOMADAction,
    FormulaType,
    nomad_search_entries,
    nomad_get_raw_files,
    nomad_get_archive,
)

configure_logging()
logger = get_logger(__name__)

mcp = FastMCP("NOMAD Central Materials Database")


@mcp.tool()
async def search_nomad_entries(
    formula: Optional[str] = None,
    formula_type: FormulaType = FormulaType.reduced,
    program_name: Optional[str] = None,
    start: int = 1,
    end: int = 10,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[NOMADEntry]:
    """Search NOMAD database for materials entries.

    Args:
        formula: Chemical formula (e.g., "Si2O4", "C6H6")
        formula_type: Type of chemical formula to search (default: reduced)
        program_name: Computational program (e.g., "Gaussian", "ORCA")
        start: Starting entry number (1-based, default: 1)
        end: Ending entry number (1-based, default: 10)
        date_from: Start date for upload time filter (ISO format: "2024-01-01")
        date_to: End date for upload time filter (ISO format: "2024-12-31")

    Returns:
        List of NOMADEntry objects matching the search criteria
    """
    logger.info(f"Searching NOMAD entries: formula={formula}, formula_type={formula_type.name}, program={program_name}, range={start}-{end}")
    
    try:
        entries = await asyncio.to_thread(
            nomad_search_entries,
            formula=formula,
            formula_type=formula_type,
            program_name=program_name,
            start=start,
            end=end,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(f"Found {len(entries)} NOMAD entries")
        return entries
    except Exception as e:
        logger.error(f"Error searching NOMAD entries: {str(e)}")
        raise



@mcp.tool()
async def get_nomad_raw_files(entry_id: str) -> str:
    """Download and extract NOMAD raw files to .data directory.

    Args:
        entry_id: NOMAD entry ID

    Returns:
        Path to extracted files directory
    """
    logger.info(f"Downloading NOMAD raw files for entry: {entry_id}")
    
    try:
        result_path = await asyncio.to_thread(nomad_get_raw_files, entry_id)
        logger.info(f"Downloaded NOMAD raw files to: {result_path}")
        return result_path
    except Exception as e:
        logger.error(f"Error downloading NOMAD raw files for {entry_id}: {str(e)}")
        raise


@mcp.tool()
async def get_nomad_archive(
    entry_id: str, section: Optional[str] = None
) -> Dict[str, Any]:
    """Download NOMAD archive data for detailed computational results.

    Args:
        entry_id: NOMAD entry ID
        section: Optional section to retrieve (e.g., "run", "workflow", "results")

    Returns:
        Archive data as dictionary
    """
    logger.info(f"Downloading NOMAD archive for entry: {entry_id}, section: {section}")
    
    try:
        archive_data = await asyncio.to_thread(nomad_get_archive, entry_id, section)
        logger.info(f"Downloaded NOMAD archive data for entry: {entry_id}")
        return archive_data
    except Exception as e:
        logger.error(f"Error downloading NOMAD archive for {entry_id}: {str(e)}")
        raise


@mcp.prompt()
async def nomad_materials_prompt(
    search_query: str, action: NOMADAction = NOMADAction.search, max_entries: int = 5
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
        return f"""
        Search the NOMAD materials database for: {search_query}

        Use `search_nomad_entries` with appropriate parameters to find up to {max_entries} relevant computational entries. Focus on:
        - Chemical formula matching (supports reduced, hill, anonymous, descriptive formats)
        - Computational method information  
        - Program versions and metadata
        - Recent high-quality calculations

        Formula type options:
        - reduced (default): simplified chemical formula
        - hill: Hill notation (C, H, then alphabetical)
        - anonymous: anonymized formula representation
        - descriptive: human-readable chemical names

        Return a list of NOMADEntry objects with detailed metadata including formula_type.
        """
    
    elif action == NOMADAction.download:
        return f"""
        Download raw computational files from NOMAD for: {search_query}

        Assuming you have specific entry IDs, use `get_nomad_raw_files` to download the raw computational files to the .data directory. 
        The files will be extracted and ready for parsing with other tools like cclib or custom_gaussian.
        """
    
    else:  # search_and_download
        return f"""
        Search and download materials data from NOMAD for: {search_query}

        1. First use `search_nomad_entries` to find up to {max_entries} relevant entries
        2. Then use `get_nomad_raw_files` to download the raw files for promising entries
        3. Files will be available in .data/[entry_id]/ for further analysis

        This comprehensive workflow provides both metadata and raw computational data for analysis.
        """


if __name__ == "__main__":
    mcp.run()
