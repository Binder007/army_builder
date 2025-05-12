import json
import os
import random
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UNITS_DIR = os.path.join(SCRIPT_DIR, "units")
import mage_rules
import warrior_rules  # Import the new warrior skills module

def load_unit_data(filepath):
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
        print("\n+++ AVAILABLE COMBATANTS +++")
        for i, unit in enumerate(units):
            print(f"[{i + 1}] {unit}")
        print("++++++++++++++++++++++++++++")
        return units
    else:
        print("\nNo units available yet. The arena is empty.")
        return []

def get_unit_by_name(unit_name):
    filepath = os.path.join(UNITS_DIR, f"{unit_name}.json")
    return load_unit_data(filepath)

def calculate_derived_stats(unit_data, active_effects=None):
    """Calculates derived stats based on physical and mental attributes, considering active effects."""
    base_str = unit_data['stats'].get('str', 10)
    base_dex = unit_data['stats'].get('dex', 10)
    base_con = unit_data['stats'].get('con', 10)
    base_int = unit_data['stats'].get('int', 10)
    base_wis = unit_data['stats'].get('wis', 10)

    modified_str = base_str
    modified_dex = base_dex
    modified_con = base_con
    modified_int = base_int
    modified_wis = base_wis

    if active_effects:
        for effect in active_effects:
            if effect['stat'] == 'str':
                modified_str += effect['modifier']
            elif effect['stat'] == 'dex':
                modified_dex += effect['modifier']
            elif effect['stat'] == 'con':
                modified_con += effect['modifier']
            elif effect['stat'] == 'int':
                modified_int += effect['modifier']
            elif effect['stat'] == 'wis':
                modified_wis += effect['modifier']
            elif effect.get('source') and effect['source'] == unit_data['name']: # Apply self-buffs from skills
                if effect['stat'] == 'str':
                    modified_str += effect['modifier']
                elif effect['stat'] == 'dex':
                    modified_dex += effect['modifier']
                elif effect['stat'] == 'con':
                    modified_con += effect['modifier']
                elif effect['stat'] == 'ac':
                    ac_bonus = effect['modifier']
                # We'll handle temporary damage bonuses directly in the battle loop

    hitroll = modified_dex // 2
    damroll = modified_str // 3
    ac = 10 + modified_dex // 4 + active_effects.get('ac', 0) if isinstance(active_effects, dict) and 'ac' in active_effects else 10 + modified_dex // 4
    hp_total = modified_con * 5
    mana_total = (modified_int + modified_wis) * 5
    stamina_total = (modified_str + modified_dex + modified_con) * 3

    # Calculate regeneration rates (adjusted)
    hp_regen = modified_con // 8
    mana_regen = (modified_int + modified_wis) // 8
    stamina_regen = (modified_str + modified_con) // 8

    return {
        'hitroll': hitroll,
        'damroll': damroll,
        'ac': ac,
        'hp_total': hp_total,
        'mana_total': mana_total,
        'stamina_total': stamina_total,
        'can_cast_spell': True,
        'hp_regen': hp_regen,
        'mana_regen': mana_regen,
        'stamina_regen': stamina_regen
    }

# ... (rest of your main script)


def battle(unit1_data, unit2_data, slow_mode):
    unit1_derived = calculate_derived_stats(unit1_data)
    unit2_derived = calculate_derived_stats(unit2_data)
    unit1_active_effects = []
    unit2_active_effects = []
    unit1_derived['hp_current'] = unit1_derived['hp_total']
    unit1_derived['mana_current'] = unit1_derived['mana_total']
    unit1_derived['stamina_current'] = unit1_derived['stamina_total']
    unit2_derived['hp_current'] = unit2_derived['hp_total']
    unit2_derived['mana_current'] = unit2_derived['mana_total']
    unit2_derived['stamina_current'] = unit2_derived['stamina_total']
    unit1_spell_cooldown = 0
    unit2_spell_cooldown = 0
    unit1_skill_cooldowns = {}  # Initialize skill cooldowns for unit 1
    unit2_skill_cooldowns = {}  # Initialize skill cooldowns for unit 2
    unit1_temp_damage_bonus = 0
    unit2_temp_damage_bonus = 0

    print("\n+++ BATTLE COMMENCES! +++")
    print(f"{unit1_data['name']} (HP: {unit1_derived['hp_current']}/{unit1_derived['hp_total']}, AC: {unit1_derived['ac']}, Hit: +{unit1_derived['hitroll']}, Dam: +{unit1_derived['damroll']}, Mana: {unit1_derived['mana_current']}/{unit1_derived['mana_total']}, Stamina: {unit1_derived['stamina_current']}/{unit1_derived['stamina_total']})")
    print(f"VERSUS")
    print(f"{unit2_data['name']} (HP: {unit2_derived['hp_current']}/{unit2_derived['hp_total']}, AC: {unit2_derived['ac']}, Hit: +{unit2_derived['hitroll']}, Dam: +{unit2_derived['damroll']}, Mana: {unit2_derived['mana_current']}/{unit2_derived['mana_total']}, Stamina: {unit2_derived['stamina_current']}/{unit2_derived['stamina_total']})")
    print("--------------------------")

    round_number = 1
    while unit1_derived['hp_current'] > 0 and unit2_derived['hp_current'] > 0:
        print(f"\n++ ROUND {round_number} ++")

        # --- Unit 1's Turn ---
        # Apply and manage Unit 1's effects
        effects_to_remove_1 = []
        for i, effect in enumerate(unit1_active_effects):
            print(f"{unit1_data['name']} is under the effect of +{effect['modifier']} {effect['stat']} for {effect['duration']} more turns.")
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                effects_to_remove_1.append(i)
        for index in sorted(effects_to_remove_1, reverse=True):
            del unit1_active_effects[index]
        unit1_derived.update(calculate_derived_stats(unit1_data, unit1_active_effects))

        print(f"{unit1_data['name']} considers their actions...")
        action1 = "attack"  # Default action
        possible_actions_1 = ["attack"]
        can_unit1_cast = "can_cast" in unit1_data['tags'] and unit1_spell_cooldown <= 0
        if can_unit1_cast:
            possible_actions_1.append("cast")
        available_skills_1 = [tag[6:] for tag in unit1_data['tags'] if tag.startswith("skill_")]
        can_unit1_use_skill = any(
            warrior_rules.get_skill_cost(unit1_data, skill) <= unit1_derived['stamina_current'] and
            unit1_skill_cooldowns.get(skill, 0) <= 0
            for skill in available_skills_1
        )
        if can_unit1_use_skill and available_skills_1:
            possible_actions_1.append("skill")

        chosen_action_type_1 = random.choice(possible_actions_1)

        if chosen_action_type_1 == "attack":
            attack_roll_1 = random.randint(1, 20) + unit1_derived['hitroll']
            print(f"  ...swings their weapon...")
            damage_roll = random.randint(1, 4) + unit1_derived['damroll'] + unit1_temp_damage_bonus
            unit1_temp_damage_bonus = 0  # Reset temporary damage bonus
            if attack_roll_1 >= unit2_derived['ac']:
                unit2_derived['hp_current'] -= damage_roll
                print(f"    ...a solid hit! {unit2_data['name']} takes {damage_roll} damage. [HP: {unit2_derived['hp_current']}]")
            else:
                print(f"    ...misses their foe!")
        elif chosen_action_type_1 == "cast":
            available_spells = [tag[6:] for tag in unit1_data['tags'] if tag.startswith("spell_")]
            if available_spells:
                chosen_spell = mage_rules.choose_action(unit1_data, unit2_data, unit1_derived['mana_current'], True).split('_')[1]
                spell_cost = mage_rules.get_spell_cost(unit1_data, chosen_spell)
                spell_cooldown = mage_rules.get_spell_cooldown(chosen_spell)
                if spell_cost is not None and unit1_derived['mana_current'] >= spell_cost:
                    unit1_derived['mana_current'] -= spell_cost
                    spell_result = mage_rules.cast_spell(unit1_data, unit2_data, chosen_spell)
                    if isinstance(spell_result, dict) and "effect" in spell_result:
                        unit1_active_effects.append(spell_result)
                    elif isinstance(spell_result, int): # Damage or heal
                        unit2_derived['hp_current'] -= spell_result
                        print(f"  ...caused {spell_result} damage/healing. [HP: {unit2_derived['hp_current']}], [Mana: {unit1_derived['mana_current']}]")
                    else:
                        print(f"  ...had no immediate effect.")
                    unit1_spell_cooldown = spell_cooldown
        elif chosen_action_type_1 == "skill":
            usable_skill = warrior_rules.choose_skill(
                unit1_data, unit2_data, unit1_derived['stamina_current'], available_skills_1, unit1_skill_cooldowns
            )
            if usable_skill:
                skill_cost = warrior_rules.get_skill_cost(unit1_data, usable_skill)
                unit1_derived['stamina_current'] -= skill_cost
                skill_result = warrior_rules.use_skill(unit1_data, unit2_data, usable_skill)
                skill_cooldown = warrior_rules.get_skill_cooldown(usable_skill)
                unit1_skill_cooldowns[usable_skill] = skill_cooldown
                if isinstance(skill_result, dict) and "effect" in skill_result:
                    unit1_active_effects.append(skill_result['effect'])
                elif isinstance(skill_result, int): # Direct damage (not currently implemented in warrior_rules)
                    unit2_derived['hp_current'] -= skill_result
                    print(f"  ...dealt {skill_result} damage. [HP: {unit2_derived['hp_current']}], [Stamina: {unit1_derived['stamina_current']}]")
                elif skill_result is None and usable_skill == "power_strike":
                    print(f"  ...prepares a powerful strike!")

        # Decrement Unit 1's cooldowns
        if unit1_spell_cooldown > 0:
            unit1_spell_cooldown -= 1
        for skill in list(unit1_skill_cooldowns.keys()):
            if unit1_skill_cooldowns[skill] > 0:
                unit1_skill_cooldowns[skill] -= 1
            elif unit1_skill_cooldowns[skill] <= 0:
                del unit1_skill_cooldowns[skill]

        # Check if unit 2 has fallen
        if unit2_derived['hp_current'] <= 0:
            break

        # --- Unit 2's Turn ---
        # Apply and manage Unit 2's effects
        effects_to_remove_2 = []
        for i, effect in enumerate(unit2_active_effects):
            print(f"{unit2_data['name']} is under the effect of +{effect['modifier']} {effect['stat']} for {effect['duration']} more turns.")
            effect['duration'] -= 1
            if effect['duration'] <= 0:
                effects_to_remove_2.append(i)
        for index in sorted(effects_to_remove_2, reverse=True):
            del unit2_active_effects[index]
        unit2_derived.update(calculate_derived_stats(unit2_data, unit2_active_effects))

        print(f"\n{unit2_data['name']} prepares their response...")
        action2 = "attack"  # Default action
        possible_actions_2 = ["attack"]
        can_unit2_cast = "can_cast" in unit2_data['tags'] and unit2_spell_cooldown <= 0
        if can_unit2_cast:
            possible_actions_2.append("cast")
        available_skills_2 = [tag[6:] for tag in unit2_data['tags'] if tag.startswith("skill_")]
        can_unit2_use_skill = any(
            warrior_rules.get_skill_cost(unit2_data, skill) <= unit2_derived['stamina_current'] and
            unit2_skill_cooldowns.get(skill, 0) <= 0
            for skill in available_skills_2
        )
        if can_unit2_use_skill and available_skills_2:
            possible_actions_2.append("skill")

        chosen_action_type_2 = random.choice(possible_actions_2)
        
        if chosen_action_type_2 == "attack":
            attack_roll_2 = random.randint(1, 20) + unit2_derived['hitroll']
            print(f"  ...strikes back with their weapon...")
            damage_roll = random.randint(1, 4) + unit2_derived['damroll'] + unit2_temp_damage_bonus
            unit2_temp_damage_bonus = 0  # Reset temporary damage bonus
            if attack_roll_2 >= unit1_derived['ac']:
                unit1_derived['hp_current'] -= damage_roll
                print(f"    ...a telling blow! {unit1_data['name']} suffers {damage_roll} damage. [HP: {unit1_derived['hp_current']}]")
            else:
                print(f"    ...their attack fails to find purchase!")
        elif chosen_action_type_2 == "cast":
            available_spells = [tag[6:] for tag in unit2_data['tags'] if tag.startswith("spell_")]
          
            if available_spells:
                print(f"Spell cooldown (Unit1): {unit1_spell_cooldown}")
                chosen_spell = mage_rules.choose_action(unit2_data, unit1_data, unit2_derived['mana_current'], True).split('_')[1]
                spell_cost = mage_rules.get_spell_cost(unit2_data, chosen_spell)
                spell_cooldown = mage_rules.get_spell_cooldown(chosen_spell)
                if spell_cost is not None and unit2_derived['mana_current'] >= spell_cost:
                    unit2_derived['mana_current'] -= spell_cost
                    spell_result = mage_rules.cast_spell(unit2_data, unit1_data, chosen_spell)
                    if isinstance(spell_result, dict) and "effect" in spell_result:
                        unit2_active_effects.append(spell_result)
                    elif isinstance(spell_result, int): # Damage or heal
                        unit1_derived['hp_current'] -= spell_result
                        print(f"  ...caused {spell_result} damage/healing. [HP: {unit1_derived['hp_current']}], [Mana: {unit2_derived['mana_current']}]")
                    else:
                        print(f"  ...had no immediate effect.")
                    unit2_spell_cooldown = spell_cooldown
        elif chosen_action_type_2 == "skill":
            usable_skill = warrior_rules.choose_skill(
                unit2_data, unit1_data, unit2_derived['stamina_current'], available_skills_2, unit2_skill_cooldowns
            )
            if usable_skill:
                skill_cost = warrior_rules.get_skill_cost(unit2_data, usable_skill)
                unit2_derived['stamina_current'] -= skill_cost
                skill_result = warrior_rules.use_skill(unit2_data, unit1_data, usable_skill)
                skill_cooldown = warrior_rules.get_skill_cooldown(usable_skill)
                unit2_skill_cooldowns[usable_skill] = skill_cooldown
                if isinstance(skill_result, dict) and "effect" in skill_result:
                    unit2_active_effects.append(skill_result['effect'])
                elif isinstance(skill_result, int): # Direct damage (not currently implemented in warrior_rules)
                    unit1_derived['hp_current'] -= skill_result
                    print(f"  ...dealt {skill_result} damage. [HP: {unit1_derived['hp_current']}], [Stamina: {unit2_derived['stamina_current']}]")
                elif skill_result is None and usable_skill == "power_strike":
                    print(f"  ...prepares a powerful strike!")

        # Decrement Unit 2's cooldowns
        if unit2_spell_cooldown > 0:
            unit2_spell_cooldown -= 1
        for skill in list(unit2_skill_cooldowns.keys()):
            if unit2_skill_cooldowns[skill] > 0:
                unit2_skill_cooldowns[skill] -= 1
            elif unit2_skill_cooldowns[skill] <= 0:
                del unit2_skill_cooldowns[skill]

        # Check if unit 1 has fallen
        if unit1_derived['hp_current'] <= 0:
            break

        # Apply regeneration at the end of the round
        unit1_derived['hp_current'] = min(unit1_derived['hp_current'] + unit1_derived['hp_regen'], unit1_derived['hp_total'])
        unit1_derived['mana_current'] = min(unit1_derived['mana_current'] + unit1_derived['mana_regen'], unit1_derived['mana_total'])
        unit1_derived['stamina_current'] = min(unit1_derived['stamina_current'] + unit1_derived['stamina_regen'], unit1_derived['stamina_total'])
        unit2_derived['hp_current'] = min(unit2_derived['hp_current'] + unit2_derived['hp_regen'], unit2_derived['hp_total'])
        unit2_derived['mana_current'] = min(unit2_derived['mana_current'] + unit2_derived['mana_regen'], unit2_derived['mana_total'])
        unit2_derived['stamina_current'] = min(unit2_derived['stamina_current'] + unit2_derived['stamina_regen'],
        unit2_derived['stamina_total'])
        unit2_derived['stamina_current'] = min(unit2_derived['stamina_current'] + unit2_derived['stamina_regen'], unit2_derived['stamina_total'])

        # Display end-of-round stats
        print(f"\n++ END OF ROUND {round_number} ++")
        print(f"{unit1_data['name']} (HP: {unit1_derived['hp_current']}/{unit1_derived['hp_total']}, Mana: {unit1_derived['mana_current']}/{unit1_derived['mana_total']}, Stamina: {unit1_derived['stamina_current']}/{unit1_derived['stamina_total']})")
        print(f"{unit2_data['name']} (HP: {unit2_derived['hp_current']}/{unit2_derived['hp_total']}, Mana: {unit2_derived['mana_current']}/{unit2_derived['mana_total']}, Stamina: {unit2_derived['stamina_current']}/{unit2_derived['stamina_total']})")
        print("--------------------------")

        if slow_mode:
            time.sleep(8)

        round_number += 1

    print("\n+++ BATTLE ENDS! +++")
    if unit1_derived['hp_current'] <= 0:
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
