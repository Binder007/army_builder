import time
from derived_stats import calculate_derived_stats
from combat_state import CombatState
from combat_core import resolve_action, apply_regen
import unit_loader
from combat_loop import run_battle
import derived_stats

def select_unit(units):
    for i, name in enumerate(units):
        print(f"[{i + 1}] {name}")
    while True:
        try:
            index = int(input("> ")) - 1
            if 0 <= index < len(units):
                return units[index]
        except ValueError:
            pass
        print("Invalid selection.")

def main():
    units = unit_loader.list_unit_files()
    print("Select Unit 1:")
    unit1_name = select_unit(units)
    print("Select Unit 2:")
    unit2_name = select_unit(units)

    unit1 = unit_loader.load_unit(unit1_name)
    unit2 = unit_loader.load_unit(unit2_name)

    slow = input("Enable slow mode? (y/n): ").lower() == "y"
    run_battle(unit1, unit2, slow_mode=slow)

if __name__ == "__main__":
    main()