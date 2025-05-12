# stat_analyzer.py
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "units")
STATS_TO_ANALYZE = ["str", "dex", "con", "int", "wis", "cha"]
STAT_PRICE = 25
BALANCED_STAT_TOTAL = STAT_PRICE * len(STATS_TO_ANALYZE)

def load_unit_data(filepath):
    """Loads unit data from a JSON file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON in '{filepath}'.")
        return None

def analyze_stat_balance():
    """Loads unit data and analyzes the balance of their stats relative to a target."""
    unit_files = [f for f in os.listdir(UNITS_DIR) if f.endswith(".json")]

    if not unit_files:
        print("No unit files found in the 'units' directory.")
        return

    print(f"\n--- Unit Stat Balance Analysis (Stat Price: {STAT_PRICE}) ---")
    print(f"Balanced Total Stat Points: {BALANCED_STAT_TOTAL}\n")

    for filename in unit_files:
        filepath = os.path.join(UNITS_DIR, filename)
        unit_data = load_unit_data(filepath)
        if unit_data and 'name' in unit_data and 'stats' in unit_data and 'cost' in unit_data:
            total_stat_points = sum(unit_data['stats'].get(stat, 0) for stat in STATS_TO_ANALYZE)
            stat_difference = total_stat_points - BALANCED_STAT_TOTAL
            print(f"Unit: {unit_data['name']}")
            print(f"  Cost: {unit_data['cost']}")
            print(f"  Total Stat Points: {total_stat_points}")
            print(f"  Difference from Balanced: {stat_difference} ({(stat_difference / BALANCED_STAT_TOTAL) * 100:.2f}%)")
            print("-" * 30)
        else:
            print(f"Warning: Could not process unit data in '{filename}'. Ensure 'name', 'stats', and 'cost' fields exist.")

if __name__ == "__main__":
    analyze_stat_balance()
