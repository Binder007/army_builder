import json
import os

# Automatically determine the path to the "units" folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "units")

def list_unit_files():
    """Returns a list of available unit file names (without .json extension)."""
    return [f.replace(".json", "") for f in os.listdir(UNITS_DIR) if f.endswith(".json")]

def load_unit(unit_name):
    """Loads a unit JSON file by name and returns the parsed data."""
    path = os.path.join(UNITS_DIR, f"{unit_name}.json")
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Unit file not found: {path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {path}")
        return None

def get_unit_by_name(unit_name):
    """Alias for load_unit for compatibility with legacy code."""
    return load_unit(unit_name)