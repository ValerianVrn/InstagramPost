"""
scripts/post.py
🧳 Gourmet Pastry Transformer
  - HF Llama 3.3 70B (free)   → text / JSON generation
  - Gemini API (gemini-3.5-flash)  → (fallback if HF usage limit reached) text / JSON generation
  - HF FLUX.1-schnell (free)  → image generation
  - Pollinations API (free)   → (fallback if HF usage limit reached) image generation
  - tmpfiles.org (free)       → temporary public image hosting
  - Instagram Graph API       → publishing

Usage:
  python scripts/post.py                        # normal daily run
  python scripts/post.py 2024-01-15             # date override
  python scripts/post.py --dry-run              # no API calls, fake responses
  python scripts/post.py 2024-01-15 --dry-run   # both
  python scripts/post.py --reset                # wipe state and start over
"""

import os, sys, json, random, requests
from datetime import date
from huggingface_hub import InferenceClient

# ── Args ──────────────────────────────────────────────────────────────────────
args     = sys.argv[1:]
DRY_RUN  = "--dry-run" in args
RESET    = "--reset"   in args
date_arg = next((a for a in args if not a.startswith("--")), None)

# ── Config ────────────────────────────────────────────────────────────────────
IG_API      = "https://graph.facebook.com/v19.0"
TOKEN       = os.environ.get("IG_ACCESS_TOKEN", "fake-token")
IG_ID       = os.environ.get("IG_ACCOUNT_ID",   "fake-id")
IG_SECRET   = os.environ.get("IG_ACCOUNT_SECRET",   "fake-secret")
HF_TOKEN    = os.environ.get("HF_API_TOKEN", "fake-hf-token")
HF_MODEL    = "black-forest-labs/FLUX.1-schnell"  # free, fast, high quality
HF_API      = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
STATE_FILE  = "traveller_state.json"

hf = None if DRY_RUN else InferenceClient(api_key=HF_TOKEN)

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

# ── AI call ───────────────────────────────────────────────────────────────
def ai_json(prompt, fake):
    if DRY_RUN:
        print("  [DRY-RUN] Using fake response")
        return fake
 
    from json_repair import repair_json
 
    # ── Try HF first ──────────────────────────────────────────────────────────
    try:
        response = hf.chat.completions.create(
            model="Qwen/Qwen3-0.6B:featherless-ai",
            # model="meta-llama/Llama-3.3-70B-Instruct:together",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=700,
        )
        raw = response.choices[0].message.content
        print(f"  AI response (raw): {raw}")
        return json.loads(repair_json(raw))
 
    except Exception as e:
        if "429" not in str(e) and "402" not in str(e) and "rate" not in str(e).lower():
            raise  # not a rate limit error — re-raise immediately
        print(f"  ⚠️  HF rate limited ({e}) — falling back to Gemini...")
 
    # ── Gemini fallback ───────────────────────────────────────────────────────
    from google import genai
    GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "fake-key")
    if not GEMINI_KEY or GEMINI_KEY == "fake-key":
        raise RuntimeError("HF rate limited and no GEMINI_API_KEY set as fallback.")
    genai.Client(api_key=GEMINI_KEY)
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-3.5-flash",
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
            "city":       data["city"],
            "flag":       data["flag"],
            "neighbours": data["neighbours"],
            "arrived_on": str(d),
            "stay_days":  random.randint(2, 4),
            "visited":    [data["country"]],
        }

    days_here = (d - date.fromisoformat(state["arrived_on"])).days

    if days_here >= state["stay_days"]:
        print(f"  ✈️  {days_here} days in {state['country']} — moving on!")
        visited = state.get("visited", [])
        current_country    = state["country"]
        current_neighbours = state["neighbours"]
        data = ai_json(
            f"A pastry traveller just finished visiting {current_country}.\n"
            f"Known neighbours: {current_neighbours}.\n"
            f"Recently visited (avoid): {visited[-6:]}.\n"
            "Pick the next country and city (geographically close, not recently visited).\n"
            "Respond ONLY in raw JSON, no markdown:\n"
            '{"country": "name", "city": "name", "flag": "emoji", "neighbours": ["list", "of", "neighbours"], '
            f'"travel_note": "fun one-liner about crossing from {current_country} to this country"}}',
            FAKE_MOVE
        )
        return {
            "country":     data["country"],
            "city":        data["city"],
            "flag":        data["flag"],
            "neighbours":  data["neighbours"],
            "arrived_on":  str(d),
            "stay_days":   random.randint(2, 4),
            "visited":     (visited + [data["country"]])[-20:],
            "came_from":   state["country"],
            "travel_note": data.get("travel_note", ""),
        }

    print(f"  📍 Day {days_here + 1}/{state['stay_days']} in {state['country']}")
    return state

# ── Post generation ───────────────────────────────────────────────────────────
def generate_post(state, d):
    print(f"\n🥐 Generating post for {state['flag']} {state['country']}...")
    days_here   = (d - date.fromisoformat(state["arrived_on"])).days + 1
    stay_days   = state["stay_days"]
    flag        = state["flag"]
    country     = state["country"]
    city        = state["city"]

    return ai_json(
        f"You run a pastry travel Instagram.\n"
        f"Location: {flag} {city}, {country} (day {days_here}/{stay_days})\n"
        f"Date: {d}\n\n"
        f"Pick ONE iconic local pastry of {city} if any otherwise another pastry of {country} and create the post.\n"
        f"Respond ONLY in raw JSON, no markdown:\n"
        "{\n"
        '  "pastry_name": "name",\n'
        f'  "image_prompt": "photorealistic photo of the pastry (characteristics), iconic landmark of {city} blurred behind, no text, appetizing",\n'
        '  "characteristics": ["texture/look", "key flavour", "one quirky fact"],\n'
        f'  "caption": "Day {days_here}/{stay_days} in {country} {flag} icon. Short characteristics, Fun/historical fact on the pastry or city with humour, hashtags on new line"\n'
        "}",
        FAKE_POST
    )

# ── Image generation: Hugging Face → file.io ──────────────────────────────────
def generate_image(plan, state, d):
    import time, io
    from huggingface_hub import InferenceClient

    if DRY_RUN:
        print("  [DRY-RUN] Skipping image generation")
        return "https://placehold.co/1080x1080/png"

    seed = abs(hash(f"{d}-{state['country']}-{plan['pastry_name']}")) % 99999

    # ── Try HF first ──────────────────────────────────────────────────────────
    try:
        # ── Step A: Generate via Hugging Face (free) ──────────────────────────────
        print(f"  🎨 Generating image with FLUX (seed {seed})...")
        hf_client = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
        image = hf_client.text_to_image(
            plan["image_prompt"],
            model="black-forest-labs/FLUX.1-schnell",
        )
        # Convert PIL image → JPEG bytes
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=90)
        image_bytes = buffer.getvalue()
        print(f"  ✓ Image generated ({len(image_bytes)//1024}KB)")

        # ── Step B: Upload to tmpfiles.org → permanent public URL ────────────────
        # file.io has become unreliable; tmpfiles.org is simpler and more stable.
        print("  ☁️  Uploading image to tmpfiles.org...")
        upload = requests.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": ("pastry.jpg", image_bytes, "image/jpeg")},
            timeout=30
        )
        print(f"  Upload status: {upload.status_code}")
        print(f"  Upload response: {upload.text}")
        upload.raise_for_status()
        result = upload.json()
        # tmpfiles.org returns {"status": "success", "data": {"url": "https://tmpfiles.org/..."}}
        # The direct file URL replaces /dl/ with nothing — we need the raw file link
        raw_url = result["data"]["url"]
        # Convert https://tmpfiles.org/1234/pastry.jpg
        #      to https://tmpfiles.org/dl/1234/pastry.jpg  (direct download link)
        public_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
        print(f"  ✓ Public URL: {public_url}")
        return public_url

    except Exception as e:
        if "429" not in str(e) and "402" not in str(e) and "rate" not in str(e).lower():
            raise  # not a rate limit error — re-raise immediately
        print(f"  ⚠️  HF rate limited ({e}) — falling back to Pollinations...")
 
    # ── Pollinations fallback ───────────────────────────────────────────────────────
    prompt = requests.utils.quote(plan["image_prompt"])
    return f"https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1080&nologo=true&seed={seed}&model=flux"
    
# ── Token refresh ─────────────────────────────────────────────────────────────
def refresh_token(token):
    """
    Refreshes a long-lived Instagram token. Valid for 60 days, reset on each refresh.
    Call this every run — it's idempotent and keeps the token alive indefinitely.
    Saves the (possibly new) token back into traveller_state.json.
    """
    print("🔑 Refreshing token...")
    if DRY_RUN:
        print("  [DRY-RUN] Skipping token refresh")
        return token

    r = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={"grant_type": "fb_exchange_token", "client_id": {IG_ID}, "client_secret": {IG_SECRET}, "fb_exchange_token": token}
    )
    if not r.ok:
        # Non-fatal — log and continue with existing token
        print(f"  ⚠️  Token refresh failed ({r.status_code}): {r.text}")
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
    mode   = "DRY-RUN" if DRY_RUN else "LIVE"

    print(f"\n🧳 Gourmet Pastry Transformer [{mode}]")

    TOKEN = refresh_token(TOKEN)
    state = get_location(d)
    plan = generate_post(state, d)
    url     = generate_image(plan, state, d)
    post_id = publish(url, plan['caption'])

    if not DRY_RUN:
        print(f"\n✅ Posted! ID: {post_id}")

    save_state(state)
    print("\n✓ Done.\n")