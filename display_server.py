#!/usr/bin/env python3
"""
Anzeigematrix Display Server für Raspberry Pi
Einfacher HTTP-Server für Konnektivitätsprüfung und Display-Management
"""

from flask import Flask, jsonify, request
from datetime import datetime
import socket
import os
import subprocess
import json
import threading
from pathlib import Path

# File Watcher (optional - nur wenn watchdog installiert ist)
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    
    class ConfigHandler(FileSystemEventHandler):
        """Überwacht Änderungen an der Konfigurationsdatei"""
        def __init__(self, callback):
            self.callback = callback
        
        def on_modified(self, event):
            if event.src_path.endswith('display_config.json'):
                print("📁 Config file changed")
                self.callback()
                
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("⚠️  Watchdog not installed - using polling fallback")
    ConfigHandler = None  # Placeholder

app = Flask(__name__)

# Pfad zur Konfigurationsdatei - im gleichen Verzeichnis wie das Script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'display_config.json')

def load_config():
    """Konfiguration aus JSON-Datei laden"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            print(f"📖 Config loaded: {config.get('current_app', 'unknown')}")
            return config
    except FileNotFoundError:
        print("📝 Creating default config file...")
        # Standard-Konfiguration erstellen
        default_config = {
            'display_id': 'raspberry_display_001',
            'display_name': 'Raspberry Pi Display',
            'location': 'Lobby',
            'current_app': 'dashboard',
            'app_settings': {},
            'startup_time': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        save_config(default_config)
        return default_config
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing config file: {e}")
        return None

def save_config(config):
    """Konfiguration in JSON-Datei speichern"""
    config['last_updated'] = datetime.now().isoformat()
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"💾 Config saved: {config.get('current_app', 'unknown')}")
    except Exception as e:
        print(f"❌ Error saving config: {e}")

def on_config_change():
    """Callback für Konfigurationsänderungen"""
    global DISPLAY_CONFIG
    new_config = load_config()
    if new_config:
        DISPLAY_CONFIG = new_config
        print(f"🔄 Configuration reloaded: {DISPLAY_CONFIG['current_app']}")

def start_file_watcher():
    """File Watcher starten (falls verfügbar)"""
    if not WATCHDOG_AVAILABLE:
        print("📊 Starting polling-based config monitoring...")
        # Starte Polling in separatem Thread
        def polling_thread():
            last_modified = 0
            while True:
                try:
                    if os.path.exists(CONFIG_FILE):
                        current_modified = os.path.getmtime(CONFIG_FILE)
                        if current_modified != last_modified and last_modified != 0:
                            print("📁 Config file changed (polling)")
                            on_config_change()
                        last_modified = current_modified
                except Exception as e:
                    print(f"❌ Polling error: {e}")
                
                import time
                time.sleep(2)  # Poll every 2 seconds
        
        thread = threading.Thread(target=polling_thread, daemon=True)
        thread.start()
        return None
    
    try:
        event_handler = ConfigHandler(on_config_change)
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(CONFIG_FILE) or '.', recursive=False)
        observer.start()
        print("👀 File watcher started (watchdog)")
        return observer
    except Exception as e:
        print(f"⚠️  Could not start file watcher: {e}")
        return None

# Globale Konfiguration laden
DISPLAY_CONFIG = load_config() or {
    'display_id': 'raspberry_display_001',
    'display_name': 'Raspberry Pi Display',
    'location': 'Lobby',
    'current_app': 'dashboard',
    'app_settings': {},
    'startup_time': datetime.now().isoformat()
}

def get_system_info():
    """System-Informationen sammeln"""
    try:
        # CPU-Temperatur (Raspberry Pi spezifisch)
        temp = None
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = round(int(f.read().strip()) / 1000.0, 1)
        
        # Hostname und IP
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        
        # Uptime
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_hours = round(uptime_seconds / 3600, 1)
        
        return {
            'hostname': hostname,
            'ip_address': ip,
            'cpu_temp': temp,
            'uptime_hours': uptime_hours,
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'hostname': 'unknown',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@app.route('/')
def home():
    """Basis-Endpoint für Konnektivitätsprüfung"""
    return jsonify({
        'status': 'online',
        'message': 'Anzeigematrix Display Server',
        'display': DISPLAY_CONFIG,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def status():
    """Detaillierter Status-Endpoint"""
    system_info = get_system_info()
    
    return jsonify({
        'status': 'online',
        'display': DISPLAY_CONFIG,
        'system': system_info,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/display/current-app')
def get_current_app():
    """Aktuell laufende App abrufen"""
    return jsonify({
        'current_app': DISPLAY_CONFIG['current_app'],
        'app_settings': DISPLAY_CONFIG.get('app_settings', {}),
        'display_id': DISPLAY_CONFIG['display_id'],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/display/status')
def get_display_status():
    """Display-Status für Synchronisation mit Mobile App"""
    config = load_config()
    return jsonify({
        'success': True,
        'current_app': config['current_app'],
        'settings': config.get('app_settings', {}),
        'display_id': config['display_id'],
        'is_online': True,
        'last_update': config.get('last_update', datetime.now().isoformat()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/display/set-app', methods=['POST'])
def set_current_app():
    """App auf dem Display setzen - ERWEITERT"""
    global DISPLAY_CONFIG
    data = request.get_json()
    
    if not data or 'app_id' not in data:
        return jsonify({'error': 'app_id required'}), 400
    
    app_id = data['app_id']
    app_settings = data.get('settings', {})
    
    # Gültige Apps erweitert
    valid_apps = ['dashboard', 'weather', 'calendar', 'db_fahrplan', 'news', 'slideshow', 'menu']
    
    if app_id not in valid_apps:
        return jsonify({
            'error': 'Invalid app_id',
            'valid_apps': valid_apps
        }), 400
    
    # Konfiguration aktualisieren
    DISPLAY_CONFIG['current_app'] = app_id
    DISPLAY_CONFIG['app_settings'] = app_settings
    
    # In JSON-Datei speichern
    save_config(DISPLAY_CONFIG)
    
    print(f"📱 App switched to: {app_id}")
    if app_settings:
        print(f"⚙️  Settings: {app_settings}")
    
    return jsonify({
        'success': True,
        'current_app': app_id,
        'settings': app_settings,
        'display_id': DISPLAY_CONFIG['display_id'],
        'message': f'App switched to {app_id}',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system/reboot', methods=['POST'])
def reboot_system():
    """System neustarten (vorsichtig verwenden!)"""
    try:
        # In Produktionsumgebung: subprocess.run(['sudo', 'reboot'])
        return jsonify({
            'message': 'Reboot command received (disabled in demo)',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ping')
def ping():
    """Einfacher Ping-Endpoint"""
    return jsonify({
        'pong': True,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Anzeigematrix Display Server...")
    print(f"📺 Display ID: {DISPLAY_CONFIG['display_id']}")
    print(f"📍 Location: {DISPLAY_CONFIG['location']}")
    print(f"📱 Current App: {DISPLAY_CONFIG['current_app']}")
    print(f"📁 Config File: {CONFIG_FILE}")
    
    # File Watcher starten
    observer = start_file_watcher()
    
    print("🌐 Server will be available on:")
    print("   - http://localhost:80")
    print("   - http://YOUR_PI_IP:80")
    print()
    print("📡 Endpoints:")
    print("   GET  /                     - Basic status")
    print("   GET  /api/status           - Detailed status")
    print("   GET  /api/ping             - Simple ping")
    print("   GET  /api/display/current-app")
    print("   POST /api/display/set-app  - Set app with settings")
    print("   POST /api/system/reboot")
    print()
    
    try:
        # Server starten
        app.run(
            host='0.0.0.0',  # Auf allen Interfaces hören
            port=80,         # Standard HTTP-Port
            debug=False      # Für Produktion auf False setzen
        )
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        if observer:
            observer.stop()
            observer.join()
        print("✅ Server stopped")
