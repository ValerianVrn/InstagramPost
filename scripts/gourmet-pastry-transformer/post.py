"""
gourmet-pastry-transformer/post.py — entry point for the Gourmet Pastry Traveller account.

Usage:
  python gourmet-pastry-transformer/post.py              # today
  python gourmet-pastry-transformer/post.py 2024-03-15  # date override
  python gourmet-pastry-transformer/post.py --dry-run
  python gourmet-pastry-transformer/post.py --reset
"""

import os, sys
from datetime import date

# Allow imports from the parent directory (common.py, state.py)
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from common   import ai_json, generate_image, refresh_token, publish
from state    import load_state, save_state
from location import get_location, STATE_FILE

# ── Args ──────────────────────────────────────────────────────────────────────
args     = sys.argv[1:]
DRY_RUN  = "--dry-run" in args
RESET    = "--reset"   in args
date_arg = next((a for a in args if not a.startswith("--")), None)

TOKEN = os.environ.get("IG_ACCESS_TOKEN", "fake-token")
IG_ID = os.environ.get("IG_ACCOUNT_ID",  "fake-id")

FAKE_POST = {
    "pastry_name": "Pastel de Nata",
    "image_prompt": "photorealistic pastel de nata on ceramic plate, Belem Tower blurred background, warm golden light",
    "characteristics": ["Lisbon has a 300-year-old rivalry over who makes the best one"],
    "caption": "Day 1/3 in Lisbon 🇵🇹 — already on my fourth Pastel de Nata. The custard is wobbly, the shell is crispy, and my diet is officially over. Have you tried one fresh from the oven?\n\n#pasteldanata #portugal #pastrytraveller #foodtravel",
}


# ── Post generation ───────────────────────────────────────────────────────────

def generate_post(state, d):
    days_here       = (d - date.fromisoformat(state["arrived_on"])).days + 1
    stay_days       = state["stay_days"]
    city            = state["city"]
    country         = state["country"]
    flag            = state["flag"]
    posted_pastries = state.get("posted_pastries", [])

    avoid = (
        f"Already posted in {country} (avoid these): {posted_pastries}.\n"
        if posted_pastries else ""
    )

    return ai_json(
        f"You run a fun pastry travel Instagram called 'Gourmet Pastry Traveller'.\n"
        f"Location: {flag} {city}, {country} — day {days_here} of {stay_days}. Date: {d}\n"
        f"{avoid}\n"
        f"Pick ONE iconic local pastry from {city} (or {country} if none specific to the city).\n"
        "Respond ONLY in raw JSON, no markdown:\n"
        "{\n"
        '  "pastry_name": "name",\n'
        f'  "image_prompt": "photorealistic food photo: pastry as hero, iconic landmark of {city} blurred behind, appetizing, no text",\n'
        '  "characteristics": ["one quirky or historical fact"],\n'
        f'  "caption": "mention {flag} {city} and day {days_here}/{stay_days}, fun/historical fact with humour, end with a question, hashtags on new line"\n'
        "}",
        fake=FAKE_POST, dry_run=DRY_RUN,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if RESET:
        save_state({}, STATE_FILE, dry_run=DRY_RUN)
        print("🗑️  State reset.")
        sys.exit(0)

    d    = date.fromisoformat(date_arg) if date_arg else date.today()
    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    print(f"\n🧳 Gourmet Pastry Traveller [{mode}] — {d}\n")

    token = refresh_token(TOKEN, dry_run=DRY_RUN)

    print("\n🗺️  Resolving location...")
    state = get_location(d, dry_run=DRY_RUN)

    print(f"\n🥐 Generating post for {state['flag']} {state['city']}, {state['country']}...")
    plan = generate_post(state, d)
    print(f"   Pastry : {plan['pastry_name']}")
    print(f"   Facts  : {plan['characteristics']}")

    print("\n🖼️  Generating image...")
    seed      = abs(hash(f"{d}-{state['country']}-{plan['pastry_name']}")) % 99999
    image_url = generate_image(plan["image_prompt"], seed, dry_run=DRY_RUN)

    print("\n📤 Publishing...")
    post_id = publish(image_url, plan["caption"], token, IG_ID, dry_run=DRY_RUN)

    if not DRY_RUN:
        print(f"\n✅ Posted! ID: {post_id}")

    # Track posted pastry to avoid repeats in the same country
    posted = state.get("posted_pastries", [])
    posted.append(plan["pastry_name"])
    state["posted_pastries"] = posted

    save_state(state, STATE_FILE, dry_run=DRY_RUN)
    print("\n✓ Done.\n")
