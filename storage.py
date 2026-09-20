import json
import os
# -----------------------
# Helpers: load / save JSON
# -----------------------
def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # Unreadable file: keep a copy instead of letting the next save overwrite it,
            # then fall back to the default so the app can still start.
            try:
                os.replace(path, path + ".corrupt")
            except OSError:
                pass
            return default
    return default

def save_json(path, data):
    # Write to a temp file first, then swap it in, so a crash mid-write can't leave a half-written file.
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp_path, path)
