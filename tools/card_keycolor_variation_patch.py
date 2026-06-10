#!/usr/bin/env python3
"""카드 키컬러 변주 강화 (CARD-KEYCOLOR-v1) — 홈 index.html 11언어.

배경(R21 UGC): "카드 썸네일 단조". 실제 카드는 이미 아티스트 키컬러(--stripe,
13색)를 좌측 스트라이프 + 배경 그라데이션 + 하단 스카이라인 실루엣(.ecard::after,
color:var(--stripe))에 반영 중. 다만 스카이라인 opacity 가 낮아(.18/.28) 키컬러
색상 신호가 약해 카드가 비슷비슷하게 보임.

처방: .ecard::after 스카이라인 실루엣 opacity 상향 (light .18→.26, dark .28→.36).
키컬러 변수(--stripe)를 그대로 활용 → 60+ 카드 자동 변주. 신규 자산 0, 가역.
텍스트 대비 무관(스카이라인은 카드 하단 z-index:0 장식, 본문 z-index 위).

멱등: CARD-KEYCOLOR-v1 marker 가드 + 정확 문자열 1:1 치환(중복/재실행 0).
dist/ = 배포 SSOT (repo-root *.html 없음).
"""

import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARKER = "CARD-KEYCOLOR-v1"

LANGS = [
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

# 정확 1:1 치환 — 스카이라인 실루엣 opacity 상향.
# light: .ecard::after 본문 내 opacity:.18 → .26
LIGHT_OLD = "z-index:0;color:var(--stripe,var(--accent));opacity:.18;-webkit-mask:url(/assets/gen/city-skyline.svg)"
LIGHT_NEW = "z-index:0;color:var(--stripe,var(--accent));opacity:.26;-webkit-mask:url(/assets/gen/city-skyline.svg)"
# dark: @media 내 .ecard::after{opacity:.28} → .36
DARK_OLD = ".ecard::after{opacity:.28}"
DARK_NEW = ".ecard::after{opacity:.36}"


def patch(path: str) -> str:
    f = DIST / path
    html = f.read_text(encoding="utf-8")
    if MARKER in html:
        return f"{path}: SKIP (already)"
    if LIGHT_OLD not in html:
        return f"{path}: FAIL (light 스카이라인 opacity:.18 미발견)"
    if DARK_OLD not in html:
        return f"{path}: FAIL (dark 스카이라인 opacity:.28 미발견)"

    html = html.replace(LIGHT_OLD, LIGHT_NEW, 1)
    html = html.replace(DARK_OLD, DARK_NEW, 1)
    # marker — </style> 직전 주석으로 박제.
    html = html.replace("</style>", "/* CARD-KEYCOLOR-v1 */</style>", 1)

    f.write_text(html, encoding="utf-8")
    return f"{path}: OK"


def main() -> int:
    results = [patch(p) for p in LANGS]
    for r in results:
        print(r)
    fail = [r for r in results if "FAIL" in r]
    return 1 if fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
