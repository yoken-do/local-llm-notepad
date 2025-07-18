
import json
from pathlib import Path

parent = Path(__file__).parent

settings_path = Path("settings.json")

def load_settings():
    if settings_path.exists():
        with open(settings_path, mode='r', encoding="utf-8") as f:
            data = json.load(f)
        if not Path(data['model']['path']).exists():
            data['model']['path'] = "gemma-3-1b-it-Q4_K_M.gguf"
    else:
        data = {
            "model": {
                "path": "gemma-3-1b-it-Q4_K_M.gguf",
                "prompt": "You helpful assistant"
            },

            "bindings": {
                "send": "Shift-Return",
                "find": "Control-f",
                "edit-system-prompt": "Control-p",
                "stop-generation": "Control-z",
                "clear": "Control-x"
            }
        }
    return data

def save_settings(data, path, prompt):
    data["model"]["path"] = path
    data["model"]["prompt"] = prompt
    with open("settings.json", mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
