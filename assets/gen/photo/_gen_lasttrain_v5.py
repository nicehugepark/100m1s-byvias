#!/usr/bin/env python3
"""last_train 무드 컷 v5 재생성 — 서울 지하철 고증 (UGC R17 적발).

v4(_gen_lasttrain_v4.py) 결과: UGC 적발 "현재 사진이 한국이 아님 —
일본풍 도색, 스크린도어 없음, 한글 사인 0". v4 프롬프트가 PSD를 명시했음에도
결과물이 일본풍으로 나왔고, 한글 역명 사인이 LEGAL_SUFFIX "no text" 가드와
충돌해 0건. 막차 '경고' 맥락은 타임라인 SVG가 담당, 사진은 '여행 설렘' 담당
(v3~v4 역할 분리 유지).

v5 변경점 — 서울 고증 강화:
- 일본풍 도색 차단 → 한국 서울메트로 톤(white-and-silver body + 단색 line stripe),
  명시적으로 "not a Japanese train"
- 스크린도어(PSD) 필수 → glass platform screen doors 강조 + half-height/full-height
- 한글 역명 사인 0 → 가상의 한글 역명 사인을 고증 요소로 명시 허용
  (LEGAL_SUFFIX의 text 금지는 '로고·브랜드·앨범아트' 한정으로 완화)
- 밝은 실내(한국 승강장은 밤에도 환함) 유지 + 설렘 무드

법무 가드 유지: 식별 가능한 얼굴 금지(뒷모습만), 로고·브랜드·앨범아트·
실존 인물·실존 역명 금지. 한글 역명은 가상 텍스트만. 2안 생성 → 우위안 채택.
"""

import base64
import os
import sys

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-byvias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"

# v5: 한글 역명 사인은 고증 요소로 허용. 금지는 로고·브랜드·앨범아트·실존 인물·실존 역명.
LEGAL_SUFFIX = (
    " No identifiable human faces; people shown only as back-facing crowd "
    "silhouettes. No brand logos, no commercial brand marks, no album art, no "
    "real-world company names. Korean station signage may show short generic/"
    "fictional Korean place names only (not a real station). Photorealistic, "
    "cinematic mood photography."
)

KOREA_AUTHENTICITY = (
    "Authentically South Korean Seoul Metro setting (clearly Korea, NOT Japan, "
    "not a Japanese train): glass platform screen doors (PSD) running along the "
    "platform edge, bright clean station interior with Korean Hangul station-name "
    "signage on the wall and pillars, a modern Seoul subway train with a clean "
    "white-and-silver body and a single colored horizontal line-stripe (generic "
    "stylized livery, no logos). "
)

PROMPTS = {
    "last_train_v5a": (
        "Bright, clean modern Seoul Metro subway station platform in the early "
        "evening. " + KOREA_AUTHENTICITY + "Spacious station with a light-colored "
        "ceiling and pale tile floor reflecting soft light, glossy platform "
        "screen door glass. A small group of cheerful young travelers seen from "
        "behind walking with a light, excited step, carrying rolling suitcases "
        "and tote bags, one holding a softly glowing pink light stick. Bright "
        "warm-white lighting with clean highlights, gentle soft bokeh, a joyful "
        "sense of travel anticipation and shared adventure, fresh and uplifting "
        "palette of warm white, soft peach and a touch of pink." + LEGAL_SUFFIX
    ),
    "last_train_v5b": (
        "Cheerful evening on a bright, clean and modern Seoul Metro platform. "
        + KOREA_AUTHENTICITY
        + "Open and well-lit station with luminous high "
        "ceiling and pale stone-look floor, Hangul station-name signs visible on "
        "pillars. Back-facing silhouettes of friends in light summer clothing "
        "with travel backpacks and a rolling suitcase stepping eagerly toward the "
        "open platform screen doors of a bright modern Korean subway train. Crisp "
        "warm-white station lighting and soft natural glow, a couple of pink light "
        "sticks glowing gently in hands, festive but fresh after-concert energy, "
        "clean and inviting palette of warm white, peach and soft magenta accents, "
        "bright and full of travel excitement, cinematic." + LEGAL_SUFFIX
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
