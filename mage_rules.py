import json
import os
import random

SPELLS_FILE = os.path.join(os.path.dirname(__file__), "spells.json")
with open(SPELLS_FILE, "r") as f:
    SPELL_DATA = json.load(f)

def get_spell_cost(caster_data, spell_name):
    if "can_cast" in caster_data['tags'] and spell_name in SPELL_DATA:
        return SPELL_DATA[spell_name]["cost"]
    return None

def get_spell_cooldown(spell_name):
    return SPELL_DATA.get(spell_name, {}).get("cooldown", 0)

def cast_spell(caster_data, target_data, spell_name):
    spell = SPELL_DATA.get(spell_name)
    if not spell:
        print(f"Unknown spell: {spell_name}")
        return None

    magnitude = spell.get("magnitude", [0, 0])
    amount = random.randint(*magnitude)

    if spell["effect"] == "damage":
        channel = spell.get("channel", "generic")
        print(f"{caster_data['name']} casts {spell_name} ({channel}) on {target_data['name']} for {amount} damage!")
        return {
            "amount": amount,
            "channel": channel,
            "type": "damage"
        }

    elif spell["effect"] == "heal":
        print(f"{caster_data['name']} casts {spell_name} and heals {target_data['name']} for {amount}!")
        return {
            "amount": -amount,
            "channel": "healing",
            "type": "heal"
        }

    else:
        print(f"{spell_name} has no recognized effect.")
        return None