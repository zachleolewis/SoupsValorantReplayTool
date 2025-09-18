#!/usr/bin/env python3
"""
VALORANT Region Configuration
Handles region-specific API endpoints and shard mapping
"""

from typing import Dict, Optional, Tuple

class RegionConfig:
    """Manages VALORANT region configuration and API endpoints"""
    
    # Region to shard mapping based on valapidocs.techchrism.me
    REGION_SHARD_MAP = {
        # North America
        'na': 'na',
        'latam': 'na', 
        'br': 'na',
        
        # Europe
        'eu': 'eu',
        
        # Asia Pacific
        'ap': 'ap',
        
        # Korea
        'kr': 'kr',
        
        # PBE (Public Beta Environment)
        'pbe': 'pbe'
    }
    
    # Match history query API regional endpoints
    MATCH_HISTORY_QUERY_ENDPOINTS = {
        'na': 'usw2.pp.sgp.pvp.net',
        'eu': 'euw3.pp.sgp.pvp.net', 
        'ap': 'apse1.pp.sgp.pvp.net',
        'kr': 'kr.pp.sgp.pvp.net',
        'pbe': 'usw2.pp.sgp.pvp.net'  # PBE uses NA endpoints
    }
    
    # Available regions for user selection
    AVAILABLE_REGIONS = [
        ('na', 'North America'),
        ('eu', 'Europe'),
        ('ap', 'Asia Pacific'), 
        ('kr', 'Korea'),
        ('latam', 'Latin America'),
        ('br', 'Brazil'),
        ('pbe', 'PBE (Beta)')
    ]
    
    def __init__(self):
        # Default to North America - no config file needed
        self.current_region = 'na'
    
    def save_region(self, region: str) -> bool:
        """Save selected region to memory (no file persistence for .exe distribution)"""
        try:
            self.current_region = region
            return True
        except Exception as e:
            print(f"Error saving region: {e}")
            return False
    
    def get_shard(self, region: Optional[str] = None) -> str:
        """Get shard for the given region"""
        region = region or self.current_region
        return self.REGION_SHARD_MAP.get(region, 'na')
    
    def get_match_history_api_base(self, region: Optional[str] = None) -> str:
        """Get match history query API base URL for region"""
        region = region or self.current_region
        shard = self.get_shard(region)
        endpoint = self.MATCH_HISTORY_QUERY_ENDPOINTS.get(shard, self.MATCH_HISTORY_QUERY_ENDPOINTS['na'])
        return f"https://{endpoint}"
    
    def get_pd_api_base(self, region: Optional[str] = None) -> str:
        """Get Player Data (PD) API base URL for region"""
        region = region or self.current_region
        shard = self.get_shard(region)
        return f"https://pd.{shard}.a.pvp.net"
    
    def get_glz_api_base(self, region: Optional[str] = None) -> str:
        """Get GLZ API base URL for region"""
        region = region or self.current_region
        shard = self.get_shard(region)
        # GLZ endpoints use region-1 format
        return f"https://glz-{region}-1.{shard}.a.pvp.net"
    
    def get_shared_api_base(self, region: Optional[str] = None) -> str:
        """Get Shared API base URL for region"""
        region = region or self.current_region
        shard = self.get_shard(region)
        return f"https://shared.{shard}.a.pvp.net"
    
    def get_region_display_name(self, region: Optional[str] = None) -> str:
        """Get display name for region"""
        region = region or self.current_region
        for code, name in self.AVAILABLE_REGIONS:
            if code == region:
                return name
        return "Unknown Region"
    
    def detect_region_from_client(self, port: int, password: str) -> Optional[str]:
        """
        Detect region from VALORANT client using the local API
        Returns region code if successful, None if failed
        """
        try:
            import requests
            import base64
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Create auth header
            auth_string = f"riot:{password}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            url = f"https://127.0.0.1:{port}/riotclient/region-locale"
            headers = {
                'Authorization': f'Basic {auth_header}'
            }
            
            response = requests.get(url, headers=headers, verify=False, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                detected_region = data.get('region', '').lower()
                
                # Map detected region to our supported regions
                if detected_region in [r[0] for r in self.AVAILABLE_REGIONS]:
                    return detected_region
                
                # Try to map common variations
                region_mappings = {
                    'north_america': 'na',
                    'latin_america': 'latam',
                    'europe': 'eu',
                    'asia_pacific': 'ap',
                    'korea': 'kr',
                    'brasil': 'br',
                    'brazil': 'br'
                }
                
                mapped_region = region_mappings.get(detected_region.replace('-', '_'))
                if mapped_region:
                    return mapped_region
                    
                print(f"❌ Unknown region detected from client: '{detected_region}'")
            else:
                print(f"❌ API request failed with status {response.status_code}")
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Connection failed: Could not connect to VALORANT client on port {port}")
        except requests.exceptions.Timeout as e:
            print(f"❌ Request timeout: VALORANT client not responding on port {port}")
        except Exception as e:
            print(f"❌ Failed to detect region from client: {e}")
        
        return None
    
    def set_region(self, region: str) -> bool:
        """Set current region and save to config"""
        if region not in [r[0] for r in self.AVAILABLE_REGIONS]:
            return False
        
        return self.save_region(region)
    
    def get_all_api_endpoints(self, region: Optional[str] = None) -> Dict[str, str]:
        """Get all API endpoints for the given region"""
        return {
            'match_history_query': self.get_match_history_api_base(region),
            'player_data': self.get_pd_api_base(region),
            'glz': self.get_glz_api_base(region),
            'shared': self.get_shared_api_base(region)
        }

# Global instance
region_config = RegionConfig()