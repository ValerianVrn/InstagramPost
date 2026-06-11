"""
common.py — shared utilities for all Instagram bot accounts.
Provides: ai_json, generate_image, refresh_token, publish
"""

import json, os, requests
from json_repair import repair_json

IG_API       = "https://graph.facebook.com/v19.0"
HF_TOKEN     = os.environ.get("HF_API_TOKEN",     "")
GEMINI_KEY   = os.environ.get("GEMINI_API_KEY",   "")
TOGETHER_KEY = os.environ.get("TOGETHER_API_KEY", "")


# ── Text generation ───────────────────────────────────────────────────────────

def ai_json(prompt, fake, dry_run=False):
    """
    Generate a JSON response from an LLM.
    Tries HF Llama first, falls back to Gemini on rate limit.
    Returns a parsed dict.
    """
    if dry_run:
        print("  [DRY-RUN] Using fake response")
        return fake

    # ── HF Llama ──────────────────────────────────────────────────────────────
    if HF_TOKEN:
        try:
            from huggingface_hub import InferenceClient
            print("  🤖 Calling HF Llama...")
            hf  = InferenceClient(api_key=HF_TOKEN)
            raw = hf.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=700,
            ).choices[0].message.content
            print(f"  Raw: {raw[:200]}")
            return json.loads(repair_json(raw))
        except Exception as e:
            if not _is_rate_limit(e):
                raise
            print(f"  ⚠️  HF rate limited — falling back to Gemini...")

    # ── Gemini fallback ───────────────────────────────────────────────────────
    if not GEMINI_KEY:
        raise RuntimeError("No HF_API_TOKEN and no GEMINI_API_KEY set.")

    import google.generativeai as genai
    genai.configure(api_key=GEMINI_KEY)

    for model in ["gemini-2.0-flash", "gemini-1.5-flash"]:
        try:
            print(f"  🤖 Calling Gemini ({model})...")
            raw = genai.GenerativeModel(model).generate_content(prompt).text
            print(f"  Raw: {raw[:200]}")
            return json.loads(repair_json(raw))
        except Exception as e:
            if not _is_unavailable(e):
                raise
            print(f"  ⚠️  {model} unavailable — trying next model...")

    raise RuntimeError("All Gemini models unavailable.")


# ── Image generation ──────────────────────────────────────────────────────────

def generate_image(prompt, seed, dry_run=False):
    """
    Generate an image via HF FLUX (free) with Together AI as fallback.
    Returns a public URL.
    """
    if dry_run:
        print("  [DRY-RUN] Skipping image generation")
        return "https://placehold.co/1080x1080/png"

    # ── HF FLUX ───────────────────────────────────────────────────────────────
    if HF_TOKEN:
        try:
            import io
            from huggingface_hub import InferenceClient
            print(f"  🎨 Generating via HF FLUX (seed {seed})...")
            hf    = InferenceClient(provider="hf-inference", api_key=HF_TOKEN)
            image = hf.text_to_image(prompt, model="black-forest-labs/FLUX.1-schnell")
            buf   = io.BytesIO()
            image.save(buf, format="JPEG", quality=90)
            image_bytes = buf.getvalue()
            print(f"  ✓ Generated ({len(image_bytes)//1024}KB)")
            return _upload_tmpfiles(image_bytes)
        except Exception as e:
            if not _is_rate_limit(e):
                raise
            print(f"  ⚠️  HF rate limited — falling back to Together AI...")

    # ── Together AI fallback ──────────────────────────────────────────────────
    if not TOGETHER_KEY:
        raise RuntimeError("No HF_API_TOKEN and no TOGETHER_API_KEY set.")

    from together import Together
    print(f"  🎨 Generating via Together AI FLUX (seed {seed})...")
    result = Together(api_key=TOGETHER_KEY).images.generate(
        model="black-forest-labs/FLUX.1-schnell",
        prompt=prompt,
        width=1024, height=1024, steps=4, seed=seed, n=1,
    )
    url = result.data[0].url
    print(f"  ✓ {url[:80]}")
    return url


# ── Token refresh ─────────────────────────────────────────────────────────────

def refresh_token(token, dry_run=False):
    """Refresh a long-lived Instagram token. Call every run to keep it alive."""
    print("🔑 Refreshing token...")
    if dry_run:
        print("  [DRY-RUN] Skipping")
        return token

    r = requests.get(
        "https://graph.facebook.com/v19.0/oauth/access_token",
        params={"grant_type": "ig_refresh_token", "access_token": token}
    )
    if not r.ok:
        print(f"  ⚠️  Refresh failed ({r.status_code}): {r.text[:120]}")
        return token

    new_token  = r.json().get("access_token", token)
    expires_in = int(r.json().get("expires_in", 0))
    print(f"  ✓ Refreshed (expires in {expires_in // 86400}d)")
    return new_token


# ── Publish ───────────────────────────────────────────────────────────────────

def publish(image_url, caption, token, ig_id, dry_run=False):
    """Create Instagram media container and publish it. Returns post ID."""
    if dry_run:
        print(f"\n{'─'*55}")
        print(f"  IMAGE  : {image_url}")
        print(f"  CAPTION:\n{caption}")
        print('─'*55)
        return "dry-run-id"

    r = requests.post(f"{IG_API}/{ig_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Container error {r.status_code}: {r.text}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Container: {data['error']['message']}")

    r = requests.post(f"{IG_API}/{ig_id}/media_publish",
        data={"creation_id": data["id"], "access_token": token})
    if not r.ok:
        raise RuntimeError(f"Publish error {r.status_code}: {r.text}")
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Publish: {data['error']['message']}")

    return data["id"]


# ── Internal helpers ──────────────────────────────────────────────────────────

def _is_rate_limit(e):
    return any(code in str(e) for code in ["429", "402"])

def _is_unavailable(e):
    return any(code in str(e) for code in ["503", "unavailable"])

def _upload_tmpfiles(image_bytes):
    """Upload raw image bytes to tmpfiles.org and return a direct public URL."""
    print("  ☁️  Uploading to tmpfiles.org...")
    r = requests.post(
        "https://tmpfiles.org/api/v1/upload",
        files={"file": ("image.jpg", image_bytes, "image/jpeg")},
        timeout=30,
    )
    r.raise_for_status()
    raw_url = r.json()["data"]["url"]
    public_url = raw_url.replace("tmpfiles.org/", "tmpfiles.org/dl/")
    print(f"  ✓ {public_url}")
    return public_url