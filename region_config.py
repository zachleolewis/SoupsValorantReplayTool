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
    
    def detect_region_from_config_endpoint(self, port: int, password: str) -> Optional[str]:
        """
        Detect region from VALORANT config endpoint using local authentication
        Returns region code if successful, None if failed
        """
        try:
            import requests
            import base64
            import json
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Create auth header
            auth_string = f"riot:{password}"
            auth_bytes = auth_string.encode('ascii')
            auth_header = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                'Authorization': f'Basic {auth_header}',
                'User-Agent': 'RiotClient/60.0.9.1234567.1234567 rso-auth (Windows;10;;Professional, x64)'
            }
            
            # Get entitlements token
            entitlements_url = f"https://127.0.0.1:{port}/entitlements/v1/token"
            response = requests.get(entitlements_url, headers=headers, verify=False, timeout=10)
            if response.status_code != 200:
                print(f"Failed to get entitlements: {response.status_code}")
                return None
            
            entitlements_data = response.json()
            access_token = entitlements_data['accessToken']
            entitlements_token = entitlements_data['token']
            
            # Get client version (optional, but good practice)
            session_url = f"https://127.0.0.1:{port}/product-session/v1/external-sessions"
            response = requests.get(session_url, headers=headers, verify=False, timeout=10)
            client_version = "release-08.07-shipping-28-927049"  # fallback
            if response.status_code == 200:
                session_data = response.json()
                if 'valorant' in session_data:
                    client_version = session_data['valorant']['version']
            
            # Platform info
            platform_info = {
                "platformType": "PC",
                "platformOS": "Windows", 
                "platformOSVersion": "10.0.19043.1.256.64bit",
                "platformChipset": "Unknown"
            }
            platform_b64 = base64.b64encode(json.dumps(platform_info).encode()).decode()
            
            # Try different regions to find the correct one
            regions_to_try = ['na', 'eu', 'ap', 'kr']
            
            for region in regions_to_try:
                config_url = f"https://shared.{region}.a.pvp.net/v1/config/{region}"
                config_headers = {
                    'Authorization': f'Bearer {access_token}',
                    'X-Riot-Entitlements-JWT': entitlements_token,
                    'X-Riot-ClientVersion': client_version,
                    'X-Riot-ClientPlatform': platform_b64,
                    'User-Agent': 'RiotClient/60.0.9.1234567.1234567 rso-auth (Windows;10;;Professional, x64)'
                }
                
                response = requests.get(config_url, headers=config_headers, verify=False, timeout=10)
                if response.status_code == 200:
                    # Successfully got config, this is the correct region
                    return region
            
            print("Could not determine region from config endpoints")
            return None
            
        except requests.exceptions.ConnectionError as e:
            print(f"Connection failed: Could not connect to VALORANT client on port {port}")
        except requests.exceptions.Timeout as e:
            print(f"Request timeout: VALORANT client not responding on port {port}")
        except Exception as e:
            print(f"Failed to detect region from config endpoint: {e}")
        
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