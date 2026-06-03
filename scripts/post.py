"""
scripts/post.py
🧳 Pastry Traveller
  - OpenAI API (gpt-4o-mini)  → text / JSON generation
  - Pollinations (free)        → image generation
  - Instagram Graph API        → publishing

Usage:
  python scripts/post.py                        # normal daily run
  python scripts/post.py 2024-01-15             # date override
  python scripts/post.py --dry-run              # no API calls, fake responses
  python scripts/post.py 2024-01-15 --dry-run   # both
  python scripts/post.py --reset                # wipe state and start over
"""

import os, sys, json, random, requests
from datetime import date
from google import genai

# ── Args ──────────────────────────────────────────────────────────────────────
args     = sys.argv[1:]
DRY_RUN  = "--dry-run" in args
RESET    = "--reset"   in args
date_arg = next((a for a in args if not a.startswith("--")), None)

# ── Config ────────────────────────────────────────────────────────────────────
IG_API     = "https://graph.facebook.com/v19.0"
TOKEN      = os.environ.get("IG_ACCESS_TOKEN", "fake-token")
IG_ID      = os.environ.get("IG_ACCOUNT_ID",   "fake-id")
IG_SECRET  = os.environ.get("IG_ACCOUNT_SECRET",   "fake-secret")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY",  "fake-key")
STATE_FILE = "traveller_state.json"

if not DRY_RUN:
    genai.Client(api_key=GEMINI_KEY)
    client = genai.Client()
else:
    client = None

# ── Season ────────────────────────────────────────────────────────────────────
def get_season(d):
    return "warm" if 4 <= d.month <= 9 else "cold"

# ── State ─────────────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            data = json.load(f)
            return data if data else None
    return None

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    print(f"  State saved → {STATE_FILE}")

# ── Fake responses (dry-run) ──────────────────────────────────────────────────
FAKE_START = {
    "country": "Portugal", "flag": "🇵🇹",
    "neighbours": ["Spain", "Morocco (by ferry)"]
}
FAKE_MOVE = {
    "country": "Spain", "flag": "🇪🇸",
    "neighbours": ["Portugal", "France", "Morocco", "Andorra"],
    "travel_note": "Crossed the border humming a fado song, immediately switched to flamenco."
}
FAKE_POST = {
    "pastry_name": "Pastel de Nata",
    "image_prompt": "photorealistic pastel de nata on ceramic plate, Belém Tower blurred background, warm golden light",
    "characteristics": ["crispy shell", "wobbly vanilla custard", "Lisbon has a 300-year-old rivalry over who makes the best one"],
    "caption": "Day 1 in Portugal and I've already eaten four of these. No regrets. 🇵🇹\nThe Pastel de Nata is basically a custard tart that went to finishing school — flaky, creamy, dusted with cinnamon.\nHave you ever had one fresh from the oven?\n\n#pasteldanata #portugal #pastrytraveller #foodtravel"
}

# ── OpenAI call ───────────────────────────────────────────────────────────────
def ai_json(prompt, fake):
    if DRY_RUN:
        print("  [DRY-RUN] Using fake response")
        return fake

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    raw = response.text

    return json.loads(raw.replace("```json", "").replace("```", "").strip())

# ── Location logic ────────────────────────────────────────────────────────────
def get_location(d):
    state = load_state()

    if state is None:
        print("  🌍 No state — picking starting country...")
        data = ai_json(
            "Pick a random interesting country to start a pastry world tour.\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "flag": "emoji", "neighbours": ["country1", "country2", "country3"]}',
            FAKE_START
        )
        return {
            "country":    data["country"],
            "flag":       data["flag"],
            "neighbours": data["neighbours"],
            "arrived_on": str(d),
            "stay_days":  random.randint(2, 4),
            "visited":    [data["country"]],
        }, True

    days_here = (d - date.fromisoformat(state["arrived_on"])).days

    if days_here >= state["stay_days"]:
        print(f"  ✈️  {days_here} days in {state['country']} — moving on!")
        visited = state.get("visited", [])
        data = ai_json(
            f"A pastry traveller just finished visiting {state['country']}.\n"
            f"Known neighbours: {state['neighbours']}.\n"
            f"Recently visited (avoid): {visited[-6:]}.\n"
            "Pick the next country (geographically close, not recently visited).\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "flag": "emoji", "neighbours": ["list", "of", "neighbours"], '
            f'"travel_note": "fun one-liner about crossing from {state['country']} to this country"',
            FAKE_MOVE
        )
        return {
            "country":     data["country"],
            "flag":        data["flag"],
            "neighbours":  data["neighbours"],
            "arrived_on":  str(d),
            "stay_days":   random.randint(2, 4),
            "visited":     (visited + [data["country"]])[-20:],
            "came_from":   state["country"],
            "travel_note": data.get("travel_note", ""),
        }, True

    print(f"  📍 Day {days_here + 1}/{state['stay_days']} in {state['country']}")
    return state, False

# ── Post generation ───────────────────────────────────────────────────────────
def generate_post(state, d, season, is_arrival):
    days_here   = (d - date.fromisoformat(state["arrived_on"])).days + 1
    stay_days   = state["stay_days"]
    came_from   = state.get("came_from", "")
    travel_note = state.get("travel_note", "")

    if is_arrival and came_from:
        narrative = f"Just arrived from {came_from}. Travel note: {travel_note}. Reference the arrival."
    elif days_here == stay_days:
        narrative = f"Last day in {state['country']} before moving on. Hint at leaving."
    else:
        narrative = f"Day {days_here} of {stay_days} in {state['country']}. Settled explorer."

    lighting = "bright sunny warm" if season == "warm" else "soft cozy indoor"

    return ai_json(
        f"You run a fun pastry travel Instagram called 'Pastry Traveller'.\n"
        f"Location: {state['flag']} {state['country']} (day {days_here}/{stay_days})\n"
        f"Context: {narrative} | Season: {season}\n\n"
        f"Pick ONE iconic local pastry and create the post.\n"
        f"Respond ONLY in raw JSON, no markdown:\n"
        "{\n"
        '  "pastry_name": "name",\n'
        f'  "image_prompt": "photorealistic food photo: pastry as hero, iconic landmark of {state["country"]} blurred behind, {lighting} lighting, no snow if warm season, no text, appetizing",\n'
        '  "characteristics": ["texture/look", "key flavour", "one quirky fact"],\n'
        '  "caption": "3-4 short punchy sentences, first person traveller tone, light humour, context-aware, ends with question, hashtags on new line"\n'
        "}",
        FAKE_POST
    )

# ── Image URL ─────────────────────────────────────────────────────────────────
def image_url(plan, state, d):
    seed   = abs(hash(f"{d}-{state['country']}-{plan['pastry_name']}")) % 99999
    prompt = requests.utils.quote(plan["image_prompt"])
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1080&nologo=true&seed={seed}&model=flux"

# ── Token refresh ─────────────────────────────────────────────────────────────
def refresh_token(token):
    """
    Refreshes a long-lived Instagram token. Valid for 60 days, reset on each refresh.
    Call this every run — it's idempotent and keeps the token alive indefinitely.
    Saves the (possibly new) token back into traveller_state.json.
    """
    if DRY_RUN:
        print("  [DRY-RUN] Skipping token refresh")
        return token

    r = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={"grant_type": "fb_exchange_token", "client_id": {IG_ID}, "client_secret": {IG_SECRET}, "fb_exchange_token": token}
    )
    if not r.ok:
        # Non-fatal — log and continue with existing token
        print(f"  ⚠️  Token refresh failed ({r.status_code}): {r.text[:120]}")
        return token

    new_token = r.json().get("access_token", token)
    expires_in = r.json().get("expires_in", "?")
    print(f"  🔑 Token refreshed (expires in {expires_in}s)")
    return new_token

# ── Publish ───────────────────────────────────────────────────────────────────
def publish(url, caption):
    if DRY_RUN:
        print(f"\n{'─'*55}")
        print("  IMAGE URL:")
        print(f"  {url}")
        print(f"\n  CAPTION:\n{caption}")
        print('─'*55)
        return "dry-run-id"

    r = requests.post(f"{IG_API}/{IG_ID}/media",
        data={"image_url": url, "caption": caption, "access_token": TOKEN})
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"]["message"])

    r = requests.post(f"{IG_API}/{IG_ID}/media_publish",
        data={"creation_id": data["id"], "access_token": TOKEN})
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"]["message"])
    return data["id"]

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if RESET:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("🗑️  State reset.")
        else:
            print("Nothing to reset.")
        sys.exit(0)

    d      = date.fromisoformat(date_arg) if date_arg else date.today()
    season = get_season(d)
    mode   = "DRY-RUN" if DRY_RUN else "LIVE"

    print(f"\n🧳 Pastry Traveller [{mode}]")
    print(f"📅 {d}  |  season: {season}\n")

    print("🔑 Refreshing token...")
    TOKEN = refresh_token(TOKEN)

    state, is_arrival = get_location(d)

    print(f"\n🥐 Generating post for {state['flag']} {state['country']}...")
    plan = generate_post(state, d, season, is_arrival)
    print(f"   Pastry : {plan['pastry_name']}")
    print(f"   Facts  : {plan['characteristics']}")

    url     = image_url(plan, state, d)
    post_id = publish(url, plan["caption"])

    if not DRY_RUN:
        print(f"\n✅ Posted! ID: {post_id}")

    save_state(state)
    print("\n✓ Done.\n")