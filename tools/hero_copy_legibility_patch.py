#!/usr/bin/env python3
"""데스크탑 히어로 카피 가독 상향 (HERO-COPY-v1) — 홈 index.html 11언어.

배경(R21 UGC, P2): 풀블리드 사진 히어로 위 보조 카피(특히 ko/en 의 4줄 안내 문구)가
밝은 사진 구간에서 가독 약함. 처방: "크기·명도 소폭 상향(어둠막 유지)".

변경:
  1. [11언어] .hero .sub text-shadow 강화 (.4 → .55) — 스크림(어둠막) 위 텍스트
     윤곽 보강. 사진 밝은 구간에서도 흰 본문 가독 ↑. 색상(.92)·배경 스크림 불변.
  2. [ko/en] 보조 2번째 sub 라인(13px) → 14px. 4줄 안내 문구 크기 소폭 상향.
     (다른 9 로케일은 본 보조 라인 부재 — task #41 ko/en 한정 추가분.)

멱등: HERO-COPY-v1 marker 가드 + 정확 1:1 치환. dist/ = 배포 SSOT.
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARKER = "HERO-COPY-v1"

ALL_LANGS = [
    "index.html",
    "en/index.html",
    "ja/index.html",
    "zh-cn/index.html",
    "zh-tw/index.html",
    "es/index.html",
    "th/index.html",
    "id/index.html",
    "pt/index.html",
    "ar/index.html",
    "vi/index.html",
]

# (1) 전 로케일 — 텍스트 섀도우 강화(어둠막 유지, 윤곽만 보강).
SHADOW_OLD = ".hero .sub{color:rgba(255,255,255,.92) !important;text-shadow:0 1px 8px rgba(0,0,0,.4)}"
SHADOW_NEW = ".hero .sub{color:rgba(255,255,255,.92) !important;text-shadow:0 1px 8px rgba(0,0,0,.55)}"

# (2) ko/en — 보조 2번째 sub 라인 13px → 14px.
SUB13_OLD = 'class="sub" style="margin-top:6px;font-size:13px;color:var(--muted)"'
SUB13_NEW = 'class="sub" style="margin-top:6px;font-size:14px;color:var(--muted)"'


def patch(path: str) -> str:
    f = DIST / path
    html = f.read_text(encoding="utf-8")
    if MARKER in html:
        return f"{path}: SKIP (already)"
    if SHADOW_OLD not in html:
        return f"{path}: FAIL (.hero .sub text-shadow .4 미발견)"

    html = html.replace(SHADOW_OLD, SHADOW_NEW, 1)
    sub_bumped = False
    if SUB13_OLD in html:  # ko/en 만 보유
        html = html.replace(SUB13_OLD, SUB13_NEW, 1)
        sub_bumped = True

    html = html.replace("</style>", "/* HERO-COPY-v1 */</style>", 1)
    f.write_text(html, encoding="utf-8")
    return f"{path}: OK (sub14={sub_bumped})"


def main() -> int:
    results = [patch(p) for p in ALL_LANGS]
    for r in results:
        print(r)
    fail = [r for r in results if "FAIL" in r]
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
