"""
scripts/post.py
🧳 Gourmet Pastry Transformer
  - HF Llama (free)            → text / JSON (Gemini as fallback)
  - FLUX.1-schnell (free)   → images (withTogether AI)
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

# ── Args ──────────────────────────────────────────────────────────────────────
args     = sys.argv[1:]
DRY_RUN  = "--dry-run" in args
RESET    = "--reset"   in args
date_arg = next((a for a in args if not a.startswith("--")), None)

# ── Config ────────────────────────────────────────────────────────────────────
IG_API        = "https://graph.facebook.com/v19.0"
TOKEN         = os.environ.get("IG_ACCESS_TOKEN",  "fake-token")
IG_ID         = os.environ.get("IG_ACCOUNT_ID",    "fake-id")
HF_TOKEN      = os.environ.get("HF_API_TOKEN",     "")
GEMINI_KEY    = os.environ.get("GEMINI_API_KEY",   "")
TOGETHER_KEY  = os.environ.get("TOGETHER_API_KEY", "")
GIST_ID    = os.environ.get("GIST_ID", "")       # your gist ID
GH_TOKEN   = os.environ.get("GH_TOKEN", "")      # personal access token (gist scope only)
GIST_FILE  = "traveller_state.json"

# ── State ─────────────────────────────────────────────────────────────────────
def load_state():
    if DRY_RUN or not GIST_ID:
        # fall back to local file
        if os.path.exists("traveller_state.json"):
            with open("traveller_state.json") as f:
                data = json.load(f)
                return data if data else None
        return None

    r = requests.get(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"Bearer {GH_TOKEN}"}
    )
    r.raise_for_status()
    content = r.json()["files"][GIST_FILE]["content"]
    data = json.loads(content)
    return data if data else None

def save_state(state):
    if DRY_RUN or not GIST_ID:
        with open("traveller_state.json", "w") as f:
            json.dump(state, f, indent=2)
        print("  State saved → local file")
        return

    r = requests.patch(
        f"https://api.github.com/gists/{GIST_ID}",
        headers={"Authorization": f"Bearer {GH_TOKEN}"},
        json={"files": {GIST_FILE: {"content": json.dumps(state, indent=2)}}}
    )
    r.raise_for_status()
    print(f"  State saved → Gist {GIST_ID}")

# ── Fake responses (dry-run) ──────────────────────────────────────────────────
FAKE_START = {
    "country": "Portugal", "city": "Lisbon", "flag": "🇵🇹",
    "neighbours": ["Spain", "Morocco (by ferry)"]
}
FAKE_MOVE = {
    "country": "Spain", "city": "Seville", "flag": "🇪🇸",
    "neighbours": ["Portugal", "France", "Morocco", "Andorra"],
    "travel_note": "Crossed the border humming a fado song, immediately switched to flamenco."
}
FAKE_POST = {
    "pastry_name": "Pastel de Nata",
    "image_prompt": "photorealistic pastel de nata on ceramic plate, Belem Tower blurred background, warm golden light",
    "characteristics": ["crispy shell", "wobbly vanilla custard", "Lisbon has a 300-year-old rivalry over who makes the best one"],
    "caption": "Day 1 in Lisbon and I've already eaten four of these. No regrets. The Pastel de Nata is basically a custard tart that went to finishing school. Have you tried one fresh from the oven?\n\n#pasteldanata #portugal #pastrytraveller #foodtravel"
}

# ── Text generation (HF → Gemini fallback) ────────────────────────────────────
def ai_json(prompt, fake):
    if DRY_RUN:
        print("  [DRY-RUN] Using fake response")
        return fake

    from json_repair import repair_json

    # ── Try HF first ──────────────────────────────────────────────────────────
    if HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            print("  🤖 Calling HF Llama...")
            hf = InferenceClient(api_key=HF_TOKEN)
            response = hf.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
            )
            raw = response.choices[0].message.content
            print(f"  AI response (raw): {raw}")
            return json.loads(repair_json(raw))
        except Exception as e:
            is_rate_limit = any(code in str(e) for code in ["429", "402"])
            if not is_rate_limit:
                raise
            print(f"  ⚠️  HF rate limited — falling back to Gemini...")

    # ── Gemini fallback ───────────────────────────────────────────────────────
    if not GEMINI_KEY:
        raise RuntimeError("No HF_API_TOKEN and no GEMINI_API_KEY set.")

    from google import genai
    print("  🤖 Calling Gemini...")
    genai.Client(api_key=GEMINI_KEY)
    client = genai.Client()
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt
            )
    except Exception as e:
        # This model is currently experiencing high demand.
        is_unavailable = any(code in str(e) for code in ["503"])
        if not is_unavailable:
            raise
        print(f"  ⚠️  gemini-3.5-flash is currently experiencing high demand. — falling back to gemini-2.5-flash...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
            )
    raw = response.text
    print(f"  Gemini response (raw): {raw}")
    return json.loads(repair_json(raw))

# ── Location logic ────────────────────────────────────────────────────────────
def get_location(d):
    state = load_state()

    if state is None:
        print("  🌍 No state — picking starting country...")
        data = ai_json(
            "Pick a random interesting country and city to start a pastry world tour.\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "city": "name", "flag": "emoji", "neighbours": ["country1", "country2", "country3"]}',
            FAKE_START
        )
        return {
            "country":    data["country"],
            "city":       data.get("city", data["country"]),
            "flag":       data["flag"],
            "neighbours": data["neighbours"],
            "arrived_on": str(d),
            "stay_days":  random.randint(2, 4),
            "visited":    [data["country"]],
            "visited_cities":   [data.get("city", data["country"])],
            "posted_pastries":  [],
        }

    days_here = (d - date.fromisoformat(state["arrived_on"])).days

    if days_here >= state["stay_days"]:
        print(f"  ✈️  {days_here} days in {state['country']} — moving on!")
        visited             = state.get("visited", [])
        current_country     = state["country"]
        current_neighbours  = state["neighbours"]
        data = ai_json(
            f"A pastry traveller just finished visiting {current_country}.\n"
            f"Known neighbours: {current_neighbours}.\n"
            f"Recently visited (avoid): {visited[-6:]}.\n"
            "Pick the next country and a specific city (geographically close, not recently visited).\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "city": "name", "flag": "emoji", "neighbours": ["country1", "country2"], '
            f'"travel_note": "fun one-liner about crossing from {current_country} to this country"}}',
            FAKE_MOVE
        )
        return {
            "country":     data["country"],
            "city":        data.get("city", data["country"]),
            "flag":        data["flag"],
            "neighbours":  data["neighbours"],
            "arrived_on":  str(d),
            "stay_days":   random.randint(2, 4),
            "visited":     (visited + [data["country"]])[-20:],
            "visited_cities":   [data.get("city", data["country"])],
            "came_from":   state["country"],
            "travel_note": data.get("travel_note", ""),
            "posted_pastries":  [],   # reset for the new country
        }

    # ── Same country, new day — pick a different city ─────────────────────────
    visited_cities = state.get("visited_cities", [state["city"]])
    current_city   = state["city"]
    current_country = state["country"]
 
    print(f"  🚆 Day {days_here + 1}/{state['stay_days']} in {current_country} — picking new city...")
    data = ai_json(
        f"A pastry traveller is exploring {current_country}.\n"
        f"Already visited these cities: {visited_cities}.\n"
        f"Pick a DIFFERENT city to visit today (not in the list above) where a local pastry is famous.\n"
        "Respond ONLY in raw JSON, no markdown:\n"
        '{"city": "name", "travel_note": "fun one-liner about the trip from '
        f'{current_city} to the new city"}}',
        fake={"city": "Porto", "travel_note": "Hopped on the train south, croissant in hand."},
    )
    new_city = data.get("city", current_city)
    print(f"  🚆 Moving from {current_city} to {new_city}")
 
    state = dict(state)  # copy to avoid mutating the loaded state
    state["city"]           = new_city
    state["visited_cities"] = (visited_cities + [new_city])[-20:]
    state["travel_note"]    = data.get("travel_note", "")
    state["posted_pastries"] = []  # new city, new pastries
    return state

# ── Post generation ───────────────────────────────────────────────────────────
def generate_post(state, d):
    days_here  = (d - date.fromisoformat(state["arrived_on"])).days + 1
    stay_days  = state["stay_days"]
    flag       = state["flag"]
    country    = state["country"]
    city       = state["city"]
    posted_pastries = state.get("posted_pastries", [])

    avoid = f"Already posted in {country} (avoid these): {posted_pastries}.\n" if posted_pastries else ""
    
    return ai_json(
        f"You run a fun pastry travel Instagram.\n"
        f"Location: {flag} {city}, {country} — day {days_here} of {stay_days}.\n"
        f"{avoid}\n"
        f"Date: {d}\n\n"
        f"Pick ONE iconic local pastry from {city} (or {country} if none specific to the city).\n"
        "Respond ONLY in raw JSON, no markdown:\n"
        "{\n"
        '  "pastry_name": "name",\n'
        f'  "image_prompt": "photorealistic photo of the pastry (characteristics), iconic landmark of {city} blurred behind, no text, appetizing",\n'
        '  "characteristics": ["one quirky or historical fact"],\n'
        f'  "caption": "first mention {city} and day {days_here}/{stay_days} with the flag icon of the country, then fun/historical fact on the pastry or city with humour, hashtags on new line"\n'
        "}",
        FAKE_POST
    )

# ── Image generation (Together AI) ──────────────────────────────
def generate_image(plan, state, d):
    if DRY_RUN:
        print("  [DRY-RUN] Skipping image generation")
        return "https://placehold.co/1080x1080/png"

    seed = abs(hash(f"{d}-{state['country']}-{plan['pastry_name']}")) % 99999

    # ── Together AI ──────────────────────────────────────────────────
    if not TOGETHER_KEY:
        raise RuntimeError("No HF_API_TOKEN and no TOGETHER_API_KEY set.")

    from together import Together
    print(f"  🎨 Generating image via Together AI FLUX.1-schnell (seed {seed})...")
    result = Together(api_key=TOGETHER_KEY).images.generate(
        model="black-forest-labs/FLUX.1-schnell",
        prompt=plan["image_prompt"],
        width=1024,
        height=1024,
        steps=4,
        seed=seed,
        n=1,
    )
    image_url = result.data[0].url
    print(f"  ✓ Image URL: {image_url}")
    return image_url

# ── Token refresh ─────────────────────────────────────────────────────────────
def refresh_token(token):
    print("🔑 Refreshing token...")
    if DRY_RUN:
        print("  [DRY-RUN] Skipping token refresh")
        return token

    # ig_refresh_token is the correct grant type for renewing a long-lived token
    r = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token}
    )
    if not r.ok:
        print(f"  ⚠️  Token refresh failed ({r.status_code}): {r.text[:120]}")
        return token

    new_token  = r.json().get("access_token", token)
    expires_in = r.json().get("expires_in", "?")
    print(f"  ✓ Token refreshed (expires in {expires_in}s ≈ {int(expires_in)//86400}d)")
    return new_token

# ── Publish ───────────────────────────────────────────────────────────────────
def publish(url, caption, token):
    if DRY_RUN:
        print(f"\n{'─'*55}")
        print(f"  IMAGE : {url}")
        print(f"\n  CAPTION:\n{caption}")
        print('─'*55)
        return "dry-run-id"

    # Create media container
    r = requests.post(f"{IG_API}/{IG_ID}/media",
        data={"image_url": url, "caption": caption, "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Container error {r.status_code}: {r.text}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Container error: {data['error']['message']}")

    # Publish
    r = requests.post(f"{IG_API}/{IG_ID}/media_publish",
        data={"creation_id": data["id"], "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Publish error {r.status_code}: {r.text}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Publish error: {data['error']['message']}")
    return data["id"]

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if RESET:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
            print("🗑️  State reset.")
        else:
            print("  Nothing to reset.")
        sys.exit(0)

    d    = date.fromisoformat(date_arg) if date_arg else date.today()
    mode = "DRY-RUN" if DRY_RUN else "LIVE"

    print(f"\n🧳 Gourmet Pastry Traveller [{mode}] — {d}\n")

    TOKEN = refresh_token(TOKEN)

    print("\n🗺️  Resolving location...")
    state = get_location(d)

    print(f"\n🥐 Generating post for {state['flag']} {state['city']}, {state['country']}...")
    plan = generate_post(state, d)
    print(f"   Pastry : {plan['pastry_name']}")
    print(f"   Facts  : {plan['characteristics']}")

    print("\n🖼️  Generating image...")
    url = generate_image(plan, state, d)

    print("\n📤 Publishing...")
    post_id = publish(url, plan["caption"], TOKEN)

    if not DRY_RUN:
        print(f"\n✅ Posted! ID: {post_id}")
 
    # Track posted pastries so we never repeat within the same country
    posted = state.get("posted_pastries", [])
    posted.append(plan["pastry_name"])
    state["posted_pastries"] = posted

    save_state(state)
    print("\n✓ Done.\n")