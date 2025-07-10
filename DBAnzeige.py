# from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics, Color
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

from PIL import Image, ImageDraw, ImageFont
import time
import datetime
import threading  # Für den separaten Thread
import importlib.resources
from db_api.Station import Station
from db_api.Train import Train
from App import App


class DBAnzeige(App):
    def __init__(self, matrix, canvas, graphics_accent_color, station="Berlin hbf"):
        super().__init__(matrix, canvas)
        self.graphics_accent_color = graphics_accent_color
        self.station = station  # Speichere den Namen der Station
        self.display_mode = "content"  # Startmodus: Laufschrift
        self.message = "Hello, test test test" #Speichere die Nachricht hier
        self.thread = None #Speichere den Thread
        self.thread_run = False
        self.font_normal = graphics.Font()
        self.font_small = graphics.Font()
        self.font_normal.LoadFont("5x7.bdf")  # Lade die Schriftart
        self.font_small.LoadFont("4x6.bdf")
        self.train_list = [] #Liste für die Züge
        self.color_font = graphics.Color(255, 255, 255)  # Weiß für den Text
        self.color_red = graphics.Color(255, 0, 0)  # Rot für den Text
        self.color_green = graphics.Color(0, 255, 0)  # Grün für den Text

    def background(self):
        # Zeichne den Rahmen
        graphics.DrawLine(self.canvas, 0, 0, 63, 0, self.graphics_accent_color)  # Top border
        graphics.DrawLine(self.canvas, 0, 15, 63, 15, self.graphics_accent_color)  # Middle border
        graphics.DrawLine(self.canvas, 0, 16, 63, 16, self.graphics_accent_color)  # Middle border
        graphics.DrawLine(self.canvas, 0, 31, 63, 31, self.graphics_accent_color)  # Bottom border
        graphics.DrawLine(self.canvas, 0, 0, 0, 31, self.graphics_accent_color)  # Left border
        graphics.DrawLine(self.canvas, 63, 0, 63, 31, self.graphics_accent_color)  # Right border
        graphics.DrawLine(self.canvas, 18, 0, 18, 31, self.graphics_accent_color) 

    def content_old(self):
        self.thread_run = True
        pos_up = 64
        text_width_up = graphics.DrawText(self.canvas, self.font_normal, pos_up, 10, self.color_font, self.train_list[0].get_final_destination())
        if text_width_up < 43:
            pos_up = 20
        else:
            pos_up = 64
        
        pos_down = 64
        if len(self.train_list) > 1:
            text_width_down = graphics.DrawText(self.canvas, self.font_normal, pos_down, 26, self.color_font, self.train_list[1].get_final_destination()) #Position ist 26
            if text_width_down <= 43:
                pos_down = 20
        else:
            text_width_down = 0

        while self.thread_run:  # Überprüfe den Anzeigemodus
            
            train_list = self.train_list
            self.canvas.Clear()
            self.display_final_destination(train_list[0], pos_up, self.color_font, upper=True) #Zeige den Endbahnhof an
            self.display_departure(train_list[0], upper=True)
            self.display_icon(train_list[0], upper=True)
            if len(train_list) > 1:
                self.display_final_destination(train_list[1], pos_down, self.color_font, upper=False) 
                self.display_departure(train_list[1], upper=False)
                self.display_icon(train_list[1], upper=False)
            self.background()


            self.matrix.SwapOnVSync(self.canvas)

            if text_width_up > 43:
                pos_up -= 1
            if text_width_down > 43:
                pos_down -= 1

            if pos_up < -text_width_up + 20:
                pos_up = 64
            if pos_down < -text_width_down + 20:
                pos_down = 64

            time.sleep(0.05)
            
    def content(self):
        self.thread_run = True
        while self.thread_run:  # Überprüfe den Anzeigemodus
            self.canvas.Clear()
            train_list = self.train_list
            pos_up = 64
            pos_down = 64
            destination_down = ""
            destination_up = train_list[0].get_final_destination()
            text_width_up = graphics.DrawText(self.canvas, self.font_normal, pos_up, 10, self.color_font, destination_up)
            
            pos_up = 20 if text_width_up < 43 else 64
            
            if len(self.train_list) > 1:
                destination_down = train_list[1].get_final_destination()
                text_width_down = graphics.DrawText(self.canvas, self.font_normal, pos_down, 26, self.color_font, destination_down) #Position ist 26
                if text_width_down <= 43:
                    pos_down = 20
            else:
                text_width_down = 0
                
            self.display_departure(train_list[0], upper=True)
            self.display_icon(train_list[0], upper=True)
            if len(train_list) > 1:
                self.display_departure(train_list[1], upper=False)
                self.display_icon(train_list[1], upper=False)
            self.background()
            while train_list == self.train_list:
                self.display_final_destination_new(destination_up, pos_up, self.color_font, upper=True)
                if len(train_list) > 1:
                    self.display_final_destination_new(destination_down, pos_down, self.color_font, upper=False)
                self.matrix.SwapOnVSync(self.canvas)
                time.sleep(0.05)
                self.display_final_destination_new(destination_up, pos_up, graphics.Color(0,0,0), upper=True)
                if len(train_list) > 1:
                    self.display_final_destination_new(destination_down, pos_down, graphics.Color(0,0,0), upper=False)
                if text_width_up > 43:
                    pos_up -= 1
                if text_width_down > 43:
                    pos_down -= 1
                if pos_up < -text_width_up + 24:
                    pos_up = 59
                if pos_down < -text_width_down + 20:
                    pos_down = 64
                # print("lsdkjf")
            
    def display_final_destination(self, train:Train, pos, color, upper=True): #Funktion um den Endpunkt anzuzeigen
        margin = 0 if upper else 16
        graphics.DrawText(self.canvas, self.font_normal, pos, 8+margin, color, train.get_final_destination())  # Verwende self.message
        # Zeichne schwarzes Rechteck oben links
        for x in range(17):
            for y in range(14):
                self.canvas.SetPixel(x + 1, y + 1 + margin, 0, 0, 0)
                
    def display_final_destination_new(self, text, pos_x, color, upper=True): #Funktion um den Endpunkt anzuzeigen
        margin = 0 if upper else 16
        for char in text:
            char_width = 5

            # Skip Zeichen ganz links außerhalb
            if pos_x + char_width < 24:
                pos_x += char_width
                continue

            # Stop, wenn außerhalb rechts
            if pos_x > 59:
                break

            # Nur zeichnen, wenn (teilweise) sichtbar
            graphics.DrawText(self.canvas, self.font_normal, pos_x, margin+8, color, char)
            pos_x += char_width
    
    def display_departure(self, train:Train, upper=True): #Funktion um den Abfahrtsort anzuzeigen
        margin = 0 if upper else 16
        departure = train.get_departure_planned()  # Hole den Abfahrtsort
        if train.get_canceled():
            color = self.color_red # Rot für gecancelte Züge
        else:
            color = self.color_font
        departure = departure.strftime("%H:%M")  # Konvertiere in lesbares Format
        graphics.DrawText(self.canvas, self.font_normal, 20, margin+15, color, departure)  # Verwende self.message
        if train.get_canceled():
            graphics.DrawText(self.canvas, self.font_normal, 47, margin+15, self.color_red, "XXX")
        elif train.get_delay() == None:
            pass
        elif train.get_delay() < 5:
            graphics.DrawText(self.canvas, self.font_normal, 47, margin+15, self.color_green, f"+{train.get_delay()}")
        else:
            graphics.DrawText(self.canvas, self.font_normal, 47, margin+15, self.color_red, f"+{train.get_delay()}")
            
    def display_icon(self, train:Train, upper=True):
        margin = 0 if upper else 16
        train_type = train.get_train_type()
        train_number = train.get_train_number()
        train_line = train.get_train_line()
        if train.get_train_type() == "S":
            try:
                icon = Image.open(f"icons/S{train_line}.png")
            except FileNotFoundError:
                icon = Image.open("icons/sbahn.png")
        else:
            icon = Image.open("icons/standard.png")
        icon = icon.convert("RGB")
        for x in range(17):
            for y in range(14):
                r, g, b = icon.getpixel((x, y))
                self.canvas.SetPixel(x + 1, y + 1 + margin, r, g, b)
        if train_type != "S":
            text = train_line if train_line else train_number
            graphics.DrawText(self.canvas, self.font_normal, 2, 8 + margin, self.color_font, train_type[:3])
            if len(text) == 4:
                graphics.DrawText(self.canvas, self.font_small, 2, 15 + margin, self.color_font, text)
            elif len(text) < 4:
                graphics.DrawText(self.canvas, self.font_normal, 2, 15 + margin, self.color_font, text)

    
    def update_message(self, new_message): #Funktion um die Nachricht zu ändern
        self.message = new_message

    def display_no_wifi(self): #Methode um No Wifi anzuzeigen
        self.canvas.Clear()
        self.background() #Rufe die Background Methode der Klasse auf
        pil_image = Image.new("RGB", (self.canvas.width, self.canvas.height))
        draw = ImageDraw.Draw(pil_image)
        draw.arc([26, 10, 38, 22], start=180, end=360, fill=(255, 0, 0))
        draw.arc([24, 8, 40, 24], start=180, end=360, fill=(255, 0, 0))
        draw.arc([22, 6, 42, 26], start=180, end=360, fill=(255, 0, 0))
        draw.ellipse([31, 16, 33, 18], fill=(255, 0, 0))
        self.canvas.SetImage(pil_image)
        self.matrix.SwapOnVSync(self.canvas)
        
    def display_no_trains(self): #Methode um No Trains anzuzeigen
        self.canvas.Clear()
        graphics.DrawText(self.canvas, self.font_normal, 9, 18, self.color_font, "No trains")
        self.matrix.SwapOnVSync(self.canvas)

    # def set_display_mode(self, mode): #Funktion um den Anzeigemodus zu setzen
    #     if mode in ("content", "no_wifi"):
    #         self.display_mode = mode
    #         if mode == "content":
    #             if len(self.train_list) == 0:
    #                 if self.thread: #Beende den alten Thread
    #                     self.thread_run = False
    #                     self.thread.join()
    #                 self.display_no_trains()
    #             else:
    #                 if self.thread is None: #Wenn der Thread nicht existiert
    #                     self.thread = threading.Thread(target=self.content)
    #                     self.thread.start()
    #         elif mode == "no_wifi":
    #             if self.thread: #Beende den alten Thread
    #                 self.thread_run = False
    #                 self.thread.join()
    #             self.display_no_wifi() #Zeige No Wifi direkt an
    #     else:
    #         raise ValueError("Invalid display mode.  Must be 'content' or 'no_wifi'.")

    def start_display(self): #Starte die Anzeige
        thread = threading.Thread(target=self.setup_display)
        thread.start()
        
    # def start_display(self): #Starte die Anzeige
    #     station = Station("Winnenden","529fc99d86062cff082818f1820c4900","ef252166427b5094f093b9e5f331508c")
    #     self.train_list = station.get_sorted_departure_list(num_hours=5)[0:1]
    #     if self.display_mode == "content":
    #         self.thread = threading.Thread(target=self.content)
    #         self.thread.start()
    #     elif self.display_mode == "no_wifi":
    #         self.display_no_wifi()
            
    def setup_display(self):
        while True:
            try:
                station = Station(self.station,"529fc99d86062cff082818f1820c4900","ef252166427b5094f093b9e5f331508c")
                train_list = station.get_sorted_departure_list(time_flag=int(datetime.datetime.now().strftime("%y%m%d%H%M")),num_hours=5)
                
            except:
                # print(f"Error fetching train data: {e}")
                station = None
                
            if station is not None:
                self.train_list = train_list[0:3]
                if len(self.train_list) == 0:
                    if self.thread: #Beende den alten Thread
                        self.thread_run = False
                        self.thread.join()
                    self.display_no_trains()
                    print("No trains available")
                else:
                    if self.thread is None or not self.thread.is_alive(): #Wenn der Thread nicht existiert
                        self.thread = threading.Thread(target=self.content)
                        self.thread.start()
                    print("Trains available")
            else:
                if self.thread: #Beende den alten Thread
                    self.thread_run = False
                    self.thread.join()
                self.display_no_wifi()
                print("No wifi available")
                
            time.sleep(60)  # Warte 5 Sekunden, bevor du die Liste aktualisierst
        
    def stop_display(self):
        if self.thread:
            self.thread.join() #Warte bis der Thread beendet ist
        self.canvas.Clear()  # Leere die Canvas
        self.matrix.SwapOnVSync(self.canvas)  # Aktualisiere die Matrix
        

# class MatrixNoWifi(MatrixHelper): #Entferne die Klasse MatrixNoWifi
#     def __init__(self, matrix, canvas, graphics_accent_color):
#         super().__init__(matrix, canvas, graphics_accent_color)
#         self.display_mode = "no_wifi"

#     def background(self): #Korrigiere die Background Methode wie im Code
#         graphics.DrawLine(self.canvas, 0, 0, 63, 0, Color(255,0,0))
#         graphics.DrawLine(self.canvas, 0, 31, 63, 31, Color(255,0,0))
#         graphics.DrawLine(self.canvas, 0, 0, 0, 31, Color(255,0,0))
#         graphics.DrawLine(self.canvas, 63, 0, 63, 31, Color(255,0,0))

if __name__ == "__main__":
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
    time.sleep(50) #Warte 5 Sekunden
    # while True:
        
    #     pass
    # try:
    #     # Simuliere einen Wechsel zwischen den Modi
    #     time.sleep(5)  # Zeige die Laufschrift für 5 Sekunden
    #     helper.set_display_mode("no_wifi")  # Wechsle zu "No Wifi"
    #     time.sleep(5)
    #     helper.update_message("Wieder verbunden!") #Ändere die Nachricht
    #     helper.set_display_mode("content")  # Zurück zur Laufschrift
    #     time.sleep(5)
    #     helper.stop_display()

    # except KeyboardInterrupt:
    #     print("Exiting...")
    #     helper.stop_display() #Stoppe den Thread vor dem Beenden
