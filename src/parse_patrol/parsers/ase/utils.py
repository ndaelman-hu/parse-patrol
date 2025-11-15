import ase.io # pyright: ignore[reportMissingImports]
from typing import Optional, Dict, List
from pydantic import BaseModel, Field # pyright: ignore[reportMissingImports]

class ASEDataModel(BaseModel):
    """A container class for data loaded from (or to be written to) a file."""
    
    # Format and metadata information
    # source_format: Optional[str] = Field(None, description="Detected file format/software (e.g., 'gaussian', 'vasp', 'orca')")
    # source_extension: Optional[str] = Field(None, description="Original file extension or type (e.g., '.fchk', 'POSCAR', '.cube')")
    # detected_software: Optional[str] = Field(None, description="Detected quantum chemistry software package")

    symbols: Optional[List[float]] = Field(None, description="Example field representing data from ASEData")

def ase_to_model(ext_data: ase.io.Atoms, filepath: str | None = None) -> ASEDataModel:
    """Convert ASE Atoms object to ASEDataModel (Pydantic) format.
    
    Args:
        ext_data: Parsed iodata object from IOData
        filepath: Original filepath for metadata extraction
    
    Returns:
        IODataModel with converted data types for JSON serialization
    """
    result = {}
    for field_name in ASEDataModel.model_fields.keys():
        # if field_name in ['source_format', 'source_extension', 'detected_software']:
        #     continue  # Already handled above
            
        value = getattr(ext_data, field_name, None)
        if value is None:
            continue
        if hasattr(value, 'tolist'):
            result[field_name] = value.tolist()
        elif isinstance(value, dict):
            result[field_name] = {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in value.items()}
        elif isinstance(value, list) and value and hasattr(value[0], 'tolist'):
            result[field_name] = [item.tolist() for item in value]
        else:
            result[field_name] = value
    return ASEDataModel(**result)


def ase_parse(filepath: str, format: str | None = None) -> ASEDataModel:
    """Parse chemistry file and return as ASEDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        ASEDataModel with parsed data converted for JSON serialization
    """
    data = ase.io.read(filepath, format=format)
    return ase_to_model(data, filepath)