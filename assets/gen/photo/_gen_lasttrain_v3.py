#!/usr/bin/env python3
"""last_train 무드 컷 재생성 — '우울'→'여행 설렘' (대표 6/10 지시).

기존(_gen_batch.py) last_train: 'lone back-facing commuter', 'melancholic
end-of-day mood', 'cinematic blue tones' = 우울·공허. 막차 '경고' 맥락은
타임라인 SVG가 담당하므로 사진은 즐거움 담당으로 역할 분리.

법무 가드 유지: 식별 가능한 얼굴 금지(뒷모습만), 로고·브랜드·앨범아트·텍스트 금지.
2안 생성 → 우위안 채택.
"""

import base64
import os
import sys

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-byvias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"

LEGAL_SUFFIX = (
    " No identifiable human faces. People shown only as back-facing crowd "
    "silhouettes. No logos, no brand marks, no album art, no text in the image. "
    "Photorealistic, cinematic mood photography."
)

PROMPTS = {
    "last_train_v3a": (
        "Warm and lively Seoul subway platform in the evening, a bright modern "
        "Korean metro train with clean brushed-aluminum body and a colored "
        "line-stripe (generic stylized design, not a real branded train, no "
        "logos) stopped at the platform, a small group of cheerful young "
        "travelers seen from behind carrying rolling suitcases and tote bags, "
        "one holding a glowing pink light stick, warm golden platform lighting, "
        "soft bokeh, sense of excitement and shared adventure heading home from "
        "a great concert, warm amber and soft pink color grading, uplifting "
        "travel mood." + LEGAL_SUFFIX
    ),
    "last_train_v3b": (
        "Cheerful evening departure on a Seoul metro platform, back-facing "
        "silhouettes of friends with travel backpacks and a rolling suitcase "
        "walking toward a bright modern stylized Korean subway train (no brand, "
        "no logos), warm tungsten platform lights glowing, gentle lens flare, "
        "festive after-concert energy, a couple of pink light sticks glowing in "
        "hands, warm and inviting palette of amber, peach and soft magenta, "
        "joyful travel-anticipation atmosphere, cinematic." + LEGAL_SUFFIX
    ),
}


def load_key():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENAI_API_KEY not found in .env")


def generate(api_key, slug, prompt):
    resp = requests.post(
        "https://api.openai.com/v1/images/generations",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "prompt": prompt,
            "size": LANDSCAPE,
            "quality": "high",
            "n": 1,
        },
        timeout=180,
    )
    if resp.status_code != 200:
        print(f"  {slug}: ERROR {resp.status_code}: {resp.text[:300]}")
        return False
    b64 = resp.json()["data"][0]["b64_json"]
    out = f"{OUT_RAW}/{slug}.png"
    with open(out, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  {slug}: saved {out} ({os.path.getsize(out) // 1024}KB)")
    return True


def main():
    os.makedirs(OUT_RAW, exist_ok=True)
    key = load_key()
    only = sys.argv[1:] or list(PROMPTS)
    for slug in only:
        generate(key, slug, PROMPTS[slug])


if __name__ == "__main__":
    main()
