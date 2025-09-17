# Soup's Valorant Replay Tool

A tool for viewing any replay of the same game mode in your client.
# WARNING! 
This tool has not been aproved by Riot Games and could lead to your account being banned for using it. Most likely this is not the case since its a simple swap of files but just be warned!

## For Users

### Installation
1. Download the latest release from the releases section
2. Run `SoupsValorantReplayTool.exe`

### Usage
1. Launch the application
2. Select replay files to download
3. Choose your download location
4. Click download to save your replays

## For Developers

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
python -m PyInstaller --onefile --windowed --add-data "OneTapWhite.png;." --add-data "OneTapBlack.png;." --add-data "endpoints.json;." --icon="OneTapBlack.png" --name="SoupsValorantReplayTool" modern_replay_injector_ui.py
```

### Development
- Main UI: `modern_replay_injector_ui.py`
- File management: `replay_file_manager.py`
- Metadata handling: `replay_metadata.py`
- Archive folder contains development history and alternative implementations

## Requirements
- Windows OS
- VALORANT installed
- Python 3.8+ (for development)