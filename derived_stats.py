def calculate_derived_stats(unit_data, active_effects=None, previous=None):
    stats = unit_data.get("stats", {})
    base_str = stats.get('str', 10)
    base_dex = stats.get('dex', 10)
    base_con = stats.get('con', 10)
    base_int = stats.get('int', 10)
    base_wis = stats.get('wis', 10)

    # Apply active effects if any
    if active_effects:
        for effect in active_effects:
            if effect.get('stat') == 'str':
                base_str += effect.get('modifier', 0)
            elif effect.get('stat') == 'dex':
                base_dex += effect.get('modifier', 0)
            elif effect.get('stat') == 'con':
                base_con += effect.get('modifier', 0)
            elif effect.get('stat') == 'int':
                base_int += effect.get('modifier', 0)
            elif effect.get('stat') == 'wis':
                base_wis += effect.get('modifier', 0)

    # Derived calculations
    hitroll = base_dex // 2
    damroll = base_str // 3
    ac = 10 + base_dex // 4
    hp_total = base_con * 5
    mana_total = (base_int + base_wis) * 5
    stamina_total = (base_str + base_dex + base_con) * 3

    # Regen
    hp_regen = base_con // 8
    mana_regen = (base_int + base_wis) // 8
    stamina_regen = (base_str + base_con) // 8

    # Resistances
    resistances = unit_data.get("resistances", {})

    derived = {
        'hitroll': hitroll,
        'damroll': damroll,
        'ac': ac,
        'hp_total': hp_total,
        'mana_total': mana_total,
        'stamina_total': stamina_total,
        'hp_regen': hp_regen,
        'mana_regen': mana_regen,
        'stamina_regen': stamina_regen,
        'resistances': resistances,
    }

    # Preserve current values if previous stats exist
    if previous:
        derived['hp_current'] = previous.get('hp_current', hp_total)
        derived['mana_current'] = previous.get('mana_current', mana_total)
        derived['stamina_current'] = previous.get('stamina_current', stamina_total)
    else:
        derived['hp_current'] = hp_total
        derived['mana_current'] = mana_total
        derived['stamina_current'] = stamina_total

    return derived