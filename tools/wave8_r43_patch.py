#!/usr/bin/env python3
"""WAVE8 — R43 2심 조니 확정 fix (idempotent dist patch, 11 locales).

P0-1 점프 동선 A": 4박/7박 점프를 2박3일과 동일 44px 칩으로 통일
     (W6COURSE underline override 제거) + Codex wave7 터치 실개선분 흡수.
P1③ 터치 잔존 — 히트영역 44px (시각 불변: 숨김 radio 44, ckstep ::before 히트확장).
P1④ radius 토큰 3종 통일 (--r-s:8 / --r-m:12 / --r-pill:999, 50%·0은 자연값 유지).
P1⑤ 폴백 모노그램 색·이니셜 변주 (hike/show 카테고리 색 신설 + data-ph-var 3주기
     + ph-init 고스트 이니셜 표시. 실이미지 카드는 변주 비활성 — 가짜 이미지 생성 0).
P1⑥ 면책성 문구 6건 → 인트로 1건 통합 (가격·잔량 + 제휴 + 인스타 저작권).
P1⑦ 공연일 점프 above-the-fold — hero CTA 옆 ghost 칩 (#showday-c0, W4SHOWDAY JS
     가 패널 radio 자동 해소).

코스 리치 페이지는 ko(root)·en 2개 locale에만 존재(9 locale은 경량 이벤트 페이지 —
코스 섹션 자체 부재). 홈 터치 CSS(W8R43H)는 11 locale 전량 적용.
검증: tools/locale_parity_gate.py 11/11.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

LOCALES = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

COURSE = "twice-thisisfor-seoul.html"
HOME = "index.html"

# ---------------------------------------------------------------- P0-1 ----
# W6COURSE underline override 제거 → s4/s7 점프가 base 칩(44px rose chip)으로 통일.
W6_CSS_UNIFIED = (
    "/*W6COURSE*/.showday-jump{min-height:44px;box-sizing:border-box;max-width:100%}"
)
W6_RE = re.compile(
    r"/\*W6COURSE\*/\.showday-jump\{.*?\}"
    r"(?:\.showday-jump\[data-w6-course-jump=[^{]*\{.*?\})?"
    r"(?:\.showday-jump\[data-w6-course-jump=[^{]*\] svg\{display:none\})?"
    r"(?:\.showday-jump\[data-w6-course-jump=[^{]*\]:hover\{.*?\})?"
)

# Codex wave7 터치 실개선분 흡수 (ota-btn 등 — 문자열 치환, 미적용 시 no-op).
WAVE7_REPLACEMENTS = [
    (
        ".jump-nav a{display:inline-flex;align-items:center;gap:5px;font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;padding:7px 12px;min-height:36px;border:1px solid var(--line);border-radius:999px;background:var(--card)}",
        ".jump-nav a{display:inline-flex;align-items:center;gap:5px;font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;padding:9px 12px;min-height:44px;box-sizing:border-box;border:1px solid var(--line);border-radius:999px;background:var(--card)}",
    ),
    (
        ".ota-btn{display:inline-flex;align-items:center;min-height:36px;color:#C7396B;font-size:12px;font-weight:600;text-decoration:none}",
        ".ota-btn{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;color:#C7396B;font-size:12px;font-weight:600;text-decoration:none}",
    ),
    (
        ".steps5 .s5-go{display:inline-flex;align-items:center;min-height:32px;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none}",
        ".steps5 .s5-go{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none}",
    ),
    (
        ".langbar .lng{display:inline-flex;align-items:center;min-height:36px;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:8px}",
        ".langbar .lng{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:8px}",
    ),
    (
        ".langpick>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:6px 12px;border:1px solid var(--line);border-radius:8px;font-size:12px;font-weight:600;color:var(--muted);background:var(--card)}",
        ".langpick>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;min-height:44px;box-sizing:border-box;padding:6px 12px;border:1px solid var(--line);border-radius:8px;font-size:12px;font-weight:600;color:var(--muted);background:var(--card);min-width:140px;white-space:nowrap}",
    ),
    (
        ".langpick .langmenu .lng{display:flex;align-items:center;min-height:40px;padding:8px 12px;border-radius:6px;font-size:13px;color:var(--muted);text-decoration:none}",
        ".langpick .langmenu .lng{display:flex;align-items:center;min-height:44px;box-sizing:border-box;padding:8px 12px;border-radius:6px;font-size:13px;color:var(--muted);text-decoration:none}",
    ),
    (
        ".showday-jump{display:inline-flex;align-items:center;gap:6px;min-height:40px;margin:4px 0 8px;padding:6px 12px;font-size:13px;font-weight:600;color:#AD2E5C;text-decoration:none;background:var(--rose-soft);border:1px solid #F3B6CC;border-radius:10px}",
        ".showday-jump{display:inline-flex;align-items:center;gap:6px;min-height:44px;box-sizing:border-box;margin:4px 0 8px;padding:6px 12px;font-size:13px;font-weight:600;color:#AD2E5C;text-decoration:none;background:var(--rose-soft);border:1px solid #F3B6CC;border-radius:10px}",
    ),
    (
        ".stay-iglink{align-self:flex-start;font-size:12px;color:var(--muted);text-decoration:none;font-weight:500;min-height:36px;display:inline-flex;align-items:center;gap:5px;margin-top:0}",
        ".stay-iglink{align-self:flex-start;font-size:12px;color:var(--muted);text-decoration:none;font-weight:500;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center;gap:5px;margin-top:0}",
    ),
    (
        "display:inline-flex;align-items:center;min-height:32px;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none",
        "display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none",
    ),
    (
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:6px 10px;'",
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'",
    ),
    (
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'\n  +'border:1px solid var(--line);border-radius:999px;background:transparent;min-height:32px;display:inline-flex;align-items:center;white-space:nowrap}'",
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'\n  +'border:1px solid var(--line);border-radius:999px;background:transparent;display:inline-flex;align-items:center;white-space:nowrap}'",
    ),
    (
        "+'.affbar-x{flex:0 0 auto;border:0;background:transparent;color:var(--muted);font-size:18px;line-height:1;padding:4px 6px;cursor:pointer}';",
        "+'.affbar-x{flex:0 0 auto;border:0;background:transparent;color:var(--muted);font-size:18px;line-height:1;min-width:44px;min-height:44px;padding:0;cursor:pointer}';",
    ),
]

# ---------------------------------------------------------------- P1④ ----
# radius 토큰 통일 — 긴 값 먼저 (16px 후 6px 등 부분일치 방지). var()는 재실행 무변.
RADIUS_MAP = [
    ("border-radius:999px", "border-radius:var(--r-pill)"),
    ("border-radius:16px", "border-radius:var(--r-m)"),
    ("border-radius:14px", "border-radius:var(--r-m)"),
    ("border-radius:12px", "border-radius:var(--r-m)"),
    ("border-radius:10px", "border-radius:var(--r-m)"),
    ("border-radius:8px", "border-radius:var(--r-s)"),
    ("border-radius:7px", "border-radius:var(--r-s)"),
    ("border-radius:6px", "border-radius:var(--r-s)"),
    ("border-radius:4px", "border-radius:var(--r-s)"),
    (
        "border-radius:2px",
        "border-radius:var(--r-pill)",
    ),  # 3px 폭 장식 tick — 클램프로 시각 동등
]

# ---------------------------------------------------------------- CSS ----
W8_COURSE_CSS = (
    "/*W8R43C*/"
    ":root{--r-s:8px;--r-m:12px;--r-pill:999px}"
    # ③ 터치 — 시각 불변 히트영역 (숨김 radio 44 / ckstep ::before 44 확장)
    'input[name="crs"],input[name="stay-len"]{width:44px;height:44px}'
    ".iglink,.back,.srclink,.maplink{min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center}"
    ".chchip{min-height:44px;box-sizing:border-box}"
    ".toc a{min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center}"
    ".oshow{min-height:44px;box-sizing:border-box}"
    "summary,.langpick>summary{min-height:44px;box-sizing:border-box}"
    '.ckstep::before{content:"";position:absolute;left:50%;top:50%;width:44px;height:44px;transform:translate(-50%,-50%)}'
    # ⑤ 폴백 모노그램 — 누락 카테고리 색 신설 + 고스트 이니셜 + 3주기 변주
    '.place-ph[data-cat="hike"]{--ph-band:linear-gradient(90deg,#9BBF8E,#C9DEC0);--ph-chip-bg:#E4F0DC;--ph-chip-ink:#41663B}'
    '.place-ph[data-cat="show"]{--ph-band:linear-gradient(90deg,#B66AC0,#8E4E9A);--ph-chip-bg:#F2E4F4;--ph-chip-ink:#6E3A78}'
    ".place-ph .ph-init{display:block;position:absolute;right:12px;top:calc(50% + 4px);transform:translateY(-50%);"
    "font-size:18px;font-weight:800;line-height:1;color:var(--ph-chip-ink,var(--muted));opacity:.4;pointer-events:none;user-select:none}"
    ".place-ph:has(img) .ph-init{display:none}"
    '.place-ph[data-ph-var="1"]::before{filter:hue-rotate(10deg) saturate(1.12)}'
    '.place-ph[data-ph-var="2"]::before{filter:hue-rotate(-12deg) brightness(1.04)}'
    '.place-ph[data-ph-var="1"] .ph-init{opacity:.5}'
    '.place-ph[data-ph-var="2"] .ph-init{opacity:.3}'
    "@media (prefers-color-scheme:dark){"
    '.place-ph[data-cat="hike"]{--ph-band:linear-gradient(90deg,#6E9462,#4E7444);--ph-chip-bg:#1E2C1A;--ph-chip-ink:#B8DCB0}'
    '.place-ph[data-cat="show"]{--ph-band:linear-gradient(90deg,#A05CAC,#7A4084);--ph-chip-bg:#2C1E30;--ph-chip-ink:#DCB8E4}'
    "}"
    # ⑦ above-the-fold 공연일 점프 — hero ghost 칩 (base .showday-jump 위에 hero 톤)
    ".hero-jump{margin:12px 0 0 10px;background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.55);"
    "color:#fff;backdrop-filter:blur(2px)}"
    ".hero-jump:hover{background:rgba(255,255,255,.26);color:#fff}"
    "@media (max-width:480px){.hero-jump{margin-left:0}}"
)

W8_HOME_CSS = (
    "/*W8R43H*/"
    # .linfo>summary 등 기존 룰과 동일 특이성 + 후순위 배치로 override
    ".linfo>summary,.langpick>summary,.tourgrp>summary,details summary{min-height:44px;box-sizing:border-box}"
    ".hf-chip{min-height:44px}"
    ".tg-row{min-height:44px;box-sizing:border-box}"
    ".tabs>input{width:44px;height:44px}"
)

# ---------------------------------------------------------------- P1⑥ ----
DISC_MERGED = {
    "": (
        "가격·잔량 전망은 추정이며 실제와 다를 수 있습니다. 예약·결제 책임은 이용자 본인에게 있습니다. "
        "본 페이지의 예약 링크는 제휴(수수료) 링크이며, 이용자가 추가로 부담하는 비용은 없습니다. "
        "인스타그램 게시물은 에디터가 직접 고른 공개 게시물로, 저작권은 각 게시자에게 있으며 "
        "원본이 삭제·비공개되면 표시되지 않을 수 있습니다."
    ),
    "en": (
        "Price and availability forecasts are estimated and may differ from actual. "
        "You are solely responsible for booking and payment. "
        "Booking links on this page are affiliate (commission) links — no additional cost to you. "
        "Instagram posts are public posts hand-picked by our editor; copyright belongs to each poster, "
        "and if the original is deleted or set private it may not display."
    ),
}

JUMP_LABEL = {"": "공연일 일정 바로가기 →", "en": "Jump to show day →"}

CAL_SVG = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" aria-hidden="true"><path d="M8 2v4M16 2v4M3 9h18M5 5h14a1 1 0 0 1 1 1v14'
    'a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1z"/></svg>'
)


def _append_css(s: str, block: str, marker: str) -> str:
    if marker in s:
        return s
    return s.replace("</style>", block + "</style>", 1)


def _consolidate_disc(s: str, lang: str) -> str:
    """⑥ 면책성 문구 6건 → 인트로 1건 통합 (idempotent: data-w8-disc 마커)."""
    if 'data-w8-disc="1"' not in s:
        m = re.search(r'<p class="disc">(.*?)</p>', s, re.S)
        if m:
            s = (
                s[: m.start()]
                + f'<p class="disc" data-w8-disc="1">{DISC_MERGED[lang]}</p>'
                + s[m.end() :]
            )
    s = re.sub(r'\s*<p class="ig-disc"[^>]*>.*?</p>', "", s, flags=re.S)
    s = re.sub(r'\s*<p class="disc disc-aff"[^>]*>.*?</p>', "", s, flags=re.S)
    return s


def _insert_fold_jump(s: str, lang: str) -> str:
    """⑦ hero CTA 직후 공연일 점프 칩 (idempotent: data-w8-fold 마커)."""
    if 'data-w8-fold="1"' in s:
        return s
    m = re.search(r'(<a class="hero-cta"[^>]*>.*?</a>)', s, re.S)
    if not m:
        return s
    chip = (
        f'<a class="showday-jump hero-jump" data-w8-fold="1" href="#showday-c0">'
        f"{CAL_SVG}{JUMP_LABEL[lang]}</a>"
    )
    return s[: m.end(1)] + chip + s[m.end(1) :]


def _vary_placeholders(s: str) -> str:
    """⑤ place-ph data-ph-var 3주기 재부여 + 누락 ph-init 삽입 (결정적·idempotent)."""
    s = re.sub(r' data-ph-var="\d"', "", s)  # 재부여 전 초기화 → 결정적
    out, pos, idx = [], 0, 0
    pat = re.compile(r'<div class="place-ph"[^>]*>')
    for m in pat.finditer(s):
        tag = m.group(0)
        var = idx % 3
        idx += 1
        if var:
            tag = tag.replace(
                '<div class="place-ph"', f'<div class="place-ph" data-ph-var="{var}"', 1
            )
        out.append(s[pos : m.start()] + tag)
        pos = m.end()
        # 누락 ph-init 삽입 — 실이미지(<img) 카드는 제외 (place-ph 비-img 내부는 div 미중첩)
        end = s.find("</div>", pos)
        inner = s[pos:end]
        if "ph-init" not in inner and "<img" not in inner:
            label = re.search(r'aria-label="([^"]+)"', m.group(0))
            if label:
                init = label.group(1).strip()[:1].upper()
                out.append(
                    inner + f'<span class="ph-init" aria-hidden="true">{init}</span>'
                )
                pos = end
    out.append(s[pos:])
    return "".join(out)


def patch_course(s: str, lang: str) -> str:
    if '<div class="sl-panel sl-4">' not in s:
        return s  # 경량 페이지(코스 섹션 부재) — 대상 아님
    s = W6_RE.sub(W6_CSS_UNIFIED, s, count=1)  # P0-1 칩 통일
    # P0-1 라벨 동형 — s4/s7 칩 라벨을 2박3일 칩 워딩에 정렬 (재실행 no-op)
    s = re.sub(
        r'(<a class="showday-jump" data-w6-course-jump="1"[^>]*>(?:<svg.*?</svg>)?)공연일로 이동 →',
        r"\g<1>공연 당일 한눈에 보기 →",
        s,
        flags=re.S,
    )
    s = re.sub(
        r'(<a class="showday-jump" data-w6-course-jump="1"[^>]*>(?:<svg.*?</svg>)?)Jump to show day →',
        r"\g<1>Show day at a glance →",
        s,
        flags=re.S,
    )
    for old, new in WAVE7_REPLACEMENTS:  # wave7 터치 실개선분 흡수
        s = s.replace(old, new)
    for old, new in RADIUS_MAP:  # ④ 토큰 통일
        s = s.replace(old, new)
    # ③ 버튼형 inline-style 앵커 (WOWPASS) 44px — 본문 인라인 링크는 WCAG 2.5.8 예외로 잔존
    s = s.replace(
        'style="display:inline-block;padding:8px 14px;background:var(--accent-bg)',
        'style="display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:8px 14px;background:var(--accent-bg)',
    )
    s = _append_css(s, W8_COURSE_CSS, "W8R43C")
    s = _consolidate_disc(s, lang)  # ⑥
    s = _insert_fold_jump(s, lang)  # ⑦
    s = _vary_placeholders(s)  # ⑤
    return s


def patch_home(s: str) -> str:
    s = _append_css(s, W8_HOME_CSS, "W8R43H")
    # 아카이브 summary 인라인 min-height:36px → 44px (인라인이 CSS보다 우선이므로 직접 치환)
    s = s.replace(
        "cursor:pointer;font-size:13px;font-weight:600;color:var(--muted);min-height:36px;display:flex;align-items:center",
        "cursor:pointer;font-size:13px;font-weight:600;color:var(--muted);min-height:44px;display:flex;align-items:center",
    )
    return s


def main() -> None:
    for loc in LOCALES:
        base = DIST / loc if loc else DIST
        for name in (COURSE, HOME):
            p = base / name
            if not p.exists():
                print(f"  MISSING {p.relative_to(ROOT)}")
                continue
            s = p.read_text(encoding="utf-8")
            if name == COURSE:
                new = patch_course(s, "en" if loc == "en" else "")
            else:
                new = patch_home(s)
            if new != s:
                p.write_text(new, encoding="utf-8")
                print(f"  patched {p.relative_to(ROOT)}")
            else:
                print(f"  unchanged {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
