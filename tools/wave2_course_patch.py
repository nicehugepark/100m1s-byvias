#!/usr/bin/env python3
"""ByBias 코스 페이지 R25 wave2 패치 (WAVE2-COURSE-v1) — ko+en 멱등 적용.

코스 섹션은 ko·en만 존재 (44a6f17a에서 타 9언어 grep 0건 확인).
dist/ = 라이브 SSOT (FLR-20260611-TEC-001).

  P1①  en 390px 코스(베이스) 탭 행 crs-tabbar 화면 밖 클리핑 51.3px
       (scrollbar-width:none → affordance 0) → flex-wrap + 모바일 탭 유연폭
       + crs-tag 축약(ellipsis) → 클리핑 0.
  P1③  비활성 탭 테두리 ≥3:1 — sl-bar(#ccc9bb→#807c6e light / #4d4a40→#7d7868 dark)
       + crs-tabs(var(--line)→var(--tabline)). WCAG 1.4.11.
  조니⑤ 15,117px·h2 0개 → sec-hd·박스 헤더 h2 시맨틱 전환 + 상단 빠른 점프(목차).
       앵커: 공연장 / 일정 / 코스(#stay-len 기존 id) / 숙소 / 티켓팅.

실행: python3 tools/wave2_course_patch.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARK = "WAVE2-COURSE-v1"

FILES = {
    "twice-thisisfor-seoul.html": "ko",
    "en/twice-thisisfor-seoul.html": "en",
}

# ── P1① crs-tabbar 클리핑 ──
CRS_OLD = (
    ".crs-tabbar{position:sticky;top:0;z-index:5;display:flex;gap:6px;"
    "overflow-x:auto;scrollbar-width:none;background:var(--card);"
    "padding:8px 0;margin:6px 0 2px}"
)
CRS_NEW = (
    ".crs-tabbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:6px;"
    "background:var(--card);padding:8px 0;margin:6px 0 2px}"
)

# ── P1③ 탭 테두리 ──
SL_LIGHT_OLD = "border:1px solid #ccc9bb"
SL_LIGHT_NEW = "border:1px solid var(--tabline,#807c6e)"
SL_DARK_OLD = ".sl-bar label{border-color:#4d4a40}"
SL_DARK_NEW = ".sl-bar label{border-color:var(--tabline,#7d7868)}"
CRS_BORDER_OLD = None  # 파일 내 .crs-tabs label 룰에서 var(--line) → var(--tabline)

CSS_BLOCK = (
    f"/* {MARK} */"
    ":root{--tabline:#807c6e}"
    "@media(prefers-color-scheme:dark){:root{--tabline:#7d7868}}"
    # P1① 모바일: 탭 유연폭 + 보조태그 축약 — 어떤 라벨 길이에서도 클리핑 0
    "@media(max-width:480px){"
    # white-space:normal — 라벨 상속 nowrap 이 wrap 차단(클리핑 9px 잔존 원인)
    ".crs-tabs .crs-tabbar label{flex:1 1 45%;min-width:0;white-space:normal;"
    "overflow-wrap:anywhere}"
    ".crs-tabs label .crs-tag{max-width:100%;white-space:nowrap;"
    "overflow:hidden;text-overflow:ellipsis}}"
    # 조니⑤ h2 시맨틱 — UA 기본 마진/크기 리셋(기존 시각 보존)
    "h2.sec-hd{font-size:14px;margin:0 0 8px}"
    # TOC 칩 + 앵커 스크롤 마진(sticky crs-tabbar 가림 방지)
    ".toc{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0 2px}"
    ".toc a{font-size:12.5px;font-weight:600;color:var(--muted);text-decoration:none;"
    "border:1px solid var(--tabline,#807c6e);border-radius:8px;padding:6px 12px;"
    "background:var(--card)}"
    ".toc a:hover{color:var(--accent);border-color:var(--accent)}"
    '[id^="sec-"],#stay-len{scroll-margin-top:74px}'
)

SEC_HD_RE = re.compile(r'<div class="sec-hd"([^>]*)>([^<]{2,80})</div>')
BOXHDR_RE = re.compile(
    r'<div style="font-weight:600;font-size:14px(;margin-top:1[24]px)?">([^<]{2,60})</div>'
)

# TOC 앵커 매핑: (id, 텍스트 판별 substring, TOC 라벨)
TOC_DEF = {
    "ko": [
        ("sec-venue", "공연장", "공연장"),
        ("sec-schedule", "공연 일정", "일정"),
        ("stay-len", None, "코스"),  # 기존 id
        ("sec-stays", "함께 묵는 숙소", "숙소"),
        ("sec-ticketing", "티켓팅", "티켓팅"),
    ],
    "en": [
        ("sec-venue", "Venue", "Venue"),
        ("sec-schedule", "Schedule", "Schedule"),
        ("stay-len", None, "Courses"),
        ("sec-stays", "Stays near", "Stays"),
        ("sec-ticketing", "Ticketing", "Ticketing"),
    ],
}
TOC_ARIA = {"ko": "바로가기", "en": "Quick jump"}


def to_h2(html, lang):
    """sec-hd·박스 헤더 div → h2 + TOC 앵커 id 부여. (변환 수, id 부여 목록) 반환."""
    toc = TOC_DEF[lang]
    assigned = set()

    def pick_id(text):
        for sid, key, _ in toc:
            if key and key in text and sid not in assigned:
                assigned.add(sid)
                return f' id="{sid}"'
        return ""

    n = 0

    def sec_hd(m):
        nonlocal n
        n += 1
        return f'<h2 class="sec-hd"{m.group(1)}{pick_id(m.group(2))}>{m.group(2)}</h2>'

    def boxhdr(m):
        nonlocal n
        n += 1
        mt = m.group(1) or ""
        style = f"font-weight:600;font-size:14px{mt};margin:{'14px' if mt else '0'} 0 0".replace(
            ";margin-top:14px;margin:14px 0 0", ";margin:14px 0 0"
        ).replace(";margin-top:12px;margin:14px 0 0", ";margin:12px 0 0")
        return f'<h2 style="{style}"{pick_id(m.group(2))}>{m.group(2)}</h2>'

    html = SEC_HD_RE.sub(sec_hd, html)
    html = BOXHDR_RE.sub(boxhdr, html)
    return html, n, assigned


def toc_nav(lang, assigned):
    links = "".join(
        f'<a href="#{sid}">{label}</a>'
        for sid, key, label in TOC_DEF[lang]
        if sid in assigned or key is None
    )
    return f'<nav class="toc" aria-label="{TOC_ARIA[lang]}">{links}</nav>\n'


def process(path, lang):
    f = DIST / path
    html = f.read_text(encoding="utf-8")
    if MARK in html:
        return f"{path}: SKIP (already)"
    stats = {}
    # P1① crs-tabbar
    if CRS_OLD not in html:
        return f"{path}: FAIL (crs-tabbar 패턴 미발견)"
    html = html.replace(CRS_OLD, CRS_NEW, 1)
    # P1③ 테두리
    stats["sl_border"] = html.count(SL_LIGHT_OLD)
    html = html.replace(SL_LIGHT_OLD, SL_LIGHT_NEW)
    if SL_DARK_OLD in html:
        html = html.replace(SL_DARK_OLD, SL_DARK_NEW, 1)
        stats["sl_dark"] = 1
    # .crs-tabs label 룰 내 var(--line) → var(--tabline)
    m = re.search(r"\.crs-tabs label\{[^}]*\}", html)
    if m and "border:1px solid var(--line)" in m.group(0):
        html = (
            html[: m.start()]
            + m.group(0).replace(
                "border:1px solid var(--line)",
                "border:1px solid var(--tabline,#807c6e)",
            )
            + html[m.end() :]
        )
        stats["crs_border"] = 1
    # 조니⑤ h2 + TOC
    html, stats["h2"], assigned = to_h2(html, lang)
    anchor = '<div class="box outlook">'
    if anchor in html:
        html = html.replace(anchor, toc_nav(lang, assigned) + anchor, 1)
        stats["toc"] = sorted(assigned)
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)
    f.write_text(html, encoding="utf-8")
    return f"{path}: OK {stats}"


def main():
    results = [process(p, lang) for p, lang in FILES.items()]
    for r in results:
        print(r)
    return 1 if any("FAIL" in r for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
