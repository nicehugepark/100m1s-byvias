#!/usr/bin/env python3
"""last_train 무드 컷 v6 재생성 — 가짜 역명 제거 (대표 고증 룰).

v5(_gen_lasttrain_v5.py) 결과: 라이브 last_train.jpg(v5)에 한글 역명 사인
"동호"(천장)·"서림 / Seorim"(기둥)이 박혔는데 둘 다 AI가 지어낸 실존하지 않는
역명이었음 = 고증 붕괴 (FLR-20260606-AGT-001 고유명사 환각 회귀 동형).

ROOT: v5 LEGAL_SUFFIX가 "fictional Korean place names only" 를 명시 허용했고
KOREA_AUTHENTICITY가 "Hangul station-name signage on the wall and pillars" 를
명시 요구 → 모델이 가짜 역명을 그려넣음.

v6 변경점 — 대표 룰 (verbatim): "역 이름이 글자로 들어갈 경우 해당 역의 이미지를
검색해보고 반드시 현실과 동일한 이미지를 생성. 그렇지 않으면 고증이 더 깨진다."
→ 옵션 a 채택: 읽히는 역명 글자가 없는 구도.
- 한글 역명 사인 요구 제거. 대신 "no readable station name text" 명시.
- 사인은 범용 wayfinding 만 (방향 화살표, "나가는 곳 Exit" 류 픽토그램),
  또는 사인을 원경 블러/앵글 회피로 글자 판독 불가.
- 같은 컨셉 유지: 밝고 깨끗한 서울 지하철 승강장, 스크린도어(PSD),
  뒷모습 원정 팬 소수(캐리어·응원봉), 여행 설렘.

법무 가드 유지: 식별 가능한 얼굴 금지(뒷모습만), 로고·브랜드·앨범아트·
실존 인물 금지. 2안 생성 → 우위안 채택. 한글/유사 한글 역명 판독 시 FAIL.
"""

import base64
import os
import sys

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-byvias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"

# v6: 읽히는 역명 텍스트 0. 사인은 범용 wayfinding 픽토그램만 (역명 아님).
LEGAL_SUFFIX = (
    " No identifiable human faces; people shown only as back-facing crowd "
    "silhouettes. No brand logos, no commercial brand marks, no album art, no "
    "real-world company names. CRITICAL: no readable station-name text anywhere "
    "in the frame — do NOT render any Korean Hangul or Latin station name; any "
    "signage must be either generic wayfinding pictograms (directional arrows, "
    "exit icon) or kept distant/out-of-focus so no place name is legible. "
    "Photorealistic, cinematic mood photography."
)

KOREA_AUTHENTICITY = (
    "Authentically South Korean Seoul Metro setting (clearly Korea, NOT Japan, "
    "not a Japanese train): glass platform screen doors (PSD) running along the "
    "platform edge, bright clean station interior, a modern Seoul subway train "
    "with a clean white-and-silver body and a single colored horizontal "
    "line-stripe (generic stylized livery, no logos). No station-name signs. "
)

PROMPTS = {
    "last_train_v6a": (
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
    "last_train_v6b": (
        "Cheerful evening on a bright, clean and modern Seoul Metro platform. "
        + KOREA_AUTHENTICITY
        + "Open and well-lit station with luminous high "
        "ceiling and pale stone-look floor, clean pillars without any name "
        "signage. Back-facing silhouettes of friends in light summer clothing "
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
