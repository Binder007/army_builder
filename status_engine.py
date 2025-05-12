def apply_effects(derived_stats, active_effects, unit_name=None):
    """Applies all active effects to derived stats (modifies in-place)."""
    # Reset all derived bonuses to base before reapplying effects
    bonuses = {
        "str": 0,
        "dex": 0,
        "con": 0,
        "int": 0,
        "wis": 0,
        "ac": 0
    }

    for effect in active_effects:
        if unit_name and effect.get("source") and effect["source"] != unit_name:
            continue  # Only apply self-buffs to the appropriate unit

        stat = effect.get("stat")
        mod = effect.get("modifier", 0)
        if stat in bonuses:
            bonuses[stat] += mod

    # Apply bonuses to derived stats
    for stat, bonus in bonuses.items():
        if stat == "ac":
            derived_stats["ac"] += bonus
        elif stat == "str":
            derived_stats["hitroll"] += bonus // 2
            derived_stats["damroll"] += bonus // 3
            derived_stats["stamina_total"] += bonus * 3
        elif stat == "dex":
            derived_stats["hitroll"] += bonus // 2
            derived_stats["ac"] += bonus // 4
            derived_stats["stamina_total"] += bonus * 3
        elif stat == "con":
            derived_stats["hp_total"] += bonus * 5
            derived_stats["stamina_total"] += bonus * 3
        elif stat == "int":
            derived_stats["mana_total"] += bonus * 5
        elif stat == "wis":
            derived_stats["mana_total"] += bonus * 5

def tick_and_clean_effects(active_effects):
    """Decrements durations and removes expired effects."""
    expired = []
    for effect in active_effects:
        effect['duration'] -= 1
        if effect['duration'] <= 0:
            expired.append(effect)
    for e in expired:
        active_effects.remove(e)
    return expired