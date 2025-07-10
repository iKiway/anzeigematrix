import json


with open("test.json", "r") as f:
    config = json.load(f)

app_value = config.get("current_app")  # Standardwert "db", falls nicht vorhanden

if app_value == "clock":

    print(app_value)
else:
    print(app_value)