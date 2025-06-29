import streamlit as st
import itertools

# Settings
IGNORE_MULTIPLIERS = False
IGNORE_FIRE_RATE = False

# Item format: (name, ap%, cdr%, cost, required, character)
ITEMS = [
    ("Compensator", 5, 0, 1000, 0, "all"),
    ("Weapon Grease", 0, 5, 1000, 0, "all"),
    ("Aftermarket Firing Pin", 0, 10, 3750, 0, "all"),
    ("Advanced Nanobiotics", 5, 10, 4000, 0, "all"),
    ("Shieldbuster", 5, 0, 4000, 0, "all"),
    ("Stockpile", 5, 0, 4000, 0, "all"),
    ("Technoleech", 5, 0, 4500, 0, "all"),
    ("Icy Coolant", 10, 0, 5500, 0, "all"),
    ("Talon Modification Module", 15, 0, 6000, 0, "all"),
    ("Code Breaker", 15, 0, 9000, 0, "all"),
    ("Salvaged Slugs", 0, 10, 9000, 0, "all"),
    ("Volskaya Ordnance", 0, 10, 9500, 0, "all"),
    ("Commander's Clip", 0, 10, 10000, 0, "all"),
    ("Weapon Jammer", 10, 10, 10000, 0, "all"),
    ("Amari's Antidote", 15, 0, 11000, 0, "all"),
    ("Booster Jets", 0, 20, 11000, 0, "all"),
    ("Hardlight Accelerator", 10, 0, 11000, 0, "all"),
    ("El-sa'ka Suppressor", 10, 0, 11000, 0, "all"),
    ("The Closer", 20, 0, 14500, 0, "all"),
    ("Eye of the Spider", 25, 0, 14500, 0, "all"),
    ("Custom Stock", 5, 0, 3750, 0, "all"),
    ("Aerial Distresser", 0, 10, 10000, 0, "all"),
    ("Emergecy Chip", 5, 0, 4500, 0, "all"),

    # Juno
    ("Gravitational Push", 7.5, 10, 10000, 0, "juno"),
    ("Pulse Spike", 0, 10, 11000, 0, "juno"),
    ("Vantage Shot", 5, 0, 4000, 0, "juno"),
    ("Long Range Blaster", 15, 0, 12000, 0, "juno"),

    # Kiriko
    ("Asa's Armament", 0, 10, 4000, 0, "kiriko"),
    ("Farsight Focus Sash", 10, 0, 5000, 0, "kiriko"),
    ("Teamwork Toolkit", 10, 0, 5000, 0, "kiriko"),
    ("Spirit's Guidance", 15, 0, 12000, 0, "kiriko"),

    # Mei
    ("Focused Flurries", 0, 15, 10000, 0, "mei"),
    ("Snowboot", 0, 15, 10000, 0, "mei"),
    ("Himalayan Hat", 0, 15, 10000, 0, "mei"),

    # Mercy
    ("Midair mobilizer", 5, 10, 4000, 0, "mercy"),
    ("Caduceus Ex", 10, 0, 10000, 0, "mercy"),
    ("Celestial Clip", 10, 0, 10000, 0, "mercy"),
    ("Chain Evoker", 0, 0, 10000, 0, "mercy"),
]

# UI
st.title("DPS Optimizer")

base_damage = st.number_input("Base Damage", min_value=1.0, value=1.0, step=0.1)
base_fire_rate = st.number_input("Base Fire Rate (shots/sec)", min_value=0.1, value=1.0, step=0.1)

characters = sorted(set(i[5] for i in ITEMS if i[5] != "all"))
characters.insert(0, "Generic")
character = st.selectbox("Select Character", characters)

ignore_fire_rate = st.checkbox("Ignore Fire Rate Bonus", value=IGNORE_FIRE_RATE)
ignore_multiplier = st.checkbox("Ignore Bonus Multiplier", value=IGNORE_MULTIPLIERS)
max_items = st.slider("Max Number of Items", 1, 6, 6)
max_cost = st.number_input("Max Total Cost", min_value=0, max_value=200000, value=200000, step=1000)

item_names = [item[0] for item in ITEMS]
blacklisted_items = st.multiselect("Blacklist Items (Exclude these):", options=item_names)
required_items = st.multiselect("Required Items (Must be included):", options=[i for i in item_names if i not in blacklisted_items])


def filter_items(character, blacklist):
    if character == "Generic":
        return [item for item in ITEMS if item[5] == "all" and item[0] not in blacklist]
    return [item for item in ITEMS if (item[5] == "all" or item[5] == character) and item[0] not in blacklist]


def calculate_dps(combo):
    total_damage_bonus = sum(item[1] for item in combo) / 100
    total_fire_rate_bonus = sum(item[2] for item in combo) / 100 if not ignore_fire_rate else 0
    total_cost = sum(item[3] for item in combo)
    total_multiplier_bonus = 0 if ignore_multiplier else sum(item[4] if len(item) > 4 else 0 for item in combo)

    final_damage = base_damage * (1 + total_damage_bonus)
    final_fire_rate = base_fire_rate * (1 + total_fire_rate_bonus)
    raw_dps = final_damage * final_fire_rate
    total_dps = raw_dps * (1 + total_multiplier_bonus)

    return total_dps, total_damage_bonus, total_fire_rate_bonus, final_damage, final_fire_rate, total_cost, total_multiplier_bonus


def find_best_combo(items, max_items, max_cost, required_names):
    required_items = [item for item in items if item[0] in required_names]
    optional_items = [item for item in items if item[0] not in required_names]

    min_required = len(required_items)
    max_optional = max_items - min_required

    best = (None, 0, ())

    for r in range(0, max_optional + 1):
        for combo in itertools.combinations(optional_items, r):
            full_combo = list(combo) + required_items
            if len(full_combo) > max_items:
                continue
            dps, dmg_bonus, fire_bonus, dmg, fire_rate, cost, mult = calculate_dps(full_combo)
            if cost > max_cost:
                continue
            if dps > best[1]:
                best = (full_combo, dps, (dmg_bonus, fire_bonus, dmg, fire_rate, cost, mult))

    return best


def get_color(cost):
    if cost <= 2000:
        return "green"
    elif cost <= 8000:
        return "aqua"
    else:
        return "purple"


filtered = filter_items(character, blacklisted_items)
best_combo, dps, stats = find_best_combo(filtered, max_items, max_cost, required_items)

if best_combo:
    st.subheader("Best DPS Combo:")
    for item in best_combo:
        color = get_color(item[3])
        st.markdown(
            f"<span style='color:{color}; font-weight:bold'>- {item[0]}</span> "
            f"(Damage: {item[1]}%, Fire Rate: {item[2]}%, Cost: {item[3]})",
            unsafe_allow_html=True
        )

    dmg_bonus, fire_bonus, dmg, fire_rate, cost, mult = stats
    st.markdown("---")
    st.write(f"**Total Cost:** {cost} / {max_cost}")
    st.write(f"**Total Damage Bonus:** {dmg_bonus * 100:.2f}%")
    st.write(f"**Total Fire Rate Bonus:** {fire_bonus * 100:.2f}%" if not ignore_fire_rate else "**Fire Rate Bonus Ignored**")
    if not ignore_multiplier:
        st.write(f"**Bonus Multiplier:** {mult * 100:.2f}%")
    st.write(f"**Final Damage per Shot:** {dmg:.2f}")
    st.write(f"**Final Fire Rate:** {fire_rate:.2f} shots/sec")
    st.success(f"Max DPS: {dps:.2f}")
else:
    st.error("No valid item combinations within cost threshold.")
