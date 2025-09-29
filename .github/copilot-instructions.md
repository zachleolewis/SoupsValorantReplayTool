````instructions# VALORANT Replay Tool - AI Coding Guidelines

# VALORANT Replay Tool - AI Coding Guidelines

## Project Overview

## Project OverviewThis is a Python desktop application that enables VALORANT players to view any downloaded replay by temporarily swapping replay files during the loading process. The tool uses VALORANT's local APIs for authentication and metadata, with a modern dark-themed GUI.

This is a Python desktop application that enables VALORANT players to view any downloaded replay by temporarily swapping replay files during the loading process. The tool uses VALORANT's local APIs for authentication and metadata, with a modern dark-themed GUI.

## Architecture

## Architecture

### Core Components

### Core Components- **`modern_replay_injector_ui.py`** - Main tkinter-based GUI with tabbed interface

- **`modern_replay_injector_ui.py`** - Main tkinter-based GUI with tabbed interface- **`replay_file_manager.py`** - File operations, backup/restore, and session monitoring

- **`replay_file_manager.py`** - File operations, backup/restore, and session monitoring- **`replay_metadata.py`** - VALORANT API integration for match data and metadata

- **`replay_metadata.py`** - VALORANT API integration for match data and metadata- **`region_config.py`** - Region-specific API endpoint management

- **`region_config.py`** - Region-specific API endpoint management- **`build_v1_1.py`** - PyInstaller build script for executable distribution

- **`build_v1_1.py`** - PyInstaller build script for executable distribution

### Key Design Patterns

### Key Design Patterns

#### 1. VALORANT Local API Integration

#### 1. VALORANT Local API Integration```python

```python# Always use lockfile authentication for local API access

# Always use lockfile authentication for local API accesslockfile_path = r"C:\Users\{username}\AppData\Local\Riot Games\Riot Client\Config\lockfile"

lockfile_path = r"C:\Users\{username}\AppData\Local\Riot Games\Riot Client\Config\lockfile"# Parse format: name:pid:port:password:protocol

# Parse format: name:pid:port:password:protocol# Use https://127.0.0.1:{port} with Basic auth

# Use https://127.0.0.1:{port} with Basic auth```

```

#### 2. Session State Monitoring

#### 2. Session State Monitoring```python

```python# Monitor VALORANT client state changes via session polling

# Monitor VALORANT client state changes via session pollingprevious_state = 'MENUS'

previous_state = 'MENUS'current_state = session.get('loopState')  # MENUS, REPLAY, etc.

current_state = session.get('loopState')  # MENUS, REPLAY, etc.if previous_state == 'MENUS' and current_state == 'REPLAY':

if previous_state == 'MENUS' and current_state == 'REPLAY':    perform_injection()

    perform_injection()```

```

#### 3. File Swapping Technique

#### 3. File Swapping Technique```python

```python# Backup original, copy injection file, restore after replay ends

# Backup original, copy injection file, restore after replay endsbackup_success = self.file_manager.backup_file(host_path)

backup_success = self.file_manager.backup_file(host_path)shutil.copy2(injection_file, host_file)  # Temporary swap

shutil.copy2(injection_file, host_file)  # Temporary swap# Auto-restore when replay ends via session monitoring

# Auto-restore when replay ends via session monitoring```

```

#### 4. Region-Aware API Calls

#### 4. Region-Aware API Calls```python

```python# Use region-specific endpoints for all VALORANT APIs

# Use region-specific endpoints for all VALORANT APIspd_base = f"https://pd.{region}.a.pvp.net"  # Player Data

pd_base = f"https://pd.{region}.a.pvp.net"  # Player Dataglz_base = f"https://glz-{region}-1.{region}.a.pvp.net"  # Game Lobby

glz_base = f"https://glz-{region}-1.{region}.a.pvp.net"  # Game Lobbyshared_base = f"https://shared.{region}.a.pvp.net"  # Shared services

shared_base = f"https://shared.{region}.a.pvp.net"  # Shared services```

```

## Critical Developer Workflows

#### 5. Callback-Based Event System

```python### Development Setup

# Register callbacks for session state changes```bash

self.session_monitor.add_callback('replay_start', self.on_replay_start)# Install dependencies

self.session_monitor.add_callback('replay_end', self.on_replay_end)pip install -r requirements.txt

self.session_monitor.add_callback('error', self.on_monitor_error)

```# Run development version

python modern_replay_injector_ui.py

## Critical Developer Workflows

# VALORANT must be running for API access and testing

### Development Setup```

```bash

# Install dependencies### Building Executables

pip install -r requirements.txt```bash

# Use PyInstaller for standalone .exe creation

# Run development versionpython build_v1_1.py

python modern_replay_injector_ui.py

# Includes all dependencies and assets

# VALORANT must be running for API access and testing# Output: releases/v1.1/SoupsValorantReplayTool_v1.1.exe

``````



### Building Executables### Testing Injection Flow

```bash1. Start VALORANT client

# Use PyInstaller for standalone .exe creation2. Run the tool and select region (auto-detect preferred)

python build_v1_1.py3. Select host replay file (what user clicks "Play" on)

4. Select injection file (what actually loads)

# Includes all dependencies and assets5. Start monitoring

# Output: releases/v1.1/SoupsValorantReplayTool_v1.1.exe6. Click "Play" on host replay in VALORANT

```7. Tool detects state change and performs swap

8. Tool monitors for replay end and auto-restores

### Testing Injection Flow

1. Start VALORANT client## Project-Specific Conventions

2. Run the tool and select region (auto-detect preferred)

3. Select host replay file (what user clicks "Play" on)### Error Handling

4. Select injection file (what actually loads)```python

5. Start monitoring# Extensive try/catch with user-friendly messages

6. Click "Play" on host replay in VALORANTtry:

7. Tool detects state change and performs swap    result = risky_operation()

8. Tool monitors for replay end and auto-restoresexcept Exception as e:

    messagebox.showerror("Error", f"Operation failed: {e}")

### UI Theming and Styling    self.log(f"❌ Error: {e}", "error")

```python```

# Apply Sun Valley dark theme

sv_ttk.set_theme("dark")### Logging System

```python

# Custom color scheme with forest green accents# Color-coded logging with timestamps

colors = {self.log("✅ Success message", "success")  # Green

    'accent': '#228B22',      # Forest Greenself.log("⚠️ Warning message", "warning")  # Orange

    'success': '#32CD32',     # Lime Greenself.log("❌ Error message", "error")     # Red

    'warning': '#ff8c00',     # Orangeself.log("🔍 Info message", "info")       # Blue

    'error': '#d13438',       # Red```

    'surface': '#2d2d30',     # Dark surface

}### Threading for UI Responsiveness

``````python

# Always use threads for long-running operations

## Project-Specific Conventionsdef load_metadata_async():

    # Heavy API calls here

### Error Handling    pass

```python

# Extensive try/catch with user-friendly messagesthreading.Thread(target=load_metadata_async, daemon=True).start()

try:```

    result = risky_operation()

except Exception as e:### UUID Match ID Extraction

    messagebox.showerror("Error", f"Operation failed: {e}")```python

    self.log(f"❌ Error: {e}", "error")# VALORANT replay filenames are UUIDs

```filename = "e1fb7880-f892-40c6-9e39-5c3c97f69e77.vrf"

match_id = filename.replace('.vrf', '')  # Remove extension

### Logging System```

```python

# Color-coded logging with timestamps### API Authentication Headers

self.log("✅ Success message", "success")  # Green```python

self.log("⚠️ Warning message", "warning")  # Orange# Standard headers for VALORANT API calls

self.log("❌ Error message", "error")     # Redheaders = {

self.log("🔍 Info message", "info")       # Blue    'Authorization': f'Bearer {access_token}',

```    'X-Riot-Entitlements-JWT': entitlements_token,

    'X-Riot-ClientPlatform': base64.b64encode(platform_json),

### Threading for UI Responsiveness    'X-Riot-ClientVersion': client_version

```python}

# Always use threads for long-running operations```

def load_metadata_async():

    # Heavy API calls here## Common Patterns & Gotchas

    pass

### VALORANT Path Detection

threading.Thread(target=load_metadata_async, daemon=True).start()```python

```# Multiple possible paths for VALORANT installation

possible_paths = [

### UUID Match ID Extraction    Path(os.environ.get('LOCALAPPDATA', '')) / 'VALORANT' / 'Saved' / 'Demos',

```python    Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'VALORANT' / 'Saved' / 'Demos'

# VALORANT replay filenames are UUIDs]

filename = "e1fb7880-f892-40c6-9e39-5c3c97f69e77.vrf"```

match_id = filename.replace('.vrf', '')  # Remove extension

```### Map/Agent ID Conversions

```python

### API Authentication Headers# Internal IDs to display names

```pythonmap_conversions = {

# Standard headers for VALORANT API calls    'Ascent': 'Ascent',

headers = {    'Bonsai': 'Split',      # /Game/Maps/Bonsai/Bonsai

    'Authorization': f'Bearer {access_token}',    'Duality': 'Bind',      # /Game/Maps/Duality/Duality

    'X-Riot-Entitlements-JWT': entitlements_token,    # ... etc

    'X-Riot-ClientPlatform': base64.b64encode(platform_json),}

    'X-Riot-ClientVersion': client_version```

}

```### Single Instance Enforcement

```python

## Common Patterns & Gotchas# Prevent multiple instances using lockfile

lock_file = os.path.join(tempfile.gettempdir(), 'soups_valorant_tool.lock')

### VALORANT Path Detectionif os.path.exists(lock_file):

```python    sys.exit(1)  # Already running

# Multiple possible paths for VALORANT installation```

possible_paths = [

    Path(os.environ.get('LOCALAPPDATA', '')) / 'VALORANT' / 'Saved' / 'Demos',### UI Color Scheme

    Path(os.environ.get('USERPROFILE', '')) / 'AppData' / 'Local' / 'VALORANT' / 'Saved' / 'Demos'```python

]# Consistent forest green theme

```colors = {

    'accent': '#228B22',      # Forest Green

### Map/Agent ID Conversions    'success': '#32CD32',     # Lime Green

```python    'warning': '#ff8c00',     # Orange

# Internal IDs to display names    'error': '#d13438',       # Red

map_conversions = {    'surface': '#2d2d30',     # Dark surface

    'Ascent': 'Ascent',}

    'Bonsai': 'Split',      # /Game/Maps/Bonsai/Bonsai```

    'Duality': 'Bind',      # /Game/Maps/Duality/Duality

    # ... etc### Platform Info for API Calls

}```python

```# Required platform info for VALORANT API authentication

platform_json = {

### Single Instance Enforcement    "platformType": "PC",

```python    "platformOS": "Windows",

# Prevent multiple instances using lockfile    "platformOSVersion": "10.0.19041.1.256.64bit",

lock_file = os.path.join(tempfile.gettempdir(), 'soups_valorant_tool.lock')    "platformChipset": "Unknown"

if os.path.exists(lock_file):}

    sys.exit(1)  # Already runningplatform_header = base64.b64encode(json.dumps(platform_json).encode()).decode()

``````



### Platform Info for API Calls### SSL Verification for Local APIs

```python```python

# Required platform info for VALORANT API authentication# Always disable SSL verification for local VALORANT API calls

platform_json = {response = requests.get(url, auth=('riot', password), verify=False)

    "platformType": "PC",urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    "platformOS": "Windows",```

    "platformOSVersion": "10.0.19041.1.256.64bit",

    "platformChipset": "Unknown"### Backup System with Timestamps

}```python

platform_header = base64.b64encode(json.dumps(platform_json).encode()).decode()# Timestamped backups prevent conflicts

```timestamp = int(time.time())

backup_name = f"{replay_file.stem}_backup_{timestamp}.vrf"

### SSL Verification for Local APIsbackup_path = self.backup_directory / backup_name

```pythonshutil.copy2(replay_file, backup_path)

# Always disable SSL verification for local VALORANT API calls```

response = requests.get(url, auth=('riot', password), verify=False)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)### Session Monitoring Callbacks

``````python

# Register callbacks for session state changes

### Backup System with Timestampsself.session_monitor.add_callback('error', self.on_monitor_error)

```pythonself.session_monitor.add_callback('state_change', self.on_state_change)

# Timestamped backups prevent conflicts```

timestamp = int(time.time())

backup_name = f"{replay_file.stem}_backup_{timestamp}.vrf"## Dependencies & Requirements

backup_path = self.backup_directory / backup_name- **Python 3.8+** required

shutil.copy2(replay_file, backup_path)- **Windows-only** (VALORANT is Windows-exclusive)

```- **VALORANT client must be running** for API access

- **Internet connection** required for metadata fetching

## Dependencies & Requirements- **tkinter** (built-in), **requests**, **sv-ttk**, **pywinstyles**

- **Python 3.8+** required

- **Windows-only** (VALORANT is Windows-exclusive)## Development Resources

- **VALORANT client must be running** for API access- **`archive/`** folder contains development history and alternative implementations

- **Internet connection** required for metadata fetching- **`VALORANT_Replay_Research_Complete_Report.md`** - Comprehensive API research documentation

- **tkinter** (built-in), **requests**, **sv-ttk**, **pywinstyles**- **`replay_backups/`** - Automatic backup storage for injected files

- **`releases/`** - Versioned executable distributions

## Development Resources

- **`archive/`** folder contains development history and alternative implementations## Security Considerations

- **`VALORANT_Replay_Research_Complete_Report.md`** - Comprehensive API research documentation- Uses VALORANT's official local APIs only

- **`replay_backups/`** - Automatic backup storage for injected files- No account credentials stored or transmitted

- **`releases/`** - Versioned executable distributions- Temporary file operations with automatic cleanup

- Backup system prevents data loss

## Security Considerations- SSL verification disabled for local API calls (standard practice)

- Uses VALORANT's official local APIs only- No account credentials stored or transmitted

- No account credentials stored or transmitted- Temporary file operations with automatic cleanup

- Temporary file operations with automatic cleanup- Backup system prevents data loss

- Backup system prevents data loss- SSL verification disabled for local API calls (standard practice)

- SSL verification disabled for local API calls (standard practice)

## Testing Guidelines

## Testing Guidelines- Always test with VALORANT client running

- Always test with VALORANT client running- Verify region detection works across different regions

- Verify region detection works across different regions- Test injection flow end-to-end

- Test injection flow end-to-end- Check backup/restore functionality

- Check backup/restore functionality- Validate metadata loading for different game modes

- Validate metadata loading for different game modes- Test UI responsiveness during long operations

- Test UI responsiveness during long operations

## File Organization

## File Organization- Keep API logic in dedicated modules (`replay_metadata.py`, `region_config.py`)

- Keep API logic in dedicated modules (`replay_metadata.py`, `region_config.py`)- UI code in main file with clear tab separation

- UI code in main file with clear tab separation- File operations centralized in `replay_file_manager.py`

- File operations centralized in `replay_file_manager.py`- Build scripts separate from application code

- Build scripts separate from application code- Assets (PNG files) in root directory for PyInstaller bundling

- Assets (PNG files) in root directory for PyInstaller bundling- Archive folder contains development history and alternative implementations</content>

- Archive folder contains development history and alternative implementations<parameter name="filePath">c:\Users\zachl\OneDrive\Documents\GitHub\SoupsValorantReplayTool\.github\copilot-instructions.md