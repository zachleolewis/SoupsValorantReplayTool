# Soup's Valorant Replay Tool

A tool for viewing any replay of the same game mode in your client.

WARNING: This tool has not been approved by Riot Games and could lead to your account being banned for using it. Most likely this is not the case since it is a simple swap of files but just be warned!

## For Users

### Installation
1. Go to the [Releases](https://github.com/zachleolewis/SoupsValorantReplayTool/releases) page
2. Download the latest `SoupsValorantReplayTool.exe` file
3. Run the executable

### Usage
1. Launch the application
2. Select your VALORANT region
3. Choose a host replay file (the one you want to click "Play" on in VALORANT)
4. Choose an injection replay file (the one you actually want to watch)
5. Start monitoring
6. Click "Play" on the host replay in VALORANT
7. The tool will automatically swap the files and load your chosen replay

### Requirements
- Windows OS
- VALORANT installed and running
- Internet connection for metadata

## For Developers

### Overview
This Python application enables VALORANT players to view any downloaded replay by temporarily swapping replay files during the loading process. The tool uses VALORANT's local APIs for authentication and metadata, with a modern dark-themed GUI built with tkinter.

### How It Works
The tool works by monitoring VALORANT's session state and performing file operations at the right moment:

1. **File Swapping Technique**: When a replay is loaded in VALORANT, the tool temporarily replaces the replay file that VALORANT expects with a different one
2. **Session Monitoring**: Uses VALORANT's local API to detect when the client transitions from menu to replay mode
3. **Automatic Backup/Restore**: Creates backups of original files and automatically restores them when the replay ends
4. **Region-Aware API Calls**: Connects to region-specific VALORANT API endpoints for metadata and authentication

### Architecture
- `modern_replay_injector_ui.py` - Main tkinter-based GUI with tabbed interface
- `replay_file_manager.py` - File operations, backup/restore, and session monitoring
- `replay_metadata.py` - VALORANT API integration for match data and metadata
- `region_config.py` - Region-specific API endpoint management
- `build_v1_1.py` - PyInstaller build script for executable distribution

### Installation
1. Clone this repository
2. Install Python 3.8 or higher
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running
```
python modern_replay_injector_ui.py
```

### Building
To create an executable:
```
python build_v1_1.py
```

This uses PyInstaller to create a standalone .exe file with all dependencies included.

### Development Setup
- VALORANT must be running for API access and testing
- The tool reads authentication tokens from VALORANT's lockfile
- Test with actual VALORANT client to verify injection flow
- Archive folder contains development history and alternative implementations

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with VALORANT running
5. Submit a pull request

### Requirements
- Windows OS (VALORANT is Windows-exclusive)
- VALORANT installed
- Python 3.8+ (for development)
- tkinter (built-in), requests, sv-ttk, pywinstyles
