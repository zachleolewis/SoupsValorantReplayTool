#!/usr/bin/env python3
"""
VALORANT Replay Injector - Modern UI Edition
Ultra-modern, polished interface with Sun Valley theme
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from replay_file_manager import ReplayFileManager, SessionMonitor
from replay_metadata import ReplayMetadataFetcher
from region_config import region_config
import tempfile

# Install sv-ttk if not available
try:
    import sv_ttk
except ImportError:
    print("Installing sv-ttk theme...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sv-ttk"])
    import sv_ttk

# Optional: Dark title bar on Windows
try:
    import pywinstyles
    TITLE_BAR_SUPPORT = True
except ImportError:
    TITLE_BAR_SUPPORT = False

class ModernReplayInjectorGUI:
    def __init__(self):
        # Check for existing instance
        lock_file = os.path.join(tempfile.gettempdir(), 'soups_valorant_tool.lock')
        if os.path.exists(lock_file):
            messagebox.showerror("Already Running", "The VALORANT Replay Tool is already running!")
            sys.exit(1)
        else:
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            self.lock_file = lock_file
        
        # Initialize main window with optimizations
        self.root = tk.Tk()
        self.root.title("Soup's Valorant Replay Tool")
        self.root.geometry("1000x850")  # Increased height to accommodate confirmation section
        self.root.minsize(900, 800)  # Also increased minimum size
        
        # Set window icon
        try:
            # Use black logo for window icon (shows on taskbar)
            icon_path = Path(__file__).parent / "OneTapBlack.png"
            if icon_path.exists():
                icon_image = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon_image)
        except Exception as e:
            print(f"Could not load window icon: {e}")
        
        # Performance optimizations
        self.root.configure(bg='#202020')
        
        # Advanced performance optimizations for Windows
        try:
            # Try to enable hardware acceleration on Windows
            import platform
            if platform.system() == "Windows":
                # Enable double buffering and hardware acceleration hints
                self.root.tk.call('tk', 'windowingsystem')  # Check windowing system
                self.root.wm_attributes('-topmost', False)  # Ensure not always on top
                
                # Optimize rendering by reducing unnecessary redraws
                self.root.configure(highlightthickness=0)
                
        except Exception as e:
            print(f"Could not apply advanced optimizations: {e}")
        
        # Reduce update frequency for better performance
        self.root.tk.call('tk', 'scaling', 1.0)  # Disable DPI scaling adjustments
        
        # Disable some visual effects that cause lag
        self.root.option_add('*tearOff', False)  # Disable menu tear-off
        self.root.option_add('*TCombobox*Listbox.selectBackground', '#0078d4')
        
        # Apply modern theme
        sv_ttk.set_theme("dark")
        
        # Apply dark title bar on Windows if supported
        if TITLE_BAR_SUPPORT:
            self.apply_theme_to_titlebar()
        
        # Enhanced colors for modern UI with forest green theme
        self.colors = {
            'accent': '#228B22',           # Forest Green (primary)
            'success': '#32CD32',          # Lime Green (success actions)
            'warning': '#ff8c00',          # Orange (warnings)
            'error': '#d13438',            # Red (errors)
            'surface': '#2d2d30',          # Dark surface
            'card': '#3c3c3c',            # Card background
            'text_primary': '#ffffff',     # Primary text
            'text_secondary': '#cccccc',   # Secondary text
            'text_muted': '#999999',       # Muted text
            'border': '#484848',           # Border color
            'hover': '#2F4F2F',            # Dark forest green hover
            'selected': '#228B22',         # Forest green selection
        }
        
        # Initialize components
        self.file_manager = ReplayFileManager()
        self.session_monitor = SessionMonitor()
        self.metadata_fetcher = ReplayMetadataFetcher()
        
        # State variables
        self.selected_host_replay = None
        self.selected_injection_file = None
        self.monitoring_active = False
        self.injection_ready = False
        
        # Setup monitoring callbacks
        self.session_monitor.add_callback('error', self.on_monitor_error)
        
        self.setup_modern_styles()
        self.setup_modern_ui()
        
        # Attempt to auto-detect region on startup
        self.root.after(1000, self.attempt_startup_region_detection)  # Delay to allow UI to load
        
        self.refresh_replay_list()
        
    def apply_theme_to_titlebar(self):
        """Apply dark theme to Windows title bar"""
        if not TITLE_BAR_SUPPORT:
            return
            
        try:
            version = sys.getwindowsversion()
            if version.major == 10 and version.build >= 22000:
                # Windows 11
                pywinstyles.change_header_color(self.root, "#1c1c1c")
            elif version.major == 10:
                # Windows 10
                pywinstyles.apply_style(self.root, "dark")
                # Hack to update title bar color on Windows 10
                self.root.wm_attributes("-alpha", 0.99)
                self.root.wm_attributes("-alpha", 1)
        except Exception as e:
            print(f"Could not apply title bar theme: {e}")
            
    def setup_modern_styles(self):
        """Setup modern enhanced styles - optimized for performance"""
        style = ttk.Style()
        
        # Enhanced button styles - simplified for performance
        style.configure('Accent.TButton',
                       background=self.colors['accent'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 12, 'bold'))  # Increased from 11
        
        style.map('Accent.TButton',
                 background=[('active', '#2F4F2F')])  # Dark forest green hover
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 12, 'bold'))  # Increased from 11
        
        style.map('Success.TButton',
                 background=[('active', '#228B22')])  # Forest green hover
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))  # Increased from 10
        
        style.configure('Error.TButton',
                       background=self.colors['error'],
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))  # Increased from 10
        
        # Enhanced label styles - simplified
        style.configure('Title.TLabel',
                       font=('Segoe UI', 22, 'bold'),  # Increased from 20
                       foreground=self.colors['text_primary'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 12),
                       foreground=self.colors['text_secondary'])
        
        style.configure('SectionHeader.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground=self.colors['text_primary'])
        
        style.configure('CardHeader.TLabel',
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.colors['text_primary'])
        
        style.configure('Status.TLabel',
                       font=('Segoe UI', 11),
                       foreground=self.colors['text_secondary'])
        
        style.configure('Muted.TLabel',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_muted'])
        
        # Enhanced treeview styles - optimized
        style.configure('Modern.Treeview',
                       font=('Segoe UI', 10),
                       rowheight=28,  # Slightly smaller for performance
                       borderwidth=0)
        
        style.configure('Modern.Treeview.Heading',
                       font=('Segoe UI', 10, 'bold'))  # Smaller font for performance
        
        # Text widget styling will be done manually since it's not ttk
        
    def setup_modern_ui(self):
        """Setup the modern UI with enhanced styling - optimized"""
        # Simplified main container
        main_container = tk.Frame(self.root, bg='#202020')
        main_container.pack(fill="both", expand=True)
        
        # Simplified header section
        header_frame = tk.Frame(main_container, bg='#2d2d30', height=80)  # Even more compact
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Simplified header content
        header_content = tk.Frame(header_frame, bg='#2d2d30')
        header_content.pack(expand=True, fill="both", padx=20, pady=10)
        
        # Title section with logo
        title_label = tk.Label(
            header_content,
            text="Soup's Valorant Replay Tool",
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 20, 'bold')  # Increased font size
        )
        title_label.pack(side="left")
        
        # Add logo to the right side of title
        try:
            logo_path = Path(__file__).parent / "OneTapWhite.png"
            if logo_path.exists():
                self.logo_image = tk.PhotoImage(file=str(logo_path))
                # Resize logo to fit nicely (subsample to make smaller)
                self.logo_image = self.logo_image.subsample(4)  # Single parameter for uniform scaling
                logo_label = tk.Label(
                    header_content,
                    image=self.logo_image,
                    bg='#2d2d30'
                )
                logo_label.pack(side="right", padx=(15, 0))
        except Exception as e:
            print(f"Could not load app logo: {e}")
        
        # Removed subtitle as requested
        
        # Simplified content area
        content_frame = tk.Frame(main_container, bg='#1e1e1e')
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Create simplified notebook
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill="both", expand=True, pady=(15, 0))
        
        # Setup tabs with simplified styling
        self.setup_modern_region_tab()
        self.setup_modern_selection_tab()
        self.setup_modern_control_tab()
        self.setup_modern_log_tab()
        self.setup_modern_analysis_tab()
        
        # Add interactive footer with contact links
        footer_frame = tk.Frame(main_container, bg='#1e1e1e')
        footer_frame.pack(side="bottom", fill="x", pady=(8, 3))
        
        # Create horizontal layout for contact links
        contact_container = tk.Frame(footer_frame, bg='#1e1e1e')
        contact_container.pack()
        
        # Twitter/X link
        twitter_label = tk.Label(
            contact_container,
            text="Twitter / X: @soupzachary",
            bg='#1e1e1e',
            fg='#1DA1F2',  # Twitter blue color
            font=('Segoe UI', 10, 'underline'),  # Increased from 9 to 10
            cursor="hand2"
        )
        twitter_label.pack(side="left", padx=(0, 15))
        twitter_label.bind("<Button-1>", lambda e: self.open_twitter())
        
        # Separator
        sep1 = tk.Label(contact_container, text="•", bg='#1e1e1e', fg='#888888', font=('Segoe UI', 10))  # Increased from 9 to 10
        sep1.pack(side="left", padx=(0, 15))
        
        # Email link
        email_label = tk.Label(
            contact_container,
            text="Email: zachleolewis@gmail.com",
            bg='#1e1e1e',
            fg='#34A853',  # Gmail green color
            font=('Segoe UI', 10, 'underline'),  # Increased from 9 to 10
            cursor="hand2"
        )
        email_label.pack(side="left", padx=(0, 15))
        email_label.bind("<Button-1>", lambda e: self.open_email())
        
        # Separator
        sep2 = tk.Label(contact_container, text="•", bg='#1e1e1e', fg='#888888', font=('Segoe UI', 10))  # Increased from 9 to 10
        sep2.pack(side="left", padx=(0, 15))
        
        # Discord link
        discord_label = tk.Label(
            contact_container,
            text="Discord: soup0330",
            bg='#1e1e1e',
            fg='#7289DA',  # Discord purple color
            font=('Segoe UI', 10, 'underline'),  # Increased from 9 to 10
            cursor="hand2"
        )
        discord_label.pack(side="left")
        discord_label.bind("<Button-1>", lambda e: self.open_discord())
        
    def setup_modern_region_tab(self):
        """Setup modern region selection tab"""
        region_frame = ttk.Frame(self.notebook)
        self.notebook.add(region_frame, text="🌍 Region Settings")
        
        # Main container
        main_container = tk.Frame(region_frame, bg='#202020')
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Region selection card
        region_card = self.create_modern_card(main_container, "🌍 VALORANT Region Configuration")
        region_card.pack(fill="x", pady=(0, 20))
        
        # Instructions
        instruction_text = ("Select your VALORANT region to ensure proper API connectivity. "
                          "This setting affects replay metadata loading and match detection. "
                          "If you're unsure, try 'Auto-Detect' or select the region where your VALORANT account was created. "
                          "Note: Region setting is temporary and will reset to North America when you restart the app.")
        
        instruction_frame = tk.Frame(region_card, bg='#2d2d30')
        instruction_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        instruction_label = tk.Label(
            instruction_frame,
            text=instruction_text,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 11),
            wraplength=800,
            justify="left"
        )
        instruction_label.pack(anchor="w")
        
        # Current region display
        current_region_frame = tk.Frame(region_card, bg='#2d2d30')
        current_region_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        current_label = tk.Label(
            current_region_frame,
            text="Current Region:",
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 12, 'bold')
        )
        current_label.pack(side="left")
        
        self.current_region_display = tk.Label(
            current_region_frame,
            text=f"{region_config.get_region_display_name()} ({region_config.current_region.upper()})",
            bg='#2d2d30',
            fg=self.colors['accent'],
            font=('Segoe UI', 12, 'bold')
        )
        self.current_region_display.pack(side="left", padx=(10, 0))
        
        # Region selection
        selection_frame = tk.Frame(region_card, bg='#2d2d30')
        selection_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        selection_label = tk.Label(
            selection_frame,
            text="🔍 Auto-Detect Region:",
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        selection_label.pack(anchor="w", pady=(0, 10))
        
        # Auto-detect button (only option now)
        auto_detect_btn = ttk.Button(
            selection_frame,
            text="🔍 Detect Region from VALORANT",
            command=self.auto_detect_region,
            style='Accent.TButton'
        )
        auto_detect_btn.pack(anchor="w")
        
        # Instructions for auto-detection
        detect_instruction = tk.Label(
            selection_frame,
            text="Click the button above to automatically detect your VALORANT region using your lockfile. Make sure VALORANT is running.",
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 10),
            wraplength=700,
            justify="left"
        )
        detect_instruction.pack(anchor="w", pady=(15, 0))
        
        # Status display
        self.region_status_var = tk.StringVar(value="✅ Default region: North America (temporary setting)")
        self.region_status_label = tk.Label(
            selection_frame,
            textvariable=self.region_status_var,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 10)
        )
        self.region_status_label.pack(anchor="w", pady=(15, 0))
        
    def save_region_selection(self):
        """Save the selected region"""
        try:
            selected = self.region_combo.get()
            # Extract region code from "Display Name (CODE)" format
            region_code = selected.split('(')[-1].replace(')', '').lower()
            
            if region_config.set_region(region_code):
                self.current_region_display.configure(
                    text=f"{region_config.get_region_display_name()} ({region_code.upper()})"
                )
                self.region_status_var.set("✅ Region set for this session!")
                self.log(f"🌍 Region changed to: {region_config.get_region_display_name()}", "success")
                
                # Update metadata fetcher region
                if hasattr(self, 'metadata_fetcher'):
                    self.metadata_fetcher.update_region(region_code)
                    
                # Update session monitor region
                if hasattr(self, 'session_monitor'):
                    self.session_monitor.update_region()
                
                # Refresh replay list with new region
                try:
                    self.refresh_replay_list()
                    self.log("🔄 Refreshed replay list with new region", "info")
                except Exception as refresh_error:
                    self.log(f"⚠️ Could not refresh replay list: {refresh_error}", "warning")
                    
            else:
                self.region_status_var.set("❌ Failed to save region")
                
        except Exception as e:
            self.region_status_var.set(f"❌ Error: {e}")
            
    def auto_detect_region(self):
        """Auto-detect region from VALORANT config endpoint using lockfile"""
        try:
            # Read lockfile - use generic path that works on any system
            lockfile_path = Path(os.environ['LOCALAPPDATA']) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'
            
            if not lockfile_path.exists():
                messagebox.showerror("Error", "VALORANT lockfile not found. Please make sure VALORANT is running.")
                self.region_status_var.set("❌ VALORANT lockfile not found - please start VALORANT first")
                return
            
            with open(lockfile_path, 'r') as f:
                lockfile_data = f.read().strip()
            
            # Parse lockfile (format: name:pid:port:password:protocol)
            parts = lockfile_data.split(':')
            if len(parts) != 5:
                messagebox.showerror("Error", "Invalid lockfile format")
                self.region_status_var.set("❌ Invalid lockfile format")
                return
            
            port = int(parts[2])
            password = parts[3]
            
            # Detect region using config endpoint
            self.region_status_var.set("🔍 Detecting region from VALORANT config...")
            self.root.update()
            
            detected_region = region_config.detect_region_from_config_endpoint(port, password)
            
            if detected_region:
                # Set the detected region
                if region_config.set_region(detected_region):
                    self.current_region_display.config(
                        text=f"{region_config.get_region_display_name()} ({detected_region.upper()})"
                    )
                    self.region_status_var.set(f"✅ Region detected and set to: {region_config.get_region_display_name()} ({detected_region.upper()})")
                    
                    # Show success message
                    messagebox.showinfo("Success", 
                        f"Region successfully detected!\n\n"
                        f"Region: {region_config.get_region_display_name()}\n"
                        f"Code: {detected_region.upper()}\n\n"
                        f"This region will be used for all API calls and replay metadata loading.")
                else:
                    self.region_status_var.set("❌ Failed to set detected region")
                    messagebox.showerror("Error", "Failed to set the detected region")
            else:
                self.region_status_var.set("❌ Could not detect region from VALORANT")
                messagebox.showerror("Detection Failed", 
                    "Could not detect your VALORANT region.\n\n"
                    "Please make sure:\n"
                    "• VALORANT is running\n"
                    "• You are logged into your account\n"
                    "• Your firewall/antivirus isn't blocking connections")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid port in lockfile: {e}")
            self.region_status_var.set("❌ Invalid lockfile data")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect region: {e}")
            self.region_status_var.set("❌ Region detection failed")
            
    def attempt_startup_region_detection(self):
        """Attempt to detect region automatically on startup"""
        try:
            # Check if VALORANT lockfile exists - use generic path
            lockfile_path = Path(os.environ['LOCALAPPDATA']) / 'Riot Games' / 'Riot Client' / 'Config' / 'lockfile'
            
            if lockfile_path.exists():
                self.log("🔍 VALORANT detected - attempting automatic region detection...", "info")
                # Try to detect region automatically
                self.auto_detect_region()
            else:
                self.log("ℹ️ VALORANT not detected - region will remain as default (North America)", "info")
                self.region_status_var.set("ℹ️ VALORANT not running - using default region (North America)")
                
        except Exception as e:
            self.log(f"⚠️ Startup region detection failed: {e}", "warning")
            self.region_status_var.set("⚠️ Could not auto-detect region on startup")
            
    def setup_modern_selection_tab(self):
        """Setup modern file selection tab"""
        selection_frame = ttk.Frame(self.notebook)
        self.notebook.add(selection_frame, text="📁 File Selection")
        
        # Main container - simplified, no scrolling
        main_container = tk.Frame(selection_frame, bg='#202020')
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Host replay card
        host_card = self.create_modern_card(main_container, "Step 1: Select Host Replay")
        host_card.pack(fill="both", expand=True, pady=(0, 15))
        
        # Instructions
        instruction_text = ("Select the replay you want to click 'Play' on. This replay will be temporarily "
                          "replaced during injection to load your chosen file instead.")
        
        instruction_frame = tk.Frame(host_card, bg='#2d2d30')
        instruction_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        instruction_label = tk.Label(
            instruction_frame,
            text=instruction_text,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 10),
            wraplength=800,
            justify="left"
        )
        instruction_label.pack(anchor="w")
        
        # Refresh button
        button_frame = tk.Frame(host_card, bg='#2d2d30')
        button_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        refresh_btn = ttk.Button(
            button_frame,
            text="🔄 Refresh List",
            command=self.refresh_replay_list,
            style='Accent.TButton'
        )
        refresh_btn.pack(side="right")
        
        # Modern replay list - more compact
        list_container = tk.Frame(host_card, bg='#2d2d30')
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Create modern treeview with smaller height and performance optimizations
        columns = ('filename', 'map', 'mode', 'score', 'size', 'date')
        self.replay_tree = ttk.Treeview(list_container, columns=columns, show='headings', 
                                       height=6, style='Modern.Treeview')
        
        # Performance optimization: configure virtual events
        self.replay_tree.configure(selectmode='browse')  # Single selection for performance
        
        # Configure columns with modern styling
        self.replay_tree.heading('filename', text='📄 Filename')
        self.replay_tree.heading('map', text='🗺️ Map')
        self.replay_tree.heading('mode', text='🎮 Game Mode')
        self.replay_tree.heading('score', text='🏆 Score')
        self.replay_tree.heading('size', text='📦 Size')
        self.replay_tree.heading('date', text='📅 Date Modified')
        
        self.replay_tree.column('filename', width=250, minwidth=180)
        self.replay_tree.column('map', width=100, minwidth=80)
        self.replay_tree.column('mode', width=120, minwidth=100)
        self.replay_tree.column('score', width=90, minwidth=70)
        self.replay_tree.column('size', width=80, minwidth=60)
        self.replay_tree.column('date', width=130, minwidth=110)
        
        # Modern scrollbar for tree
        tree_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.replay_tree.yview)
        self.replay_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.replay_tree.pack(side="left", fill="both", expand=True)
        tree_scrollbar.pack(side="right", fill="y")
        
        # Bind selection (but don't confirm automatically)
        self.replay_tree.bind('<<TreeviewSelect>>', self.on_host_replay_hover)
        
        # Host replay confirmation section
        confirmation_frame = tk.Frame(host_card, bg='#2d2d30')
        confirmation_frame.pack(fill="x", padx=25, pady=(10, 25))
        
        # Selected replay display
        selection_display_frame = tk.Frame(confirmation_frame, bg='#2d2d30')
        selection_display_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            selection_display_frame,
            text="Selected Host Replay:",
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 11, 'bold')
        ).pack(side="left")
        
        self.selected_host_display = tk.Label(
            selection_display_frame,
            text="⚠️ No replay selected",
            bg='#2d2d30',
            fg='#ff8c00',  # Orange warning color
            font=('Segoe UI', 11),
            wraplength=400
        )
        self.selected_host_display.pack(side="left", padx=(10, 0))
        
        # Confirmation button
        button_frame = tk.Frame(confirmation_frame, bg='#2d2d30')
        button_frame.pack(fill="x")
        
        self.confirm_host_btn = ttk.Button(
            button_frame,
            text="✅ Confirm Host Selection",
            command=self.confirm_host_selection,
            style='Success.TButton',
            state="disabled"
        )
        self.confirm_host_btn.pack(side="left")
        
        # Initialize state variables for confirmation
        self.pending_host_replay = None
        self.host_confirmed = False
        
        # Injection file card - more compact
        injection_card = self.create_modern_card(main_container, "Step 2: Select Injection File")
        injection_card.pack(fill="x", pady=(15, 0))
        
        # Instructions for injection
        injection_instruction = ("Choose the replay file you want to inject. This file will replace the host "
                               "replay temporarily, allowing you to view different match data.")
        
        injection_inst_frame = tk.Frame(injection_card, bg='#2d2d30')
        injection_inst_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        injection_inst_label = tk.Label(
            injection_inst_frame,
            text=injection_instruction,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 10),
            wraplength=800,
            justify="left"
        )
        injection_inst_label.pack(anchor="w")
        
        # Modern file selection with enhanced dark theme container
        file_selection_frame = tk.Frame(injection_card, bg='#2d2d30')
        file_selection_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        file_label = tk.Label(
            file_selection_frame,
            text="💾 Selected File:",
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 11, 'bold')
        )
        file_label.pack(anchor="w", pady=(0, 8))
        
        # File selection row with dark theme container
        file_row = tk.Frame(file_selection_frame, bg='#2d2d30')
        file_row.pack(fill="x")
        
        self.injection_file_var = tk.StringVar(value="No file selected")
        
        # Create a dark-themed container that matches the UI theme
        input_container = tk.Frame(file_row, bg='#1a1a1a', relief="flat", bd=0)
        input_container.pack(side="left", fill="x", expand=True, padx=(0, 12))
        
        # Add a subtle border that matches the theme
        border_frame = tk.Frame(input_container, bg=self.colors['border'], height=1)
        border_frame.pack(fill="x", side="bottom")
        
        # Use a Label with consistent dark styling that matches the log area
        self.injection_file_label = tk.Label(
            input_container,
            textvariable=self.injection_file_var,
            font=('Consolas', 10),
            bg='#1a1a1a',  # Match the log text background color
            fg=self.colors['text_primary'],  # Use theme's primary text color
            anchor="w",
            padx=8,
            pady=6
        )
        self.injection_file_label.pack(fill="both", expand=True)
        
        browse_btn = ttk.Button(
            file_row,
            text="📂 Browse Files",
            command=self.browse_injection_file,
            style='Accent.TButton'
        )
        browse_btn.pack(side="right")
        
    def create_modern_card(self, parent, title):
        """Create a modern card container - simplified for performance"""
        # Simplified card frame
        card_frame = tk.Frame(parent, bg='#2d2d30', relief="flat", bd=1)
        
        # Simplified header
        header_label = tk.Label(
            card_frame,
            text=title,
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 13, 'bold'),
            anchor="w"
        )
        header_label.pack(fill="x", padx=20, pady=(15, 10))
        
        return card_frame
        
    def setup_modern_control_tab(self):
        """Setup modern control tab"""
        control_frame = ttk.Frame(self.notebook)
        self.notebook.add(control_frame, text="⚡ Injection Control")
        
        # Main container
        main_container = tk.Frame(control_frame, bg='#202020')
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Control card
        control_card = self.create_modern_card(main_container, "Step 3: Start Injection Process")
        control_card.pack(fill="x", pady=(0, 20))
        
        # Instructions
        instruction_text = ("Ready to inject? Click START INJECTION below, then navigate to VALORANT and "
                          "click 'Play' on your selected replay. The injection will happen automatically. "
                          "Use 'Stop Monitor' to cancel the injection monitoring if you change your mind or "
                          "need to select different files. The monitor will automatically stop after a successful injection.")
        
        instruction_frame = tk.Frame(control_card, bg='#2d2d30')
        instruction_frame.pack(fill="x", padx=25, pady=(0, 30))
        
        instruction_label = tk.Label(
            instruction_frame,
            text=instruction_text,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 12),
            wraplength=800,  # Reduced from 900 to account for padding
            justify="left"
        )
        instruction_label.pack(anchor="w")
        
        # Modern button layout
        button_container = tk.Frame(control_card, bg='#2d2d30')
        button_container.pack(pady=(0, 30))
        
        # Main action button
        self.start_btn = ttk.Button(
            button_container,
            text="🚀 START INJECTION",
            command=self.start_injection_monitoring,
            style='Success.TButton'
        )
        self.start_btn.pack(pady=10)
        
        # Secondary buttons row
        secondary_buttons = tk.Frame(button_container, bg='#2d2d30')
        secondary_buttons.pack(pady=(15, 0))
        
        self.stop_btn = ttk.Button(
            secondary_buttons,
            text="⏹️ Stop Monitor",
            command=self.stop_monitoring,
            style='Warning.TButton',
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=(0, 15))
        
        self.restore_btn = ttk.Button(
            secondary_buttons,
            text="🔄 Restore Original",
            command=self.restore_original,
            style='Error.TButton',
            state="disabled"
        )
        self.restore_btn.pack(side="left")
        
        # Status card
        status_card = self.create_modern_card(main_container, "📊 System Status")
        status_card.pack(fill="x")
        
        # Status content
        status_content = tk.Frame(status_card, bg='#2d2d30')
        status_content.pack(fill="x", padx=25, pady=(0, 25))
        
        # Status indicators
        self.status_var = tk.StringVar(value="Ready - Select files and start monitoring")
        self.status_label = tk.Label(
            status_content,
            textvariable=self.status_var,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 11)
        )
        self.status_label.pack(anchor="w", pady=(0, 10))
        
        self.monitor_status_var = tk.StringVar(value="🔴 Monitor: Stopped")
        self.monitor_status_label = tk.Label(
            status_content,
            textvariable=self.monitor_status_var,
            bg='#2d2d30',
            fg='#F44336',  # Red color for stopped state
            font=('Segoe UI', 11, 'bold')
        )
        self.monitor_status_label.pack(anchor="w")
        
    def setup_modern_log_tab(self):
        """Setup modern log tab"""
        log_frame = ttk.Frame(self.notebook)
        self.notebook.add(log_frame, text="📋 Activity Log")
        
        # Main container
        main_container = tk.Frame(log_frame, bg='#202020')
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Log card
        log_card = self.create_modern_card(main_container, "📝 Real-time Activity Log")
        log_card.pack(fill="both", expand=True)
        
        # Log content area
        log_content = tk.Frame(log_card, bg='#2d2d30')
        log_content.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        # Modern text widget with styling
        self.log_text = tk.Text(
            log_content,
            bg='#1a1a1a',
            fg=self.colors['text_primary'],
            font=('Consolas', 11),
            wrap=tk.WORD,
            borderwidth=0,
            insertbackground=self.colors['text_primary'],
            selectbackground=self.colors['selected'],
            relief="flat",
            padx=15,
            pady=15
        )
        
        # Modern scrollbar for log
        log_scrollbar = ttk.Scrollbar(log_content, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
        
        # Configure text tags for colored output
        self.log_text.tag_configure("success", foreground="#4caf50")
        self.log_text.tag_configure("warning", foreground="#ff9800")
        self.log_text.tag_configure("error", foreground="#f44336")
        self.log_text.tag_configure("info", foreground="#2196f3")
        self.log_text.tag_configure("timestamp", foreground="#999999")
        
        # Initial log messages
        self.log("🎉 VALORANT Replay Injector Ready", "success")
        self.log("👋 Welcome! Select files to begin injection process", "info")
        
    def setup_modern_analysis_tab(self):
        """Setup modern replay downloader tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="⬇ Replay Downloader")
        
        # Main container
        main_container = tk.Frame(analysis_frame, bg='#202020')
        main_container.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Analysis card
        analysis_card = self.create_modern_card(main_container, "⬇ Download Your Replays")
        analysis_card.pack(fill="both", expand=True)
        
        # Instructions
        instruction_frame = tk.Frame(analysis_card, bg='#2d2d30')
        instruction_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        instruction_text = ("Download your local replay files with descriptive names. "
                          "Make sure you have downloaded the replays you want in the VALORANT client first. "
                          "Select a replay below to export it with a readable filename.")
        
        instruction_label = tk.Label(
            instruction_frame,
            text=instruction_text,
            bg='#2d2d30',
            fg=self.colors['text_secondary'],
            font=('Segoe UI', 12),  # Increased from 11
            wraplength=800,  # Reduced from 900 to account for padding
            justify="left"
        )
        instruction_label.pack(anchor="w")
        
        # Controls row
        controls_frame = tk.Frame(analysis_card, bg='#2d2d30')
        controls_frame.pack(fill="x", padx=25, pady=(0, 20))
        
        refresh_analysis_btn = ttk.Button(
            controls_frame,
            text="🔄 Refresh Analysis",
            command=self.refresh_analysis,
            style='Accent.TButton'
        )
        refresh_analysis_btn.pack(side="right")
        
        # Analysis table
        table_container = tk.Frame(analysis_card, bg='#2d2d30')
        table_container.pack(fill="both", expand=True, padx=25, pady=(0, 20))
        
        # Modern analysis treeview
        analysis_columns = ('filename', 'map', 'mode', 'score', 'date', 'size')
        self.analysis_tree = ttk.Treeview(table_container, columns=analysis_columns, 
                                         show='headings', height=8, style='Modern.Treeview')  # Reduced height from 12 to 8
        
        # Configure columns
        self.analysis_tree.heading('filename', text='📄 Original Filename')
        self.analysis_tree.heading('map', text='🗺️ Map')
        self.analysis_tree.heading('mode', text='🎮 Game Mode')
        self.analysis_tree.heading('score', text='🏆 Score')
        self.analysis_tree.heading('date', text='📅 Date')
        self.analysis_tree.heading('size', text='📦 Size')
        
        self.analysis_tree.column('filename', width=280, minwidth=200)
        self.analysis_tree.column('map', width=120, minwidth=80)
        self.analysis_tree.column('mode', width=140, minwidth=100)
        self.analysis_tree.column('score', width=100, minwidth=80)
        self.analysis_tree.column('date', width=130, minwidth=100)
        self.analysis_tree.column('size', width=90, minwidth=70)
        
        # Analysis scrollbar
        analysis_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=analysis_scrollbar.set)
        
        self.analysis_tree.pack(side="left", fill="both", expand=True)
        analysis_scrollbar.pack(side="right", fill="y")
        
        # Export controls
        export_frame = tk.Frame(analysis_card, bg='#2d2d30')
        export_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        export_label = tk.Label(
            export_frame,
            text="💾 Export Selected Replay:",
            bg='#2d2d30',
            fg=self.colors['text_primary'],
            font=('Segoe UI', 12, 'bold')
        )
        export_label.pack(side="left")
        
        self.export_btn = ttk.Button(
            export_frame,
            text="📤 Export with Descriptive Name",
            command=self.export_selected_replay,
            style='Accent.TButton',  # Changed from Success.TButton to be more visible
            state="disabled"
        )
        self.export_btn.pack(side="right", padx=(10, 0), pady=5)  # Added padding
        
        # Bind selection events
        self.analysis_tree.bind('<<TreeviewSelect>>', self.on_analysis_select)
        
    # All the original functionality methods remain exactly the same
    def refresh_replay_list(self):
        """Refresh the replay list with threaded metadata loading"""
        try:
            # Clear existing items
            for item in self.replay_tree.get_children():
                self.replay_tree.delete(item)
            
            # Get replays
            replays = self.file_manager.get_downloaded_replays()
            
            if not replays:
                self.replay_tree.insert('', 'end', values=(
                    'No replay files found', '', '', '', '', ''
                ))
                return
            
            self.log(f"🔍 Loading metadata for {len(replays)} replay files...", "info")
            
            # Store replays for metadata loading
            self.replay_data = {}
            
            # First, add all replays with basic info (no metadata yet)
            for i, replay in enumerate(replays):
                # Format size and date
                size_mb = round(replay['size'] / (1024 * 1024), 1)
                size_str = f"{size_mb} MB"
                date_str = replay['date_modified'].strftime("%Y-%m-%d %H:%M")
                
                # Insert with "Loading..." placeholders
                item_id = self.replay_tree.insert('', 'end', values=(
                    replay['filename'],
                    'Loading...',
                    'Loading...',
                    'Loading...',
                    size_str,
                    date_str
                ))
                # Store replay data for later metadata update
                self.replay_data[item_id] = replay
            
            # Now load metadata in background thread
            def load_metadata_async():
                for item_id, replay in self.replay_data.items():
                    try:
                        # Get metadata using just the filename
                        filename = replay['filename']
                        metadata = self.metadata_fetcher.get_replay_metadata(filename)
                        
                        if metadata:
                            map_name = metadata.get('map', 'Unknown')
                            mode = metadata.get('mode', 'Unknown')
                            score = metadata.get('score', 'Unknown')
                        else:
                            map_name = 'Unknown'
                            mode = 'Unknown'
                            score = 'Unknown'
                        
                        # Update UI in main thread
                        self.root.after(0, self._update_tree_item, item_id, map_name, mode, score)
                        
                    except Exception as e:
                        self.root.after(0, self._update_tree_item, item_id, f'Error: {e}', '', '')
            
            # Start metadata loading in background
            metadata_thread = threading.Thread(target=load_metadata_async, daemon=True)
            metadata_thread.start()
            
            self.log(f"✅ Found {len(replays)} replay files", "success")
            
        except Exception as e:
            self.log(f"❌ Error refreshing replay list: {e}", "error")
    
    def _update_tree_item(self, item_id, map_name, mode, score):
        """Update tree item with metadata in main thread"""
        try:
            current_values = list(self.replay_tree.item(item_id, 'values'))
            if len(current_values) >= 6:
                current_values[1] = map_name  # Map
                current_values[2] = mode      # Mode  
                current_values[3] = score     # Score
                self.replay_tree.item(item_id, values=current_values)
        except Exception as e:
            print(f"Error updating tree item: {e}")
            
    def on_host_replay_hover(self, event):
        """Handle host replay hover/selection (shows preview but doesn't confirm)"""
        selection = self.replay_tree.selection()
        if not selection:
            self.selected_host_display.configure(
                text="⚠️ No replay selected",
                fg='#ff8c00'
            )
            self.confirm_host_btn.configure(state="disabled")
            self.pending_host_replay = None
            return
            
        item = self.replay_tree.item(selection[0])
        filename = item['values'][0]
        
        if filename == 'No replay files found':
            return
        
        # Find full replay info from stored data or file manager
        if hasattr(self, 'replay_data') and selection[0] in self.replay_data:
            # Use stored data from threaded loading
            self.pending_host_replay = self.replay_data[selection[0]]
        else:
            # Fallback: find in file manager data
            replays = self.file_manager.get_downloaded_replays()
            for replay in replays:
                if replay['filename'] == filename:
                    self.pending_host_replay = replay
                    break
        
        if self.pending_host_replay:
            # Show preview of selected file
            self.selected_host_display.configure(
                text=f"🎯 Preview: {filename}",
                fg=self.colors['text_secondary']
            )
            self.confirm_host_btn.configure(state="normal")
    
    def confirm_host_selection(self):
        """Confirm the host replay selection"""
        if self.pending_host_replay:
            self.selected_host_replay = self.pending_host_replay
            self.host_confirmed = True
            
            filename = self.selected_host_replay['filename']
            
            # Update display to show confirmed status
            self.selected_host_display.configure(
                text=f"✅ Confirmed: {filename}",
                fg='#4CAF50'  # Green color for confirmed
            )
            
            self.confirm_host_btn.configure(
                text="✅ Host Confirmed",
                state="disabled"
            )
            
            self.log(f"✅ Host replay confirmed: {filename}", "success")
            self.update_injection_ready()
            
    def on_host_replay_select(self, event):
        """Legacy method - now redirects to hover method"""
        self.on_host_replay_hover(event)
                
    def browse_injection_file(self):
        """Browse for injection file"""
        file_path = filedialog.askopenfilename(
            title="Select Injection Replay File",
            filetypes=[("VALORANT Replay Files", "*.vrf"), ("All Files", "*.*")],
            defaultextension=".vrf"
        )
        
        if file_path:
            self.selected_injection_file = file_path
            filename = Path(file_path).name
            self.injection_file_var.set(filename)
            self.log(f"📁 Selected injection file: {filename}", "info")
            self.update_injection_ready()
            
    def update_injection_ready(self):
        """Update injection ready status"""
        if (hasattr(self, 'host_confirmed') and self.host_confirmed and 
            self.selected_host_replay and self.selected_injection_file):
            self.injection_ready = True
            self.status_var.set("✅ Ready for injection!")
        else:
            self.injection_ready = False
            if not hasattr(self, 'host_confirmed') or not self.host_confirmed:
                self.status_var.set("⏳ Confirm host replay selection first")
            elif not self.selected_injection_file:
                self.status_var.set("⏳ Select injection file")
            else:
                self.status_var.set("⏳ Select both files to continue")
            
    def start_injection_monitoring(self):
        """Start injection monitoring"""
        if not self.injection_ready:
            messagebox.showwarning("Not Ready", "Please select both host replay and injection file first!")
            return
        
        if not self.session_monitor.get_session_info():
            messagebox.showerror("VALORANT Not Running", 
                               "VALORANT client not detected. Please start VALORANT first!")
            return
        
        if not self.selected_host_replay or not self.selected_injection_file:
            messagebox.showerror("Selection Error", "Host replay or injection file not selected!")
            return
        
        self.monitoring_active = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.monitor_status_var.set("🟢 Monitor: Active")
        self.monitor_status_label.configure(fg='#4CAF50')  # Green color for active
        
        # Console output
        print("\n" + "="*50)
        print("INJECTION MONITORING STARTED")
        print("="*50)
        print(f"Host replay: {self.selected_host_replay['filename']}")
        print(f"Host path: {self.selected_host_replay['path']}")
        print(f"Injection file: {Path(self.selected_injection_file).name}")
        print(f"Injection path: {self.selected_injection_file}")
        print("Click 'Play' on your replay in VALORANT to trigger injection!")
        print("="*50)
        
        self.log("🚀 INJECTION MONITORING STARTED", "success")
        self.log(f"🎯 Host: {self.selected_host_replay['filename']}", "info")
        self.log(f"💉 Injection: {Path(self.selected_injection_file).name}", "info")
        self.log("🎮 Click 'Play' on your selected replay in VALORANT now!", "warning")
        
        # Show popup reminder to user
        messagebox.showinfo("Injection Active", 
                           f"Monitoring started! 🎮\n\n"
                           f"Now go to VALORANT and click 'Play' on:\n"
                           f"📁 {self.selected_host_replay['filename']}\n\n"
                           f"The injection will happen automatically when the replay starts loading!")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.custom_monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def custom_monitoring_loop(self):
        """Custom monitoring loop"""
        previous_state = None
        injection_ready = True
        
        print("Starting live monitoring loop...")
        
        while self.monitoring_active:
            try:
                session = self.session_monitor.get_session_info()
                if not session:
                    time.sleep(1)
                    continue
                
                current_state = session.get('loopState')
                current_version = session.get('version')
                
                # State change detection
                if current_state != previous_state:
                    timestamp = time.strftime("%H:%M:%S")
                    print(f"[{timestamp}] State change: {previous_state} -> {current_state} (version: {current_version})")
                    self.log(f"🔄 [{timestamp}] State: {previous_state} -> {current_state}", "info")
                    
                    # Detect replay start
                    if previous_state == 'MENUS' and current_state == 'REPLAY' and injection_ready:
                        if not self.selected_host_replay or not self.selected_injection_file:
                            print("Cannot inject - missing selections!")
                            continue
                            
                        print("REPLAY LOADING DETECTED!")
                        print("PERFORMING AUTOMATIC INJECTION...")
                        self.log("🎯 REPLAY LOADING DETECTED!", "success")
                        self.log("💉 PERFORMING AUTOMATIC INJECTION...", "success")
                        
                        # Convert to Path objects
                        host_path = Path(self.selected_host_replay['path'])
                        injection_path = Path(self.selected_injection_file)
                        
                        # Create backup
                        backup_success = self.file_manager.backup_file(host_path)
                        if backup_success:
                            print(f"Backup created: {self.file_manager.current_backup}")
                            self.log("💾 Backup created", "info")
                        else:
                            print("Backup creation failed!")
                            self.log("❌ Backup creation failed!", "error")
                            continue
                        
                        # Perform injection
                        success = self.file_manager.inject_replay_file(host_path, injection_path)
                        if success:
                            print("INJECTION SUCCESSFUL!")
                            print(f"File swapped: {injection_path.stat().st_size} bytes")
                            self.log("✅ INJECTION SUCCESSFUL!", "success")
                            self.status_var.set("INJECTED - Replay file swapped!")
                            self.restore_btn.configure(state="normal")
                        else:
                            print("Injection failed!")
                            self.log("❌ Injection failed!", "error")
                    
                    # Detect replay end
                    elif previous_state == 'REPLAY' and current_state == 'MENUS':
                        print("Replay ended - AUTO-RESTORING original file...")
                        self.log("🔄 Replay ended - Auto-restoring...", "warning")
                        self.restore_original()
                
                previous_state = current_state
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                self.log(f"❌ Monitor error: {e}", "error")
                time.sleep(1)
        
        print("Session monitoring stopped")
        self.log("⏹️ Monitoring stopped", "warning")
        
    def stop_monitoring(self):
        """Stop session monitoring"""
        self.monitoring_active = False
        
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.monitor_status_var.set("🔴 Monitor: Stopped")
        self.monitor_status_label.configure(fg='#F44336')  # Red color for stopped
        
        self.log("⏹️ Stopped monitoring", "warning")
        
    def restore_original(self):
        """Restore original replay file"""
        self.log("🔄 Restoring original replay file...", "info")
        
        success = self.file_manager.restore_original_file()
        
        if success:
            print("Original file restored!")
            self.log("✅ Original file restored!", "success")
            self.status_var.set("✅ Original file restored")
            self.restore_btn.configure(state="disabled")
        else:
            print("Restore failed!")
            self.log("❌ Restore failed!", "error")
            
    def on_monitor_error(self, error):
        """Handle monitoring errors"""
        self.log(f"❌ Monitor error: {error}", "error")
        
    def log(self, message, tag=""):
        """Add message to log with optional styling - optimized"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Batch log updates for better performance
        self.root.after_idle(self._update_log, timestamp, message, tag)
        
    def _update_log(self, timestamp, message, tag):
        """Internal method to update log display"""
        # Insert timestamp with special formatting
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insert message with tag if provided
        if tag:
            self.log_text.insert(tk.END, f"{message}\n", tag)
        else:
            self.log_text.insert(tk.END, f"{message}\n")
        
        # Limit log size for performance
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 1000:  # Keep only last 1000 lines
            self.log_text.delete(1.0, f"{lines-1000}.0")
        
        self.log_text.see(tk.END)
        
    def refresh_analysis(self):
        """Refresh the replay analysis table"""
        try:
            # Clear existing items
            for item in self.analysis_tree.get_children():
                self.analysis_tree.delete(item)
            
            # Get replays
            replays = self.file_manager.get_downloaded_replays()
            
            if not replays:
                self.analysis_tree.insert('', 'end', values=(
                    'No replay files found', '', '', '', '', ''
                ))
                return
            
            self.log("🔍 Analyzing replay files...", "info")
            
            # Analyze each replay
            for i, replay in enumerate(replays):
                try:
                    # Get metadata using just the filename (like the original)
                    filename = replay['filename']
                    metadata = self.metadata_fetcher.get_replay_metadata(filename)
                    
                    if metadata:
                        map_name = metadata.get('map', 'Unknown')
                        mode = metadata.get('mode', 'Unknown')
                        score = metadata.get('score', 'Unknown')
                    else:
                        map_name = 'Error loading'
                        mode = 'Error loading'
                        score = 'Error loading'
                    
                    # Format size and date
                    size_mb = round(replay['size'] / (1024 * 1024), 1)
                    size_str = f"{size_mb} MB"
                    date_str = replay['date_modified'].strftime("%Y-%m-%d")
                    
                    self.analysis_tree.insert('', 'end', values=(
                        replay['filename'],
                        map_name,
                        mode,
                        score,
                        date_str,
                        size_str
                    ))
                    
                except Exception as e:
                    self.analysis_tree.insert('', 'end', values=(
                        replay['filename'],
                        f'Error: {e}',
                        '',
                        '',
                        replay['date_modified'].strftime("%Y-%m-%d"),
                        f"{round(replay['size'] / (1024 * 1024), 1)} MB"
                    ))
            
            self.log(f"✅ Analysis complete - {len(replays)} replays processed", "success")
            
        except Exception as e:
            self.log(f"❌ Error analyzing replays: {e}", "error")
            
    def on_analysis_select(self, event):
        """Handle analysis table selection"""
        selection = self.analysis_tree.selection()
        if selection:
            self.export_btn.configure(state="normal")
        else:
            self.export_btn.configure(state="disabled")
            
    def export_selected_replay(self):
        """Export selected replay with descriptive name"""
        selection = self.analysis_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a replay to export!")
            return
            
        item = self.analysis_tree.item(selection[0])
        values = item['values']
        
        if len(values) < 6:
            return
            
        filename = values[0]
        map_name = values[1]
        mode = values[2]
        score = values[3]
        
        if filename == 'No replay files found' or 'Error:' in map_name:
            messagebox.showerror("Cannot Export", "Cannot export this replay due to errors!")
            return
        
        # Find the original file
        replays = self.file_manager.get_downloaded_replays()
        source_file = None
        for replay in replays:
            if replay['filename'] == filename:
                source_file = replay['path']
                break
        
        if not source_file:
            messagebox.showerror("File Not Found", "Could not locate the original replay file!")
            return
        
        # Generate descriptive filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_map = map_name.replace(' ', '_').replace('/', '_')
        safe_mode = mode.replace(' ', '_').replace('/', '_')
        safe_score = score.replace(' ', '_').replace('/', '_').replace('(', '').replace(')', '')
        
        # Create descriptive name
        if score != 'Unknown' and score != '':
            descriptive_name = f"VALORANT_{safe_map}_{safe_mode}_{safe_score}_{timestamp}.vrf"
        else:
            descriptive_name = f"VALORANT_{safe_map}_{safe_mode}_{timestamp}.vrf"
        
        # Ask user where to save
        save_path = filedialog.asksaveasfilename(
            title="Export Replay As",
            defaultextension=".vrf",
            filetypes=[("VALORANT Replay Files", "*.vrf"), ("All Files", "*.*")],
            initialfile=descriptive_name
        )
        
        if save_path:
            try:
                import shutil
                shutil.copy2(source_file, save_path)
                self.log(f"✅ Exported replay to: {Path(save_path).name}", "success")
                messagebox.showinfo("Export Successful", f"Replay exported successfully to:\n{save_path}")
            except Exception as e:
                self.log(f"❌ Export failed: {e}", "error")
                messagebox.showerror("Export Failed", f"Failed to export replay:\n{e}")
    
    def open_twitter(self):
        """Open Twitter/X profile"""
        import webbrowser
        webbrowser.open("https://twitter.com/soupzachary")
        
    def open_email(self):
        """Open email client"""
        import webbrowser
        webbrowser.open("mailto:zachleolewis@gmail.com")
        
    def open_discord(self):
        """Copy Discord username to clipboard and show message"""
        try:
            import pyperclip
            pyperclip.copy("soup0330")
            messagebox.showinfo("Discord", 
                              "Discord username 'soup0330' copied to clipboard!\n\n"
                              "Add me as a friend on Discord or find me in VALORANT servers.")
        except ImportError:
            # Fallback if pyperclip not available
            self.root.clipboard_clear()
            self.root.clipboard_append("soup0330")
            messagebox.showinfo("Discord", 
                              "Discord username 'soup0330' copied to clipboard!\n\n"
                              "Add me as a friend on Discord!")
        
    def run(self):
        """Start the application"""
        # Handle window closing
        def on_closing():
            self.monitoring_active = False
            # Clean up lock file
            if hasattr(self, 'lock_file') and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            self.root.destroy()
            
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        self.root.mainloop()

def main():
    """Main function"""
    app = ModernReplayInjectorGUI()
    app.run()

if __name__ == "__main__":
    main()
