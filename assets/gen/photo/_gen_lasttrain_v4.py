#!/usr/bin/env python3
"""last_train 무드 컷 v4 재생성 — v3 '여전히 우울' (대표 6/11 지시).

v3(_gen_lasttrain_v3.py) 결과: 어두운 플랫폼 + 짙은 오렌지 일색 = 여전히
우울·답답. 대표 verbatim "승강장 이미지는 너무 우울해 보여. 여행하는
즐거움이 느껴지지 않잖아." 막차 '경고' 맥락은 타임라인 SVG가 담당하므로
사진은 '여행 설렘' 담당으로 역할 분리(v3 의도 유지).

v4 변경점 — 밝기·청결·활기 강화:
- 어두운 터널형 플랫폼 → 밝고 깨끗한 현대식 역사(밝은 천장·타일·유리)
- 짙은 앰버 일색 → 따뜻하되 밝은 화이트밸런스, 깨끗한 하이라이트
- 정적 → 가벼운 발걸음·기대감, 활기

법무 가드 유지: 식별 가능한 얼굴 금지(뒷모습만), 로고·브랜드·앨범아트·
텍스트·실존 인물 금지. 2안 생성 → 우위안 채택.
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
    "last_train_v4a": (
        "Bright, clean and airy modern Seoul subway station platform in the "
        "early evening, spacious station with a light-colored ceiling, glossy "
        "platform-screen-door glass and pale tile floor reflecting soft light, "
        "a sleek modern Korean metro train with a clean white-and-silver body "
        "and a simple colored line-stripe (generic stylized design, not a real "
        "branded train, no logos) waiting at the platform, a small group of "
        "cheerful young travelers seen from behind walking with a light, "
        "excited step, carrying rolling suitcases and tote bags, one holding a "
        "softly glowing pink light stick, bright warm-white lighting with clean "
        "highlights, gentle soft bokeh, a joyful sense of travel anticipation "
        "and shared adventure, fresh and uplifting palette of warm white, soft "
        "peach and a touch of pink, vibrant and hopeful mood." + LEGAL_SUFFIX
    ),
    "last_train_v4b": (
        "Cheerful evening on a bright, clean and modern Seoul metro platform, "
        "open and well-lit station with glass platform screen doors, pale "
        "stone-look floor and a luminous high ceiling, back-facing silhouettes "
        "of friends in light summer clothing with travel backpacks and a "
        "rolling suitcase stepping eagerly toward a bright modern stylized "
        "Korean subway train (no brand, no logos, white-and-silver body), crisp "
        "warm-white station lighting and soft natural glow, a couple of pink "
        "light sticks glowing gently in hands, festive but fresh after-concert "
        "energy, clean and inviting palette of warm white, peach and soft "
        "magenta accents, bright and full of travel excitement, cinematic."
        + LEGAL_SUFFIX
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
