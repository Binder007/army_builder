from derived_stats import calculate_derived_stats

class CombatState:
    def __init__(self, unit1, unit2):
        self.unit1 = unit1
        self.unit2 = unit2
        self.unit1_stats = calculate_derived_stats(unit1)
        self.unit2_stats = calculate_derived_stats(unit2)
        self.unit1_effects = []
        self.unit2_effects = []
        self.unit1_cooldowns = {'spell_cooldown': 0, 'skill_cooldown': 0}
        self.unit2_cooldowns = {'spell_cooldown': 0, 'skill_cooldown': 0}

    def is_battle_over(self):
        return self.unit1_stats['hp_current'] <= 0 or self.unit2_stats['hp_current'] <= 0