#!/usr/bin/env python3
"""
Debug script to test VALORANT client connection and region detection
"""

import sys
from pathlib import Path
import os

# Add the project directory to the path
sys.path.append(str(Path(__file__).parent))

from region_config import region_config
from replay_metadata import ReplayMetadataFetcher

def test_valorant_connection():
    """Test connection to VALORANT client"""
    print("🔍 Testing VALORANT Client Connection")
    print("=" * 50)
    
    # Test 1: Check if lockfile exists
    lockfile_paths = [
        os.path.expanduser("~/AppData/Local/Riot Games/Riot Client/Config/lockfile"),
        "C:/Users/" + os.getenv('USERNAME', '') + "/AppData/Local/Riot Games/Riot Client/Config/lockfile"
    ]
    
    lockfile_found = None
    for path in lockfile_paths:
        if os.path.exists(path):
            lockfile_found = path
            print(f"✅ Lockfile found: {path}")
            break
    
    if not lockfile_found:
        print("❌ No lockfile found. VALORANT is not running.")
        print("   Please start VALORANT and try again.")
        return False
    
    # Test 2: Parse lockfile
    try:
        with open(lockfile_found, 'r') as f:
            data = f.read().strip()
            parts = data.split(':')
            if len(parts) >= 5:
                name, pid, port, password, protocol = parts
                print(f"✅ Lockfile parsed successfully:")
                print(f"   Process: {name} (PID: {pid})")
                print(f"   Port: {port}")
                print(f"   Protocol: {protocol}")
            else:
                print(f"❌ Invalid lockfile format: {data}")
                return False
    except Exception as e:
        print(f"❌ Error reading lockfile: {e}")
        return False
    
    # Test 3: Test basic connection
    print(f"\n🌐 Testing connection to port {port}...")
    try:
        import requests
        import base64
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        # Test basic help endpoint first
        auth_string = f"riot:{password}"
        auth_bytes = auth_string.encode('ascii')
        auth_header = base64.b64encode(auth_bytes).decode('ascii')
        
        base_url = f"https://127.0.0.1:{port}"
        headers = {'Authorization': f'Basic {auth_header}'}
        
        # Try help endpoint first
        response = requests.get(f"{base_url}/help", headers=headers, verify=False, timeout=5)
        print(f"📡 Help endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Basic connection successful")
        else:
            print("❌ Basic connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False
    
    # Test 4: Test region detection
    print(f"\n🗺️ Testing region detection...")
    try:
        detected_region = region_config.detect_region_from_client(int(port), password)
        if detected_region:
            print(f"✅ Region detected: {detected_region}")
            return True
        else:
            print("❌ Region detection failed")
            return False
    except Exception as e:
        print(f"❌ Region detection error: {e}")
        return False

def test_metadata_fetcher():
    """Test the ReplayMetadataFetcher initialization"""
    print("\n🔧 Testing ReplayMetadataFetcher")
    print("=" * 50)
    
    try:
        fetcher = ReplayMetadataFetcher()
        print(f"✅ MetadataFetcher created")
        print(f"   Lockfile path: {fetcher.lockfile_path}")
        print(f"   Port: {fetcher.port}")
        print(f"   Has password: {'Yes' if fetcher.password else 'No'}")
        print(f"   Region: {fetcher.region}")
        
        if fetcher.port and fetcher.password:
            print("✅ Credentials available for auto-detection")
            return True
        else:
            print("❌ Missing credentials for auto-detection")
            return False
            
    except Exception as e:
        print(f"❌ MetadataFetcher error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 VALORANT Connection & Region Detection Test")
    print("=" * 60)
    
    connection_ok = test_valorant_connection()
    metadata_ok = test_metadata_fetcher()
    
    print("\n" + "=" * 60)
    if connection_ok and metadata_ok:
        print("🎉 All tests passed! Auto-detection should work.")
    else:
        print("❌ Some tests failed. Check the output above for issues.")
        if not connection_ok:
            print("   → VALORANT client connection issue")
        if not metadata_ok:
            print("   → MetadataFetcher initialization issue")