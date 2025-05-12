# stat_visualizer.py
import json
import os
import matplotlib.pyplot as plt

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "units")
STATS_TO_ANALYZE = ["str", "dex", "con", "int", "wis", "cha"]

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

def visualize_stat_spread():
    """Loads unit data and visualizes the spread of key stats using box plots."""
    unit_stats = {stat: [] for stat in STATS_TO_ANALYZE}
    unit_files = [f for f in os.listdir(UNITS_DIR) if f.endswith(".json")]

    if not unit_files:
        print("No unit files found in the 'units' directory.")
        return

    for filename in unit_files:
        filepath = os.path.join(UNITS_DIR, filename)
        unit_data = load_unit_data(filepath)
        if unit_data and 'stats' in unit_data:
            for stat in STATS_TO_ANALYZE:
                if stat in unit_data['stats']:
                    unit_stats[stat].append(unit_data['stats'][stat])

    plt.figure(figsize=(10, 6))
    positions = range(len(STATS_TO_ANALYZE))
    labels = [stat.upper() for stat in STATS_TO_ANALYZE]
    data_to_plot = [unit_stats[stat] for stat in STATS_TO_ANALYZE]

    plt.boxplot(data_to_plot, positions=positions, labels=labels)
    plt.title("Unit Stat Spread")
    plt.xlabel("Stat")
    plt.ylabel("Value")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_stat_spread()
