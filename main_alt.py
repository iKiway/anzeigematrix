from Canvas import MatrixHelper
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

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

helper = MatrixHelper(matrix, canvas, graphics_accent_color) #Erstelle ein Objekt von MatrixHelper
# no_wifi_display = MatrixNoWifi(matrix, canvas, graphics_accent_color) #Entfernt

helper.start_display() #Starte die Anzeige