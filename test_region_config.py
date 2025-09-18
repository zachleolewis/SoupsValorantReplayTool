#!/usr/bin/env python3
"""
Test script to validate region configuration functionality
"""

import sys
from pathlib import Path

# Add the project directory to the path
sys.path.append(str(Path(__file__).parent))

from region_config import RegionConfig

def test_region_configuration():
    """Test the region configuration system"""
    print("🧪 Testing VALORANT Region Configuration")
    print("=" * 50)
    
    # Test 1: Initialize region config
    config = RegionConfig()
    print(f"✅ Default region: {config.current_region}")
    print(f"✅ Region display name: {config.get_region_display_name()}")
    
    # Test 2: Test region mappings
    print("\n🗺️ Testing region to shard mappings:")
    for region_code, region_name in config.AVAILABLE_REGIONS:
        shard = config.get_shard(region_code)
        print(f"   {region_name} ({region_code}) → shard: {shard}")
    
    # Test 3: Test API endpoint generation
    print("\n🔗 Testing API endpoint generation:")
    test_regions = ['na', 'eu', 'ap', 'kr']
    
    for region in test_regions:
        print(f"\n   Region: {region}")
        endpoints = config.get_all_api_endpoints(region)
        for api_name, endpoint in endpoints.items():
            print(f"     {api_name}: {endpoint}")
    
    # Test 4: Test region setting and saving
    print("\n💾 Testing region persistence:")
    original_region = config.current_region
    
    # Try setting to EU
    if config.set_region('eu'):
        print("   ✅ Successfully set region to EU")
        print(f"   ✅ Current region: {config.current_region}")
    else:
        print("   ❌ Failed to set region to EU")
    
    # Restore original region
    if config.set_region(original_region):
        print(f"   ✅ Restored original region: {config.current_region}")
    else:
        print(f"   ❌ Failed to restore original region")
    
    # Test 5: Test invalid region handling
    print("\n🚫 Testing invalid region handling:")
    if config.set_region('invalid_region'):
        print("   ❌ Should not accept invalid region")
    else:
        print("   ✅ Correctly rejected invalid region")
    
    print("\n" + "=" * 50)
    print("🎉 Region configuration test completed!")

if __name__ == "__main__":
    try:
        test_region_configuration()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)