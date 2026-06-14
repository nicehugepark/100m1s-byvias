#!/usr/bin/env python3
"""hero 무드 컷 v3 재생성 — 장소 비식별 + 장면 현실성 (대표 catch R17-wave3).

v2(_gen_hero_v2.py) 결과 대표 적발:
- 실존 랜드마크(KSPO돔)의 사진풍 AI 재현 = 신규 룰 ⑧ 위반.
- 공연 전 야외 잔디광장에 응원봉 수천 군집 = 현실에 없는 장면
  (관객은 입장 전 응원봉을 켜 들고 대규모로 야외 집결하지 않는다).
- "KSPO Dome · Olympic Park at night" 실명 단정 캡션.

v3 변경점 — 장소 비식별 + 실재 장면:
- 외부 건물·돔·랜드마크 외형 전면 제거. 공연장 "내부" 관중석에서 본 시점.
- 응원봉 바다 클로즈업(보케·무대 조명 글로우), 식별 가능한 건축물 0.
- 인물은 뒷모습·실루엣만, 식별 얼굴 0.
- 이 장면(공연 중 실내 응원봉 물결)은 현실에 실제로 존재 → 장면 현실성 충족.

법무 가드 유지(LEGAL_SUFFIX): 식별 얼굴 0, 로고·브랜드·앨범아트·텍스트 0.
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
    " No identifiable human faces. People shown only as distant back-facing "
    "crowd silhouettes. No logos, no brand marks, no album art, no text in the "
    "image. Photorealistic, cinematic mood photography."
)

# 핵심: 공연장 내부 시점 + 식별 가능한 건축물·랜드마크 0 (장소 비식별)
NO_LANDMARK = (
    "Shot from inside a concert arena seating bowl during the show, looking "
    "across the audience. NO recognizable building exterior, NO dome, NO city "
    "skyline, NO observation tower, NO landmark — only the dark interior with "
    "stage light glow above. The setting is deliberately non-identifiable. "
)

PROMPTS = {
    "hero_v3a": (
        "Cinematic close-up of a sea of glowing pink and magenta light sticks "
        "raised by a concert crowd, seen from within the audience. "
        + NO_LANDMARK
        + "Thousands of pink lights stretching into soft bokeh, warm stage light "
        "haze spilling over the heads of back-facing silhouetted fans in the "
        "foreground, dramatic magenta-and-purple color grading, shallow depth of "
        "field, dreamy atmospheric mood, epic live-concert energy." + LEGAL_SUFFIX
    ),
    "hero_v3b": (
        "Wide cinematic shot from the upper stands of an arena during a concert, "
        "an ocean of pink and magenta light sticks filling the dark seating bowl. "
        + NO_LANDMARK
        + "Soft bokeh of countless pink lights, distant stage glow and beams of "
        "light from above, back-facing crowd silhouettes, moody pink-purple "
        "cinematic tone, subtle film grain, immersive and emotional atmosphere."
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
