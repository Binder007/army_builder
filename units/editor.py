# unit_editor/editor.py
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "..", "units")

def load_json(filepath):
    """
    Loads JSON data from the given filepath.

    Args:
        filepath (str): The path to the JSON file.

    Returns:
        dict or None: The loaded JSON data as a dictionary, or None if an error occurs.
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON in '{filepath}'.")
        return None

def list_units():
    units = [f.replace(".json", "") for f in os.listdir(UNITS_DIR) if f.endswith(".json")]
    if units:
        print("\n--- Available Units ---")
        for unit in units:
            print(f"- {unit}")
        print("-----------------------")
    else:
        print("\nNo units available yet.")

def inspect_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    unit_data = load_json(filepath)
    if unit_data:
        print(f"\n--- {unit_data['name']} ---")
        print(f"Description: {unit_data['description']}")
        print("Stats:")
        for key, value in unit_data['stats'].items():
            print(f"  {key.capitalize()}: {value}")
        print(f"Cost: {unit_data['cost']}")
        print(f"Type: {unit_data['type']}")
        if 'tags' in unit_data:
            print(f"Tags: {', '.join(unit_data['tags'])}")
        print("----------------------")

def add_unit():
    unit_name = input("Enter the name of the new unit: ").strip()
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    if os.path.exists(filepath):
        print(f"Error: Unit '{unit_name}' already exists.")
        return

    description = input("Enter the unit's description: ").strip()
    stats = {}
    print("Enter unit stats (leave blank to finish):")
    while True:
        stat_name = input("  Stat name: ").strip()
        if not stat_name:
            break
        while True:
            stat_value_str = input(f"  Value for '{stat_name}': ").strip()
            try:
                stat_value = int(stat_value_str)
                stats[stat_name.lower()] = stat_value
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

    while True:
        cost_str = input("Enter the unit's cost: ").strip()
        try:
            cost = int(cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    unit_type = input("Enter the unit's type: ").strip()
    tags_str = input("Enter any tags for the unit (comma-separated, leave blank for none): ").strip()
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    new_unit = {
        "name": unit_name,
        "description": description,
        "stats": stats,
        "cost": cost,
        "type": unit_type,
        "tags": tags
    }

    try:
        with open(filepath, 'w') as f:
            json.dump(new_unit, f, indent=2)
        print(f"Unit '{unit_name}' added successfully.")
    except IOError:
        print(f"Error: Could not write to file '{filepath}'.")

def edit_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    unit_data = load_json(filepath)
    if not unit_data:
        return

    print(f"\n--- Editing '{unit_data['name']}' ---")

    unit_data['description'] = input(f"New description (current: {unit_data['description']}): ").strip() or unit_data['description']

    print("\nCurrent stats:")
    for key, value in unit_data['stats'].items():
        new_value_str = input(f"  {key.capitalize()} (current: {value}): ").strip()
        if new_value_str:
            try:
                unit_data['stats'][key] = int(new_value_str)
            except ValueError:
                print("Invalid value. Keeping the current value.")

    while True:
        new_cost_str = input(f"New cost (current: {unit_data['cost']}): ").strip() or str(unit_data['cost'])
        try:
            unit_data['cost'] = int(new_cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    unit_data['type'] = input(f"New type (current: {unit_data['type']}): ").strip() or unit_data['type']

    tags_str = input(f"New tags (comma-separated, current: {', '.join(unit_data['tags'])}): ").strip()
    unit_data['tags'] = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

    try:
        with open(filepath, 'w') as f:
            json.dump(unit_data, f, indent=2)
        print(f"Unit '{unit_name}' updated successfully.")
    except IOError:
        print(f"Error: Could not write to file '{filepath}'.")

def delete_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    if os.path.exists(filepath):
        confirm = input(f"Are you sure you want to delete '{unit_name}'? (yes/no): ").lower()
        if confirm == 'yes':
            try:
                os.remove(filepath)
                print(f"Unit '{unit_name}' deleted.")
            except OSError:
                print(f"Error: Could not delete file '{filepath}'.")
        else:
            print("Deletion cancelled.")
    else:
        print(f"Error: Unit '{unit_name}' not found.")

def clone_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    unit_data = load_json(filepath)
    if not unit_data:
        return

    new_unit_name = input(f"Enter the name for the cloned unit (current: '{unit_data['name']}_clone'): ").strip() or f"{unit_data['name']}_clone"
    new_filepath = os.path.join(UNITS_DIR, f"{new_unit_name}.json")
    if os.path.exists(new_filepath):
        print(f"Error: Unit '{new_unit_name}' already exists.")
        return

    unit_data['name'] = new_unit_name

    try:
        with open(new_filepath, 'w') as f:
            json.dump(unit_data, f, indent=2)
        print(f"Unit '{unit_name}' cloned to '{new_unit_name}' successfully.")
    except IOError:
        print(f"Error: Could not write to file '{new_filepath}'.")

def main():
    while True:
        print("\n--- Unit Editor ---")
        print("1. List Units")
        print("2. Inspect Unit")
        print("3. Add Unit")
        print("4. Edit Unit")
        print("5. Delete Unit")
        print("6. Clone Unit")
        print("7. Exit Editor")

        choice = input("Enter your choice: ")

        if choice == '1':
            list_units()
        elif choice == '2':
            unit_name = input("Enter unit name to inspect: ")
            inspect_unit(unit_name)
        elif choice == '3':
            add_unit()
        elif choice == '4':
            unit_name = input("Enter unit name to edit: ")
            edit_unit(unit_name)
        elif choice == '5':
            unit_name = input("Enter unit name to delete: ")
            delete_unit(unit_name)
        elif choice == '6':
            unit_name = input("Enter unit name to clone: ")
            clone_unit(unit_name)
        elif choice == '7':
            print("Exiting Unit Editor.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
