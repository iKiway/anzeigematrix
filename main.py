from Canvas import MatrixHelper
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from App import App
from DBAnzeige import DBAnzeige
from Clock import Clock
import json

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

app_value_old = None
helper: App

# JSON-Datei laden und Wert von "app" überprüfen
with open("display_config.json", "r") as f:
    config = json.load(f)

app_value = config.get("current_app")
if app_value != app_value_old:
    locals().get('helper', None) and helper.stop_display()
    if app_value == "clock":
        helper = Clock(matrix, canvas, graphics_accent_color)
        print("Clock app selected")
    elif app_value == "db_fahrplan":
        helper = DBAnzeige(matrix, canvas, graphics_accent_color)
        print("DB Fahrplan app selected")
    elif app_value == "dashboard":
        helper = App(matrix, canvas)
        print("Dashboard app selected")
    else:
        helper = None
        print("Unknown app selected")
    if helper:
        helper.start_display()
        print(app_value)
    app_value_old = app_value
# no_wifi_display = MatrixNoWifi(matrix, canvas, graphics_accent_color) #Entfernt

# helper.start_display() #Starte die Anzeige