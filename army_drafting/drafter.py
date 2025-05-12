# army_drafting/drafter.py
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "..", "units")
RULES_DIR = os.path.join(SCRIPT_DIR, "..", "army_rules")
DRAFTED_ARMIES_DIR = os.path.join(SCRIPT_DIR, "..", "drafted_armies")

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

def save_json(filepath, data):
    """Saves JSON data to the given filepath."""
    try:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except IOError:
        print(f"Error: Could not save data to '{filepath}'.")
        return False

def list_available_units():
    """Lists all available units from the units directory."""
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

def get_unit_data(unit_name):
    """Loads the data for a specific unit."""
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    return load_json(filepath)

def display_unit_details(unit_data):
    """Displays the details of a unit."""
    if unit_data:
        print(f"\n--- {unit_data['name']} ---")
        print(f"Description: {unit_data['description']}")
        print(f"Cost: {unit_data['cost']}")
        print("Stats:")
        for key, value in unit_data['stats'].items():
            print(f"  {key.capitalize()}: {value}")
        if 'tags' in unit_data:
            print(f"Tags: {', '.join(unit_data['tags'])}")
        print("----------------------")

def load_drafting_rules():
    """Loads the army drafting rules from the army_rules directory."""
    filepath = os.path.join(RULES_DIR, "rules.json")
    rules = load_json(filepath)
    if rules and 'point_limit' in rules:
        return rules
    else:
        print("Warning: Could not load drafting rules or 'point_limit' not found. Setting point limit to 0.")
        return {'point_limit': 0}

def set_point_limit():
    """Allows the user to set or change the army point limit."""
    global current_point_limit
    while True:
        point_limit_str = input(f"Enter the army point limit (current: {current_point_limit}): ").strip()
        if not point_limit_str:
            return current_point_limit # Keep the current limit if nothing is entered
        try:
            point_limit = int(point_limit_str)
            if point_limit >= 0:
                return point_limit
            else:
                print("Point limit must be a non-negative number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def add_unit_to_army(army, unit_name, point_limit, quantity=1):
    """Adds a specified quantity of a unit to the drafted army."""
    unit_data = get_unit_data(unit_name)
    if unit_data:
        if 'cost' in unit_data:
            cost_of_batch = unit_data['cost'] * quantity
            if sum(unit['cost'] for unit in army) + cost_of_batch <= point_limit:
                for _ in range(quantity):
                    army.append(unit_data)
                print(f"{quantity} x '{unit_data['name']}' added to the army.")
            else:
                print(f"Error: Adding {quantity} x '{unit_data['name']}' would exceed the point limit of {point_limit}.")
        else:
            print(f"Error: Unit '{unit_name}' has no 'cost' defined.")
    return army

def remove_unit_from_army(army, index):
    """Removes a unit from the drafted army by its list index."""
    if 1 <= index <= len(army):
        removed_unit = army.pop(index - 1)
        print(f"'{removed_unit['name']}' removed from the army.")
    else:
        print("Invalid unit number in the army.")
    return army

def display_current_army(army):
    """Displays the units currently in the drafted army."""
    if army:
        print("\n--- Current Army Composition ---")
        total_cost = sum(unit['cost'] for unit in army)
        unit_counts = {}
        for unit in army:
            unit_counts[unit['name']] = unit_counts.get(unit['name'], 0) + 1

        for unit_name, count in unit_counts.items():
            # Find the cost of one unit
            cost = next((u['cost'] for u in army if u['name'] == unit_name), 0)
            print(f"- {count} x {unit_name} (Cost per unit: {cost}, Total Cost: {count * cost})")

        print(f"--------------------------------")
        print(f"Total Cost: {total_cost}")
    else:
        print("\nArmy is currently empty.")

def list_saved_armies():
    """Lists all saved armies in the drafted_armies directory."""
    armies = [f.replace(".json", "") for f in os.listdir(DRAFTED_ARMIES_DIR) if f.endswith(".json")]
    if armies:
        print("\n--- Saved Armies ---")
        for i, army_name in enumerate(armies):
            print(f"{i + 1}. {army_name}")
        print("--------------------")
        return armies
    else:
        print("\nNo saved armies yet.")
        return []

def load_saved_army(army_name):
    """Loads a saved army from the drafted_armies directory."""
    filepath = os.path.join(DRAFTED_ARMIES_DIR, f"{army_name}.json")
    saved_army_data = load_json(filepath)
    if saved_army_data and 'units' in saved_army_data:
        loaded_army = []
        for unit_name, quantity in saved_army_data['units'].items():
            unit_data = get_unit_data(unit_name)
            if unit_data:
                for _ in range(quantity):
                    loaded_army.append(unit_data)
        return loaded_army, saved_army_data.get('name', army_name.replace("_", " ").replace(".json", ""))
    else:
        print(f"Error: Could not load army '{army_name}'. Invalid format.")
        return [], "new unsaved army"

def save_drafted_army(army, army_name=""):
    """Saves the currently drafted army to a JSON file in the drafted_armies directory."""
    if not os.path.exists(DRAFTED_ARMIES_DIR):
        os.makedirs(DRAFTED_ARMIES_DIR)

    if not army_name:
        army_name = input("Enter a name for this drafted army (e.g., my_first_draft): ").strip().replace(" ", "_")
    filename = army_name + ".json"
    filepath = os.path.join(DRAFTED_ARMIES_DIR, filename)

    # Save a simplified version with counts and the army name
    saved_army_data = {'name': army_name.replace("_", " ").replace(".json", ""), 'units': {}}
    for unit in army:
        saved_army_data['units'][unit['name']] = saved_army_data['units'].get(unit['name'], 0) + 1

    if save_json(filepath, saved_army_data):
        print(f"Army composition saved to '{filepath}' successfully.")
        return army_name.replace("_", " ").replace(".json", "")
    else:
        return "new unsaved army"

def main():
    global current_point_limit
    current_army_name = "new unsaved army"
    rules = load_drafting_rules()
    current_point_limit = rules.get('point_limit', 0)
    drafted_army = []

    while True:
        current_total_cost = sum(unit['cost'] for unit in drafted_army)
        print("\n--- Army Drafter ---")
        print(f"Current Army: {current_army_name}")
        print(f"Current Point Limit: {current_point_limit}")
        print(f"Current Total Cost: {current_total_cost}")
        print(f"Current Army Size: {len(drafted_army)}")
        print("1. List Available Units")
        print("2. View Unit Details")
        print("3. Add Unit(s) to Army")
        print("4. Remove Unit from Army")
        print("5. Display Current Army")
        print("6. Set/Change Point Limit")
        print("7. Save Drafted Army")
        print("8. Load Saved Army")
        print("9. Exit Drafter")

        choice = input("Enter your choice: ")

        if choice == '1':
            list_available_units()
        elif choice == '2':
            available_units = list_available_units()
            if available_units:
                try:
                    unit_index = int(input("Enter the number of the unit to view: "))
                    if 1 <= unit_index <= len(available_units):
                        unit_name = available_units[unit_index - 1]
                        unit_data = get_unit_data(unit_name)
                        display_unit_details(unit_data)
                    else:
                        print("Invalid unit number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif choice == '3':
            available_units = list_available_units()
            if available_units:
                try:
                    unit_index = int(input("Enter the number of the unit to add: "))
                    if 1 <= unit_index <= len(available_units):
                        unit_name = available_units[unit_index - 1]
                        while True:
                            quantity_str = input(f"Enter the quantity of '{unit_name}' to add (default: 1): ").strip()
                            quantity = 1
                            if quantity_str:
                                try:
                                    quantity = int(quantity_str)
                                    if quantity > 0:
                                        break
                                    else:
                                        print("Quantity must be a positive number.")
                                except ValueError:
                                    print("Invalid input. Please enter a number.")
                            else:
                                break # Use default quantity of 1
                        drafted_army = add_unit_to_army(drafted_army, unit_name, current_point_limit, quantity)
                    else:
                        print("Invalid unit number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif choice == '4':
            if drafted_army:
                display_current_army(drafted_army)
                try:
                    unit_index_remove = int(input("Enter the number of the unit to remove: "))
                    drafted_army = remove_unit_from_army(drafted_army, unit_index_remove)
                except ValueError:
                    print("Invalid input. Please enter a number.")
            else:
                print("Army is currently empty. Nothing to remove.")
        elif choice == '5':
            display_current_army(drafted_army)
        elif choice == '6':
            current_point_limit = set_point_limit()
        elif choice == '7':
            if drafted_army:
                current_army_name = save_drafted_army(drafted_army)
            else:
                print("Cannot save an empty army.")
        elif choice == '8':
            saved_armies = list_saved_armies()
            if saved_armies:
                try:
                    army_index = int(input("Enter the number of the army to load: "))
                    if 1 <= army_index <= len(saved_armies):
                        selected_army_name = saved_armies[army_index - 1]
                        drafted_army, current_army_name = load_saved_army(selected_army_name)
                        current_total_cost = sum(unit['cost'] for unit in drafted_army) # Recalculate cost
                        print(f"Army '{current_army_name}' loaded successfully.")
                    else:
                        print("Invalid army number.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        elif choice == '9':
            print("Exiting Army Drafter.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
