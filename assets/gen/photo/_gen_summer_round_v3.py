#!/usr/bin/env python3
"""여름 무드 + 비식별 + 9호선 골드 라운드 v3 — 누적 요구사항 통합 재생성.

R18 고증 적발: 직전 비식별 재생성(_gen_landmark_v2.py)이 그 전 라운드의
"여름"(공연 7/10~12 한여름) 요구를 모르고 "spring / cherry blossom"(봄·벚꽃)을
넣어 계절을 회귀시켰음 = 웨이브 간 요구사항 유실 회귀 (FLR-20260611 류).

본 v3는 누적 요구사항을 한 스크립트에 동시 반영 — 하나라도 빠지면 재회귀.

공통 가드 (전 이미지):
  ① 한여름(공연 7/10~12) — 계절 단서는 여름(짙은 녹음, 여름 차림). 벚꽃/봄 금지.
  ② 실존 랜드마크(롯데타워·N서울타워 등) 식별 가능 형태 금지 — 비식별 유지.
  ③ 읽히는 텍스트(역명·간판) 0.
  ④ 인물은 공간에 맞는 소수 뒷모습, 원근 정합.
  ⑤ 장면 현실성(AI 위화감 최소).

개별:
  1. seokchon         — 여름 밤/골든아워 호숫가 산책로, 짙은 녹음, 호수 반영. 벚꽃 금지. 타워 비식별.
  2. step_lotte_night — 여름 밤 호숫가/공원 야경 무드(조명 반영). 벚꽃 금지. 타워 비식별.
  3. last_train       — 밝은 한국 지하철 승강장 + 9호선 정합(차량/노선 색 = 골드·샴페인 계열).
                        스크린도어(PSD), 역명 무텍스트(픽토그램만), 캐리어·응원봉 뒷모습 소수, 설렘.

9호선 livery 고증 (WebSearch 2건 corroboration, 2026-06-11):
  - 서울지하철 9호선 노선색 = 골드(먼셀 10YR 6.0/10), 공식 노선도상 샴페인 골드.
  - 차량 노선 스트라이프 = 골드. (en.namu.wiki/Seoul_Subway_Line_9, fnnews.com 2006-02-20)

각 슬러그 2안 생성 → 우위안 채택(_webify.py 로 webify). 가드 위반 시 FAIL 재생성.
"""

import base64
import os
import sys

import requests

OUT_RAW = "/Users/seongjinpark/company/100m1s-byvias/assets/gen/photo/raw"
ENV_PATH = "/Users/seongjinpark/company/100m1s/.env"
MODEL = "gpt-image-1.5"
LANDSCAPE = "1536x1024"

# ① 여름 + ② 비식별 + ③ 무텍스트 + ④ 뒷모습 공통 가드.
LEGAL_SUFFIX = (
    " No identifiable human faces; people shown only as back-facing "
    "silhouettes. No logos, no brand marks, no text, no readable signage of any "
    "kind in the image. Photorealistic, cinematic mood photography."
)

# ② 식별 랜드마크 금지.
NO_LANDMARK = (
    "IMPORTANT: no recognizable landmark, no tall observation tower, no "
    "skyscraper skyline, no identifiable building — the location is deliberately "
    "generic and non-identifiable. "
)

# ① 한여름 단서 강제 (벚꽃/봄 명시 배제).
SUMMER = (
    "It is the height of midsummer (mid-July): lush deep-green summer foliage, "
    "dense leafy trees in full summer leaf, people in light summer clothing. "
    "Absolutely NO cherry blossoms, NO pink petals, NO spring blossom — this is "
    "deep summer, not spring. "
)

PROMPTS = {
    # 1. 석촌호수 무드 — 여름 밤/골든아워 호숫가 (롯데타워 없음, 벚꽃 없음)
    "seokchon_v3a": (
        "Cinematic golden-hour summer evening by a calm urban lake lined with "
        "lush deep-green leafy trees, warm low sun reflected on still water, a "
        "paved lakeside walking path, a few back-facing strollers in light summer "
        "clothing in the distance. "
        + SUMMER
        + NO_LANDMARK
        + "Dreamy travel mood, warm green-and-amber tones."
        + LEGAL_SUFFIX
    ),
    "seokchon_v3b": (
        "Wide cinematic view of a city lakeside park on a warm summer evening, "
        "rows of full-leaved green trees arching over a quiet waterside promenade, "
        "soft golden dusk light, calm reflective water mirroring the green canopy. "
        + SUMMER
        + NO_LANDMARK
        + "Romantic summer travel atmosphere, warm golden-green color grade."
        + LEGAL_SUFFIX
    ),
    # 2. step_lotte_night 무드 — 여름 밤 호숫가/공원 야경 (롯데타워 없음, 벚꽃 없음)
    "step_lotte_night_v3a": (
        "Cinematic summer night by a calm urban lake, lush green trees lit softly "
        "by warm park lamps, lamp glow and soft bokeh of distant lights reflecting "
        "on still dark water, a quiet lakeside path, romantic warm summer-evening "
        "mood. "
        + SUMMER
        + NO_LANDMARK
        + "Moody blue-and-amber night tones, peaceful travel atmosphere."
        + LEGAL_SUFFIX
    ),
    "step_lotte_night_v3b": (
        "Atmospheric summer night view of a lakeside park promenade, glowing park "
        "lamps and warm bokeh of distant city lights mirrored on calm water, dense "
        "green summer foliage framing the foreground. "
        + SUMMER
        + NO_LANDMARK
        + "Cinematic warm summer-evening mood, deep blue and amber light contrast."
        + LEGAL_SUFFIX
    ),
    # 3. last_train 무드 — 밝은 서울 지하철 9호선(골드 livery) 승강장, 역명 무텍스트
    "last_train_v3a": (
        "Bright, clean modern Seoul Metro Line 9 subway station platform in the "
        "early summer evening. Authentically South Korean Seoul Metro setting "
        "(clearly Korea, NOT Japan): glass platform screen doors (PSD) running "
        "along the platform edge, bright clean station interior, a modern Seoul "
        "subway train whose body carries a distinctive champagne-GOLD horizontal "
        "line-stripe (Seoul Line 9 is the gold line), clean white-and-silver body "
        "with that warm gold accent stripe. A small group of cheerful young "
        "travelers seen from behind in light summer clothing, walking with an "
        "excited step, carrying rolling suitcases and tote bags, one holding a "
        "softly glowing pink light stick. Bright warm-white lighting, gentle soft "
        "bokeh, joyful sense of travel anticipation." + NO_LANDMARK + LEGAL_SUFFIX
    ),
    "last_train_v3b": (
        "Cheerful summer evening on a bright, clean and modern Seoul Metro Line 9 "
        "platform. Authentically South Korean (clearly Korea, NOT Japan): glass "
        "platform screen doors, luminous high ceiling, pale stone-look floor, "
        "clean pillars. A bright modern Korean subway train at the platform with a "
        "warm champagne-GOLD horizontal stripe along its white-and-silver body "
        "(Seoul Line 9 gold livery). Back-facing silhouettes of friends in light "
        "summer clothing with travel backpacks and a rolling suitcase stepping "
        "eagerly toward the open screen doors, a couple of pink light sticks "
        "glowing gently. Crisp warm-white lighting, festive but fresh "
        "after-concert energy, cinematic." + NO_LANDMARK + LEGAL_SUFFIX
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
