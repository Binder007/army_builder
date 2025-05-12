import json
import os
import random

SKILLS_FILE = os.path.join(os.path.dirname(__file__), "skills.json")
with open(SKILLS_FILE, "r") as f:
    SKILL_DATA = json.load(f)

def get_skill_cost(unit_data, skill_name):
    return SKILL_DATA.get(skill_name, {}).get("cost", None)

def get_skill_cooldown(skill_name):
    return SKILL_DATA.get(skill_name, {}).get("cooldown", 0)

def use_skill(user, target, skill_name):
    skill = SKILL_DATA.get(skill_name)
    if not skill:
        print(f"Unknown skill: {skill_name}")
        return None

    effect_type = skill.get("effect")

    if effect_type == "damage":
        amount = random.randint(*skill["magnitude"])
        print(f"{user['name']} uses {skill_name} on {target['name']} for {amount} damage!")
        return amount

    elif effect_type in ["buff", "debuff"]:
        effect = {
            "stat": skill.get("stat"),
            "modifier": skill.get("modifier"),
            "duration": skill.get("duration"),
            "source": user['name']
        }

        if effect_type == "buff":
            print(f"{user['name']} uses {skill_name} and gains +{skill['modifier']} {skill['stat']} for {skill['duration']} turns.")
        else:
            print(f"{user['name']} uses {skill_name} on {target['name']} reducing their {skill['stat']} by {abs(skill['modifier'])} for {skill['duration']} turns.")

        return {"effect": effect}

    else:
        print(f"{skill_name} has no recognized effect type.")
        return None

def choose_skill(user, target, stamina, available, cooldowns):
    usable = [
        s for s in available
        if get_skill_cost(user, s) is not None
        and get_skill_cost(user, s) <= stamina
        and cooldowns.get(s, 0) <= 0
    ]
    if usable:
        return random.choice(usable)
    return None