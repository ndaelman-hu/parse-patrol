#!/usr/bin/env python3
"""
Simple example of running NOMAD integration tests for Parse Patrol.

This script demonstrates how to:
1. Search NOMAD for real quantum chemistry files
2. Download and parse them with available parsers
3. Clean up afterwards

Run this to test your Parse Patrol installation with real data.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"  
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


def test_basic_nomad_functionality():
    """Test basic NOMAD search without downloading files."""
    print("🔍 Testing NOMAD search functionality...")
    
    try:
        from parse_patrol.databases.nomad.utils import nomad_search_entries
        
        # Search for simple water molecules
        entries = nomad_search_entries(
            formula="H2O",
            start=1,
            end=3  # Just get a few entries
        )
        
        print(f"✅ Found {len(entries)} H2O entries in NOMAD")
        
        if entries:
            entry = entries[0]
            print(f"   Sample entry: {entry.entry_id}")
            print(f"   Formula: {entry.formula}")
            print(f"   Program: {entry.program_name}")
        
        return True
        
    except ImportError as e:
        print(f"❌ NOMAD dependencies not available: {e}")
        print("   Install with: pip install requests")
        return False
    except Exception as e:
        print(f"❌ NOMAD search failed: {e}")
        return False


def test_parser_availability():
    """Check which parsers are available."""
    print("\n📋 Checking parser availability...")
    
    parsers = [
        ("cclib", "parse_patrol.parsers.cclib.utils"),
        ("iodata", "parse_patrol.parsers.iodata.utils"), 
        ("gaussian", "parse_patrol.parsers.gaussian.utils"),
    ]
    
    available = []
    
    for name, module in parsers:
        try:
            __import__(module)
            print(f"   ✅ {name} parser available")
            available.append(name)
        except ImportError:
            print(f"   ❌ {name} parser not available")
    
    print(f"   📊 Total available: {len(available)}/{len(parsers)}")
    return available


def test_simple_download_and_parse():
    """Test downloading and parsing a single file."""
    print("\n📥 Testing file download and parsing...")
    
    try:
        from parse_patrol.databases.nomad.utils import nomad_search_entries, nomad_get_raw_files
        
        # Search for Gaussian files (most common)
        entries = nomad_search_entries(
            program_name="Gaussian",
            formula="H2O",
            start=1,
            end=5
        )
        
        if not entries:
            print("   ⚠️  No Gaussian H2O files found in NOMAD")
            return False
        
        print(f"   Found {len(entries)} Gaussian entries")
        
        # Try to download the first one
        entry = entries[0]
        print(f"   Downloading entry: {entry.entry_id}")
        
        download_path = nomad_get_raw_files(entry.entry_id)
        print(f"   ✅ Downloaded to: {download_path}")
        
        # Look for parseable files
        download_dir = Path(download_path)
        files = list(download_dir.rglob("*.log")) + list(download_dir.rglob("*.out"))
        
        if not files:
            print("   ⚠️  No .log or .out files found")
            return False
        
        test_file = files[0]
        print(f"   Testing file: {test_file.name}")
        
        # Try parsing with cclib if available
        try:
            from parse_patrol.parsers.cclib.utils import cclib_parse
            result = cclib_parse(str(test_file))
            
            if result:
                print("   ✅ Successfully parsed with cclib!")
                if hasattr(result, 'source_format'):
                    print(f"      Detected format: {result.source_format}")
                return True
            else:
                print("   ❌ Parsing returned no data")
                return False
                
        except ImportError:
            print("   ⚠️  cclib not available for parsing test")
            return False
        except Exception as e:
            print(f"   ❌ Parsing failed: {e}")
            return False
        
    except Exception as e:
        print(f"   ❌ Download/parse test failed: {e}")
        return False
    
    finally:
        # Clean up
        try:
            import shutil
            data_dir = Path(".data")
            if data_dir.exists():
                shutil.rmtree(data_dir)
                print("   🧹 Cleaned up downloaded files")
        except Exception as e:
            print(f"   ⚠️  Cleanup failed: {e}")


def main():
    """Run all basic tests."""
    print("🧪 Parse Patrol Integration Test Example")
    print("=" * 50)
    
    # Test 1: Basic NOMAD search
    search_ok = test_basic_nomad_functionality()
    
    # Test 2: Parser availability 
    available_parsers = test_parser_availability()
    
    # Test 3: Download and parse (only if dependencies available)
    if search_ok and available_parsers:
        download_ok = test_simple_download_and_parse()
    else:
        print("\n⚠️  Skipping download test - missing dependencies")
        download_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   NOMAD search: {'✅' if search_ok else '❌'}")
    print(f"   Parsers available: {len(available_parsers)}")
    print(f"   Download/parse: {'✅' if download_ok else '❌'}")
    
    if search_ok and available_parsers:
        print("\n🎉 Parse Patrol is working! Ready for integration tests.")
        print("   Run full tests with: uv run python tests/run_nomad_tests.py")
    else:
        print("\n💡 Install missing dependencies:")
        if not search_ok:
            print("   pip install requests  # for NOMAD access")
        if not available_parsers:
            print("   pip install cclib qc-iodata  # for parsers")
    
    return search_ok and bool(available_parsers)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)