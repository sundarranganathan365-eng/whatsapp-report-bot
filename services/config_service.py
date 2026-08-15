import os, json

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "..", "bot_config.json")

class ConfigService:
    DEFAULT_CONFIG = {
        "is_active": True,
        "default_reply": (
            "👋 *Welcome to the Student Report Bot!*\n\n"
            "Please send student details in this format:\n"
            "  `Name: Rahul, Class: 10A, Roll: 23`\n\n"
            "You will be able to choose between:\n"
            "1️⃣ *Weekly Report* (7-day snapshot & tests)\n"
            "2️⃣ *Full Academic Overview* (All-time stats & insights)"
        )
    }

    def _load_config(self):
        if not os.path.exists(CONFIG_FILE):
            self._save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return self.DEFAULT_CONFIG
            
    def _save_config(self, config_data):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)

    def get_config(self):
        return self._load_config()

    def update_config(self, updates):
        config = self._load_config()
        config.update(updates)
        self._save_config(config)
        return config

config_service = ConfigService()
