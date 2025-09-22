#!/usr/bin/env python3
"""
VALORANT Replay File Manager
Handles detection, backup, and injection of .vrf replay files
"""

import os
import shutil
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from requests.auth import HTTPBasicAuth
import base64
from region_config import region_config

class ReplayFileManager:
    def __init__(self):
        self.replay_directory = self._find_replay_directory()
        self.backup_directory = self._create_backup_directory()
        self.current_backup = None
        
    def _find_replay_directory(self) -> Optional[Path]:
        """Find VALORANT replay directory"""
        # Common VALORANT replay paths
        possible_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / 'VALORANT' / 'Saved' / 'Demos',
            Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'VALORANT' / 'Saved' / 'Demos',
            Path('C:') / 'Users' / os.environ.get('USERNAME', '') / 'AppData' / 'Local' / 'VALORANT' / 'Saved' / 'Demos'
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
                
        return None
    
    def _create_backup_directory(self) -> Path:
        """Create backup directory for replay files"""
        backup_dir = Path.cwd() / 'replay_backups'
        backup_dir.mkdir(exist_ok=True)
        return backup_dir
    
    def get_downloaded_replays(self) -> List[Dict]:
        """Get list of downloaded replay files"""
        if not self.replay_directory or not self.replay_directory.exists():
            return []
            
        replays = []
        for vrf_file in self.replay_directory.glob('*.vrf'):
            mod_time = datetime.fromtimestamp(vrf_file.stat().st_mtime)
            
            file_info = {
                'filename': vrf_file.name,
                'path': vrf_file,
                'size': vrf_file.stat().st_size,
                'date_modified': mod_time,  # Fixed: changed from 'modified' to 'date_modified'
                'match_id': vrf_file.stem  # Filename without extension
            }
            replays.append(file_info)
            
        # Sort by modification time (newest first)
        replays.sort(key=lambda x: x['date_modified'], reverse=True)
        return replays
    
    def backup_file(self, replay_file: Path) -> bool:
        """Create backup of original replay file"""
        try:
            timestamp = int(time.time())
            backup_name = f"{replay_file.stem}_backup_{timestamp}.vrf"
            backup_path = self.backup_directory / backup_name
            
            shutil.copy2(replay_file, backup_path)
            self.current_backup = backup_path
            
            print(f"✅ Backup created: {backup_name}")
            return True
            
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def inject_replay_file(self, host_file: Path, injection_file: Path) -> bool:
        """Inject new replay file by replacing host file"""
        try:
            # Create backup first
            if not self.backup_file(host_file):
                return False
            
            # Copy injection file over host file (must have same name)
            shutil.copy2(injection_file, host_file)
            
            print(f"✅ Injected {injection_file.name} -> {host_file.name}")
            return True
            
        except Exception as e:
            print(f"❌ Injection failed: {e}")
            return False
    
    def restore_original_file(self) -> bool:
        """Restore original file from backup"""
        if not self.current_backup or not self.current_backup.exists():
            print("❌ No backup found to restore")
            return False
            
        try:
            # Extract original filename from backup name
            backup_name = self.current_backup.stem
            original_name = backup_name.split('_backup_')[0] + '.vrf'
            original_path = self.replay_directory / original_name
            
            # Restore from backup
            shutil.copy2(self.current_backup, original_path)
            
            print(f"✅ Restored original file: {original_name}")
            return True
            
        except Exception as e:
            print(f"❌ Restore failed: {e}")
            return False
    
    def cleanup_backups(self, keep_latest: int = 5):
        """Clean up old backup files"""
        if not self.backup_directory.exists():
            return
            
        backups = list(self.backup_directory.glob('*_backup_*.vrf'))
        if len(backups) <= keep_latest:
            return
            
        # Sort by modification time and remove oldest
        backups.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for old_backup in backups[keep_latest:]:
            try:
                old_backup.unlink()
                print(f"🗑️ Cleaned up old backup: {old_backup.name}")
            except Exception as e:
                print(f"❌ Failed to cleanup {old_backup.name}: {e}")

class SessionMonitor:
    """Monitor VALORANT session state for replay loading detection"""
    
    def __init__(self):
        self.credentials = self._get_credentials()
        self.is_monitoring = False
        self.callbacks = {
            'replay_start': [],
            'replay_end': [],
            'error': []
        }
    
    def update_region(self):
        """Update region-specific endpoints after region change"""
        if self.credentials and region_config.current_region:
            self.credentials['game_api_base'] = region_config.get_glz_api_base()
            print(f"Updated session monitor to use GLZ endpoint: {self.credentials['game_api_base']}")
    
    def _get_credentials(self) -> Optional[Dict]:
        """Get VALORANT API credentials from lockfile"""
        try:
            lockfile_path = Path(os.environ['LOCALAPPDATA']) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'
            
            if not lockfile_path.exists():
                return None
                
            with open(lockfile_path, 'r') as f:
                name, tag, port, password, protocol = f.read().strip().split(':')
            
            base_url = f"https://127.0.0.1:{port}"
            
            # Get API tokens
            response = requests.get(f"{base_url}/entitlements/v1/token",
                                  auth=HTTPBasicAuth('riot', password),
                                  verify=False)
            
            if response.status_code != 200:
                return None
                
            token_data = response.json()
            
            # Get client version
            response = requests.get(f"{base_url}/product-session/v1/external-sessions",
                                  auth=HTTPBasicAuth('riot', password),
                                  verify=False)
            
            sessions = response.json()
            client_version = None
            for session_id, session_data in sessions.items():
                if session_data.get('productId') == 'valorant':
                    client_version = session_data.get('version', 'release-08.11-shipping-15-2813485')
                    break
            
            platform_info = {
                "platformType": "PC",
                "platformOS": "Windows", 
                "platformOSVersion": "10.0.19041.1.256.64bit",
                "platformChipset": "Unknown"
            }
            
            return {
                'base_url': base_url,
                'password': password,
                'game_api_base': region_config.get_glz_api_base() if region_config.current_region else None,  # Use region-specific GLZ endpoint
                'access_token': token_data['accessToken'],
                'entitlements_token': token_data['token'],
                'client_version': client_version,
                'platform_info': platform_info,
                'player_id': token_data['subject']
            }
            
        except Exception as e:
            print(f"❌ Failed to get credentials: {e}")
            return None
    
    def get_session_info(self) -> Optional[Dict]:
        """Get current session information"""
        if not self.credentials or not self.credentials.get('game_api_base'):
            return None
            
        try:
            headers = {
                'Authorization': f"Bearer {self.credentials['access_token']}",
                'X-Riot-Entitlements-JWT': self.credentials['entitlements_token'],
                'X-Riot-ClientPlatform': base64.b64encode(json.dumps(self.credentials['platform_info']).encode()).decode(),
                'X-Riot-ClientVersion': self.credentials['client_version']
            }
            
            response = requests.get(
                f"{self.credentials['game_api_base']}/session/v1/sessions/{self.credentials['player_id']}",
                headers=headers,
                verify=False
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"❌ Session info error: {e}")
            return None
    
    def add_callback(self, event: str, callback):
        """Add callback for session events"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def start_monitoring(self):
        """Start monitoring session state changes"""
        self.is_monitoring = True
        previous_state = None
        
        print("🔍 Starting session monitoring...")
        
        while self.is_monitoring:
            try:
                session = self.get_session_info()
                if not session:
                    time.sleep(1)
                    continue
                
                current_state = session.get('loopState')
                
                # Detect replay start
                if previous_state == 'MENUS' and current_state == 'REPLAY':
                    print("🎬 REPLAY LOADING DETECTED!")
                    for callback in self.callbacks['replay_start']:
                        callback(session)
                
                # Detect replay end  
                elif previous_state == 'REPLAY' and current_state == 'MENUS':
                    print("🏁 REPLAY ENDED!")
                    for callback in self.callbacks['replay_end']:
                        callback(session)
                
                previous_state = current_state
                time.sleep(0.5)  # 500ms polling
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                for callback in self.callbacks['error']:
                    callback(e)
                time.sleep(1)
        
        print("🛑 Session monitoring stopped")
    
    def stop_monitoring(self):
        """Stop session monitoring"""
        self.is_monitoring = False

# Test the components
if __name__ == "__main__":
    print("🎮 VALORANT Replay File Manager Test")
    print("=" * 50)
    
    # Test replay file detection
    manager = ReplayFileManager()
    replays = manager.get_downloaded_replays()
    
    print(f"📁 Replay directory: {manager.replay_directory}")
    print(f"💾 Backup directory: {manager.backup_directory}")
    print(f"📋 Found {len(replays)} replay files:")
    
    for replay in replays[:5]:  # Show first 5
        print(f"   • {replay['filename']} ({replay['size']} bytes)")
    
    # Test session monitoring
    print("\n🔍 Testing session monitoring...")
    monitor = SessionMonitor()
    session = monitor.get_session_info()
    
    if session:
        print(f"✅ Session connected: {session.get('loopState', 'Unknown')}")
    else:
        print("❌ Could not connect to VALORANT session")