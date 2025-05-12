# unit_editor/editor.py
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "..", "units")

def load_json(filepath):
    """Loads JSON data from the given filepath."""
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
        for i, unit in enumerate(units):
            print(f"{i + 1}. {unit}")
        print("-----------------------")
        return units
    else:
        print("\nNo units available yet.")
        return []

def get_unit_by_index(units, index):
    if 1 <= index <= len(units):
        return units[index - 1]
    else:
        print("Invalid unit number.")
        return None

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
    return unit_data # Return the loaded data

def add_unit():
    unit_name = input("Enter the name of the new unit: ").strip().replace(" ", "_").lower()
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    if os.path.exists(filepath):
        print(f"Error: Unit '{unit_name}' already exists.")
        return None # Indicate failure

    new_unit = {
        'name': unit_name,
        'description': input("Enter the unit's description: ").strip(),
        'stats': {},
        'cost': 0,
        'type': input("Enter the unit's type: ").strip().lower(),
        'tags': []
    }

    print("\nEnter the unit's stats (leave name blank to finish):")
    while True:
        stat_name = input("  Stat name: ").strip().lower()
        if not stat_name:
            break
        while True:
            stat_value_str = input(f"  Value for '{stat_name}': ").strip()
            try:
                new_unit['stats'][stat_name] = int(stat_value_str)
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

    while True:
        cost_str = input("Enter the unit's cost: ").strip()
        try:
            new_unit['cost'] = int(cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    tags_str = input("Enter the unit's tags (comma-separated): ").strip()
    new_unit['tags'] = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

    try:
        with open(filepath, 'w') as f:
            json.dump(new_unit, f, indent=2)
        print(f"Unit '{unit_name}' added successfully.")
        return new_unit # Indicate success by returning the new unit data
    except IOError:
        print(f"Error: Could not write to file '{filepath}'.")
        return None # Indicate failure

def edit_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    unit_data = load_json(filepath)
    if not unit_data:
        return None # Indicate failure

    print(f"\n--- Editing '{unit_data['name']}' ---")

    unit_data['description'] = input(f"New description (current: {unit_data['description']}): ").strip() or unit_data['description']

    print("\nCurrent stats:")
    for key, value in list(unit_data['stats'].items()):
        new_value_str = input(f"  {key.capitalize()} (current: {value}, type 'del' to delete): ").strip().lower()
        if new_value_str == 'del':
            del unit_data['stats'][key]
        elif new_value_str:
            try:
                unit_data['stats'][key] = int(new_value_str)
            except ValueError:
                print("Invalid value. Keeping the current value.")
        elif key not in unit_data['stats']:
            pass
        else:
            print("Keeping the current value.")

    print("\nAdd new stats (leave name blank to finish):")
    while True:
        new_stat_name = input("  New stat name: ").strip().lower()
        if not new_stat_name:
            break
        while True:
            new_stat_value_str = input(f"  Value for '{new_stat_name}': ").strip()
            try:
                new_stat_value = int(new_stat_value_str)
                unit_data['stats'][new_stat_name] = new_stat_value
                break
            except ValueError:
                print("Invalid value. Please enter a number.")

    while True:
        new_cost_str = input(f"New cost (current: {unit_data['cost']}): ").strip() or str(unit_data['cost'])
        try:
            unit_data['cost'] = int(new_cost_str)
            break
        except ValueError:
            print("Invalid cost. Please enter a number.")

    unit_data['type'] = input(f"New type (current: {unit_data['type']}): ").strip() or unit_data['type']

    tags_str = input(f"New tags (comma-separated, current: {', '.join(unit_data['tags'])}): ").strip()
    unit_data['tags'] = [tag.strip().lower() for tag in tags_str.split(',') if tag.strip()]

    try:
        with open(filepath, 'w') as f:
            json.dump(unit_data, f, indent=2)
        print(f"Unit '{unit_name}' updated successfully.")
        return unit_data # Indicate success by returning the updated unit data
    except IOError:
        print(f"Error: Could not write to file '{filepath}'.")
        return None # Indicate failure


def delete_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    if os.path.exists(filepath):
        confirm = input(f"Are you sure you want to delete '{unit_name}'? (yes/no): ").lower()
        if confirm == 'yes':
            try:
                os.remove(filepath)
                print(f"Unit '{unit_name}' deleted.")
                return True # Indicate successful deletion
            except OSError:
                print(f"Error: Could not delete file '{filepath}'.")
                return False # Indicate deletion failure
        else:
            print("Deletion cancelled.")
            return False # Indicate cancellation
    else:
        print(f"Error: Unit '{unit_name}' not found.")
        return False # Indicate unit not found

def clone_unit(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    unit_data = load_json(filepath)
    if not unit_data:
        return None # Indicate failure

    new_unit_name = input(f"Enter the name for the cloned unit (current: '{unit_data['name']}'): ").strip().replace(" ", "_").lower()
    new_filepath = os.path.join(UNITS_DIR, f"{new_unit_name}.json")
    if os.path.exists(new_filepath):
        print(f"Error: Unit '{new_unit_name}' already exists.")
        return None # Indicate failure

    unit_data['name'] = new_unit_name

    try:
        with open(new_filepath, 'w') as f:
            json.dump(unit_data, f, indent=2)
        print(f"Unit '{unit_name}' cloned to '{new_unit_name}' successfully.")
        return unit_data # Indicate success by returning the cloned unit data
    except IOError:
        print(f"Error: Could not write to file '{new_filepath}'.")
        return None # Indicate failure

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
        elif choice in ['2', '4', '5', '6']:
            units = list_units()
            if units:
                try:
                    unit_index = int(input("Enter the number of the unit to operate on: "))
                    unit_name = get_unit_by_index(units, unit_index)
                    if unit_name:
                        if choice == '2':
                            inspect_unit(unit_name)
                        elif choice == '4':
                            edit_unit(unit_name)
                        elif choice == '5':
                            delete_unit(unit_name)
                        elif choice == '6':
                            clone_unit(unit_name)
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif choice == '3':
            add_unit()
        elif choice == '7':
            print("Exiting Unit Editor.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
