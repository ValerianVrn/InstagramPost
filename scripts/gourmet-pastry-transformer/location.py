"""
gourmet-pastry-transformer/location.py — traveller movement logic.
Handles country stays, city-per-day rotation, and neighbour selection.
Depends on common.ai_json and state.load_state / save_state.
"""

import random
from datetime import date
from common import ai_json

STATE_FILE = "traveller_state.json"

FAKE_START = {
    "country": "Portugal", "city": "Lisbon", "flag": "🇵🇹",
    "neighbours": ["Spain", "Morocco (by ferry)"],
}
FAKE_MOVE = {
    "country": "Spain", "city": "Seville", "flag": "🇪🇸",
    "neighbours": ["Portugal", "France", "Morocco", "Andorra"],
    "travel_note": "Crossed the border humming fado, immediately switched to flamenco.",
}
FAKE_CITY = {
    "city": "Porto",
    "travel_note": "Hopped on the train north, pastel de nata in hand.",
}


def get_location(d, dry_run=False):
    """
    Return the traveller's current state for date d.
    Handles three cases:
      1. No state yet       → pick a starting country + city
      2. Stay expired       → move to a neighbouring country
      3. Same country, new day → move to a new city within the country
    """
    from state import load_state
    state = load_state(STATE_FILE, dry_run=dry_run)

    # ── 1. First run ever ─────────────────────────────────────────────────────
    if state is None:
        print("  🌍 No state — picking starting country...")
        data = ai_json(
            "Pick a random interesting country and city to start a pastry world tour.\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "city": "name", "flag": "emoji", "neighbours": ["c1", "c2", "c3"]}',
            fake=FAKE_START, dry_run=dry_run,
        )
        return _new_country_state(data, d)

    days_here = (d - date.fromisoformat(state["arrived_on"])).days

    # ── 2. Time to move to a new country ─────────────────────────────────────
    if days_here >= state["stay_days"]:
        print(f"  ✈️  {days_here} days in {state['country']} — moving on!")
        visited           = state.get("visited", [])
        current_country   = state["country"]
        current_neighbours = state["neighbours"]

        data = ai_json(
            f"A pastry traveller just finished visiting {current_country}.\n"
            f"Known neighbours: {current_neighbours}.\n"
            f"Recently visited (avoid): {visited[-6:]}.\n"
            "Pick the next country and a first city to visit.\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "city": "name", "flag": "emoji", "neighbours": ["c1", "c2"], '
            f'"travel_note": "fun one-liner about crossing from {current_country} to this country"}}',
            fake=FAKE_MOVE, dry_run=dry_run,
        )
        new_state = _new_country_state(data, d)
        new_state["visited"]     = (visited + [data["country"]])[-20:]
        new_state["came_from"]   = current_country
        new_state["travel_note"] = data.get("travel_note", "")
        return new_state

    # ── 3. Same country — move to a new city ──────────────────────────────────
    visited_cities  = state.get("visited_cities", [state["city"]])
    current_city    = state["city"]
    current_country = state["country"]

    print(f"  🚆 Day {days_here + 1}/{state['stay_days']} in {current_country} — picking new city...")
    data = ai_json(
        f"A pastry traveller is exploring {current_country}.\n"
        f"Already visited: {visited_cities}.\n"
        f"Pick a DIFFERENT city famous for a local pastry (not in the list above).\n"
        "Respond ONLY in raw JSON, no markdown:\n"
        '{"city": "name", "travel_note": "fun one-liner about the journey from '
        f'{current_city} to the new city"}}',
        fake=FAKE_CITY, dry_run=dry_run,
    )
    new_city = data.get("city", current_city)
    print(f"  🚆 {current_city} → {new_city}")

    state = dict(state)
    state["city"]            = new_city
    state["visited_cities"]  = (visited_cities + [new_city])[-20:]
    state["travel_note"]     = data.get("travel_note", "")
    state["posted_pastries"] = []   # new city = fresh pastry slate
    return state


# ── Internal ──────────────────────────────────────────────────────────────────

def _new_country_state(data, d):
    """Build a fresh state dict when arriving in a new country."""
    return {
        "country":          data["country"],
        "city":             data.get("city", data["country"]),
        "flag":             data["flag"],
        "neighbours":       data["neighbours"],
        "arrived_on":       str(d),
        "stay_days":        random.randint(2, 4),
        "visited":          [data["country"]],
        "visited_cities":   [data.get("city", data["country"])],
        "posted_pastries":  [],
        "travel_note":      "",
        "came_from":        "",
    }
