#!/usr/bin/env python3
"""
🪶 Ibis Setup 🪶 - Desktop configuration tool for Ibis Dash
WIZARD STYLE - Step by step setup with loading popups
Version 4.0 - UI polish: auto-advance, Personalize tab, Options tab, consistent styling 🪶🪶🪶

Steps:
1. Connect - Connect to board via USB (auto-loads existing config)
2. WiFi - Enter WiFi credentials (tests connection)
3. Strava - Enter API credentials, get refresh token
4. Personalize - Name, sport, goal, refresh interval
5. Options (🤌) - Delete data from board
"""

import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import json
import time
import webbrowser
import threading
import urllib.parse
import urllib.request
import http.server
import socketserver
import random

APP_TITLE = "🪶 Ibis Setup 🪶"
APP_VERSION = "4.1"
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 630
LOADING_WIDTH = 450
LOADING_HEIGHT = 250
BAUD_RATE = 115200
SERIAL_TIMEOUT = 15
WRITE_TIMEOUT = 15

# ╔═══════════════════════════════════════════════════════════════════════════════╗
# ║                        🎨 COLOR SCHEME - EDIT HERE 🎨                         ║
# ╚═══════════════════════════════════════════════════════════════════════════════╝

COLOR_BG = "#101022"
COLOR_CARD = "#102a4a"
COLOR_LOADING_BG = "#0a0a1a"
COLOR_ACCENT = "#e94560"
COLOR_SUCCESS = "#4fd2b0"
COLOR_DANGER = "#e94560"
COLOR_TEXT = "#eef1fa"
COLOR_TEXT_DIM = "#9da3cc"
COLOR_LINK = "#7bb8ff"
COLOR_BTN_PRIMARY = "#e94560"
COLOR_BTN_PRIMARY_HOVER = "#ff5e79"
COLOR_BTN_SECONDARY = "#1c3f7a"
COLOR_BTN_SECONDARY_HOVER = "#285799"
COLOR_BTN_SUCCESS = "#4fd2b0"
COLOR_BTN_SUCCESS_HOVER = "#6ae5c4"
COLOR_BTN_DANGER = "#e94560"
COLOR_BTN_DANGER_HOVER = "#ff5e79"
COLOR_BTN_TEXT = "#ffffff"
COLOR_CONNECTED = "#4fd2b0"
COLOR_DISCONNECTED = "#e94560"
COLOR_STEP_INACTIVE = "#1c3f7a"
COLOR_STEP_ACTIVE = "#e94560"
COLOR_STEP_COMPLETE = "#4fd2b0"

# Consistent subtitle font (white, same as field labels)
SUBTITLE_FONT = ('Segoe UI', 11)
SUBTITLE_COLOR = "#ffffff"

SPORT_TYPES = ["Run", "Ride", "Swim", "Hike", "Walk"]
TRACK_PERIODS = ["Yearly", "Monthly", "Weekly"]
REFRESH_OPTIONS = [
    ("Every hour", 1, "~3-5 days battery"),
    ("Every 6 hours", 6, "~2-3 weeks battery"),
    ("Every 12 hours", 12, "~1 month battery"),
    ("Once a day", 24, "~2 months battery"),
    ("Every 2 days", 48, "~3-4 months battery"),
    ("Once a week", 168, "~6+ months battery")
]
F = "🪶"

OAUTH_REDIRECT_PORT = 8089
OAUTH_REDIRECT_URI = f"http://localhost:{OAUTH_REDIRECT_PORT}/callback"
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_TOKEN_URL = "https://www.strava.com/oauth/token"

# Funny loading messages for different operations
FUNNY_MESSAGES = {
    'connect': [
        "Waking up the sleepy ibis...",
        "Teaching the ibis to speak USB...",
        "Bribing the ibis with virtual worms...",
        "Convincing the ibis we're friends..."
    ],
    'load_config': [
        "Ibis is rummaging through its nest...",
        "Reading the ibis's diary...",
        "Asking the ibis what it remembers...",
        "Ibis is checking its notes..."
    ],
    'save_config': [
        "Ibis is writing this down...",
        "Teaching the ibis your WiFi password...",
        "Ibis is taking notes (with its beak)...",
        "Storing secrets in the ibis nest..."
    ],
    'test_wifi': [
        "Ibis is looking for the internet...",
        "Ibis is sniffing for WiFi signals...",
        "Teaching the ibis to connect to WiFi...",
        "Ibis is trying to remember the password...",
        "Checking if the internet has worms..."
    ],
    'fetch_strava': [
        "Ibis is stalking your Strava profile...",
        "Ibis is counting your kilometers...",
        "Ibis is judging your running pace...",
        "Fetching your athletic achievements...",
        "Ibis is very impressed with your stats...",
        "Downloading proof of your fitness..."
    ],
    'update_display': [
        "Ibis is pecking at the screen...",
        "Ibis is painting with e-ink...",
        "Ibis is doing its screen dance...",
        "Arranging pixels with beak precision...",
        "Ibis is making art happen...",
        "The ibis is very focused right now..."
    ],
    'wipe': [
        "Ibis is forgetting everything...",
        "Erasing the ibis's memories...",
        "Ibis is having a fresh start...",
        "Wiping the ibis's tiny brain clean...",
        "Teaching the ibis to forget..."
    ],
    'updating': [
        "Updating the ibis's knowledge...",
        "Teaching the ibis new tricks...",
        "Ibis is learning your preferences...",
        "Refreshing the ibis's memory..."
    ]
}


class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, callback=None, **kwargs):
        self.callback = callback
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path.startswith('/callback'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            if 'code' in params:
                self.wfile.write("""<html><body style="font-family:'Segoe UI',Arial,sans-serif;background:#1a1a2e;color:#eaeaea;text-align:center;padding:60px 20px;">
                    <h1 style="color:#4ecca3;font-size:52px;font-weight:900;letter-spacing:3px;margin-bottom:10px;">SUCCESS!!!</h1>
                    <p style="font-size:20px;color:#9da3cc;margin-top:20px;">YOU CAN NOW CLOSE THIS WINDOW</p></body></html>""".encode())
                if self.callback:
                    self.callback(params['code'][0])
            else:
                self.wfile.write(b"<html><body style='font-family:Arial;background:#1a1a2e;color:#e94560;text-align:center;padding:50px;'><h1>Authorization failed.</h1></body></html>")
                if self.callback:
                    self.callback(None)
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


class IbisSetupWizard:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        
        self.serial_conn = None
        self.connected = False
        self.current_step = 0
        self.total_steps = 5  # Connect, WiFi, Strava, Personalize, Options
        self.loading_overlay = None
        self.loading_animation_id = None
        
        # Track which steps are complete (properly validated)
        self.wifi_complete = False
        self.strava_complete = False
        
        # Track if setup has been completed at least once this session
        self.setup_done = False
        
        # Data variables
        self.port_var = tk.StringVar()
        self.ssid_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.client_id_var = tk.StringVar()
        self.client_secret_var = tk.StringVar()
        self.refresh_token_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.sport_var = tk.StringVar(value="Run")
        self.period_var = tk.StringVar(value="Yearly")
        self.goal_var = tk.StringVar(value="1000")
        self.refresh_var = tk.StringVar(value="Once a day")
        self.battery_var = tk.StringVar(value="~2 months battery")
        self.token_status_var = tk.StringVar(value="")
        
        self.create_ui()
        self.show_step(0)
        self.scan_ports()
    
    def create_ui(self):
        self.main_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Header
        header = tk.Frame(self.main_frame, bg=COLOR_BG)
        header.pack(fill=tk.X, pady=(0, 12))
        tk.Label(header, text=f"{F} Ibis Setup {F}", font=('Segoe UI', 24, 'bold'),
                bg=COLOR_BG, fg=COLOR_ACCENT).pack()
        
        # Step indicator
        self.create_step_indicator()
        
        # Content area
        self.content_frame = tk.Frame(self.main_frame, bg=COLOR_CARD)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=12)
        
        # Navigation
        self.create_navigation()
    
    def create_step_indicator(self):
        indicator = tk.Frame(self.main_frame, bg=COLOR_BG)
        indicator.pack(fill=tk.X, pady=(0, 8))
        
        steps = ["Connect", "WiFi", "Strava", "Personalize", "Options"]
        self.step_labels = []
        self.step_dots = []
        
        inner = tk.Frame(indicator, bg=COLOR_BG)
        inner.pack(fill=tk.X)
        
        for i, name in enumerate(steps):
            frame = tk.Frame(inner, bg=COLOR_BG)
            frame.pack(side=tk.LEFT, expand=True, padx=6)

            
            dot = tk.Label(frame, text="\u25CF", font=('Segoe UI', 14), bg=COLOR_BG, 
                          fg=COLOR_STEP_INACTIVE, cursor='hand2')
            dot.pack()
            dot.bind('<Button-1>', lambda e, step=i: self.jump_to_step(step))
            self.step_dots.append(dot)
            
            label = tk.Label(frame, text=name, font=('Segoe UI', 8), bg=COLOR_BG, 
                           fg=COLOR_TEXT_DIM, cursor='hand2')
            label.pack()
            label.bind('<Button-1>', lambda e, step=i: self.jump_to_step(step))
            self.step_labels.append(label)
    
    def jump_to_step(self, step):
        """Allow jumping to any step once connected"""
        if not self.connected and step > 0:
            self.show_popup(f"{F} Not Connected", "Please connect to your board first!", popup_type="warning")
            return
        self.show_step(step)
    
    def update_step_indicator(self):
        """Update step indicator with checkmarks only for completed steps"""
        for i, (dot, label) in enumerate(zip(self.step_dots, self.step_labels)):
            # Options tab (4) always shows pinched fingers emoji, never changes
            if i == 4:
                if i == self.current_step:
                    dot.config(fg=COLOR_STEP_ACTIVE, text="\U0001F90C")
                    label.config(fg=COLOR_TEXT)
                else:
                    dot.config(fg=COLOR_STEP_INACTIVE, text="\U0001F90C")
                    label.config(fg=COLOR_TEXT_DIM)
                continue
            
            is_complete = False
            if i == 0:
                is_complete = self.connected
            elif i == 1:
                is_complete = self.wifi_complete
            elif i == 2:
                is_complete = self.strava_complete
            
            if is_complete:
                dot.config(fg=COLOR_STEP_COMPLETE, text="\u2713")
                label.config(fg=COLOR_STEP_COMPLETE)
            elif i == self.current_step:
                dot.config(fg=COLOR_STEP_ACTIVE, text="\u25CF")
                label.config(fg=COLOR_TEXT)
            else:
                dot.config(fg=COLOR_STEP_INACTIVE, text="\u25CF")
                label.config(fg=COLOR_TEXT_DIM)
    
    def create_navigation(self):
        nav = tk.Frame(self.main_frame, bg=COLOR_BG)
        nav.pack(fill=tk.X, pady=(8, 0))
        
        BTN_WIDTH = 12
        
        self.back_btn = tk.Button(nav, text="\u2190 Back", command=self.go_back,
                                 bg=COLOR_BTN_SECONDARY, fg=COLOR_BTN_TEXT,
                                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT,
                                 width=BTN_WIDTH, pady=8, cursor='hand2', highlightthickness=0,
                                 activebackground=COLOR_BTN_SECONDARY_HOVER)
        self.back_btn.pack(side=tk.LEFT)
        
        self.next_btn = tk.Button(nav, text="Next \u2192", command=self.go_next,
                                 bg=COLOR_BTN_PRIMARY, fg=COLOR_BTN_TEXT,
                                 font=('Segoe UI', 10, 'bold'), relief=tk.FLAT,
                                 width=BTN_WIDTH, pady=8, cursor='hand2', highlightthickness=0,
                                 activebackground=COLOR_BTN_PRIMARY_HOVER)
        self.next_btn.pack(side=tk.RIGHT)
    
    def show_step(self, step_num):
        self.current_step = step_num
        self.update_step_indicator()
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if step_num == 0:
            self.back_btn.pack_forget()
        else:
            self.back_btn.pack(side=tk.LEFT)
        
        if step_num == 0:
            self.show_connect_step()
            self.next_btn.config(text="Next \u2192", bg=COLOR_BTN_PRIMARY, 
                                activebackground=COLOR_BTN_PRIMARY_HOVER)
            self.next_btn.pack(side=tk.RIGHT)
        elif step_num == 1:
            self.show_wifi_step()
            self.next_btn.config(text="Save WiFi \u2192", bg=COLOR_BTN_SUCCESS,
                                activebackground=COLOR_BTN_SUCCESS_HOVER)
            self.next_btn.pack(side=tk.RIGHT)
        elif step_num == 2:
            self.show_strava_step()
            self.next_btn.config(text="Save Strava \u2192", bg=COLOR_BTN_SUCCESS,
                                activebackground=COLOR_BTN_SUCCESS_HOVER)
            self.next_btn.pack(side=tk.RIGHT)
        elif step_num == 3:
            self.show_settings_step()
            self.next_btn.config(text="Finish Setup", bg=COLOR_BTN_SUCCESS,
                                activebackground=COLOR_BTN_SUCCESS_HOVER)
            self.next_btn.pack(side=tk.RIGHT)
        elif step_num == 4:
            self.show_options_step()
            self.next_btn.pack_forget()
    
    # ==================== STEP 1: CONNECT ====================
    def show_connect_step(self):
        content = tk.Frame(self.content_frame, bg=COLOR_CARD, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=f"Connect Your Board",
                font=('Segoe UI', 16, 'bold'), bg=COLOR_CARD, fg=COLOR_ACCENT).pack(pady=(0, 8))
        
        tk.Label(content, text="Plug in your Ibis board via USB and select the port below.",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(pady=(0, 20))
        
        port_row = tk.Frame(content, bg=COLOR_CARD)
        port_row.pack(pady=8)
        
        tk.Label(port_row, text="USB Port:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_combo = ttk.Combobox(port_row, textvariable=self.port_var, width=28, state='readonly')
        self.port_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(port_row, text=f"{F} Refresh", command=self.scan_ports,
                 bg=COLOR_CARD, fg=COLOR_TEXT, font=('Segoe UI', 11),
                 relief=tk.FLAT, cursor='hand2').pack(side=tk.LEFT)
        
        self.connect_btn = tk.Button(content, text="Connect", command=self.toggle_connection,
                                    bg=COLOR_BTN_PRIMARY, fg=COLOR_BTN_TEXT,
                                    font=('Segoe UI', 12, 'bold'), relief=tk.FLAT,
                                    padx=35, pady=8, cursor='hand2', highlightthickness=0)
        self.connect_btn.pack(pady=15)
        
        self.conn_status = tk.Label(content, text="\u2716 Not connected",
                                   bg=COLOR_CARD, fg=COLOR_DISCONNECTED, font=('Segoe UI', 11))
        self.conn_status.pack()
        
        help_link = tk.Label(content, text=f"Connection issues? Click here for help",
                            bg=COLOR_CARD, fg=COLOR_LINK, font=('Segoe UI', 11, 'underline'), cursor='hand2')
        help_link.pack(pady=(15, 0))
        help_link.bind('<Button-1>', lambda e: self.show_connection_help())
        
        self.update_connect_ui()
    
    # ==================== STEP 2: WIFI ====================
    def show_wifi_step(self):
        content = tk.Frame(self.content_frame, bg=COLOR_CARD, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=f"{F} WiFi Settings {F}",
                font=('Segoe UI', 16, 'bold'), bg=COLOR_CARD, fg=COLOR_ACCENT).pack(pady=(0, 8))
        
        tk.Label(content, text="Enter your home WiFi so Ibis can connect to the internet.*",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(pady=(0, 20))
        
        form = tk.Frame(content, bg=COLOR_CARD)
        form.pack()
        
        row1 = tk.Frame(form, bg=COLOR_CARD)
        row1.pack(fill=tk.X, pady=8)
        tk.Label(row1, text="WiFi Name (SSID):", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=16, anchor='w').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.ssid_var, width=28, font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        row2 = tk.Frame(form, bg=COLOR_CARD)
        row2.pack(fill=tk.X, pady=8)
        tk.Label(row2, text="WiFi Password:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=16, anchor='w').pack(side=tk.LEFT)
        self.pw_entry = tk.Entry(row2, textvariable=self.password_var, width=28,
                                font=('Segoe UI', 11), show='\u2022')
        self.pw_entry.pack(side=tk.LEFT)
        
        self.show_pw = tk.BooleanVar()
        tk.Checkbutton(row2, text="Show", variable=self.show_pw, bg=COLOR_CARD,
                      fg=COLOR_TEXT_DIM, selectcolor=COLOR_BG, activebackground=COLOR_CARD,
                      command=lambda: self.pw_entry.config(show='' if self.show_pw.get() else '\u2022')
                      ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(content, 
                text="*WiFi only connects briefly to fetch Strava stats at each refresh interval.",
                bg=COLOR_CARD, fg=COLOR_TEXT_DIM, font=('Segoe UI', 9),
                justify=tk.CENTER).pack(pady=(20, 0))
    
    # ==================== STEP 3: STRAVA ====================
    def show_strava_step(self):
        content = tk.Frame(self.content_frame, bg=COLOR_CARD, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=f"Connect Strava",
                font=('Segoe UI', 16, 'bold'), bg=COLOR_CARD, fg=COLOR_ACCENT).pack(pady=(0, 8))
        
        subtitle_frame = tk.Frame(content, bg=COLOR_CARD)
        subtitle_frame.pack(pady=(0, 3))
        tk.Label(subtitle_frame, text="Go to",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(side=tk.LEFT)
        strava_link = tk.Label(subtitle_frame, text=" strava.com/settings/api ",
                              font=('Segoe UI', 11, 'underline'), bg=COLOR_CARD, fg=COLOR_LINK, cursor='hand2')
        strava_link.pack(side=tk.LEFT)
        strava_link.bind('<Button-1>', lambda e: webbrowser.open("https://www.strava.com/settings/api"))
        tk.Label(subtitle_frame, text="and find your API credentials.",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(side=tk.LEFT)

        tk.Label(content, text="Fill in the Client ID and Client Secret below.",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(pady=(0, 5))
        
        help_link = tk.Label(content, text="Don't have a Strava API yet? Click here for help!",
                            bg=COLOR_CARD, fg=COLOR_LINK, font=('Segoe UI', 11, 'underline'), cursor='hand2')
        help_link.pack(pady=(0, 15))
        help_link.bind('<Button-1>', lambda e: self.show_strava_help())
        
        form = tk.Frame(content, bg=COLOR_CARD)
        form.pack()
        
        row1 = tk.Frame(form, bg=COLOR_CARD)
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Client ID:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=13, anchor='w').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.client_id_var, width=30, font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        row2 = tk.Frame(form, bg=COLOR_CARD)
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Client Secret:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=13, anchor='w').pack(side=tk.LEFT)
        tk.Entry(row2, textvariable=self.client_secret_var, width=30,
                font=('Segoe UI', 11), show='\u2022').pack(side=tk.LEFT)
        
        token_section = tk.Frame(content, bg=COLOR_CARD)
        token_section.pack(pady=(15, 0))
        
        tk.Button(token_section, text="\U0001F511 Let Ibis In! \U0001F511", command=self.start_oauth_flow,
                 bg=COLOR_BTN_SUCCESS, fg=COLOR_BTN_TEXT, font=('Segoe UI', 12, 'bold'),
                 relief=tk.FLAT, padx=25, pady=10, cursor='hand2', highlightthickness=0).pack()
        
        # Checkmark right under the button
        if self.refresh_token_var.get():
            tk.Label(token_section, text="\u2713 The Ibis has Strava access!", bg=COLOR_CARD,
                    fg=COLOR_SUCCESS, font=('Segoe UI', 11, 'bold')).pack(pady=(8, 0))
    
    # ==================== STEP 4: PERSONALIZE ====================
    def show_settings_step(self):
        content = tk.Frame(self.content_frame, bg=COLOR_CARD, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=f"Personalize Your Dashboard",
                font=('Segoe UI', 16, 'bold'), bg=COLOR_CARD, fg=COLOR_ACCENT).pack(pady=(0, 8))
        
        tk.Label(content, text="Personalize your dashboard, set your name, sport, and goals.",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR).pack(pady=(0, 20))
        
        form = tk.Frame(content, bg=COLOR_CARD)
        form.pack()
        
        row1 = tk.Frame(form, bg=COLOR_CARD)
        row1.pack(fill=tk.X, pady=5)
        tk.Label(row1, text="Your Name:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=18, anchor='w').pack(side=tk.LEFT)
        tk.Entry(row1, textvariable=self.name_var, width=22, font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        tk.Label(form, text=f"Leave blank to display 'STRAVA STATS' as the title",
                bg=COLOR_CARD, fg=COLOR_TEXT_DIM, font=('Segoe UI', 9)).pack(anchor='w', pady=(0, 5))
        
        row2 = tk.Frame(form, bg=COLOR_CARD)
        row2.pack(fill=tk.X, pady=5)
        tk.Label(row2, text="Sport Type:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=18, anchor='w').pack(side=tk.LEFT)
        ttk.Combobox(row2, textvariable=self.sport_var, values=SPORT_TYPES,
                    state='readonly', width=19).pack(side=tk.LEFT)
        
        row3 = tk.Frame(form, bg=COLOR_CARD)
        row3.pack(fill=tk.X, pady=5)
        tk.Label(row3, text="Distance Goal (km):", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=18, anchor='w').pack(side=tk.LEFT)
        tk.Entry(row3, textvariable=self.goal_var, width=12, font=('Segoe UI', 11)).pack(side=tk.LEFT)
        
        row4 = tk.Frame(form, bg=COLOR_CARD)
        row4.pack(fill=tk.X, pady=5)
        tk.Label(row4, text="Tracking Period:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=18, anchor='w').pack(side=tk.LEFT)
        ttk.Combobox(row4, textvariable=self.period_var, values=TRACK_PERIODS,
                    state='readonly', width=19).pack(side=tk.LEFT)
        
        row5 = tk.Frame(form, bg=COLOR_CARD)
        row5.pack(fill=tk.X, pady=5)
        tk.Label(row5, text="Refresh Interval:", bg=COLOR_CARD, fg=COLOR_TEXT,
                font=('Segoe UI', 11), width=18, anchor='w').pack(side=tk.LEFT)
        combo = ttk.Combobox(row5, textvariable=self.refresh_var,
                            values=[o[0] for o in REFRESH_OPTIONS], state='readonly', width=14)
        combo.pack(side=tk.LEFT)
        combo.bind('<<ComboboxSelected>>', self.update_battery)
        
        tk.Label(row5, textvariable=self.battery_var, bg=COLOR_CARD,
                fg=COLOR_SUCCESS, font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT, padx=(10, 0))
    
    # ==================== STEP 5: OPTIONS ====================
    def show_options_step(self):
        content = tk.Frame(self.content_frame, bg=COLOR_CARD, padx=30, pady=25)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(content, text=" Delete Data From Board ",
                font=('Segoe UI', 16, 'bold'), bg=COLOR_CARD, fg=COLOR_DANGER).pack(pady=(0, 8))
        
        tk.Label(content, text="This will erase your WiFi credentials, Strava connection,\nand all personal settings from the board.",
                font=SUBTITLE_FONT, bg=COLOR_CARD, fg=SUBTITLE_COLOR,
                justify=tk.CENTER).pack(pady=(0, 15))
        
        tk.Button(content, text="Delete Data", command=self.wipe_config,
                 bg=COLOR_BTN_DANGER, fg=COLOR_BTN_TEXT,
                 font=('Segoe UI', 11, 'bold'), relief=tk.FLAT,
                 padx=25, pady=10, cursor='hand2', highlightthickness=0,
                 activebackground=COLOR_BTN_DANGER_HOVER).pack()
    
    # ==================== CUSTOM STYLED POPUP ====================
    def _center_on_parent(self, window, w, h):
        """Center a window over the main window (not the screen)"""
        self.root.update_idletasks()
        px = self.root.winfo_x()
        py = self.root.winfo_y()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        window.geometry(f"{w}x{h}+{x}+{y}")
    
    def show_popup(self, title, message, popup_type="info", yes_no=False):
        """Show a styled popup that matches the app theme - centered on parent"""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        
        line_count = message.count('\n') + 1
        if line_count > 6 or len(message) > 300:
            popup_width = 500
            popup_height = 400
        else:
            popup_width = 450
            popup_height = 310
        
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        
        self._center_on_parent(popup, popup_width, popup_height)
        
        popup.configure(bg=COLOR_LOADING_BG)
        
        center = tk.Frame(popup, bg=COLOR_LOADING_BG)
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        if popup_type == "error":
            title_color = COLOR_DANGER
        elif popup_type == "warning":
            title_color = COLOR_ACCENT
        elif popup_type == "success":
            title_color = COLOR_SUCCESS
        else:
            title_color = COLOR_ACCENT
        
        tk.Label(center, text=title, font=('Segoe UI', 14, 'bold'),
                bg=COLOR_LOADING_BG, fg=title_color).pack(pady=(0, 15))
        
        tk.Label(center, text=message, font=('Segoe UI', 11),
                bg=COLOR_LOADING_BG, fg=COLOR_TEXT, wraplength=popup_width - 60, justify=tk.CENTER).pack(pady=(0, 25))
        
        self.popup_result = False
        
        def on_yes():
            self.popup_result = True
            popup.destroy()
        
        def on_no():
            self.popup_result = False
            popup.destroy()
        
        def on_ok():
            popup.destroy()
        
        btn_frame = tk.Frame(center, bg=COLOR_LOADING_BG)
        btn_frame.pack()
        
        if yes_no:
            tk.Button(btn_frame, text="Yes", command=on_yes,
                     bg=COLOR_BTN_SUCCESS, fg=COLOR_BTN_TEXT, font=('Segoe UI', 10, 'bold'),
                     relief=tk.FLAT, padx=25, pady=8, cursor='hand2', highlightthickness=0
                     ).pack(side=tk.LEFT, padx=10)
            tk.Button(btn_frame, text="No", command=on_no,
                     bg=COLOR_BTN_SECONDARY, fg=COLOR_BTN_TEXT, font=('Segoe UI', 10, 'bold'),
                     relief=tk.FLAT, padx=25, pady=8, cursor='hand2', highlightthickness=0
                     ).pack(side=tk.LEFT, padx=10)
        else:
            tk.Button(btn_frame, text="OK", command=on_ok,
                     bg=COLOR_BTN_PRIMARY, fg=COLOR_BTN_TEXT, font=('Segoe UI', 10, 'bold'),
                     relief=tk.FLAT, padx=30, pady=8, cursor='hand2', highlightthickness=0
                     ).pack()
        
        popup.wait_window()
        return self.popup_result
    
    # ==================== SETUP COMPLETE POPUP ====================
    def show_setup_complete_popup(self):
        """Special popup after successful setup - Close app or Go back"""
        popup = tk.Toplevel(self.root)
        popup.title(f"{F} Setup Complete! {F}")
        
        popup_width = 480
        popup_height = 340
        
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()
        
        self._center_on_parent(popup, popup_width, popup_height)
        
        popup.configure(bg=COLOR_LOADING_BG)
        
        center = tk.Frame(popup, bg=COLOR_LOADING_BG)
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center, text="Setup Complete!",
                font=('Segoe UI', 18, 'bold'),
                bg=COLOR_LOADING_BG, fg=COLOR_SUCCESS).pack(pady=(0, 15))
        
        tk.Label(center, text="The dashboard is now correctly displaying\nyour Strava stats! You can now:",
                font=('Segoe UI', 11),
                bg=COLOR_LOADING_BG, fg=COLOR_TEXT, justify=tk.CENTER).pack(pady=(0, 20))
        
        btn_frame = tk.Frame(center, bg=COLOR_LOADING_BG)
        btn_frame.pack()
        
        def close_app():
            popup.destroy()
            self.root.destroy()
        
        close_btn = tk.Button(btn_frame, text="\u2716  Close Ibis Setup  \u2716", command=close_app,
                             bg=COLOR_BTN_DANGER, fg=COLOR_BTN_TEXT, 
                             font=('Segoe UI', 12, 'bold'),
                             relief=tk.FLAT, padx=20, pady=12, cursor='hand2', highlightthickness=0,
                             activebackground=COLOR_BTN_DANGER_HOVER)
        close_btn.pack(pady=(0, 12), fill=tk.X)
        
        def go_back():
            popup.destroy()
            self.show_step(self.current_step)
        
        back_btn = tk.Button(btn_frame, text=f"{F}  Go back to Ibis Setup  {F}", command=go_back,
                            bg=COLOR_BTN_SECONDARY, fg=COLOR_BTN_TEXT,
                            font=('Segoe UI', 11, 'bold'),
                            relief=tk.FLAT, padx=20, pady=10, cursor='hand2', highlightthickness=0,
                            activebackground=COLOR_BTN_SECONDARY_HOVER)
        back_btn.pack(fill=tk.X)
    
    def update_battery(self, event=None):
        for name, val, est in REFRESH_OPTIONS:
            if name == self.refresh_var.get():
                self.battery_var.set(est)
                break
    
    def get_goal_value(self):
        goal_str = self.goal_var.get().strip()
        if not goal_str:
            return 1000.0
        try:
            return float(goal_str)
        except ValueError:
            return None
    
    # ==================== NAVIGATION ====================
    def go_back(self):
        if self.current_step > 0:
            self.show_step(self.current_step - 1)
    
    def go_next(self):
        if self.current_step == 0:
            if not self.connected:
                self.show_popup(f"{F} Not Connected", "Please connect to your board first!", popup_type="warning")
                return
            self.show_step(1)
        elif self.current_step == 1:
            if not self.ssid_var.get().strip():
                self.show_popup(f"{F} Missing WiFi", "Please enter your WiFi name!", popup_type="warning")
                return
            self.save_wifi()
        elif self.current_step == 2:
            self.save_strava()
        elif self.current_step == 3:
            self.finish_setup()
    
    # ==================== LOADING OVERLAY ====================
    def show_loading(self, title, message, show_dashboard_msg=False):
        if self.loading_overlay:
            self.loading_overlay.destroy()
        
        self.loading_overlay = tk.Toplevel(self.root)
        self.loading_overlay.title(title)
        self.loading_overlay.geometry(f"{LOADING_WIDTH}x{LOADING_HEIGHT}")
        self.loading_overlay.resizable(False, False)
        self.loading_overlay.transient(self.root)
        self.loading_overlay.grab_set()
        
        self._center_on_parent(self.loading_overlay, LOADING_WIDTH, LOADING_HEIGHT)
        
        self.loading_overlay.configure(bg=COLOR_LOADING_BG)
        
        center = tk.Frame(self.loading_overlay, bg=COLOR_LOADING_BG)
        center.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(center, text=title, font=('Segoe UI', 16, 'bold'),
                bg=COLOR_LOADING_BG, fg=COLOR_ACCENT).pack(pady=(0, 15))
        
        self.feather_label = tk.Label(center, text=F, font=('Segoe UI', 12),
                                      bg=COLOR_LOADING_BG, fg=COLOR_ACCENT)
        self.feather_label.pack(pady=(0, 12))
        
        self.loading_msg = tk.Label(center, text=message, font=('Segoe UI', 11),
                                   bg=COLOR_LOADING_BG, fg=COLOR_SUCCESS, wraplength=400)
        self.loading_msg.pack(pady=(0, 8))
        
        # Only show the dashboard message for Finish Setup
        if show_dashboard_msg:
            tk.Label(center, text="This window will close once your dashboard\nsuccessfully displays your stats",
                    font=('Segoe UI', 11), bg=COLOR_LOADING_BG, fg=COLOR_TEXT,
                    justify=tk.CENTER).pack()
        
        self.grow_feathers()
        # Don't call update() here - it blocks the animation loop
        self.loading_overlay.update_idletasks()
    
    def grow_feathers(self):
        try:
            if not self.loading_overlay or not self.loading_overlay.winfo_exists():
                return
            
            current = self.feather_label.cget('text')
            # Keep adding feathers up to 15, then cycle back to 1
            # This ensures continuous animation that stays within the box
            if len(current) < 15:
                self.feather_label.config(text=current + F)
            else:
                self.feather_label.config(text=F)
            
            # Always reschedule the next animation frame
            self.loading_animation_id = self.loading_overlay.after(150, self.grow_feathers)
        except Exception as e:
            print(f"Animation error (continuing): {e}")
            # Even on error, try to reschedule
            if self.loading_overlay and self.loading_overlay.winfo_exists():
                self.loading_animation_id = self.loading_overlay.after(150, self.grow_feathers)
    
    def update_loading(self, message):
        if self.loading_overlay and self.loading_overlay.winfo_exists():
            self.loading_msg.config(text=message)
            # Use update_idletasks instead of update to avoid blocking the animation
            self.loading_overlay.update_idletasks()
            # Ensure animation is still running
            if not self.loading_animation_id or self.loading_animation_id not in self.loading_overlay.tk.call('after', 'info'):
                self.grow_feathers()
    
    def hide_loading(self):
        if self.loading_animation_id and self.loading_overlay:
            try:
                self.loading_overlay.after_cancel(self.loading_animation_id)
            except:
                pass
        if self.loading_overlay:
            self.loading_overlay.destroy()
            self.loading_overlay = None
    
    def get_funny_message(self, category):
        if category in FUNNY_MESSAGES:
            return random.choice(FUNNY_MESSAGES[category])
        return "Ibis is doing ibis things..."
    
    # ==================== SERIAL COMMUNICATION ====================
    def scan_ports(self):
        ports = [f"{p.device} - {p.description}" for p in serial.tools.list_ports.comports()]
        if hasattr(self, 'port_combo'):
            self.port_combo['values'] = ports
            if ports:
                self.port_combo.current(0)
    
    def toggle_connection(self):
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        port_str = self.port_var.get()
        if not port_str:
            self.show_popup(f"{F} No Port", "Please select a USB port!", popup_type="warning")
            return
        
        self.show_loading(f"{F} Connecting {F}", self.get_funny_message('connect'))
        
        try:
            port = port_str.split(' - ')[0]
            self.serial_conn = serial.Serial(port, BAUD_RATE, timeout=SERIAL_TIMEOUT,
                                            write_timeout=WRITE_TIMEOUT)
            time.sleep(2)
            self.serial_conn.reset_input_buffer()
            
            self.update_loading(self.get_funny_message('connect'))
            
            response = self.send_command("PING", wait_for="PONG")
            if response and "PONG" in response:
                self.connected = True
                self.update_connect_ui()
                
                self.update_loading(self.get_funny_message('load_config'))
                self.auto_load_config()
                
                self.hide_loading()
                
                # Auto-advance after successful connect
                if self.wifi_complete and self.strava_complete:
                    self.show_step(3)  # Everything set up -> Personalize
                elif self.wifi_complete:
                    self.show_step(2)  # WiFi done -> Strava
                else:
                    self.show_step(1)  # Fresh board -> WiFi
            else:
                raise Exception("No response from board")
        except Exception as e:
            self.hide_loading()
            self.show_popup(f"{F} Connection Failed", f"Could not connect:\n{e}\n\nMake sure board is in setup mode!", popup_type="error")
            if self.serial_conn:
                self.serial_conn.close()
                self.serial_conn = None
    
    def auto_load_config(self):
        response = self.send_command("GET_CONFIG", wait_for="OK")
        
        if not response:
            return
        
        try:
            start, end = response.find('{'), response.rfind('}') + 1
            if start >= 0 and end > start:
                c = json.loads(response[start:end])
                
                if c.get('ssid'):
                    self.ssid_var.set(c.get('ssid', ''))
                    self.password_var.set(c.get('password', ''))
                    self.wifi_complete = True
                
                if c.get('clientID'):
                    self.client_id_var.set(c.get('clientID', ''))
                    self.client_secret_var.set(c.get('clientSecret', ''))
                    self.refresh_token_var.set(c.get('refreshToken', ''))
                    if c.get('clientID') and c.get('clientSecret') and c.get('refreshToken'):
                        self.strava_complete = True
                
                self.name_var.set(c.get('name', ''))
                self.sport_var.set(c.get('sport', 'Run'))
                self.goal_var.set(str(c.get('goal', 1000)))
                idx = c.get('trackPeriod', 0)
                if idx < len(TRACK_PERIODS):
                    self.period_var.set(TRACK_PERIODS[idx])
                hrs = c.get('refreshHours', 24)
                for n, v, e in REFRESH_OPTIONS:
                    if v == hrs:
                        self.refresh_var.set(n)
                        self.battery_var.set(e)
                        break
                
                self.update_step_indicator()
        except Exception as e:
            print(f"Auto-load failed: {e}")
    
    def disconnect(self):
        if self.serial_conn:
            self.serial_conn.close()
            self.serial_conn = None
        self.connected = False
        self.wifi_complete = False
        self.strava_complete = False
        self.update_connect_ui()
        self.update_step_indicator()
    
    def update_connect_ui(self):
        try:
            if self.connected:
                self.conn_status.config(text=f"\u2713 Connected {F}", fg=COLOR_CONNECTED)
                self.connect_btn.config(text="Disconnect", bg=COLOR_BTN_SUCCESS)
                self.next_btn.config(bg=COLOR_BTN_SUCCESS, activebackground=COLOR_BTN_SUCCESS_HOVER)
            else:
                self.conn_status.config(text="\u2716 Not connected", fg=COLOR_DISCONNECTED)
                self.connect_btn.config(text="Connect", bg=COLOR_BTN_PRIMARY)
                self.next_btn.config(bg=COLOR_BTN_PRIMARY, activebackground=COLOR_BTN_PRIMARY_HOVER)
        except:
            pass
    
    def send_command(self, command, wait_for=None, timeout=SERIAL_TIMEOUT):
        if not self.serial_conn:
            return None
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.serial_conn.reset_input_buffer()
                self.serial_conn.reset_output_buffer()
                time.sleep(0.2)
                
                cmd_bytes = f"{command}\n".encode('utf-8')
                
                for i in range(0, len(cmd_bytes), 32):
                    self.serial_conn.write(cmd_bytes[i:i+32])
                    self.serial_conn.flush()
                    time.sleep(0.05)
                
                time.sleep(0.5)
                
                response = ""
                start_time = time.time()
                while time.time() - start_time < timeout:
                    # Process Tkinter events to keep animations running
                    try:
                        self.root.update()
                    except:
                        pass
                    
                    if self.serial_conn.in_waiting > 0:
                        response += self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                        if wait_for and wait_for in response:
                            time.sleep(0.3)
                            if self.serial_conn.in_waiting > 0:
                                response += self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                            break
                        if any(x in response for x in ["OK", "SUCCESS", "WIPED", "ERROR", "FAILED"]):
                            if not wait_for:
                                break
                    time.sleep(0.05)
                
                if response:
                    return response
                    
            except (PermissionError, OSError, serial.SerialException) as e:
                print(f"Connection lost or port busy (attempt {attempt+1}/{max_retries}): {e}")
                # Connection lost - update UI
                if self.connected and (isinstance(e, OSError) or isinstance(e, serial.SerialException)):
                    print("Board disconnected!")
                    self.root.after(0, self.handle_disconnection)
                    return None
                time.sleep(1)
                if attempt < max_retries - 1:
                    continue
                else:
                    print(f"Send error after {max_retries} attempts: {e}")
                    return None
            except Exception as e:
                print(f"Send error: {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)
                    continue
                return None
        
        return None
    
    def handle_disconnection(self):
        """Handle board disconnection - update UI to show disconnected state"""
        if self.serial_conn:
            try:
                self.serial_conn.close()
            except:
                pass
            self.serial_conn = None
        
        self.connected = False
        self.update_connect_ui()
        self.update_step_indicator()
        
        # Hide any loading overlay
        if self.loading_overlay:
            self.hide_loading()
        
        # Show error popup
        self.show_popup(f"{F} Connection Lost", 
                       "Board disconnected!\n\nPlease reconnect and try again.",
                       popup_type="error")
    
    # ==================== WIPE ====================
    def wipe_config(self):
        if not self.connected:
            self.show_popup(f"{F} Not Connected", "Please connect to your board first!", popup_type="warning")
            return
        
        if not self.show_popup(f"{F} Confirm Delete", 
                "Are you sure you want to erase ALL settings?\n\n"
                "This will remove:\n"
                "\u2022 WiFi credentials\n"
                "\u2022 Strava connection\n"
                "\u2022 All personalization\n\n"
                "This cannot be undone!\n\n"
                "(This may take up to a minute)",
                popup_type="warning", yes_no=True):
            return
        
        self.show_loading(f"{F} Deleting Data {F}", self.get_funny_message('wipe'))
        
        response = self.send_command("DELETE_DATA", wait_for="SETUP_SCREEN_DRAWN", timeout=60)
        
        if response and "WIPED" in response:
            self.ssid_var.set('')
            self.password_var.set('')
            self.name_var.set('')
            self.client_id_var.set('')
            self.client_secret_var.set('')
            self.refresh_token_var.set('')
            self.sport_var.set('Run')
            self.goal_var.set('1000')
            self.period_var.set('Yearly')
            self.refresh_var.set('Once a day')
            self.battery_var.set('~2 months battery')
            
            self.wifi_complete = False
            self.strava_complete = False
            self.setup_done = False
            self.update_step_indicator()
            
            self.hide_loading()
            self.show_popup(f"{F} Data Deleted", "All settings erased!\n\nBoard is ready for fresh setup.", popup_type="success")
        else:
            self.hide_loading()
            self.show_popup(f"{F} Error", "Failed to delete data from board.", popup_type="error")
    
    # ==================== SAVE FUNCTIONS ====================
    def save_wifi(self):
        self.show_loading(f"{F} Saving WiFi {F}", self.get_funny_message('save_config'))
        
        config = {
            'ssid': self.ssid_var.get().strip(),
            'password': self.password_var.get(),
            'name': self.name_var.get().strip(),
            'title': '',
            'clientID': self.client_id_var.get().strip(),
            'clientSecret': self.client_secret_var.get().strip(),
            'refreshToken': self.refresh_token_var.get().strip(),
            'sport': self.sport_var.get(),
            'goal': self.get_goal_value() or 1000,
            'trackPeriod': TRACK_PERIODS.index(self.period_var.get())
        }
        for n, v, _ in REFRESH_OPTIONS:
            if n == self.refresh_var.get():
                config['refreshHours'] = v
                break
        
        response = self.send_command(f"SET_CONFIG:{json.dumps(config, separators=(',', ':'))}", wait_for="SUCCESS", timeout=10)
        
        if not response or "SUCCESS" not in response:
            self.hide_loading()
            self.show_popup(f"{F} Error", "Failed to save configuration.", popup_type="error")
            return
        
        self.update_loading(self.get_funny_message('test_wifi'))
        
        wifi_response = self.send_command("TEST_WIFI", wait_for="WIFI_", timeout=25)
        
        self.hide_loading()
        
        if not wifi_response or "WIFI_OK" not in wifi_response:
            self.show_popup(f"{F} WiFi Failed", "WiFi connection failed!\n\nPlease check your credentials.", popup_type="warning")
            return
        
        self.wifi_complete = True
        self.update_step_indicator()
        
        # Auto-advance
        if self.strava_complete:
            self.show_popup(f"{F} WiFi Updated", "WiFi credentials saved and tested!", popup_type="success")
            self.show_step(3)  # Strava already done -> Personalize
        else:
            self.show_popup(f"{F} WiFi Saved", "WiFi credentials saved and tested!\n\nNow let's connect Strava.", popup_type="success")
            self.show_step(2)  # Next: Strava
    
    def save_strava(self):
        has_strava = bool(self.client_id_var.get().strip() and 
                         self.client_secret_var.get().strip() and 
                         self.refresh_token_var.get().strip())
        
        if not has_strava:
            if self.show_popup(f"{F} Skip Strava?", 
                    "No Strava credentials entered.\n\nSkip Strava connection and continue?",
                    popup_type="warning", yes_no=True):
                self.show_step(3)
            return
        
        self.show_loading(f"{F} Saving Strava {F}", self.get_funny_message('save_config'))
        
        time.sleep(0.5)
        
        config = {
            'ssid': self.ssid_var.get().strip(),
            'password': self.password_var.get(),
            'name': self.name_var.get().strip(),
            'title': '',
            'clientID': self.client_id_var.get().strip(),
            'clientSecret': self.client_secret_var.get().strip(),
            'refreshToken': self.refresh_token_var.get().strip(),
            'sport': self.sport_var.get(),
            'goal': self.get_goal_value() or 1000,
            'trackPeriod': TRACK_PERIODS.index(self.period_var.get())
        }
        for n, v, _ in REFRESH_OPTIONS:
            if n == self.refresh_var.get():
                config['refreshHours'] = v
                break
        
        response = self.send_command(f"SET_CONFIG:{json.dumps(config, separators=(',', ':'))}", wait_for="SUCCESS", timeout=15)
        
        self.hide_loading()
        
        if not response or "SUCCESS" not in response:
            if response and ("Configuration saved" in response or "saved" in response.lower() or "OK" in response):
                self.strava_complete = True
                self.update_step_indicator()
                self.show_popup(f"{F} Strava Saved", 
                               "Strava credentials saved!\n\n(Minor communication glitch ignored)", 
                               popup_type="success")
                self.show_step(3)
            else:
                self.show_popup(f"{F} Save Error", 
                               "Communication error while saving.\n\nYou can:\n\u2022 Try 'Save Strava' again\n\u2022 Skip to 'Finish Setup' (it will save then)", 
                               popup_type="warning")
            return
        
        self.strava_complete = True
        self.update_step_indicator()
        
        # Auto-advance to Personalize
        self.show_popup(f"{F} Strava Saved", "Strava credentials saved!", popup_type="success")
        self.show_step(3)
    
    def finish_setup(self):
        has_wifi = bool(self.ssid_var.get().strip())
        has_strava = bool(self.client_id_var.get().strip() and 
                         self.client_secret_var.get().strip() and 
                         self.refresh_token_var.get().strip())
        
        if not has_wifi or not has_strava:
            missing = []
            if not has_wifi:
                missing.append("WiFi")
            if not has_strava:
                missing.append("Strava")
            self.show_popup(f"{F} Missing Settings", 
                           f"Please enter and save {' and '.join(missing)}\ncredentials first!",
                           popup_type="warning")
            return
        
        goal_str = self.goal_var.get().strip()
        if goal_str:
            try:
                float(goal_str)
            except ValueError:
                self.show_popup(f"{F} Invalid Goal", 
                               "Distance goal must be a number!\n\nExample: 1000",
                               popup_type="warning")
                return
        
        self.show_loading(f"{F} Finishing Setup {F}", self.get_funny_message('save_config'), show_dashboard_msg=True)
        
        config = {
            'ssid': self.ssid_var.get().strip(),
            'password': self.password_var.get(),
            'name': self.name_var.get().strip(),
            'title': '',
            'clientID': self.client_id_var.get().strip(),
            'clientSecret': self.client_secret_var.get().strip(),
            'refreshToken': self.refresh_token_var.get().strip(),
            'sport': self.sport_var.get(),
            'goal': self.get_goal_value() or 1000,
            'trackPeriod': TRACK_PERIODS.index(self.period_var.get())
        }
        for n, v, _ in REFRESH_OPTIONS:
            if n == self.refresh_var.get():
                config['refreshHours'] = v
                break
        
        response = self.send_command(f"SET_CONFIG:{json.dumps(config, separators=(',', ':'))}", wait_for="SUCCESS", timeout=10)
        
        if not response or "SUCCESS" not in response:
            self.hide_loading()
            self.show_popup(f"{F} Error {F}", "Failed to save configuration.", popup_type="error")
            return
        
        has_strava = bool(config['clientID'] and config['clientSecret'] and config['refreshToken'])
        has_wifi = bool(config['ssid'])
        
        if has_strava and has_wifi:
            self.update_loading(self.get_funny_message('fetch_strava'))
            strava_response = self.send_command("FETCH_STRAVA", wait_for="DASHBOARD_DRAWN", timeout=90)
            
            self.hide_loading()
            
            if strava_response and "DASHBOARD_DRAWN" in strava_response:
                self.setup_done = True
                self.show_setup_complete_popup()
            else:
                self.show_popup(f"{F} Almost Done", 
                               "Settings saved but couldn't fetch Strava data.\n\n"
                               "Try pressing BOOT button on the board\n"
                               "or click Finish Setup again.",
                               popup_type="warning")
        elif has_wifi:
            self.update_loading("Updating display...")
            self.send_command("SHOW_SETUP_SCREEN", wait_for="SETUP_SCREEN_DRAWN", timeout=60)
            
            self.hide_loading()
            self.show_popup(f"{F} WiFi Saved", 
                           "WiFi settings saved!\n\n"
                           "Add Strava credentials to see your stats.",
                           popup_type="success")
        else:
            self.hide_loading()
            self.show_popup(f"{F} Missing Settings", 
                           "Please enter WiFi credentials first!",
                           popup_type="warning")
    
    # ==================== OAUTH ====================
    def start_oauth_flow(self):
        cid = self.client_id_var.get().strip()
        sec = self.client_secret_var.get().strip()
        
        if not cid or not sec:
            self.show_popup(f"{F} Missing Info", "Enter Client ID and Secret first!", popup_type="warning")
            return
        
        self.token_status_var.set(f"{F} Opening browser...")
        self.root.update()
        
        def run_server():
            try:
                handler = lambda *a, **k: OAuthCallbackHandler(*a, callback=self.oauth_callback, **k)
                with socketserver.TCPServer(("", OAUTH_REDIRECT_PORT), handler) as httpd:
                    httpd.timeout = 120
                    httpd.handle_request()
            except Exception as e:
                self.root.after(0, lambda: self.token_status_var.set(f"Error: {e}"))
        
        threading.Thread(target=run_server, daemon=True).start()
        time.sleep(0.3)
        
        auth_params = {
            'client_id': cid,
            'redirect_uri': OAUTH_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'read,activity:read_all',
            'approval_prompt': 'auto'
        }
        webbrowser.open(f"{STRAVA_AUTH_URL}?{urllib.parse.urlencode(auth_params)}")
    
    def oauth_callback(self, code):
        if code:
            self.root.after(100, lambda: self.exchange_token(code))
        else:
            self.root.after(0, lambda: self.token_status_var.set("Authorization failed"))
    
    def exchange_token(self, code):
        self.token_status_var.set(f"{F} Getting token...")
        try:
            data = urllib.parse.urlencode({
                'client_id': self.client_id_var.get().strip(),
                'client_secret': self.client_secret_var.get().strip(),
                'code': code,
                'grant_type': 'authorization_code'
            }).encode()
            
            req = urllib.request.Request(STRAVA_TOKEN_URL, data=data, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                if 'refresh_token' in result:
                    self.refresh_token_var.set(result['refresh_token'])
                    self.token_status_var.set("")
                    self.show_step(2)  # Refresh to show checkmark
                else:
                    self.token_status_var.set("No token in response")
        except Exception as e:
            self.token_status_var.set(f"Error: {e}")
    
    # ==================== HELP ====================
    def show_connection_help(self):
        self.show_popup(f"{F} Connection Help",
            "1. Make sure USB cable is plugged in\n\n"
            "2. Wait for screen to finish drawing\n\n"
            "3. Stare at the board to assert dominance\n\n"
            "4. Try turning it off and on again\n\n"
            "5. ACT LED should be blinking green\n\n"
            f"6. Click '{F} Refresh' and try again")
    
    def show_strava_help(self):
        self.show_popup(f"{F} Strava Setup Guide",
            "1. Go to strava.com/settings/api and log in\n\n"
            "2. Click 'Create an App' (or 'My API Application')\n\n"
            "3. In the 'Application Name' box, type 'Ibis Dash'\n"
            "   Fill in the other fields as you please\n\n"
            "4. Set the 'Authorization Callback Domain'\n"
            "   box to: localhost and hit 'Save'\n\n"
            "5. Strava will now show your Client ID & Client Secret\n"
            "   Enter these in Ibis Setup.\n\n"
            "6. Then click 'Let Ibis In' to connect!")


def main():
    root = tk.Tk()
    app = IbisSetupWizard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
