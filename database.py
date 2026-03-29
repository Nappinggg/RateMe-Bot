
import json
import os

class JSONDatabase:
    def __init__(self, filename):
        self.filename = filename

    # function for downloading base with running
    def load(self):
        if not os.path.exists(self.filename):
            return {} # if no file return empty
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Помилка завантаження бази: {e}")
            return {}

    # function for database saving (call everytime when someone is creating profile)
    def save(self, data):
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Помилка збереження бази: {e}")
