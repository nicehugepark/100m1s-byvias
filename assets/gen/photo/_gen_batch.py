#!/usr/bin/env python3
"""ByVias TWICE 서울 페이지 — 사진풍 무드 컷 배치 생성.

법무 가드: 실존 인물·아이돌 얼굴 금지(뒷모습 군중 실루엣만), TWICE/JYP
로고·앨범아트·공식 키비주얼 모사 금지, 텍스트 삽입 최소.
예산: 본 배치 총 30장 한도. 컷당 2안 생성 → 우위안 채택.
"""

import base64
import os
import sys
import time

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-bybias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
HARD_LIMIT = 30  # 본 배치 총 생성 한도 (시안 포함)
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"


def load_key():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("OPENAI_API_KEY"):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENAI_API_KEY not found in .env")


# 컷 정의: (slug, [안A 프롬프트, 안B 프롬프트])
LEGAL_SUFFIX = (
    " No identifiable human faces. People shown only as back-facing crowd "
    "silhouettes. No logos, no brand marks, no album art, no text in the image. "
    "Photorealistic, cinematic mood photography."
)

CUTS = [
    (
        "hero",
        [
            "Wide cinematic night view of Seoul skyline with a large domed concert "
            "arena exterior, a massive crowd of concert-goers seen from behind "
            "holding glowing pink and magenta light sticks, sea of pink lights, "
            "dramatic atmospheric haze, magenta and pink color grading, dusk to "
            "night." + LEGAL_SUFFIX,
            "Epic establishing shot of a domed stadium at night in Seoul, vast "
            "back-facing crowd silhouettes raising pink light sticks, bokeh of "
            "magenta lights, city lights in distance, moody pink-purple cinematic "
            "tone, film grain." + LEGAL_SUFFIX,
        ],
    ),
    (
        "arrival",
        [
            "Early dawn arrival hall of Incheon airport, soft morning light through "
            "large windows, a few travelers with rolling suitcases seen from behind, "
            "quiet anticipation mood, warm pastel tones, travel excitement, "
            "cinematic depth of field." + LEGAL_SUFFIX,
            "Airport arrival gate atmosphere at early morning, luggage carts and "
            "travel suitcases, back-facing traveler silhouette walking, glass "
            "facade, gentle sunrise glow, calm hopeful mood, photographic."
            + LEGAL_SUFFIX,
        ],
    ),
    (
        "seokchon",
        [
            "Seokchon Lake in Seoul with cherry blossoms in bloom, the silhouette of "
            "Lotte World Tower rising in the background, soft pink blossoms framing "
            "the water, golden hour reflection on the lake, serene springtime mood, "
            "cinematic." + LEGAL_SUFFIX,
            "Night view of Seokchon Lake with the tall illuminated Lotte Tower "
            "silhouette reflected on calm water, cherry blossom branches, city "
            "lights bokeh, tranquil evening atmosphere, moody blue and pink tones."
            + LEGAL_SUFFIX,
        ],
    ),
    (
        "concert_day",
        [
            # 손 클로즈업 회피 — 응원봉 불빛 물결 와이드샷(손 디테일 비식별).
            "Wide cinematic shot of a vast outdoor concert crowd at dusk seen entirely "
            "from behind, a flowing sea of glowing pink and magenta light sticks "
            "rising above the crowd like a wave of lights, hands and individual "
            "fingers not visible (too far and out of focus), festive anticipation, "
            "warm pink glow, atmospheric haze, shallow background, photographic."
            + LEGAL_SUFFIX,
            # 대안 — 손 프레임 밖, 멀리서 본 군중의 빛 물결.
            "Concert venue forecourt on show day at golden hour, a large line of "
            "attendees photographed from far behind, a rippling field of pink light "
            "sticks held aloft, no close-up of hands or fingers, merchandise stalls "
            "softly blurred in the distance, excited festival mood, cinematic wide "
            "angle." + LEGAL_SUFFIX,
        ],
    ),
    (
        "last_train",
        [
            # 서울 지하철 무드 — '여행 설렘'(대표 6/10 지시: 우울 금지). 막차 '경고'
            # 맥락은 타임라인 SVG가 담당하므로 사진은 즐거움 담당. v3 채택안(v3a).
            "Warm and lively Seoul subway platform in the evening, a bright modern "
            "Korean metro train with clean brushed-aluminum body and a colored "
            "line-stripe (generic stylized design, not a real branded train, no "
            "logos) stopped at the platform, a small group of cheerful young "
            "travelers seen from behind carrying rolling suitcases and tote bags, "
            "one holding a glowing pink light stick, warm golden platform lighting, "
            "soft bokeh, sense of excitement and shared adventure heading home from "
            "a great concert, warm amber and soft pink color grading, uplifting "
            "travel mood." + LEGAL_SUFFIX,
            # 대안 — 차내/플랫폼 경계, 한국 지하철 일반화 분위기.
            "Interior-to-platform view of a generic modern Korean subway station at "
            "night, a sleek silver metro car with a colored accent band along the "
            "doors (no readable signage, no brand marks), a single traveler from "
            "behind with a small bag, last train mood, soft glowing lights, calm "
            "tired atmosphere, moody cinematic photography." + LEGAL_SUFFIX,
        ],
    ),
]


def generate(api_key, prompt, out_path, counter):
    if counter[0] >= HARD_LIMIT:
        raise SystemExit(f"HARD_LIMIT {HARD_LIMIT} reached — aborting")
    counter[0] += 1
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
        print(f"  [#{counter[0]}] ERROR {resp.status_code}: {resp.text[:300]}")
        return False
    data = resp.json()["data"][0]
    b64 = data["b64_json"]
    with open(out_path, "wb") as f:
        f.write(base64.b64decode(b64))
    print(f"  [#{counter[0]}] saved {out_path} ({os.path.getsize(out_path) // 1024}KB)")
    return True


def main():
    api_key = load_key()
    # CLI: optional list of slugs to (re)generate, else all
    only = set(sys.argv[1:]) if len(sys.argv) > 1 else None
    counter = [0]
    for slug, variants in CUTS:
        if only and slug not in only:
            continue
        for i, prompt in enumerate(variants):
            tag = chr(ord("a") + i)
            out = os.path.join(OUT_RAW, f"{slug}_{tag}.png")
            print(f"[{slug}_{tag}] generating...")
            ok = generate(api_key, prompt, out, counter)
            if not ok:
                time.sleep(2)
            time.sleep(1)
    print(f"\nTOTAL GENERATED THIS RUN: {counter[0]} (hard limit {HARD_LIMIT})")


if __name__ == "__main__":
    main()
