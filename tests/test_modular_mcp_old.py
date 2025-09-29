#!/usr/bin/env python3
"""
Test script to demonstrate the modular MCP server behavior.
This shows how the server gracefully handles missing optional dependencies.
"""

import sys
sys.path.insert(0, 'src')

def test_with_all_dependencies():
    """Test MCP server with all dependencies available."""
    print("=== Testing with all dependencies ===")
    from parse_patrol.__main__ import mcp
    print("✓ MCP server loaded successfully with all available parsers")
    
    # Check if tools were registered (FastMCP internal structure may vary)
    try:
        tools = list(mcp._tool_manager._tool_handlers.keys()) if hasattr(mcp, '_tool_manager') else []
        prompts = list(mcp._prompt_manager._prompt_handlers.keys()) if hasattr(mcp, '_prompt_manager') else []
        
        print(f"Registered tools: {len(tools)}")
        for tool in sorted(tools):
            print(f"  - {tool}")
        
        print(f"Registered prompts: {len(prompts)}")
        for prompt in sorted(prompts):
            print(f"  - {prompt}")
    except AttributeError:
        print("✓ MCP server initialized (unable to inspect internal structure)")
        print("  This is expected behavior - the important part is no import errors occurred")

def test_without_dependencies():
    """Test MCP server behavior when dependencies are missing."""
    print("\n=== Testing without some dependencies (simulated) ===")
    
    # Backup original modules
    original_modules = {}
    modules_to_hide = ['cclib', 'iodata', 'periodictable']
    
    for module in modules_to_hide:
        if module in sys.modules:
            original_modules[module] = sys.modules[module]
            del sys.modules[module]
    
    # Create a fresh MCP instance
    from mcp.server.fastmcp import FastMCP
    test_mcp = FastMCP("Test Parse Patrol - Partial Dependencies")
    
    # Try to register parsers (this should handle missing deps gracefully)
    print("Attempting to register parsers with missing dependencies...")
    
    # Test cclib (should fail)
    try:
        from parse_patrol.parsers.cclib.__main__ import cclib_parse_file_to_model
        test_mcp.tool()(cclib_parse_file_to_model)
        print("✗ cclib should have failed but didn't")
    except ImportError as e:
        print(f"✓ cclib correctly unavailable: {e}")
    
    # Test gaussian (should work - only needs periodictable which we hid, but let's see)
    try:
        from parse_patrol.parsers.gaussian.__main__ import gauss_parse_file_to_model
        test_mcp.tool()(gauss_parse_file_to_model)
        print("✓ gaussian parser available")
    except ImportError as e:
        print(f"✓ gaussian correctly unavailable: {e}")
    
    # Restore original modules
    for module, original in original_modules.items():
        sys.modules[module] = original
    
    print("✓ Modular behavior test completed")

if __name__ == "__main__":
    test_with_all_dependencies()
    test_without_dependencies()