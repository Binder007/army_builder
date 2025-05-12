# debug.py

# Toggle these flags to enable or disable debug printouts in various systems

DEBUG_ACTIONS = True         # Logs action selection (spells, skills, fallback attacks)
DEBUG_EFFECTS = True         # Logs when effects are applied, ticked, or expire
DEBUG_STATS = True           # Logs recalculated derived stats each turn
DEBUG_COOLDOWNS = False      # Logs spell/skill cooldown states
DEBUG_COMBAT_FLOW = False    # Logs turn-by-turn flow markers