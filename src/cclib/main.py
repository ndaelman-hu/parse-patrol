import cclib
from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]
from typing import TypedDict, Optional, Dict, List, Any


class CCDataDict(TypedDict, total=False):
    """TypedDict representation of cclib ccData attributes"""
    aonames: Optional[List[str]]
    aooverlaps: Optional[List]
    atombasis: Optional[List[List[int]]]
    atomcharges: Optional[Dict[str, List]]
    atomcoords: Optional[List]
    atommasses: Optional[List]
    atomnos: Optional[List]
    atomspins: Optional[Dict[str, List]]
    ccenergies: Optional[List]
    charge: Optional[int]
    coreelectrons: Optional[List]
    dispersionenergies: Optional[List]
    enthalpy: Optional[float]
    entropy: Optional[float]
    etenergies: Optional[List]
    etoscs: Optional[List]
    etdips: Optional[List]
    etveldips: Optional[List]
    etmagdips: Optional[List]
    etrotats: Optional[List]
    etsecs: Optional[List]
    etsyms: Optional[List[str]]
    freeenergy: Optional[float]
    fonames: Optional[List[str]]
    fooverlaps: Optional[List]
    fragnames: Optional[List[str]]
    frags: Optional[List[List[int]]]
    gbasis: Optional[Any]
    geotargets: Optional[List]
    geovalues: Optional[List]
    grads: Optional[List]
    hessian: Optional[List]
    homos: Optional[List]
    metadata: Optional[Dict[str, Any]]
    mocoeffs: Optional[List[List]]
    moenergies: Optional[List[List]]
    moments: Optional[List]
    mosyms: Optional[List[List[str]]]
    mpenergies: Optional[List]
    mult: Optional[int]
    natom: Optional[int]
    nbasis: Optional[int]
    nmo: Optional[int]
    nmrtensors: Optional[Dict[str, Dict[str, List]]]
    nmrcouplingtensors: Optional[Dict[str, Dict[str, List]]]
    nocoeffs: Optional[List]
    nooccnos: Optional[List]
    nsocoeffs: Optional[List]
    nsooccnos: Optional[List]
    optdone: Optional[bool]
    optstatus: Optional[List]
    polarizabilities: Optional[List]
    pressure: Optional[float]
    rotconsts: Optional[List]
    scancoords: Optional[List]
    scanenergies: Optional[List]
    scannames: Optional[List[str]]
    scanparm: Optional[List]
    scfenergies: Optional[List]
    scftargets: Optional[List]
    scfvalues: Optional[List]
    temperature: Optional[float]
    time: Optional[List]
    transprop: Optional[Dict[str, Any]]
    vibanharms: Optional[List]
    vibdisps: Optional[List]
    vibfconsts: Optional[List]
    vibfreqs: Optional[List]
    vibirs: Optional[List]
    vibramans: Optional[List]
    vibrmasses: Optional[List]
    vibsyms: Optional[List[str]]
    zpve: Optional[float]

def ccdata_to_dict(ccdata: cclib.parser.data.ccData) -> CCDataDict: # type: ignore
    """Convert ccData object to CCDataDict TypedDict format.
    
    Args:
        ccdata: Parsed ccData object from cclib
    
    Returns:
        CCDataDict with converted data types for JSON serialization
    """
    result = CCDataDict()
    
    for field_name in CCDataDict.__annotations__.keys():
        if hasattr(ccdata, field_name):
            value = getattr(ccdata, field_name)
            
            # Skip None values to avoid validation errors
            if value is None:
                continue
                
            # Convert numpy arrays to lists for JSON serialization
            if hasattr(value, 'tolist'):
                result[field_name] = value.tolist()
            # Handle dict of numpy arrays  
            elif isinstance(value, dict):
                result[field_name] = {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in value.items()}
            # Handle list of numpy arrays
            elif isinstance(value, list) and value and hasattr(value[0], 'tolist'):
                result[field_name] = [item.tolist() for item in value]
            else:
                result[field_name] = value
                
    return result

mcp = FastMCP("CCLib Chemistry Parser")

@mcp.tool()
def parse_file_to_dict(filepath: str) -> CCDataDict:
    """Parse chemistry file and return as CCDataDict for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        CCDataDict with parsed data converted for JSON serialization
    """
    ccdata = cclib.io.ccopen(filepath) # type: ignore
    if ccdata is None:
        return CCDataDict()
    
    ccdata.parse()
    return ccdata_to_dict(ccdata)

if __name__ == "__main__":
    mcp.run()

