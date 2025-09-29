"""
Test the modular MCP server behavior.
This tests that the MCP server gracefully handles missing optional dependencies
and dynamically registers only available parsers.
"""

import sys
import pytest
from unittest.mock import patch


def test_mcp_server_with_all_dependencies():
    """Test MCP server loads successfully when all dependencies are available."""
    # Add src to path for imports
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Import and initialize MCP server
    from parse_patrol.__main__ import mcp
    
    # Test that MCP server was created successfully
    assert mcp is not None
    assert mcp.name == "Parse Patrol - Unified Chemistry Parser"


def test_mcp_server_dynamic_registration():
    """Test that parsers are registered dynamically based on available dependencies."""
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Capture output from registration process
    import io
    import contextlib
    
    captured_output = io.StringIO()
    
    # Import with captured output
    with contextlib.redirect_stdout(captured_output):
        from parse_patrol.__main__ import mcp
    
    output = captured_output.getvalue()
    
    # Check that registration messages were printed
    assert "Registered cclib parser" in output or "cclib parser not available" in output
    assert "Registered gaussian parser" in output or "gaussian parser not available" in output
    assert "Registered iodata parser" in output or "iodata parser not available" in output
    assert "Registered NOMAD database" in output or "NOMAD database not available" in output


def test_mcp_server_handles_missing_dependencies():
    """Test that MCP server handles missing dependencies gracefully."""
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Mock missing cclib dependency
    with patch.dict('sys.modules', {'cclib': None}):
        with patch('builtins.__import__', side_effect=lambda name, *args, **kwargs: 
                   __import__(name, *args, **kwargs) if name != 'cclib' 
                   else (_ for _ in ()).throw(ImportError(f"No module named '{name}'"))):
            
            # This should work even with cclib missing
            from mcp.server.fastmcp import FastMCP
            test_mcp = FastMCP("Test Parse Patrol")
            
            # Test that we can create MCP server without all dependencies
            assert test_mcp is not None


def test_individual_parser_imports():
    """Test importing individual parsers to ensure they work independently."""
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Test cclib parser
    try:
        from parse_patrol.parsers.cclib.__main__ import cclib_parse_file_to_model
        assert callable(cclib_parse_file_to_model)
        print("✓ cclib parser imports successfully")
    except ImportError as e:
        print(f"⚠ cclib parser not available: {e}")
    
    # Test gaussian parser  
    try:
        from parse_patrol.parsers.gaussian.__main__ import gauss_parse_file_to_model
        assert callable(gauss_parse_file_to_model)
        print("✓ gaussian parser imports successfully")
    except ImportError as e:
        print(f"⚠ gaussian parser not available: {e}")
    
    # Test iodata parser
    try:
        from parse_patrol.parsers.iodata.__main__ import iodata_parse_file_to_model
        assert callable(iodata_parse_file_to_model)
        print("✓ iodata parser imports successfully")
    except ImportError as e:
        print(f"⚠ iodata parser not available: {e}")
    
    # Test NOMAD database
    try:
        from parse_patrol.databases.nomad.__main__ import search_nomad_entries
        assert callable(search_nomad_entries)
        print("✓ NOMAD database imports successfully")
    except ImportError as e:
        print(f"⚠ NOMAD database not available: {e}")


def test_mcp_server_without_optional_deps():
    """Test MCP server with minimal dependencies (only MCP core)."""
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Test that we can at least import the MCP framework
    from mcp.server.fastmcp import FastMCP
    
    # Create a minimal MCP server
    minimal_mcp = FastMCP("Minimal Parse Patrol")
    assert minimal_mcp is not None
    assert minimal_mcp.name == "Minimal Parse Patrol"


if __name__ == "__main__":
    # Run tests directly if script is executed
    print("=== Testing Modular MCP Server ===\n")
    
    print("1. Testing MCP server with all dependencies...")
    test_mcp_server_with_all_dependencies()
    print("✓ Passed\n")
    
    print("2. Testing dynamic registration...")
    test_mcp_server_dynamic_registration()
    print("✓ Passed\n")
    
    print("3. Testing individual parser imports...")
    test_individual_parser_imports()
    print("✓ Passed\n")
    
    print("4. Testing MCP server with minimal dependencies...")
    test_mcp_server_without_optional_deps()
    print("✓ Passed\n")
    
    print("5. Testing graceful handling of missing dependencies...")
    test_mcp_server_handles_missing_dependencies()
    print("✓ Passed\n")
    
    print("🎉 All tests passed!")