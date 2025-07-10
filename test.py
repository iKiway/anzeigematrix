import json
from App import App

with open("test.json", "r") as f:
    config = json.load(f)

app_value = config.get("current_app")  # Standardwert "db", falls nicht vorhanden

helper: App
helper = App("s","b")

if app_value == "clock":
    locals().get('helper', None) and helper.stop_display()  # Stoppe die vorherige Anzeige, falls vorhanden
    print(app_value)
else:
    locals().get('helper', None) and helper.stop_display()  # Stoppe die vorherige Anzeige, falls vorhanden
    print(app_value)
    
print(config)