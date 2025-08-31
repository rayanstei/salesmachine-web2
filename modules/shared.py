import json
import os

class SharedData:
    SHARED_DIR = "shared_data"
    if not os.path.exists(SHARED_DIR):
        os.makedirs(SHARED_DIR)

    @staticmethod
    def export_prospects(prospects, filename="prospects_export.json"):
        filepath = os.path.join(SharedData.SHARED_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(prospects, f, ensure_ascii=False, indent=4)
        return filepath

    @staticmethod
    def import_prospects(filename="prospects_export.json"):
        filepath = os.path.join(SharedData.SHARED_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []