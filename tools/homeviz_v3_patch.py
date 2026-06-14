#!/usr/bin/env python3
"""ByVias 홈 비주얼 3차 (HOMEVIZ-v3) — 11언어 일괄 패치.

R20 UGC 처방 "사진이 필요 + 404 수리":
  1. [P0] city-skyline.svg 404 fix — 마스크 url 을 상대경로(assets/gen/…) →
     루트 절대경로(/assets/gen/…) 로 교정. 로케일 하위경로(/en/, /ar/ …)에서
     상대경로가 /en/assets/… 로 잘못 해석되어 11개 로케일 전부 마스크 404
     (히어로·카드 스카이라인 실루엣이 보이지 않던 진짜 원인). 루트 홈만 200.
  2. [P0] 히어로 풀블리드 비주얼 — 기검증 자산 hero.jpg(응원봉 바다, 장소 비식별,
     FoP 안전)을 .hero 배경으로. 어둠막(스크림) + 텍스트 라이트 톤으로 가독 유지.
  3. [P0] 히어로 스포트라이트 썸네일 — 가장 임박 카드 옆에 기검증 무드 이미지
     concert_day.jpg(실내 아레나, 도시 비식별) 썸네일. **이벤트별 도시 이미지가
     아니므로 일반 무드 슬롯(스포트라이트)에만** — 특정 도시 카드 박제 금지(고증).
  4. [P1] 핫위크 가로 스와이프 캐러셀 — .hotrow overflow-x scroll-snap.

설계 원칙(트랩 회피):
  - 신규 AI 실사 0. 기검증 자산만 재사용(hero.jpg / concert_day.jpg).
  - 특정 도시 카드에 무관한 도시 이미지 박제 0(고증). 무드 슬롯만.
  - 멱등(HOMEVIZ-v3 marker 가드): 재실행해도 중복 주입 0.
  - dist/ = 배포 SSOT. 마스크 절대경로 교정으로 로케일 404 구조적 봉쇄.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

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

# 히어로 스포트라이트 무드 썸네일 alt (로케일). 일반 "공연 무드" 이미지임을 정직 표기.
SPOT_ALT = {
    "ko": "공연장 무드",
    "en": "Concert mood",
    "ja": "コンサートの雰囲気",
    "zh-cn": "演出现场氛围",
    "zh-tw": "演出現場氛圍",
    "es": "Ambiente de concierto",
    "th": "บรรยากาศคอนเสิร์ต",
    "id": "Suasana konser",
    "pt": "Clima de show",
    "ar": "أجواء الحفل",
    "vi": "Không khí buổi diễn",
}

# v3 CSS — </style> 직전 주입. v2 의 .hero::before(스카이라인)·.hero-spot 위에 덧씌움.
CSS_BLOCK = (
    "/* HOMEVIZ-v3 */"
    # (2) 히어로 풀블리드 사진 — 기검증 hero.jpg. 어둠막(스크림)으로 텍스트 가독.
    ".hero{background:"
    "linear-gradient(180deg,rgba(10,6,20,.30) 0%,rgba(10,6,20,.62) 78%,rgba(10,6,20,.78) 100%),"
    "url(/assets/gen/photo/hero.jpg) center/cover no-repeat,var(--bg)}"
    # RTL 로케일은 `[dir=rtl] .hero{radial-gradient}` (specificity 0,1,1) 가 plain `.hero` 를
    # 덮으므로 동일 specificity 로 사진 배경 재지정. (ar 등 RTL 히어로 사진 미적용 봉쇄)
    "[dir=rtl] .hero{background:"
    "linear-gradient(180deg,rgba(10,6,20,.30) 0%,rgba(10,6,20,.62) 78%,rgba(10,6,20,.78) 100%),"
    "url(/assets/gen/photo/hero.jpg) center/cover no-repeat,var(--bg)}"
    ".hero .eyebrow{background:rgba(255,255,255,.16);border-color:rgba(255,255,255,.28);color:#fff}"
    ".hero h1{color:#fff;text-shadow:0 1px 12px rgba(0,0,0,.45)}"
    ".hero .sub{color:rgba(255,255,255,.92) !important;text-shadow:0 1px 8px rgba(0,0,0,.4)}"
    # 히어로 하단 스카이라인 실루엣을 사진 위에서 흰 톤으로(가독).
    ".hero::before{color:#fff !important;opacity:.22 !important}"
    # (3) 스포트라이트 썸네일 — 좌측 무드 이미지. 기존 hs-dd 앞에 배치.
    ".hero-spot .hs-thumb{flex:0 0 auto;width:54px;height:54px;border-radius:var(--r-sm);"
    "object-fit:cover;display:block}"
    "@media(max-width:380px){.hero-spot .hs-thumb{display:none}}"
    # (4) 핫위크 가로 스와이프 캐러셀.
    ".hotweek .hotrow{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;"
    "-webkit-overflow-scrolling:touch;padding-bottom:4px;scrollbar-width:none}"
    ".hotweek .hotrow::-webkit-scrollbar{display:none}"
    ".hotweek .hotcard{scroll-snap-align:start;flex:0 0 78%;max-width:300px}"
    "@media(min-width:620px){.hotweek .hotcard{flex:0 0 46%}}"
)

# (3) 스포트라이트 썸네일 — 스크립트가 그리는 hero-spot.innerHTML 의 hs-dd 앞에 <img> 삽입.
# v2 스크립트 본문에서 hs-dd 시작 토큰을 찾아 그 앞에 thumb 마크업을 끼움.
SPOT_DD_TOKEN = '\'<span class="hs-dd">'
SPOT_THUMB_TMPL = (
    '\'<img class="hs-thumb" src="/assets/gen/photo/concert_day.jpg" '
    'alt="__ALT__" width="54" height="54" loading="lazy">\'+'
)


def lang_key(path: str) -> str:
    if path == "index.html":
        return "ko"
    return path.split("/")[0]


def patch(path: str) -> str:
    f = DIST / path
    html = f.read_text(encoding="utf-8")
    if "HOMEVIZ-v3" in html:
        return f"{path}: SKIP (이미 패치됨)"
    if "HOMEVIZ-v2" not in html:
        return f"{path}: FAIL (v2 선행 패치 없음)"

    # (1) 404 fix — 모든 상대 assets/gen 마스크 url 을 루트 절대경로로.
    n404 = html.count("url(assets/gen/")
    html = html.replace("url(assets/gen/", "url(/assets/gen/")

    # (2)(4) CSS 주입 (</style> 직전, 첫 번째만).
    if "</style>" not in html:
        return f"{path}: FAIL (</style> 없음)"
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

    # (3) 스포트라이트 썸네일 — hero-spot.innerHTML 의 hs-dd 앞에 img 끼움.
    if SPOT_DD_TOKEN not in html:
        return f"{path}: FAIL (hero-spot hs-dd 토큰 미발견)"
    lk = lang_key(path)
    thumb = SPOT_THUMB_TMPL.replace("__ALT__", SPOT_ALT.get(lk, SPOT_ALT["en"]))
    html = html.replace(SPOT_DD_TOKEN, thumb + SPOT_DD_TOKEN, 1)

    f.write_text(html, encoding="utf-8")
    return f"{path}: OK (404fix={n404} thumb_alt={SPOT_ALT.get(lk, SPOT_ALT['en'])!r})"


if __name__ == "__main__":
    results = [patch(p) for p in LANGS]
    for r in results:
        print(r)
    fails = [r for r in results if "FAIL" in r]
    sys.exit(1 if fails else 0)
