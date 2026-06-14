#!/usr/bin/env python3
"""hero 무드 컷 v2 재생성 — KSPO돔 고증 (UGC R17 적발).

v1(_gen_batch.py hero) 결과 UGC 적발 2건:
- 뾰족한 돔 지붕 → 실제 KSPO돔(올림픽체조경기장)은 오목한 현수식(suspension)
  지붕(텐트형 케이블 구조, 중앙이 낮게 가라앉은 새들 모양).
- 남산 N서울타워 병치 → 송파구 올림픽공원에서는 남산타워가 보이지 않음
  (방위·거리상 오류).

v2 변경점 — 고증 강화:
- "domed arena" → 오목 현수식 지붕(low-slung saddle-shaped cable roof, center
  dipping down) 명시 + 뾰족/높은 돔 금지
- "Seoul skyline / N tower" 제거 → 올림픽공원 야경(나무·잔디광장·공원 조명),
  배경에 타워형 랜드마크 없음
- 응원봉·핑크 무드 유지, 인물은 무인 또는 원경 소수 뒷모습

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

# KSPO돔 고증 핵심: 오목 현수식 지붕 + 송파 올림픽공원 (남산타워·스카이라인 금지)
KSPO_AUTHENTICITY = (
    "The arena is a real-life style Seoul Olympic Gymnastics Arena (KSPO Dome): a "
    "wide low circular stadium with a distinctive SAGGING saddle-shaped suspension "
    "cable roof that DIPS DOWN in the center (concave, not a tall pointed dome, not "
    "a sharp peak), sitting low among trees and lawns of an urban park at night. "
    "No tall observation tower, no N Seoul Tower, no distant mountain skyline — "
    "this is the flat green Olympic Park district of Songpa, Seoul. "
)

PROMPTS = {
    "hero_v2a": (
        "Wide cinematic night view of Seoul Olympic Park before a concert. "
        + KSPO_AUTHENTICITY
        + "A vast crowd of concert-goers seen from behind in "
        "the distance holding glowing pink and magenta light sticks, a sea of pink "
        "lights spreading across the park plaza, warm park lamp glow, dramatic "
        "atmospheric haze, magenta and pink color grading, dusk-to-night mood, "
        "epic establishing shot." + LEGAL_SUFFIX
    ),
    "hero_v2b": (
        "Epic establishing night shot of the low saddle-roofed KSPO Dome arena in "
        "an urban park. " + KSPO_AUTHENTICITY + "Distant back-facing crowd "
        "silhouettes raising pink light sticks across the lawn, soft bokeh of "
        "magenta lights, gentle park lighting and trees framing the low dome, moody "
        "pink-purple cinematic tone, subtle film grain, no skyline towers."
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
