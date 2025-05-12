import time
from combat_state import CombatState
from combat_core import resolve_action, apply_regen, process_effects, tick_cooldowns
from derived_stats import calculate_derived_stats

def apply_regen(derived):
    derived['hp_current'] = min(derived['hp_total'], derived['hp_current'] + derived['hp_regen'])
    derived['mana_current'] = min(derived['mana_total'], derived['mana_current'] + derived['mana_regen'])
    derived['stamina_current'] = min(derived['stamina_total'], derived['stamina_current'] + derived['stamina_regen'])

def run_battle(unit1_data, unit2_data, slow_mode=False):
    state = CombatState(unit1_data, unit2_data)
    round_number = 1

    print(f"\n--- BATTLE BEGINS ---")
    print(f"{unit1_data['name']} vs {unit2_data['name']}\n")

    while True:
        print(f"== ROUND {round_number} ==")

        # Unit 1 acts
        print(f"\n{state.unit1['name']} acts...")
        resolve_action(
            state.unit1, state.unit2,
            state.unit1_stats, state.unit2_stats,
            state.unit1_effects, state.unit1_cooldowns
        )
        if state.is_battle_over():
            break
            
            # Unit 2 acts
        print(f"\n{state.unit2['name']} responds...")
        resolve_action(
            state.unit2, state.unit1,
            state.unit2_stats, state.unit1_stats,
            state.unit2_effects, state.unit2_cooldowns
        )
        if state.is_battle_over():
            break

        # Process ongoing effects
        process_effects(state.unit1_effects)
        process_effects(state.unit2_effects)

        # Recalculate stats with preserved resources
        state.unit1_stats = calculate_derived_stats(state.unit1, state.unit1_effects, state.unit1_stats)
        state.unit2_stats = calculate_derived_stats(state.unit2, state.unit2_effects, state.unit2_stats)

        # Apply regen
        apply_regen(state.unit1_stats)
        apply_regen(state.unit2_stats)

        # Tick cooldowns
        tick_cooldowns(state.unit1_cooldowns)
        tick_cooldowns(state.unit2_cooldowns)

        # Status update
        print("\n--- STATUS ---")
        print(f"{state.unit1['name']}: HP {state.unit1_stats['hp_current']} | Mana {state.unit1_stats['mana_current']} | Stam {state.unit1_stats['stamina_current']}")
        print(f"{state.unit2['name']}: HP {state.unit2_stats['hp_current']} | Mana {state.unit2_stats['mana_current']} | Stam {state.unit2_stats['stamina_current']}")
        print("---------------")

        round_number += 1
        if slow_mode:
            time.sleep(4)
            
            print("\n*** BATTLE ENDS ***")
    if state.unit1_stats['hp_current'] <= 0 and state.unit2_stats['hp_current'] <= 0:
        print("*** It's a draw! ***")
    else:
        winner = state.unit1 if state.unit2_stats['hp_current'] <= 0 else state.unit2
        print(f"*** {winner['name']} wins the battle! ***")