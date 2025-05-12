import random
import mage_rules
import warrior_rules
from derived_stats import calculate_derived_stats

# === Fallback attack ===
def fallback_attack(attacker, defender, attacker_derived, defender_derived):
    print(f"  {attacker['name']} swings their weapon...")
    attack_roll = random.randint(1, 20) + attacker_derived['hitroll']
    if attack_roll >= defender_derived['ac']:
        damage = random.randint(1, 4) + attacker_derived['damroll']
        defender_derived['hp_current'] -= damage
        print(f"    ...solid hit! {defender['name']} takes {damage} physical damage. [HP: {defender_derived['hp_current']}]")
    else:
        print(f"    ...misses!")

# === Resistance-aware damage application ===
def apply_damage_resistance(target, amount, channel="generic"):
    resists = target.get("resistances", {})
    reduction = resists.get(channel, 0)
    reduced = max(0, int(amount * (1 - reduction / 100)))
    return reduced

# === Action resolver ===
def choose_resolved_action(unit, derived, cooldowns):
    spell_cd = cooldowns.get('spell_cooldown', 0)
    skill_cd = cooldowns.get('skill_cooldown', 0)

    if "can_cast" in unit['tags'] and spell_cd <= 0:
        spells = [tag[6:] for tag in unit['tags'] if tag.startswith("spell_")]
        for spell in spells:
            if mage_rules.get_spell_cost(unit, spell) <= derived['mana_current']:
                return ("cast", spell)

    if skill_cd <= 0:
        skills = [tag[6:] for tag in unit['tags'] if tag.startswith("skill_")]
        for skill in skills:
            if warrior_rules.get_skill_cost(unit, skill) <= derived['stamina_current']:
                return ("skill", skill)

    return ("attack", None)

# === Main action execution ===
def resolve_action(unit, opponent, derived, opp_derived, active_effects, cooldowns):
    # Update attacker stats with current effects
    current_derived = calculate_derived_stats(unit, active_effects, derived)

    # Update opponent stats in-place to preserve reference
    opponent_derived_new = calculate_derived_stats(opponent, [], opp_derived)
    opp_derived.update(opponent_derived_new)

    action_type, value = choose_resolved_action(unit, current_derived, cooldowns)

    if action_type == "cast":
        cost = mage_rules.get_spell_cost(unit, value)
        cooldown = mage_rules.get_spell_cooldown(value)
        if cost is not None and current_derived['mana_current'] >= cost:
            current_derived['mana_current'] -= cost
            result = mage_rules.cast_spell(unit, opponent, value)
            if isinstance(result, dict):
                if result.get("type") == "damage":
                    adjusted = apply_damage_resistance(opponent, result['amount'], result.get("channel", "generic"))
                    opp_derived['hp_current'] -= adjusted
                    print(f"  {unit['name']} casts {value} for {adjusted} damage! [HP: {opp_derived['hp_current']}]")
                elif "effect" in result:
                    active_effects.append(result["effect"])
            cooldowns['spell_cooldown'] = cooldown
            return

    elif action_type == "skill":
        cost = warrior_rules.get_skill_cost(unit, value)
        cooldown = warrior_rules.get_skill_cooldown(value)
        if cost is not None and current_derived['stamina_current'] >= cost:
            current_derived['stamina_current'] -= cost
            result = warrior_rules.use_skill(unit, opponent, value)
            if isinstance(result, dict) and "effect" in result:
                active_effects.append(result["effect"])
            elif isinstance(result, int):
                opp_derived['hp_current'] -= result
                print(f"  {unit['name']} uses {value} for {result} damage! [HP: {opp_derived['hp_current']}]")
            cooldowns['skill_cooldown'] = cooldown
            return

    fallback_attack(unit, opponent, current_derived, opp_derived)

# === End-of-round regen ===
def apply_regen(derived):
    derived['hp_current'] = min(derived['hp_total'], derived['hp_current'] + derived['hp_regen'])
    derived['mana_current'] = min(derived['mana_total'], derived['mana_current'] + derived['mana_regen'])
    derived['stamina_current'] = min(derived['stamina_total'], derived['stamina_current'] + derived['stamina_regen'])

# === Effect tick ===
def process_effects(effects):
    expired = []
    for effect in effects:
        effect['duration'] -= 1
        if effect['duration'] <= 0:
            expired.append(effect)
    for e in expired:
        effects.remove(e)

# === Cooldown tick ===
def tick_cooldowns(cooldowns):
    if cooldowns.get('spell_cooldown', 0) > 0:
        cooldowns['spell_cooldown'] -= 1
    if cooldowns.get('skill_cooldown', 0) > 0:
        cooldowns['skill_cooldown'] -= 1