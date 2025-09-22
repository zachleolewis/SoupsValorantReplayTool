#!/usr/bin/env python3
"""
VALORANT Replay Metadata Fetcher
Fetches match metadata using VALORANT APIs for replay analysis
"""

import requests
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
import urllib3
from region_config import region_config

# Disable SSL warnings for local API calls
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ReplayMetadataFetcher:
    def __init__(self):
        self.lockfile_path = self._find_lockfile()
        self.port = None
        self.password = None
        self.auth_token = None
        self.entitlements_token = None
        self.user_id = None
        self.region = region_config.current_region  # Use region from config
        
        if self.lockfile_path:
            self._parse_lockfile()
            self._get_auth_tokens()
    
    def update_region(self, new_region: str):
        """Update the region for API calls"""
        self.region = new_region
        print(f"Updated metadata fetcher region to: {new_region}")
    
    def _find_lockfile(self) -> Optional[str]:
        """Find VALORANT lockfile"""
        possible_paths = [
            os.path.expanduser("~/AppData/Local/Riot Games/Riot Client/Config/lockfile"),
            "C:/Users/" + os.getenv('USERNAME', '') + "/AppData/Local/Riot Games/Riot Client/Config/lockfile"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _parse_lockfile(self):
        """Parse lockfile to get port and password"""
        if not self.lockfile_path:
            return False
        try:
            with open(self.lockfile_path, 'r') as f:
                data = f.read().strip()
                parts = data.split(':')
                if len(parts) >= 5:
                    self.port = parts[2]
                    self.password = parts[3]
                    return True
        except Exception as e:
            print(f"Error parsing lockfile: {e}")
        return False
    
    def _get_auth_tokens(self):
        """Get authentication and entitlements tokens"""
        if not self.port or not self.password:
            return False
        
        try:
            # Get entitlements token
            auth_url = f"https://127.0.0.1:{self.port}/entitlements/v1/token"
            auth_response = requests.get(
                auth_url,
                auth=('riot', self.password),
                verify=False
            )
            
            if auth_response.status_code == 200:
                entitlements_data = auth_response.json()
                self.entitlements_token = entitlements_data.get('token')
                self.auth_token = entitlements_data.get('accessToken')
                
                # Get user info
                userinfo_url = f"https://127.0.0.1:{self.port}/rso-auth/v1/authorization/userinfo"
                userinfo_response = requests.get(
                    userinfo_url,
                    auth=('riot', self.password),
                    verify=False
                )
                
                if userinfo_response.status_code == 200:
                    userinfo_data = userinfo_response.json()
                    self.user_id = userinfo_data.get('sub')
                    print(f"Debug: Retrieved user ID: {self.user_id}")
                    return True
                else:
                    print(f"Debug: Userinfo request failed: {userinfo_response.status_code}")
                    # Try to extract user ID from the entitlements token itself
                    import base64
                    try:
                        # JWT tokens have 3 parts separated by dots
                        token_parts = self.auth_token.split('.')
                        if len(token_parts) >= 2:
                            # Decode the payload (second part)
                            payload = token_parts[1]
                            # Add padding if needed
                            payload += '=' * (4 - len(payload) % 4)
                            decoded = base64.b64decode(payload)
                            token_data = json.loads(decoded)
                            self.user_id = token_data.get('sub')
                            print(f"Debug: Extracted user ID from token: {self.user_id}")
                            return True
                    except Exception as e:
                        print(f"Debug: Could not extract user ID from token: {e}")
                    return False
                    
        except Exception as e:
            print(f"Error getting auth tokens: {e}")
        return False
    
    def get_match_history(self, start_index: int = 0, end_index: int = 20, queue: Optional[str] = None) -> Optional[List[Dict]]:
        """Get match history from VALORANT API"""
        if not self.auth_token or not self.entitlements_token or not self.user_id:
            print("Authentication tokens not available")
            return None
        
        try:
            # Build URL using region config
            pd_base = region_config.get_pd_api_base(self.region)
            url = f"{pd_base}/match-history/v1/history/{self.user_id}"
            params: Dict[str, Any] = {
                'startIndex': start_index,
                'endIndex': end_index
            }
            if queue:
                params['queue'] = queue
            
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'X-Riot-Entitlements-JWT': self.entitlements_token,
                'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybVZlcnNpb24iOiAiMTAuMC4xOTA0My4xMjU3IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9',
                'X-Riot-ClientVersion': 'release-09.07-shipping-26-2442946'
            }
            
            response = requests.get(url, params=params, headers=headers, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('History', [])
            else:
                print(f"Match history request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching match history: {e}")
            return None
    
    def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information"""
        if not self.auth_token or not self.entitlements_token:
            print("Authentication tokens not available")
            return None
        
        try:
            # Build URL using region config
            pd_base = region_config.get_pd_api_base(self.region)
            url = f"{pd_base}/match-details/v1/matches/{match_id}"
            
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'X-Riot-Entitlements-JWT': self.entitlements_token,
                'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybVZlcnNpb24iOiAiMTAuMC4xOTA0My4xMjU3IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9',
                'X-Riot-ClientVersion': 'release-09.07-shipping-26-2442946'
            }
            
            response = requests.get(url, headers=headers, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Match details request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching match details: {e}")
            return None
    
    def get_replay_summary(self, match_id: str) -> Optional[Dict]:
        """Get replay summary using the new match history query API"""
        if not self.auth_token or not self.entitlements_token:
            print("Authentication tokens not available")
            return None
        
        try:
            # Use the match history query API with summary info type - region-specific
            match_history_base = region_config.get_match_history_api_base(self.region)
            url = f"{match_history_base}/match-history-query/v3/product/valorant/matchId/{match_id}/infoType/summary"
            
            headers = {
                'Authorization': f'Bearer {self.auth_token}',
                'X-Riot-Entitlements-JWT': self.entitlements_token,
                'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybVZlcnNpb24iOiAiMTAuMC4xOTA0My4xMjU3IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9',
                'X-Riot-ClientVersion': 'release-09.07-shipping-26-2442946'
            }
            
            response = requests.get(url, headers=headers, verify=False)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Replay summary request failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error fetching replay summary: {e}")
            return None
    
    def extract_match_id_from_filename(self, filename: str) -> Optional[str]:
        """Extract match ID from replay filename"""
        # Remove .vrf extension and use the UUID part
        match_id = filename.replace('.vrf', '')
        
        # Validate UUID format
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if re.match(uuid_pattern, match_id, re.IGNORECASE):
            return match_id
        return None
    
    def get_replay_metadata(self, replay_filename: str) -> Dict[str, Any]:
        """Get metadata for a replay file"""
        # Check if region is configured
        if not self.region:
            return {
                'filename': replay_filename,
                'map': 'No Region Set',
                'mode': 'No Region Set', 
                'agent': 'No Region Set',
                'score': 'No Region Set',
                'error': 'Please select a region first'
            }
        
        match_id = self.extract_match_id_from_filename(replay_filename)
        if not match_id:
            return {
                'filename': replay_filename,
                'map': 'Unknown',
                'mode': 'Unknown', 
                'agent': 'Unknown',
                'score': 'Unknown',
                'error': 'Invalid filename format'
            }
        
        # Try to get match details first (more reliable)
        match_details = self.get_match_details(match_id)
        if match_details:
            return self._parse_match_details(match_details, replay_filename)
        
        # Fallback to match history if details fail
        match_history = self.get_match_history(0, 50)  # Get recent matches
        if match_history:
            for match in match_history:
                if match.get('MatchID') == match_id:
                    return self._parse_match_history_entry(match, replay_filename)
        
        # Try replay summary as last resort
        replay_summary = self.get_replay_summary(match_id)
        if replay_summary:
            return {
                'filename': replay_filename,
                'map': 'Unknown',
                'mode': 'Unknown',
                'agent': 'Unknown',
                'score': 'Unknown',
                'game_version': replay_summary.get('GameVersion', 'Unknown'),
                'checksum': replay_summary.get('Checksum', 'Unknown')
            }
        
        return {
            'filename': replay_filename,
            'map': 'Unknown',
            'mode': 'Unknown',
            'agent': 'Unknown',
            'score': 'Unknown',
            'error': 'Could not fetch match data'
        }
    
    def _parse_match_details(self, match_details: Dict, filename: str) -> Dict[str, Any]:
        """Parse match details to extract metadata"""
        try:
            # Extract basic info
            match_info = match_details.get('matchInfo', {})
            map_id = match_info.get('mapId', '/Game/Maps/Unknown/Unknown')
            map_name = self._map_id_to_name(map_id)
            
            # Get queue info
            queue_id = match_info.get('queueID', '')
            mode = self._queue_id_to_mode(queue_id)
            
            # Find player's agent and team
            player_agent = 'Unknown'
            player_team = None
            players = match_details.get('players', [])
            for player in players:
                if player.get('subject') == self.user_id:
                    character_id = player.get('characterId', '')
                    player_agent = self._character_id_to_agent(character_id)
                    player_team = player.get('teamId', '')
                    break
            
            # Extract final score
            score = self._extract_final_score(match_details, player_team or '')
            
            return {
                'filename': filename,
                'map': map_name,
                'mode': mode,
                'agent': player_agent,
                'score': score,
                'match_id': match_details.get('matchInfo', {}).get('matchId', ''),
                'game_start': match_info.get('gameStartMillis', 0)
            }
            
        except Exception as e:
            print(f"Error parsing match details: {e}")
            return {
                'filename': filename,
                'map': 'Unknown',
                'mode': 'Unknown',
                'agent': 'Unknown',
                'score': 'Unknown',
                'error': f'Parse error: {e}'
            }
    
    def _extract_final_score(self, match_details: Dict, player_team: str) -> str:
        """Extract final score from match details"""
        try:
            teams = match_details.get('teams', [])
            if not teams or len(teams) < 2:
                return 'Unknown'
            
            # Get team scores
            team_scores = {}
            for team in teams:
                team_id = team.get('teamId', '')
                rounds_won = team.get('roundsWon', 0)
                team_scores[team_id] = rounds_won
            
            # Format score based on player's team perspective
            if len(team_scores) >= 2:
                team_ids = list(team_scores.keys())
                
                if player_team and player_team in team_scores:
                    # Player's team score first
                    player_score = team_scores[player_team]
                    opponent_team = next((tid for tid in team_ids if tid != player_team), None)
                    if opponent_team:
                        opponent_score = team_scores[opponent_team]
                        # Add win/loss indicator
                        if player_score > opponent_score:
                            return f"{player_score}-{opponent_score} (W)"
                        elif player_score < opponent_score:
                            return f"{player_score}-{opponent_score} (L)"
                        else:
                            return f"{player_score}-{opponent_score} (T)"
                else:
                    # Fallback: just show scores without W/L
                    scores = list(team_scores.values())
                    return f"{scores[0]}-{scores[1]}"
            
            return 'Unknown'
            
        except Exception as e:
            print(f"Error extracting score: {e}")
            return 'Unknown'
    
    def _parse_match_history_entry(self, match: Dict, filename: str) -> Dict[str, Any]:
        """Parse match history entry to extract metadata"""
        try:
            map_id = match.get('MapID', '/Game/Maps/Unknown/Unknown')
            map_name = self._map_id_to_name(map_id)
            
            queue_id = match.get('QueueID', '')
            mode = self._queue_id_to_mode(queue_id)
            
            # Agent info might not be in history, need details for that
            return {
                'filename': filename,
                'map': map_name,
                'mode': mode,
                'agent': 'Unknown',  # Need match details for agent
                'score': 'Unknown',  # Need match details for score
                'match_id': match.get('MatchID', ''),
                'game_start': match.get('GameStartTime', 0)
            }
            
        except Exception as e:
            print(f"Error parsing match history: {e}")
            return {
                'filename': filename,
                'map': 'Unknown',
                'mode': 'Unknown',
                'agent': 'Unknown',
                'score': 'Unknown',
                'error': f'Parse error: {e}'
            }
    
    def _map_id_to_name(self, map_id: str) -> str:
        """Convert map ID to human readable name"""
        # Extract the map name from the path
        map_name = map_id.split('/')[-1] if '/' in map_id else map_id
        
        # Map internal names to display names (based on official VALORANT API data)
        map_name_map = {
            'Ascent': 'Ascent',           # /Game/Maps/Ascent/Ascent
            'Bonsai': 'Split',            # /Game/Maps/Bonsai/Bonsai  
            'Canyon': 'Fracture',         # /Game/Maps/Canyon/Canyon
            'Duality': 'Bind',            # /Game/Maps/Duality/Duality
            'Foxtrot': 'Breeze',          # /Game/Maps/Foxtrot/Foxtrot  **FIXED**
            'Triad': 'Haven',             # /Game/Maps/Triad/Triad     **CORRECTED**
            'Port': 'Icebox',             # /Game/Maps/Port/Port
            'Pitt': 'Pearl',              # /Game/Maps/Pitt/Pitt
            'Jam': 'Lotus',               # /Game/Maps/Jam/Jam
            'Juliett': 'Sunset',          # /Game/Maps/Juliett/Juliett
            'Infinity': 'Abyss',          # /Game/Maps/Infinity/Infinity
            'Rook': 'Corrode',            # /Game/Maps/Rook/Rook
            # Team Deathmatch / Practice maps
            'HURM_Alley': 'District',     # /Game/Maps/HURM/HURM_Alley/HURM_Alley
            'HURM_Bowl': 'Kasbah',        # /Game/Maps/HURM/HURM_Bowl/HURM_Bowl
            'HURM_Helix': 'Drift',        # /Game/Maps/HURM/HURM_Helix/HURM_Helix
            'HURM_Yard': 'Piazza',        # /Game/Maps/HURM/HURM_Yard/HURM_Yard
            'HURM_HighTide': 'Glitch',    # /Game/Maps/HURM/HURM_HighTide/HURM_HighTide
            # Range/Training maps
            'Poveglia': 'The Range',      # /Game/Maps/Poveglia/Range
            'PovegliaV2': 'The Range',    # /Game/Maps/PovegliaV2/RangeV2
            'NPEV2': 'Basic Training'     # /Game/Maps/NPEV2/NPEV2
        }
        return map_name_map.get(map_name, map_name)
    
    def _queue_id_to_mode(self, queue_id: str) -> str:
        """Convert queue ID to human readable mode"""
        queue_map = {
            'competitive': 'Competitive',
            'unrated': 'Unrated',
            'spikerush': 'Spike Rush',
            'deathmatch': 'Deathmatch',
            'escalation': 'Escalation',
            'replication': 'Replication',
            'snowball': 'Snowball Fight',
            'swiftplay': 'Swiftplay'
        }
        return queue_map.get(queue_id.lower(), queue_id)
    
    def _character_id_to_agent(self, character_id: str) -> str:
        """Convert character ID to agent name"""
        # Common character ID mappings (partial list)
        character_map = {
            'add6443a-41bd-e414-f6ad-e58d267f4e95': 'Jett',
            'f94c3b30-42be-e959-889c-5aa313dba261': 'Raze',
            'a3bfb853-43b2-7238-a4f1-ad90e9e46bcc': 'Reyna',
            'eb93336a-449b-9c1b-0a54-a891f7921d69': 'Phoenix',
            '5f8d3a7f-467b-97f3-062c-13acf203c006': 'Breach',
            '6f2a04ca-43e0-be17-7f36-b3908627744d': 'Skye',
            '117ed9e3-49f3-6512-3ccf-0cada7e3823b': 'Cypher',
            '1e58de9c-4950-5125-93e9-a0aee9f98746': 'Killjoy',
            '569fdd95-4d10-43ab-ca70-79becc718b46': 'Sage',
            '320b2a48-4d9b-a075-30f1-1f93a9b638fa': 'Sova',
            '707eab51-4836-f488-046a-cda6bf494859': 'Viper',
            '8e253930-4c05-31dd-1b6c-968525494517': 'Omen',
            '9f0d8ba9-4140-b941-57d3-a7ad57c6b417': 'Brimstone',
            '41fb69c1-4189-7b37-f117-bcaf1e96f1bf': 'Astra',
            '7f94d92c-4234-0a36-9646-3a87eb8b5c89': 'Yoru',
            '22697a3d-45bf-8dd7-4fec-84a9e28c69d7': 'Chamber',
            'bb2a4828-46eb-8cd1-e765-15848195d751': 'Neon',
            'a5e4c8a6-0ea5-4e0f-97a4-70a6e4e60ba4': 'Fade',
            '95b78ed7-4637-86d9-7e41-71ba8c293152': 'Harbor',
            'e370fa57-4757-3604-3648-499e1f642d3f': 'Gekko',
            'cc8b64c8-4b25-4ff9-6e7f-37b4da43d235': 'Deadlock',
            '0e38b510-41a8-5780-5e8f-568b2a4f2d6c': 'Iso',
            '1dbf2edd-7729-4459-b1ad-0b8dc52a8afb': 'Clove',
            'efba5359-4016-a1e5-7626-b1ae76895940': 'Vyse'
        }
        return character_map.get(character_id, character_id)

def test_replay_summary():
    """Test the replay summary API to see what data it returns"""
    fetcher = ReplayMetadataFetcher()
    
    if not fetcher.auth_token:
        print("No authentication available")
        return
    
    print("Testing replay summary API...")
    print(f"User ID: {fetcher.user_id}")
    
    # Test with a sample match ID (you can replace with actual match ID from your replays)
    test_match_id = "e1fb7880-f892-40c6-9e39-5c3c97f69e77"  # Replace with actual match ID
    
    print(f"\nTesting replay summary for match ID: {test_match_id}")
    try:
        api_base = region_config.get_match_history_api_base()
        print("API URL:", f"{api_base}/match-history-query/v3/product/valorant/matchId/{test_match_id}/infoType/summary")
    except ValueError as e:
        print(f"Cannot test API - {e}")
        return
    
    summary = fetcher.get_replay_summary(test_match_id)
    if summary:
        print("\n=== REPLAY SUMMARY RESPONSE ===")
        print(json.dumps(summary, indent=2))
        print("\n=== AVAILABLE FIELDS ===")
        for key, value in summary.items():
            print(f"{key}: {type(value).__name__} = {value}")
    else:
        print("Failed to get replay summary")
        
    # Also test a few other infoTypes to see what's available
    other_info_types = ['details', 'metadata', 'info']
    for info_type in other_info_types:
        print(f"\n--- Testing infoType: {info_type} ---")
        try:
            api_base = region_config.get_match_history_api_base()
            url = f"{api_base}/match-history-query/v3/product/valorant/matchId/{test_match_id}/infoType/{info_type}"
        except ValueError as e:
            print(f"Cannot test {info_type} - {e}")
            continue
        
        try:
            headers = {
                'Authorization': f'Bearer {fetcher.auth_token}',
                'X-Riot-Entitlements-JWT': fetcher.entitlements_token,
                'X-Riot-ClientPlatform': 'ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybVZlcnNpb24iOiAiMTAuMC4xOTA0My4xMjU3IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9',
                'X-Riot-ClientVersion': 'release-09.07-shipping-26-2442946'
            }
            
            response = requests.get(url, headers=headers, verify=False)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Fields: {list(data.keys())}")
            else:
                print(f"Error: {response.text[:200]}")
        except Exception as e:
            print(f"Exception: {e}")

def test_metadata_fetcher():
    """Test the metadata fetcher"""
    fetcher = ReplayMetadataFetcher()
    
    if not fetcher.auth_token:
        print("No authentication available")
        return
    
    print("Testing metadata fetcher...")
    print(f"User ID: {fetcher.user_id}")
    
    # Test with a sample filename
    test_filename = "e1fb7880-f892-40c6-9e39-5c3c97f69e77.vrf"
    metadata = fetcher.get_replay_metadata(test_filename)
    print(f"Test metadata: {metadata}")

if __name__ == "__main__":
    print("Choose test:")
    print("1. Test metadata fetcher")
    print("2. Test replay summary API")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        test_replay_summary()
    else:
        test_metadata_fetcher()