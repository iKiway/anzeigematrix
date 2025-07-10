from App import App

class Clock(App):
    def __init__(self, matrix, canvas, graphics_accent_color):
        super().__init__(matrix, canvas)
        self.graphics_accent_color = graphics_accent_color
    
    def background(self):
        # Hier kannst du den Hintergrund für die Uhr setzen
        self.canvas.Clear()
        self.canvas.SetPixel(0, 0, self.graphics_accent_color.red, self.graphics_accent_color.green, self.graphics_accent_color.blue)
        self.matrix.SwapOnVSync(self.canvas)
        
    def start_display(self):
        self.background()
    
    def stop_display(self):
        self.canvas.Clear()
        self.matrix.SwapOnVSync(self.canvas)