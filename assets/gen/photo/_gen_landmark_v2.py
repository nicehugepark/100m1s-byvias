#!/usr/bin/env python3
"""랜드마크 3종 무드 컷 v2 — 식별 랜드마크 제거, 비식별 무드만 (대표 catch, 룰 ⑧).

대표 catch: 실존 랜드마크의 사진풍 AI 재현 = 룰 ⑧ 위반 + "가짜 티" 반감.
대상 3종 (모두 식별 가능한 타워·스카이라인 재현이 문제):
- seokchon: 석촌호수 + 롯데월드타워 + 벚꽃 → 롯데타워(식별) 제거, 벚꽃 핀 호숫가 무드만.
- step_lotte_night: 롯데월드타워 야경 → 타워 제거, 봄밤 호숫가 벚꽃·조명 반영 무드.
- step_namsan: 한양도성 성곽 + N서울타워 + 롯데 스카이라인 → N타워·스카이라인 제거,
  숲 사이 옛 성곽길 산책 무드(식별 도시 전경 없음).

처리 경로 B(비식별 추상 컷): 식별 랜드마크 0 → "가짜 랜드마크" 문제 자체 소멸.
인물은 뒷모습·실루엣만, 텍스트 0, 로고 0.
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
    " No identifiable human faces. People shown only as back-facing "
    "silhouettes. No logos, no brand marks, no text in the image. "
    "Photorealistic, cinematic mood photography."
)

NO_LANDMARK = (
    "IMPORTANT: no recognizable landmark, no tall observation tower, no skyscraper "
    "skyline, no identifiable building — the location is deliberately generic and "
    "non-identifiable. "
)

PROMPTS = {
    # 석촌호수 무드 — 벚꽃 핀 도심 호숫가 (롯데타워 없음)
    "seokchon_v2a": (
        "Cinematic spring morning by a calm urban lake lined with blooming cherry "
        "blossom trees, soft pink petals reflected on still water, a paved "
        "lakeside walking path, gentle warm sunlight, a few back-facing strollers "
        "in the distance. "
        + NO_LANDMARK
        + "Dreamy travel mood, soft pastel tones."
        + LEGAL_SUFFIX
    ),
    "seokchon_v2b": (
        "Wide cinematic view of a city lakeside park in spring, rows of cherry "
        "blossoms arching over a quiet waterside promenade, petals drifting, soft "
        "morning haze, calm reflective water. " + NO_LANDMARK + "Romantic travel "
        "atmosphere, warm pastel color grade." + LEGAL_SUFFIX
    ),
    # step_lotte_night 무드 — 봄밤 호숫가 (롯데타워 없음)
    "step_lotte_night_v2a": (
        "Cinematic spring night by a calm urban lake, cherry blossom trees lit "
        "softly, warm lamp glow reflecting on still dark water, a quiet lakeside "
        "bench and path, romantic evening mood. " + NO_LANDMARK + "Moody blue-and-"
        "amber night tones, peaceful travel atmosphere." + LEGAL_SUFFIX
    ),
    "step_lotte_night_v2b": (
        "Atmospheric night view of a lakeside park promenade in spring, glowing "
        "park lamps and soft bokeh of distant city lights mirrored on calm water, "
        "cherry blossoms in the foreground. " + NO_LANDMARK + "Cinematic evening "
        "mood, deep blue and warm light contrast." + LEGAL_SUFFIX
    ),
    # step_namsan 무드 — 숲 사이 옛 성곽길 (N타워·스카이라인 없음)
    "step_namsan_v2a": (
        "Cinematic view of an old stone fortress wall path winding through a "
        "green wooded hillside in warm afternoon light, lush summer trees framing "
        "the trail, a lone back-facing hiker walking the path. "
        + NO_LANDMARK
        + "No city skyline visible, only forest and the historic stone wall. "
        "Serene travel mood, golden light." + LEGAL_SUFFIX
    ),
    "step_namsan_v2b": (
        "Wide cinematic shot of a historic stone city-wall trail climbing through "
        "dense green forest on a hillside, dappled sunlight through leaves, weathered "
        "stone steps and wooden railing. " + NO_LANDMARK + "No skyline, no tower — "
        "just woods and the old wall. Peaceful hiking atmosphere, warm tones."
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
