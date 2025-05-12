import json
import os
import random
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "units")

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

def list_units():
    """Lists available units from the units directory."""
    units = [f.replace(".json", "") for f in os.listdir(UNITS_DIR) if f.endswith(".json")]
    if units:
        print("\n+++ AVAILABLE COMBATANTS +++")
        for i, unit in enumerate(units):
            print(f"[{i + 1}] {unit}")
        print("++++++++++++++++++++++++++++")
        return units
    else:
        print("\nNo units available yet. The arena is empty.")
        return []

def get_unit_by_name(unit_name):
    """Loads and returns unit data by name."""
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    return load_unit_data(filepath)

def calculate_derived_stats(unit_data):
    """Calculates derived stats based on physical attributes."""
    str_val = unit_data['stats'].get('str', 10)
    dex_val = unit_data['stats'].get('dex', 10)
    con_val = unit_data['stats'].get('con', 10)

    hitroll = dex_val // 2
    damroll = str_val // 3
    ac = 10 + dex_val // 4
    hp_total = con_val * 5
    hp_current = hp_total

    return {
        'hitroll': hitroll,
        'damroll': damroll,
        'ac': ac,
        'hp_total': hp_total,
        'hp_current': hp_current
    }

def battle(unit1_data, unit2_data, slow_mode):
    """Simulates a battle between two units with stylized output and simultaneous attacks per round."""
    unit1_derived = calculate_derived_stats(unit1_data)
    unit2_derived = calculate_derived_stats(unit2_data)

    print("\n+++ BATTLE COMMENCES! +++")
    print(f"{unit1_data['name']} (HP: {unit1_derived['hp_current']}/{unit1_derived['hp_total']}, AC: {unit1_derived['ac']}, Hit: +{unit1_derived['hitroll']}, Dam: +{unit1_derived['damroll']})")
    print(f"VERSUS")
    print(f"{unit2_data['name']} (HP: {unit2_derived['hp_current']}/{unit2_derived['hp_total']}, AC: {unit2_derived['ac']}, Hit: +{unit2_derived['hitroll']}, Dam: +{unit2_derived['damroll']})")
    print("--------------------------")

    unit1_hp = unit1_derived['hp_current']
    unit2_hp = unit2_derived['hp_current']
    round_number = 1

    while unit1_hp > 0 and unit2_hp > 0:
        print(f"\n++ ROUND {round_number} ++")

        # Unit 1's attack
        attack_roll_1 = random.randint(1, 20) + unit1_derived['hitroll']
        print(f"{unit1_data['name']} attacks...")
        if attack_roll_1 >= unit2_derived['ac']:
            damage_1 = unit1_derived['damroll'] + random.randint(1, 4)
            unit2_hp -= damage_1
            print(f"  ...strikes true! {unit2_data['name']} takes {damage_1} damage. [HP: {unit2_hp}]")
        else:
            print(f"  ...misses their foe!")

        # Unit 2's attack
        attack_roll_2 = random.randint(1, 20) + unit2_derived['hitroll']
        print(f"{unit2_data['name']} retaliates...")
        if attack_roll_2 >= unit1_derived['ac']:
            damage_2 = unit2_derived['damroll'] + random.randint(1, 4)
            unit1_hp -= damage_2
            print(f"  ...lands a blow! {unit1_data['name']} suffers {damage_2} damage. [HP: {unit1_hp}]")
        else:
            print(f"  ...fails to connect!")

        if slow_mode:
            time.sleep(8)

        round_number += 1

    print("\n+++ BATTLE ENDS! +++")
    if unit1_hp <= 0:
        print(f"{unit2_data['name']} has vanquished {unit1_data['name']}!")
    else:
        print(f"{unit1_data['name']} stands victorious over {unit2_data['name']}!")
    print("++++++++++++++++++++++")

def main():
    available_units = list_units()
    if not available_units:
        return

    print("\nEnter the number of the first brave combatant:")
    while True:
        try:
            choice1 = int(input("> ")) - 1
            if 0 <= choice1 < len(available_units):
                unit1_name = available_units[choice1]
                unit1_data = get_unit_by_name(unit1_name)
                break
            else:
                print("Invalid selection. Choose wisely.")
        except ValueError:
            print("Invalid input. Numbers only, adventurer.")

    print("\nEnter the number of the second unfortunate soul:")
    while True:
        try:
            choice2 = int(input("> ")) - 1
            if 0 <= choice2 < len(available_units):
                unit2_name = available_units[choice2]
                if unit2_name == unit1_name:
                    print("A combatant cannot fight themselves! Choose another.")
                    continue
                unit2_data = get_unit_by_name(unit2_name)
                break
            else:
                print("Invalid selection. The arena awaits a worthy opponent.")
        except ValueError:
            print("Invalid input. Numbers only, initiate.")

    slow_mode = input("\nEngage slow mode (8 seconds per round)? [y/N]: ").lower() == 'y'

    if unit1_data and unit2_data:
        battle(unit1_data, unit2_data, slow_mode)
    else:
        print("Alas, some combatants could not be summoned. The battle is postponed.")

if __name__ == "__main__":
    main()
