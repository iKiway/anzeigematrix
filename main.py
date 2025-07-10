from Canvas import MatrixHelper
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from App import App
from DBAnzeige import DBAnzeige
from Clock import Clock
import json
import time
import os

# Matrix initialisieren (ersetze durch deine tatsächlichen Optionen)
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.gpio_slowdown = 4
options.pwm_bits = 6
options.brightness = 100
options.pwm_lsb_nanoseconds = 130
options.show_refresh_rate = 1

# options.hardware_mapping = 'adafruit-hat'  # Oder 'adafruit-hat-pwm'

matrix = RGBMatrix(options=options)
canvas = matrix.CreateFrameCanvas()
graphics_accent_color = graphics.Color(169, 169, 169)  # Weiß

config_old = None
helper = None
last_modified_time = 0
config_file_path = "display_config.json"

def load_and_switch_app():
    global config_old, helper, last_modified_time

    try:
        # Überprüfe, ob die Datei existiert
        if not os.path.exists(config_file_path):
            print(f"Config file {config_file_path} not found")
            return
        
        # Überprüfe die letzte Änderungszeit der Datei
        current_modified_time = os.path.getmtime(config_file_path)
        if current_modified_time <= last_modified_time:
            return  # Datei wurde nicht geändert
        
        last_modified_time = current_modified_time
        
        # JSON-Datei laden
        with open(config_file_path, "r") as f:
            config = json.load(f)
        
        app_value = config.get("current_app")
        if config != config_old:
            # Stoppe die aktuelle App
            if helper:
                print(f"Stopping current app: {app_value_old}")
                helper.stop_display()
                print("Stopped current app")
                helper = None
            
            # Starte die neue App
            if app_value == "clock":
                helper = Clock(matrix, canvas, graphics_accent_color)
                print("Clock app selected")
            elif app_value == "db_fahrplan":
                helper = DBAnzeige(matrix, canvas, graphics_accent_color, config["app_settings"].get("station", "Berlin hbf"))
                print("DB Fahrplan app selected")
            elif app_value == "dashboard":
                helper = App(matrix, canvas)
                print("Dashboard app selected")
            else:
                helper = None
                print("Unknown app selected")
            
            if helper:
                helper.start_display()
                print(f"Started app: {app_value}")

            config_old = config

    except Exception as e:
        print(f"Error loading config: {e}")

# Hauptschleife
try:
    print("Starting display matrix monitor...")
    print("Press Ctrl+C to stop")
    
    while True:
        load_and_switch_app()
        time.sleep(1)  # Überprüfe jede Sekunde
        
except KeyboardInterrupt:
    print("\nStopping display matrix monitor...")
    if helper:
        helper.stop_display()
    print("Goodbye!")
except Exception as e:
    print(f"Unexpected error: {e}")
    if helper:
        helper.stop_display()