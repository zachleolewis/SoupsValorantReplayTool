#!/usr/bin/env python3
"""
Build script for VALORANT Replay Tool v1.1
Creates a standalone .exe with all dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not available"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller installed successfully")

def create_build_spec():
    """Create PyInstaller spec file for the build"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['modern_replay_injector_ui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('OneTapBlack.png', '.'),
        ('OneTapWhite.png', '.'),
    ],
    hiddenimports=[
        'sv_ttk',
        'requests',
        'tkinter',
        'tkinter.ttk',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pywinstyles',
        'pyperclip',
        'urllib3',
        'base64',
        'json',
        'threading',
        'pathlib',
        'datetime',
        'time',
        'shutil',
        'typing',
        're',
        'tempfile',
        'webbrowser',
        'ssl',
        'socket',
        'http.client',
        'urllib.parse',
        'urllib.request'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SoupsValorantReplayTool_v1.1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='OneTapBlack.png'
)
'''
    
    with open('build_v1_1.spec', 'w') as f:
        f.write(spec_content)
    
    print("✅ Created build specification file")

def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")
    
    try:
        # Run PyInstaller with the spec file
        result = subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "build_v1_1.spec"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Build completed successfully!")
            return True
        else:
            print("❌ Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def setup_release_folder():
    """Create and setup the release folder structure"""
    release_dir = Path("releases/v1.1")
    release_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created release directory: {release_dir}")
    return release_dir

def copy_executable(release_dir):
    """Copy the built executable to the release folder"""
    exe_source = Path("dist/SoupsValorantReplayTool_v1.1.exe")
    
    if exe_source.exists():
        exe_dest = release_dir / "SoupsValorantReplayTool_v1.1.exe"
        
        # Copy the executable
        import shutil
        shutil.copy2(exe_source, exe_dest)
        
        # Get file size
        size_mb = exe_dest.stat().st_size / (1024 * 1024)
        
        print(f"✅ Executable copied to: {exe_dest}")
        print(f"✅ File size: {size_mb:.1f} MB")
        return True
    else:
        print(f"❌ Executable not found at: {exe_source}")
        return False

def create_release_readme(release_dir):
    """Create a README for the release"""
    readme_content = """# VALORANT Replay Tool v1.1 - Region Support Update

## 🎉 What's New in v1.1

### ✨ Major Features Added:
- **🌍 Multi-Region Support**: Now works in all VALORANT regions!
- **🔍 Auto-Region Detection**: Automatically detects your region from VALORANT client
- **🌎 Manual Region Selection**: Choose from NA, EU, AP, KR, LATAM, BR, and PBE
- **🔗 Dynamic API Endpoints**: Uses correct regional endpoints for all API calls

### 🐛 Fixes:
- **Fixed "VALORANT client not detected"** error for non-NA regions
- **Fixed replay metadata loading** (map, game mode, score) for all regions
- **Fixed session monitoring** across different regions
- **Resolved API connectivity issues** outside North America

## 🚀 Quick Start

1. **Download** `SoupsValorantReplayTool_v1.1.exe`
2. **Run the executable** (no installation needed!)
3. **Go to "🌍 Region Settings" tab** (first tab)
4. **Click "🔍 Auto-Detect"** or manually select your region
5. **Click "💾 Set Region"** to confirm
6. **Start using the tool** - all features now work in your region!

## 📍 Supported Regions

- **North America** (na) - Default
- **Europe** (eu)
- **Asia Pacific** (ap) 
- **Korea** (kr)
- **Latin America** (latam)
- **Brazil** (br)
- **PBE** (pbe) - Public Beta Environment

## 🛠️ How to Use

### First Time Setup:
1. Launch the app and ensure VALORANT is running
2. Go to "🌍 Region Settings" tab
3. Click "🔍 Auto-Detect" to automatically detect your region
4. Or manually select your region from the dropdown
5. Click "💾 Set Region" to apply

### Normal Usage:
1. Go to "📁 File Selection" tab
2. Select your host replay file (the one you'll click 'Play' on)
3. Click "✅ Confirm Host Selection"
4. Browse and select your injection replay file
5. Go to "⚡ Injection Control" tab
6. Click "🚀 START INJECTION"
7. Go to VALORANT and click 'Play' on your selected replay
8. The injection happens automatically!

## 📋 System Requirements

- **Windows 10/11** (64-bit)
- **VALORANT** installed and running
- **Internet connection** for API access

## 🆘 Troubleshooting

### "VALORANT client not detected"
- Make sure VALORANT is running
- Try the "🔍 Auto-Detect" button in Region Settings
- Manually select your correct region

### "Loading..." for replay metadata
- Check your internet connection
- Verify you selected the correct region
- Try refreshing the replay list

### Auto-detection fails
- Restart VALORANT and try again
- Manually select your region instead
- Check that VALORANT is fully loaded (not just the launcher)

## 📞 Support

- **Twitter/X**: @soupzachary
- **Email**: zachleolewis@gmail.com  
- **Discord**: soup0330

## 🔄 Version History

- **v1.1**: Added multi-region support, auto-detection, improved UI
- **v1.0**: Initial release with basic injection functionality

---

**Note**: This tool uses VALORANT's internal APIs and is not officially supported by Riot Games. Use responsibly and follow Riot's Terms of Service.
"""
    
    readme_path = release_dir / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Created release README: {readme_path}")

def cleanup_build_files():
    """Clean up build artifacts"""
    import shutil
    
    cleanup_paths = [
        "build",
        "dist", 
        "__pycache__",
        "build_v1_1.spec"
    ]
    
    for path in cleanup_paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
    
    print("✅ Cleaned up build artifacts")

def main():
    """Main build process"""
    print("🏗️ Building VALORANT Replay Tool v1.1")
    print("=" * 50)
    
    # Step 1: Install PyInstaller
    install_pyinstaller()
    
    # Step 2: Create build specification
    create_build_spec()
    
    # Step 3: Build executable
    if not build_executable():
        print("❌ Build failed, exiting...")
        return False
    
    # Step 4: Setup release folder
    release_dir = setup_release_folder()
    
    # Step 5: Copy executable
    if not copy_executable(release_dir):
        print("❌ Failed to copy executable, exiting...")
        return False
    
    # Step 6: Cleanup
    cleanup_build_files()
    
    print("\n" + "=" * 50)
    print("🎉 BUILD COMPLETED SUCCESSFULLY!")
    print(f"📦 Release available at: releases/v1.1/")
    print(f"🚀 Executable: SoupsValorantReplayTool_v1.1.exe")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)