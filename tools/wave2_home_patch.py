#!/usr/bin/env python3
"""ByVias 홈 R25 wave2 패치 (WAVE2-HOME-v1) — 11언어 index 멱등 적용.

R25 판정 + 조니(아이브) 지적 집행. dist/ = 라이브 SSOT (FLR-20260611-TEC-001).

  P0-1 종료 이벤트 그리드 노출 봉쇄 (한쪽 코드 양끝 누락 동형 — FLR-20260428-TEC-001):
       날짜 비교 전 사용처 정책 단일화 "종료 = upcoming 그리드 제외".
       (a) 정적: data-date < 오늘 카드를 upcoming 패널 → 지난 이벤트 그리드로 이동
           (ko/en은 기존 past 관행대로 종료 배지 스왑, 타 9언어는 기존 past 카드와
            동일하게 원 배지 유지 — 번역 날조 금지).
       (b) 런타임 가드 JS: 빌드 사이 간극에 지나간 카드 display:none
           (기존 D-day JS diff<0 비표시·hotweek diff<0 제외와 정책 일치).
  P0-2① 회색 폴백 그라데이션(51장, rgba(138,138,138)) → 플랫 중립 카드
        (색 데이터 없는 카드 색칠 금지 — 다크모드 기존 단색 강등과 정합).
  P0-2② 텍스트 칩(abadge) 라벨 == 옆 이름 라벨 → 칩 제거 (이름 1회만).
  P1③  비활성 탭 테두리 대비 ≥3:1 (light #807c6e=4.18:1, dark #7d7868=3.74:1).
  조니① 임박 캐러셀이 히어로 스포트라이트와 동일 1건 중복 → 캐러셀에서 제외 (3중→2중).
  조니② 무설명 jargon 배지(초장기 선점·발표 골든창) → 콘서트 탭 상단 1줄 legend
        (배지명은 각 언어 파일에서 추출 — 설명문은 ko/en, 타 9언어 en fallback,
         home_redesign_patch eyebrow DSN §5.3 관행 정합).
  조니③ 전 카드 하단 스카이라인 실루엣 장식 제거.
  조니④ D-chip 고정 슬롯 (카드 우하단 absolute — 텍스트 길이 무관 정렬).

실행: python3 tools/wave2_home_patch.py
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
TODAY = date.today().isoformat()

# i18n 연동 — site/ 경로 추가 후 import
_SITE_SRC = Path("/Users/seongjinpark/company/100m1s/projects/bybias/site")
sys.path.insert(0, str(_SITE_SRC))
try:
    import i18n as _I18N

    _HAS_I18N = True
except ImportError:
    _HAS_I18N = False

MARK = "WAVE2-HOME-v1"

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

# ── P0-2① 회색 폴백 인라인 스타일(정확 1:1) → 플랫 중립 ──
GRAY_OLD = (
    "border-inline-start:4px solid var(--stripe);"
    "background:linear-gradient(var(--ga,135deg),rgba(138,138,138,0.10) 0%,"
    "var(--ehead-mid,#ffffff) 42%,rgba(138,138,138,0.26) 100%);--stripe:#8A8A8A"
)
GRAY_NEW = "border-inline-start:4px solid var(--line);background:var(--card)"

# ── 조니③ 스카이라인 제거 (정확 문자열) ──
SKY_LIGHT = (
    ".ecard::after{content:'';position:absolute;left:0;right:0;bottom:0;height:30px;"
    "z-index:0;color:var(--stripe,var(--accent));opacity:.26;"
    "-webkit-mask:url(/assets/gen/city-skyline.svg) bottom/auto 30px repeat-x;"
    "mask:url(/assets/gen/city-skyline.svg) bottom/auto 30px repeat-x;"
    "background:currentColor}"
)
SKY_DARK = "@media(prefers-color-scheme:dark){.ecard::after{opacity:.36}}"
SKY_PAD = ".ecard{padding-bottom:30px}"

# ── P1③ 탭 테두리 (home .tabs) ──
TAB_OLD = "border:1px solid var(--line);border-radius:9px;margin:0 6px 12px 0"
TAB_NEW = (
    "border:1px solid var(--tabline,#807c6e);border-radius:9px;margin:0 6px 12px 0"
)

# ── 조니① 핫위크가 스포트라이트(가장 임박 1건) 중복 노출 → 캐러셀은 2번째부터 ──
HW_OLD = (
    "var H=[];for(var j=0;j<L.length;j++){if(L[j].diff<=14)H.push(L[j]);}"
    "H=H.slice(0,5);"
)
HW_NEW = (
    "var hs=(spot&&L.length)?1:0;"
    "var H=[];for(var j=hs;j<L.length;j++){if(L[j].diff<=14)H.push(L[j]);}"
    "H=H.slice(0,5);"
)

# ── 신규 CSS (</style> 직전 1회 주입) ──
CSS_BLOCK = (
    f"/* {MARK} */"
    # P1③ 탭 테두리 토큰 — 비활성 탭 vs 카드/페이지 배경 ≥3:1 (WCAG 1.4.11)
    ":root{--tabline:#807c6e}"
    "@media(prefers-color-scheme:dark){:root{--tabline:#7d7868}}"
    # 조니④ D-chip 고정 슬롯: 카드 우하단 absolute — 동일 행 카드 간 y 정렬 고정
    ".grid .ecard .dday{position:absolute;bottom:13px;inset-inline-end:13px;"
    "margin:0;vertical-align:0;z-index:2}"
    # 칩의 containing block 을 카드로: 기존 .ecard>*{position:relative} 가 .c 를
    # 컨테이닝 블록으로 만들어 칩이 부유 — 카드 내 장식(ghost/skyline) 제거로 .c 의
    # z-index 레이어링 불요 → static 강등이 안전
    ".grid .ecard .c{position:static}"
    # 조니② legend
    ".lglegend{font-size:12px;color:var(--muted);margin:2px 0 10px;line-height:1.55}"
    ".lglegend .lgdot{display:inline-block;width:8px;height:8px;border-radius:50%;"
    "margin:0 4px 1px 0;vertical-align:middle}"
)

# ── 조니② legend 설명문 (ko/en 하드코딩 SSOT — 타 9언어 i18n 번역, 미이용 시 en fallback) ──
LEGEND_EXPL = {
    "ko": ("공연까지 여유 — 항공·숙소 미리 선점 구간", "막 발표됨 — 지금이 예약 적기"),
    "en": (
        "months out — lock flights &amp; stays early",
        "just announced — best time to book",
    ),
}


def _legend_expl(lang: str) -> tuple[str, str]:
    """lang별 lglegend 설명문 반환. i18n 사전 우선 → LEGEND_EXPL → en fallback."""
    if lang in LEGEND_EXPL:
        return LEGEND_EXPL[lang]
    if _HAS_I18N:
        ui = _I18N.ui(lang)
        pre = ui.get("lglegend_pre")
        ann = ui.get("lglegend_ann")
        if pre and ann:
            # HTML 엔티티 보존: &amp; → & 치환 없이 그대로 반환
            return (pre, ann)
    return LEGEND_EXPL["en"]


PAST_H2 = (
    '<h2 style="font-size:16px;font-weight:600;margin:28px 0 4px;color:var(--muted)">'
)
ENDED_BADGE_RE = re.compile(
    r'<span class="badge" style="color:var\(--muted\);background:#eeece5;font-size:11px">[^<]*</span>'
)
ECARD_RE = re.compile(r'<a class="ecard".*?</a>', re.S)
DDATE_RE = re.compile(r'class="dday" data-date="(\d{4}-\d{2}-\d{2})"')
LAST_BADGE_RE = re.compile(r'<span class="badge"[^>]*>[^<]*</span>(?=</a>$)')
# B(초장기 선점)·A(발표 골든창) 라벨 — 이모지 프리픽스(⚽/📺) 달린 타입 배지 제외
B_LABEL_RE = re.compile(
    r'<span class="badge" style="color:#0F6E56;background:#E1F5EE;font-size:11px">([^<⚽📺🎤🎪]+)</span>'
)
A_LABEL_RE = re.compile(
    r'<span class="badge" style="color:#185FA5;background:#E6F1FB;font-size:11px">([^<⚽📺🎤🎪]+)</span>'
)
ABADGE_RE = re.compile(
    r'<span class="abadge"[^>]*>(.*?)</span>(?=<div class="a">)', re.S
)
A_NAME_RE = re.compile(r'<div class="a">(.*?)</div>', re.S)
TAGS_RE = re.compile(r"<[^>]+>")

GUARD_JS = (
    f"<script>/* {MARK} pastguard */(function(){{function r(){{try{{"
    "var T=new Date();T.setHours(0,0,0,0);"
    "var cs=document.querySelectorAll('.tabpanel .ecard');"
    "for(var i=0;i<cs.length;i++){var d=cs[i].querySelector('.dday[data-date]');"
    "if(!d)continue;var p=(d.getAttribute('data-date')||'').split('-');"
    "if(p.length!==3)continue;var e=new Date(+p[0],+p[1]-1,+p[2]);e.setHours(0,0,0,0);"
    "if(Math.round((e-T)/86400000)<0){cs[i].style.display='none';}}"
    "}catch(e){}}"
    "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',r);}else{r();}"
    "})();</script>".replace("{{function r(){{try{{", "{function r(){try{")
)


def _txt(s):
    return TAGS_RE.sub("", s).strip().casefold()


def relocate_past(html):
    """upcoming 패널의 종료(data-date<오늘) 카드 → past 그리드 앞으로 이동."""
    i_past = html.find(PAST_H2)
    if i_past < 0:
        return html, 0
    ended_badge = None
    m_eb = ENDED_BADGE_RE.search(html, i_past)
    if m_eb:
        ended_badge = m_eb.group(0)
    moved = []  # (date, card_html)
    out = []
    pos = 0
    for m in ECARD_RE.finditer(html):
        if m.start() >= i_past:
            break  # past 영역 카드는 그대로
        dm = DDATE_RE.search(m.group(0))
        if dm and dm.group(1) < TODAY:
            card = m.group(0)
            if ended_badge:  # ko/en: 기존 past 관행대로 종료 배지 스왑
                card = LAST_BADGE_RE.sub(ended_badge, card)
            moved.append((dm.group(1), card))
            out.append(html[pos : m.start()])
            pos = m.end()
    out.append(html[pos:])
    html = "".join(out)
    if not moved:
        return html, 0
    moved.sort(key=lambda x: x[0], reverse=True)  # 최근 종료 먼저(past 정렬 정합)
    i_past = html.find(PAST_H2)  # 제거로 인덱스 변동 → 재탐색
    i_grid = html.find('<div class="grid">', i_past)
    if i_grid < 0:
        return html, 0
    ins = i_grid + len('<div class="grid">')
    html = html[:ins] + "".join(c for _, c in moved) + html[ins:]
    return html, len(moved)


def dedup_abadge(html):
    """ecard 내 abadge 텍스트 == .a 이름 → abadge 제거 (이름 1회만)."""
    n = 0

    def fix_card(m):
        nonlocal n
        card = m.group(0)
        am = ABADGE_RE.search(card)
        nm = A_NAME_RE.search(card)
        if am and nm and _txt(am.group(1)) == _txt(nm.group(1)):
            card = card[: am.start()] + card[am.end() :]
            n += 1
        return card

    html = ECARD_RE.sub(fix_card, html)
    return html, n


def legend_html(html, lang):
    bm = B_LABEL_RE.search(html)
    am = A_LABEL_RE.search(html)
    if not (bm and am):
        return ""
    b_expl, a_expl = _legend_expl(lang)
    return (
        '<p class="lglegend">'
        f'<span class="lgdot" style="background:#0F6E56"></span>'
        f"<b>{bm.group(1).strip()}</b> = {b_expl} &nbsp;·&nbsp; "
        f'<span class="lgdot" style="background:var(--accent-bg)"></span>'
        f"<b>{am.group(1).strip()}</b> = {a_expl}</p>"
    )


def process(path):
    f = DIST / path
    lang = "ko" if path == "index.html" else path.split("/")[0]
    html = f.read_text(encoding="utf-8")
    if MARK in html:
        return f"{path}: SKIP (already)"
    stats = {}
    # P0-2① 회색 폴백 → 플랫 (이동 전에 먼저 — 이동 카드에도 적용)
    stats["gray"] = html.count(GRAY_OLD)
    html = html.replace(GRAY_OLD, GRAY_NEW)
    # P0-2② abadge 중복 제거
    html, stats["dedup"] = dedup_abadge(html)
    # P0-1(a) 정적 이동
    html, stats["moved"] = relocate_past(html)
    # 조니③ 스카이라인 제거
    stats["sky"] = int(SKY_LIGHT in html)
    html = html.replace(SKY_LIGHT, "").replace(SKY_DARK, "").replace(SKY_PAD, "")
    # P1③ 탭 테두리
    if TAB_OLD not in html:
        return f"{path}: FAIL (tab border 패턴 미발견)"
    html = html.replace(TAB_OLD, TAB_NEW, 1)
    # 조니① 핫위크 스포트라이트 중복 제외
    if HW_OLD not in html:
        return f"{path}: FAIL (hotweek 패턴 미발견)"
    html = html.replace(HW_OLD, HW_NEW, 1)
    # 조니② legend — 콘서트 패널 직전
    lg = legend_html(html, lang)
    anchor = '<div class="tabpanel tp-c">'
    if lg and anchor in html:
        html = html.replace(anchor, lg + anchor, 1)
        stats["legend"] = 1
    # CSS + P0-1(b) 런타임 가드
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)
    html = html.replace("</body>", GUARD_JS + "</body>", 1)
    f.write_text(html, encoding="utf-8")
    return f"{path}: OK {stats}"


def main():
    results = [process(p) for p in LANGS]
    for r in results:
        print(r)
    return 1 if any("FAIL" in r for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
