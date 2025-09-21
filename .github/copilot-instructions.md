# VALORANT Replay Tool - AI Coding Guidelines

## Project Overview
This is a Python desktop application that enables VALORANT players to view any downloaded replay by temporarily swapping replay files during the loading process. The tool uses VALORANT's local APIs for authentication and metadata, with a modern dark-themed GUI.

## Architecture

### Core Components
- **`modern_replay_injector_ui.py`** - Main tkinter-based GUI with tabbed interface
- **`replay_file_manager.py`** - File operations, backup/restore, and session monitoring
- **`replay_metadata.py`** - VALORANT API integration for match data and metadata
- **`region_config.py`** - Region-specific API endpoint management
- **`build_v1_1.py`** - PyInstaller build script for executable distribution

### Key Design Patterns

#### 1. VALORANT Local API Integration
```python
# Always use lockfile authentication for local API access
lockfile_path = r"C:\Users\{username}\AppData\Local\Riot Games\Riot Client\Config\lockfile"
# Parse format: name:pid:port:password:protocol
# Use https://127.0.0.1:{port} with Basic auth
```

#### 2. Session State Monitoring
```python
# Monitor VALORANT client state changes
previous_state = 'MENUS'
current_state = session.get('loopState')  # MENUS, REPLAY, etc.
if previous_state == 'MENUS' and current_state == 'REPLAY':
    perform_injection()
```

#### 3. File Swapping Technique
```python
# Backup original, copy injection file, restore after replay ends
backup_success = self.file_manager.backup_file(host_path)
shutil.copy2(injection_file, host_file)  # Temporary swap
# Auto-restore when replay ends
```

#### 4. Region-Aware API Calls
```python
# Use region-specific endpoints for all VALORANT APIs
pd_base = f"https://pd.{region}.a.pvp.net"  # Player Data
glz_base = f"https://glz-{region}-1.{region}.a.pvp.net"  # Game Lobby
shared_base = f"https://shared.{region}.a.pvp.net"  # Shared services
```

## Critical Developer Workflows

### Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run development version
python modern_replay_injector_ui.py

# VALORANT must be running for API access and testing
```

### Building Executables
```bash
# Use PyInstaller for standalone .exe creation
python build_v1_1.py

# Includes all dependencies and assets
# Output: releases/v1.1/SoupsValorantReplayTool_v1.1.exe
```

### Testing Injection Flow
1. Start VALORANT client
2. Run the tool and select region (auto-detect preferred)
3. Select host replay file (what user clicks "Play" on)
4. Select injection file (what actually loads)
5. Start monitoring
6. Click "Play" on host replay in VALORANT
7. Tool detects state change and performs swap
8. Tool monitors for replay end and auto-restores

## Project-Specific Conventions

### Error Handling
```python
# Extensive try/catch with user-friendly messages
try:
    result = risky_operation()
except Exception as e:
    messagebox.showerror("Error", f"Operation failed: {e}")
    self.log(f"❌ Error: {e}", "error")
```

### Logging System
```python
# Color-coded logging with timestamps
self.log("✅ Success message", "success")  # Green
self.log("⚠️ Warning message", "warning")  # Orange
self.log("❌ Error message", "error")     # Red
self.log("🔍 Info message", "info")       # Blue
```

### Threading for UI Responsiveness
```python
# Always use threads for long-running operations
def load_metadata_async():
    # Heavy API calls here
    pass

threading.Thread(target=load_metadata_async, daemon=True).start()
```

### UUID Match ID Extraction
```python
# VALORANT replay filenames are UUIDs
filename = "e1fb7880-f892-40c6-9e39-5c3c97f69e77.vrf"
match_id = filename.replace('.vrf', '')  # Remove extension
```

### API Authentication Headers
```python
# Standard headers for VALORANT API calls
headers = {
    'Authorization': f'Bearer {access_token}',
    'X-Riot-Entitlements-JWT': entitlements_token,
    'X-Riot-ClientPlatform': base64.b64encode(platform_json),
    'X-Riot-ClientVersion': client_version
}
```

## Common Patterns & Gotchas

### VALORANT Path Detection
```python
# Multiple possible paths for VALORANT installation
possible_paths = [
    Path(os.environ.get('LOCALAPPDATA', '')) / 'VALORANT' / 'Saved' / 'Demos',
    Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'VALORANT' / 'Saved' / 'Demos'
]
```

### Map/Agent ID Conversions
```python
# Internal IDs to display names
map_conversions = {
    'Ascent': 'Ascent',
    'Bonsai': 'Split',      # /Game/Maps/Bonsai/Bonsai
    'Duality': 'Bind',      # /Game/Maps/Duality/Duality
    # ... etc
}
```

### Single Instance Enforcement
```python
# Prevent multiple instances using lockfile
lock_file = os.path.join(tempfile.gettempdir(), 'soups_valorant_tool.lock')
if os.path.exists(lock_file):
    sys.exit(1)  # Already running
```

### UI Color Scheme
```python
# Consistent forest green theme
colors = {
    'accent': '#228B22',      # Forest Green
    'success': '#32CD32',     # Lime Green
    'warning': '#ff8c00',     # Orange
    'error': '#d13438',       # Red
    'surface': '#2d2d30',     # Dark surface
}
```

## Dependencies & Requirements
- **Python 3.8+** required
- **Windows-only** (VALORANT is Windows-exclusive)
- **VALORANT client must be running** for API access
- **Internet connection** required for metadata fetching
- **tkinter** (built-in), **requests**, **sv-ttk**, **pywinstyles**

## Security Considerations
- Uses VALORANT's official local APIs only
- No account credentials stored or transmitted
- Temporary file operations with automatic cleanup
- Backup system prevents data loss
- SSL verification disabled for local API calls (standard practice)

## Testing Guidelines
- Always test with VALORANT client running
- Verify region detection works across different regions
- Test injection flow end-to-end
- Check backup/restore functionality
- Validate metadata loading for different game modes
- Test UI responsiveness during long operations

## File Organization
- Keep API logic in dedicated modules (`replay_metadata.py`, `region_config.py`)
- UI code in main file with clear tab separation
- File operations centralized in `replay_file_manager.py`
- Build scripts separate from application code
- Assets (PNG files) in root directory for PyInstaller bundling</content>
<parameter name="filePath">c:\Users\zachl\OneDrive\Documents\GitHub\SoupsValorantReplayTool\.github\copilot-instructions.md