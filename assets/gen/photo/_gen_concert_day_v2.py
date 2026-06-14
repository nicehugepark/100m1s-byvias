#!/usr/bin/env python3
"""concert_day 무드 컷 v2 재생성 — 실내 아레나 스케일·구조 정합 (대표 catch).

v1(_gen_batch.py concert_day) 결과 대표 적발:
- 5만석급 야외 스타디움 스케일 + 야외 무대 → KSPO돔은 1.5만석 실내 아레나
  (올림픽체조경기장). 스케일·구조 불일치.
- 막대형(형광봉) 응원봉 → TWICE 공식 캔디봉(CANDYBONG ∞)과 형태 불일치.

v2 변경점 — 장소 비식별 + 실내 아레나 스케일 정합:
- 실내 아레나 관중석에서 본 시점. 야외·스타디움·하늘·잔디 제거.
- 식별 가능한 건물 외형·돔 외관·랜드마크 0 (KSPO 외형 재현 금지, 룰 ⑧).
- 응원봉은 특정 브랜드 형태 재현 대신 핑크 보케 처리(비식별).
- 1.5만급 실내 아레나 느낌(거대 스타디움 아님).

법무 가드 유지(LEGAL_SUFFIX): 식별 얼굴 0, 로고·브랜드·앨범아트·텍스트 0.
2안 생성 → 우위안 채택.
"""

import base64
import os
import sys

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-bybias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"

LEGAL_SUFFIX = (
    " No identifiable human faces. People shown only as back-facing crowd "
    "silhouettes. No logos, no brand marks, no album art, no text in the image. "
    "Photorealistic, cinematic mood photography."
)

# 실내 아레나 스케일 정합 + 장소 비식별 (KSPO 외형 재현 금지)
INDOOR_ARENA = (
    "Interior of a mid-size indoor concert arena (roughly fifteen-thousand-seat "
    "scale, NOT a giant fifty-thousand outdoor stadium), seen from the seating "
    "tiers during a show. Enclosed dark ceiling with rigging and stage lights "
    "above — NO open sky, NO outdoor field, NO grass, NO stadium roof exterior, "
    "NO recognizable building or landmark. The venue is deliberately "
    "non-identifiable. "
)

PROMPTS = {
    "concert_day_v2a": (
        "Cinematic shot from the stands of an indoor arena on concert day, the "
        "audience a sea of soft pink light glowing in the dark seating bowl. "
        + INDOOR_ARENA
        + "Countless pink lights rendered as warm bokeh (no specific lightstick "
        "shape), distant stage glow and beams from the rigging, back-facing crowd "
        "silhouettes in the foreground, magenta-and-purple cinematic color grade, "
        "shallow depth of field, immersive concert atmosphere." + LEGAL_SUFFIX
    ),
    "concert_day_v2b": (
        "Wide cinematic interior view of a mid-size indoor arena during a K-pop "
        "concert, tiered seating filled with a glowing pink crowd. "
        + INDOOR_ARENA
        + "Pink lights as dreamy bokeh across the bowl, stage light beams cutting "
        "through atmospheric haze, back-facing silhouettes, moody pink-purple tone, "
        "subtle film grain, emotional live-show energy." + LEGAL_SUFFIX
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
