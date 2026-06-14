#!/usr/bin/env python3
"""WAVE4 (R27 2심 조니 확정) — 다크 전역 토큰화 + P1 일괄 sweep. 멱등 (마커 W4TOKENS-v1).

본질: raw hex 산재 → 색 토큰 + 다크 오버라이드 단일 레이어 (P0-4).
소스 생성기(메인 repo projects/byvias/site/generate.py)에 동일 토큰 레이어 포트 완료 —
본 sweep 은 generate.py 미포트 패치 레이어(GA4·Travelpayouts·share·stay22) 보존을 위해
라이브 dist 에 같은 레이어를 적용하는 브리지. 전면 재생성은 4 레이어 포트 후 (보고 참조).

포함 fix:
- P0-4: 토큰 주입 + raw hex→var() + corrupted dark inject 수리 (769 페이지) + dday-hot/stay22/
  showtbl/이니셜 칩 CR + 12px 플로어
- P1-6: hero keep-all + 티켓팅 D-DAY 오픈시각 표기 + 20:00 경과 문구 전환
- P1-7: en toc #sec-sources + 12px 플로어 + 빈 hero <p> + KIM JUNSU 그룹핑 + ecard 틴트 정책(임박만)
- 타치코마 P0 2건: 코스 Day3 '한눈에 보기' 버튼 무동작 + Day3 시간 라벨 세로 깨짐

모든 토큰 값 CR 검증: tools/cr_audit.py (텍스트>=4.5 / 비텍스트>=3, 라이트·다크 양 모드).
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
MARK = "/*W4TOKENS-v1*/"

LANG_DIRS = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

# ---------- 토큰 정의 (generate.py W4TOKENS-v1 와 동일 값 — SSOT 정합) ----------
TOKEN_BLOCK = (
    MARK
    + ":root{--accent-soft:#E6F1FB;--accent-line:#b9d2ef;--accent-bg:#185FA5;--on-accent:#fff;"
    "--ok:#0F6E56;--ok-soft:#E1F5EE;--warn:#A32D2D;--warn-soft:#FCEBEB;"
    "--purple:#6B3FA0;--purple-soft:#F0E9F9;--gold-soft:#fdf6ec;--gold-line:#f0e4cf;"
    "--surface-1:#fafaf7;--surface-2:#f7f6f1;--surface-acc:#f1f5fa;--surface-acc-line:#dbe6f2;"
    "--hoverline:#c9c7bd;--ehead-mid:#ffffff}"
    "@media(prefers-color-scheme:dark){:root{"
    "--ink:#ece9e0;--muted:#B3B0A5;--line:#34322c;--bg:#16150f;--card:#211f18;"
    "--accent:#8FBCEE;--accent-soft:#1A2A3E;--accent-line:#2f4a6a;--accent-bg:#2E6CB2;--on-accent:#fff;"
    "--ok:#7BD4B2;--ok-soft:#173228;--warn:#FF8A8A;--warn-soft:#3a1f1d;"
    "--purple:#C9A8F0;--purple-soft:#2A1F3D;--gold-soft:#2a2410;--gold-line:#4a3f20;"
    "--surface-1:#262420;--surface-2:#2a2820;--surface-acc:#1A2A3E;--surface-acc-line:#2f4a6a;"
    "--hoverline:#4a4840;--ehead-mid:#211f18;"
    "--urgent:#FF6B6B;--urgent-bg:#3a1f1d;--sun-chip-bg:#3a3320;--sun-chip-ink:#F2D58A}"
    "img{filter:brightness(.88)}}"
)

# ---------- 색 치환 테이블 (순서 의미 있음 — 구체 패턴 먼저) ----------
COLOR_MAP = [
    # 필 컨트롤 (흰 글자 유지 — 다크에선 --accent-bg 가 흰 글자 CR>=4.5 유지값으로 분리)
    (
        "color:#fff;background:var(--accent);border-color:var(--accent)",
        "color:var(--on-accent);background:var(--accent-bg);border-color:var(--accent-bg)",
    ),
    (
        "color:#fff;background:var(--accent)",
        "color:var(--on-accent);background:var(--accent-bg)",
    ),
    (
        "background:var(--accent);color:#fff",
        "background:var(--accent-bg);color:var(--on-accent)",
    ),
    (
        "background:#185FA5;color:#fff",
        "background:var(--accent-bg);color:var(--on-accent)",
    ),
    ("background:#185FA5", "background:var(--accent-bg)"),
    # dday-hot 긴급 변형: 흰글자→urgent 토너 (라이트 4.81 / 다크 5.43)
    (
        "dday-hot{background:var(--urgent)}",
        "dday-hot{background:var(--urgent-bg);color:var(--urgent)}",
    ),
    # 텍스트/보더 액센트
    ("color:#185FA5", "color:var(--accent)"),
    ("background:#E6F1FB", "background:var(--accent-soft)"),
    ("background:#e6f1fb", "background:var(--accent-soft)"),
    ("border:1px solid #b9d2ef", "border:1px solid var(--accent-line)"),
    ("border-color:#cfe0f2", "border-color:var(--accent-line)"),
    ("background:#eef4fb", "background:var(--accent-soft)"),
    # 경고 빨강 (rgb 표기 포함 — R27 2.33 사고)
    ("color:#A32D2D", "color:var(--warn)"),
    ("color:rgb(163,45,45)", "color:var(--warn)"),
    ("color:rgb(163, 45, 45)", "color:var(--warn)"),
    ("background:#FCEBEB", "background:var(--warn-soft)"),
    # 그린/퍼플 계열
    ("color:#0F6E56", "color:var(--ok)"),
    ("background:#E1F5EE", "background:var(--ok-soft)"),
    ("color:#6B3FA0", "color:var(--purple)"),
    ("background:#F0E9F9", "background:var(--purple-soft)"),
    # 골드 박스
    (
        "background:#fdf6ec;border:1px solid #f0e4cf",
        "background:var(--gold-soft);border:1px solid var(--gold-line)",
    ),
    # 중립 서피스 (다크 라이트 박스 잔존 봉쇄 — showtbl 헤더 포함)
    ("background:#f7f6f1", "background:var(--surface-2)"),
    ("background:#fafaf7", "background:var(--surface-1)"),
    ("background:#f3f1ea", "background:var(--surface-2)"),
    ("background:#f0eee6", "background:var(--surface-2)"),
    (
        "background:#f1f5fa;border:1px solid #dbe6f2",
        "background:var(--surface-acc);border:1px solid var(--surface-acc-line)",
    ),
    ("background:#f1f5fa", "background:var(--surface-acc)"),
]

# corrupted dark inject (세미콜론 누락 → 다크 --card 무효 = 769 페이지 다크 미지원 직접 원인)
CORRUPT = "--card:#211f18--ehead-mid:var(--card);"
CORRUPT_FIX = "--card:#211f18;--ehead-mid:#211f18;"

# ---------- V2: 실측 CR 위반 정밀 fix (cr_audit 1차 실행 218건 분석 결과) ----------
# 모든 교체 색은 WCAG 계산 검증 완료 (주석 = 측정 전/후)
FIXUPS_V2 = [
    # 라이트 muted 명도 강화 — 틴트 카드 위 .c/.subitem 3.27~3.93 → 6.2+ (vs --bg)
    ("--muted:#6b6a64", "--muted:#56554e"),
    ("--muted:#5f5e57", "--muted:#56554e"),  # v2 1차분 승급
    ("--muted:#9c998f", "--muted:#B3B0A5"),  # 다크 muted (기존 inject 포함 전역)
    # 틴트 알파 감쇠 0.10/0.26 → 0.08/0.16 — 틴트 위 텍스트 CR 회복 (정규식 별도 처리)
    # stay22 예약 CTA: 흰 글자 on #E84A7F 3.67 → #C73364 5.14 (수익 직결, R27 명시)
    ("background:#E84A7F;color:#fff", "background:#C73364;color:#fff"),
    # showday-jump fg #C7396B on #FCEAF1 4.30 → #AD2E5C 5.47
    (
        "color:#C7396B;text-decoration:none;background:#FCEAF1",
        "color:#AD2E5C;text-decoration:none;background:#FCEAF1",
    ),
    (
        ".showday-jump:hover{background:#F9DCE7;color:#E84A7F}",
        ".showday-jump:hover{background:#F9DCE7;color:#AD2E5C}",
    ),
    # ph-chip fg #9A5B2E on #FBEADD 4.21 → #8A5126 5.45
    ("color:#9A5B2E", "color:#8A5126"),
    # 종료 카드 이니셜 칩 opacity .7 → 제거 (grayscale 만으로 강등 유지, 칩 CR 3.22~4.26 → 4.5+)
    (".abadge{filter:grayscale(.85);opacity:.7}", ".abadge{filter:grayscale(.85)}"),
    # 코스 탭 crs-tag opacity 딤 제거 — 렌더 실측 4.38 본질 (가독 우선, 다크 제1원칙)
    (
        "color:var(--accent);margin-top:1px;opacity:.92",
        "color:var(--accent);margin-top:1px",
    ),
    (".crs-tag{color:#fff;opacity:.85}", ".crs-tag{color:#fff}"),
    # 코스 라이트 hero: 흰 글자 on 핑크 그라데이션 1.91~2.34 → 스크림 .62 합성 8.2 (실측 보정 2차)
    (
        "background:linear-gradient(135deg,var(--tw-apricot) 0%,var(--tw-magenta) 100%);color:#fff;",
        "background:linear-gradient(rgba(20,8,14,.62),rgba(20,8,14,.62)),"
        "linear-gradient(135deg,var(--tw-apricot) 0%,var(--tw-magenta) 100%);color:#fff;",
    ),
    # 스크림 .5 1차분 → .62 승급 (실측 hero-finale 4.31 보정)
    ("rgba(20,8,14,.5),rgba(20,8,14,.5)", "rgba(20,8,14,.62),rgba(20,8,14,.62)"),
    # 코스 hero 보조 텍스트 — 실측 잔존분 (V3)
    (
        "hero-dd-label{font-size:12px;font-weight:600;opacity:.92}",
        "hero-dd-label{font-size:12px;font-weight:600}",
    ),
    (
        "hero-dd-unit{font-size:13px;font-weight:600;opacity:.92}",
        "hero-dd-unit{font-size:13px;font-weight:600}",
    ),
    # hero-tour 라이트 다크플럼 #5A0F28 on 스크림 hero 2.12 → 라이트 핑크 (다크 변형과 동일 톤)
    (
        "color:#5A0F28;text-shadow:0 1px 1px rgba(255,255,255,.35)",
        "color:#FBD0E0;text-shadow:none",
    ),
    # hero-finale 라이트 흰 .2 칩 → 다크 .28 칩 (흰 글자 CR 9+)
    (
        "border-radius:8px;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.34)",
        "border-radius:8px;background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.34)",
    ),
    # hero-cta 핑크 필 (다크 변형 standalone) 3.67 → #C73364 5.14
    ("hero-cta{background:#E84A7F", "hero-cta{background:#C73364"),
    # 홈 hero eyebrow: 흰 .16 칩 over 사진 3.57 → 다크 칩 .72 (최악 흰 사진 가정에도 7.4)
    (
        ".eyebrow{background:rgba(255,255,255,.16);border-color:rgba(255,255,255,.28);color:#fff}",
        ".eyebrow{background:rgba(10,6,20,.72);border-color:rgba(255,255,255,.28);color:#fff}",
    ),
    # 코스 mb-cap 중복 주입 정리 (v2 초판 비멱등 잔재 — 3중 background → 1개)
    (
        "color:#fff;background:linear-gradient(transparent,rgba(0,0,0,.66) 60%);"
        "background:linear-gradient(transparent,rgba(0,0,0,.66) 60%);"
        "background:linear-gradient(transparent,rgba(0,0,0,.66) 60%);font-size:13px",
        "color:#fff;background:linear-gradient(transparent,rgba(0,0,0,.66) 60%);font-size:13px",
    ),
    # 코스 mb-cap: 사진 위 흰 캡션 text-shadow 단독 1.04 → 하단 스크림 추가 (멱등: 치환 후 패턴 소멸)
    (
        "color:#fff;font-size:13px;font-weight:600;line-height:1.4;text-shadow:0 1px 4px rgba(0,0,0,.55)}",
        "color:#fff;background:linear-gradient(transparent,rgba(0,0,0,.66) 60%);"
        "font-size:13px;font-weight:600;line-height:1.4;text-shadow:0 1px 4px rgba(0,0,0,.55)}",
    ),
]

TINT_LIGHT_RE = re.compile(r"rgba\((\d+),(\d+),(\d+),0\.10?\)( 0%)")
TINT_DEEP_RE = re.compile(r"rgba\((\d+),(\d+),(\d+),0\.26\)( 100%)")


def soften_tints(s):
    """응원색 틴트 알파 감쇠 — 그라데이션 위 muted 텍스트 CR 회복 (generate.py 동치 변경)."""
    s = TINT_LIGHT_RE.sub(r"rgba(\1,\2,\3,0.08)\4", s)
    s = TINT_DEEP_RE.sub(r"rgba(\1,\2,\3,0.16)\4", s)
    return s


PHCHIP_RE = re.compile(
    r"--ph-chip-bg:(#[0-9A-Fa-f]{6});--ph-chip-ink:(#[0-9A-Fa-f]{6})"
)


def _mix_white(h, frac):
    h = h.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return f"#{int(r + (255 - r) * frac):02x}{int(g + (255 - g) * frac):02x}{int(b + (255 - b) * frac):02x}"


def fix_phchips(s):
    """ph-chip 인라인 (bg, ink) 페어 — CR>=4.5 까지 잉크를 흑/백 방향 8% 단계 보정 (색조 보존)."""

    def rep(m):
        bg, ink = m.group(1), m.group(2)
        if _cr(ink, bg) >= 4.5:
            return m.group(0)
        light_bg = _lum(bg) > _lum(ink)
        for _ in range(12):
            ink = _mix_black(ink, 0.08) if light_bg else _mix_white(ink, 0.08)
            if _cr(ink, bg) >= 4.5:
                break
        return f"--ph-chip-bg:{bg};--ph-chip-ink:{ink}"

    return PHCHIP_RE.sub(rep, s)


FS_RE = re.compile(r"font-size:(\d+(?:\.\d+)?)px")


def _srgb(c):
    c /= 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _lum(h):
    h = h.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _srgb(r) + 0.7152 * _srgb(g) + 0.0722 * _srgb(b)


def _cr(a, b):
    la, lb = _lum(a), _lum(b)
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def _mix_black(h, frac):
    h = h.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    f = 1 - frac
    return f"#{int(r * f):02x}{int(g * f):02x}{int(b * f):02x}"


def badge_colors(bg):
    """이니셜 칩 (bg, fg) CR>=4.5 보장 — generate.py _badge_colors 와 동일 로직."""
    for _ in range(10):
        ink, wht = _cr("#1a1a18", bg), _cr("#ffffff", bg)
        if max(ink, wht) >= 4.5:
            return bg, ("#1a1a18" if ink >= wht else "#ffffff")
        bg = _mix_black(bg, 0.08)
    return bg, "#ffffff"


ABADGE_RE = re.compile(
    r'(class="abadge"[^>]*style=")background:(#[0-9A-Fa-f]{6});color:(#[0-9A-Fa-f]{6})'
)


def fix_abadge(s):
    def rep(m):
        bg, fg = badge_colors(m.group(2))
        return f"{m.group(1)}background:{bg};color:{fg}"

    return ABADGE_RE.sub(rep, s)


def floor_12px(s):
    """<style> 블록 + style 속성 내 font-size <12px → 12px (font-size:0 사용처 없음 — 사전 검증)."""

    def rep(m):
        v = float(m.group(1))
        return "font-size:12px" if 0 < v < 12 else m.group(0)

    return FS_RE.sub(rep, s)


def inject_tokens(s):
    """첫 <style> 닫는 태그 직전에 토큰 블록 주입 (멱등)."""
    if MARK in s:
        return s
    i = s.find("</style>")
    if i < 0:
        return s
    return s[:i] + TOKEN_BLOCK + s[i:]


# ---------- ecard 틴트 정책 (P1-7⑤ 의미 부여 — 임박 D-7 이내만 틴트) ----------
ECARD_RE = re.compile(
    r'(<a class="ecard"[^>]*?style="[^"]*?)background:linear-gradient\([^;"]*\);?([^"]*")'
)
DDATE_RE = re.compile(r'data-date="(\d{4})-(\d{2})-(\d{2})"')


def tint_policy(s):
    """인덱스 카드: 그라데이션 틴트 → 임박(D-7 이내)만 유지, 그 외 var(--card)."""
    today = date.today()
    out = []
    last = 0
    for m in re.finditer(r'<a class="ecard".*?</a>', s, re.S):
        card = m.group(0)
        dm = DDATE_RE.search(card)
        keep = False
        if dm:
            try:
                dd = (
                    date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))) - today
                ).days
                keep = 0 <= dd <= 7
            except ValueError:
                pass
        if not keep:
            card = ECARD_RE.sub(r"\1background:var(--card);\2", card)
        out.append(s[last : m.start()])
        out.append(card)
        last = m.end()
    out.append(s[last:])
    return "".join(out)


# ---------- KIM JUNSU 그룹핑 (P1-7④ — 동일 아티스트 4장+ → 1카드 + 도시 목록) ----------
TOUR_MORE = {
    "": "외 {n}개 도시 일정",
    "en": "+{n} more cities",
    "ja": "他{n}都市の日程",
    "zh-cn": "另外 {n} 个城市场次",
    "zh-tw": "另外 {n} 個城市場次",
    "es": "+{n} ciudades más",
    "th": "อีก {n} เมือง",
    "id": "+{n} kota lainnya",
    "pt": "+{n} cidades",
    "ar": "+{n} مدن أخرى",
    "vi": "+{n} thành phố khác",
}
GRP_CSS = (
    "/*W4GRP*/.ecard-grp{display:flex;flex-direction:column}.ecard-grp>.ecard{flex:1 1 auto}"
    ".tourgrp{margin-top:6px}.tourgrp>summary{list-style:none;cursor:pointer;font-size:12px;font-weight:600;"
    "color:var(--accent);background:var(--accent-soft);border-radius:8px;padding:8px 12px;min-height:36px;"
    "display:flex;align-items:center}.tourgrp>summary::-webkit-details-marker{display:none}"
    '.tourgrp>summary::after{content:"▾";margin-inline-start:auto;transition:transform .2s}'
    ".tourgrp[open]>summary::after{transform:rotate(180deg)}"
    ".tg-rows{display:flex;flex-direction:column;gap:4px;margin-top:6px}"
    ".tg-row{display:flex;align-items:center;gap:8px;text-decoration:none;color:var(--ink);"
    "background:var(--surface-1);border:1px solid var(--line);border-radius:8px;padding:7px 11px;font-size:13px}"
    ".tg-row:hover{border-color:var(--accent)}.tg-row .tg-d{color:var(--muted);margin-inline-start:auto}"
)
GROUP_MIN = 4


def group_artist_cards(s, lang_dir):
    """탭 패널 tp-c(콘서트) 그리드에서 동일 아티스트 GROUP_MIN+ 카드 → 그룹 1장."""
    if "/*W4GRP*/" not in s:
        i = s.find("</style>")
        if i < 0:
            return s
        s = s[:i] + GRP_CSS + s[i:]
    # 패널 경계: 카드 내부 중첩 div 로 non-greedy 조기 종료되므로 다음 tabpanel/문단까지로 한정
    start_m = re.search(r'<div class="tabpanel tp-c"><div class="grid">', s)
    if not start_m:
        return s
    g_start = start_m.end()
    nxt = s.find('class="tabpanel', g_start)
    if nxt < 0:
        nxt = s.find('<p class="disc', g_start)
    g_end = nxt if nxt > 0 else len(s)
    grid = s[g_start:g_end]
    # 닫는 </div></div> 이후 잔여 보존: 카드 외 텍스트는 그대로 유지 (카드만 치환)
    cards = re.findall(r'<a class="ecard".*?</a>', grid, re.S)
    if not cards:
        return s

    def artist_of(c):
        m = re.search(r'<div class="a">(.*?)</div>', c, re.S)
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else ""

    from collections import Counter

    counts = Counter(artist_of(c) for c in cards)
    label_t = TOUR_MORE.get(lang_dir, TOUR_MORE["en"])
    seen = set()
    out = []
    last = 0
    for m in re.finditer(r'<a class="ecard".*?</a>', grid, re.S):
        c = m.group(0)
        out.append(grid[last : m.start()])
        last = m.end()
        a = artist_of(c)
        if a and counts[a] >= GROUP_MIN:
            if a in seen:
                continue  # 그룹 흡수된 잔여 카드 제거
            seen.add(a)
            rest = [x for x in cards if artist_of(x) == a][1:]
            rows = []
            for x in rest:
                href = re.search(r'href="([^"]*)"', x)
                meta = re.search(r'<div class="c">(.*?)</div>', x, re.S)
                meta_txt = re.sub(r"<[^>]+>", "", meta.group(1)).strip() if meta else ""
                rows.append(
                    f'<a class="tg-row" href="{href.group(1) if href else "#"}">'
                    f"<span>{meta_txt}</span></a>"
                )
            out.append(
                f'<div class="ecard-grp">{c}'
                f'<details class="tourgrp"><summary>{label_t.replace("{n}", str(len(rest)))}</summary>'
                f'<div class="tg-rows">{"".join(rows)}</div></details></div>'
            )
        else:
            out.append(c)
    out.append(grid[last:])
    return s[:g_start] + "".join(out) + s[g_end:]


# ---------- 인덱스: hero keep-all + 빈 <p> + D-DAY 오픈시각/전환 ----------
OPEN_NOW = {
    "": "티켓팅 오픈 중",
    "en": "Ticketing open now",
    "ja": "チケット発売中",
    "zh-cn": "购票进行中",
    "zh-tw": "購票進行中",
    "es": "Venta de entradas abierta",
    "th": "เปิดจองบัตรแล้ว",
    "id": "Tiket sedang dijual",
    "pt": "Vendas abertas",
    "ar": "التذاكر متاحة الآن",
    "vi": "Đang mở bán vé",
}


def fix_index(s, lang_dir):
    # hero h1 단어 절단 (P1-6① '미리 싸/게' — CJK keep-all, 라틴 무영향)
    s = s.replace(
        ".hero h1{font-size:var(--fs-h1);line-height:1.25;margin:8px 0 4px}",
        ".hero h1{font-size:var(--fs-h1);line-height:1.25;margin:8px 0 4px;word-break:keep-all}",
    )
    # 티켓팅 D-DAY: TKO 항목에 오픈시각 t 주입 (소스: ticketing.draft.json general_sale 20:00 KST 검증)
    # + 20:00 경과 시 '오픈 중' 전환 (P1-6②)
    if '"e0"' in s and '"t"' not in s:
        s = re.sub(
            r'("e0": "[^"]*", "e1": "[^"]*")\}',
            r'\1, "t": "20:00", "e2": "'
            + OPEN_NOW.get(lang_dir, OPEN_NOW["en"])
            + '"}',
            s,
        )
    old_label = "esc(tkb.df===0?o.e0:o.e1)"
    new_label = (
        "esc(tkb.df===0?((o.t&&(new Date()).getHours()>=parseInt(o.t,10))?(o.e2||o.e0)"
        ":(o.e0+(o.t?' '+o.t:''))):o.e1)"
    )
    s = s.replace(old_label, new_label)
    return s


# ---------- 코스 페이지 (ko/en 신세대) — 타치코마 P0 2건 + en sec-sources ----------
SHOWDAY_JS = """<script>/*W4SHOWDAY*/(function(){document.addEventListener('click',function(ev){
var a=ev.target.closest&&ev.target.closest('a.showday-jump');if(!a)return;
var sel=a.getAttribute('href')||'';if(sel.charAt(0)!=='#')return;
var t=document.getElementById(sel.slice(1));if(!t)return;ev.preventDefault();
var sl=t.closest('.sl-panel');if(sl){var c=sl.className.match(/sl-\\d+/);if(c){var r=document.getElementById(c[0]);if(r&&r.type==='radio')r.checked=true;}}
var cp=t.closest('.crs-panel');if(cp){var m=cp.className.match(/cp-(\\d+)/);if(m){var r2=document.getElementById('crs-'+m[1]);if(r2&&r2.type==='radio')r2.checked=true;}}
var d=t.closest('details');while(d){d.open=true;d=d.parentElement&&d.parentElement.closest('details');}
requestAnimationFrame(function(){t.scrollIntoView({behavior:'smooth',block:'start'});});
});})();</script>"""


def fix_course(s, lang_dir):
    changed = False
    # ① sl-4 패널 자체 show 카드에 id 부여 + 그 패널 Day3 점프 retarget
    pm = re.search(
        r'<div class="sl-panel sl-4">.*?(?=<div class="sl-panel sl-7">|$)', s, re.S
    )
    if pm and 'id="showday-s4"' not in s:
        seg = pm.group(0)
        seg2 = seg.replace(
            'class="day-card day-card--show">',
            'class="day-card day-card--show" id="showday-s4">',
            1,
        )
        if seg2 == seg:
            seg2 = seg.replace(
                'class="day-card day-card--show"',
                'class="day-card day-card--show" id="showday-s4"',
                1,
            )
        seg2 = seg2.replace(
            'class="showday-jump" href="#showday-c0"',
            'class="showday-jump" href="#showday-s4"',
        )
        s = s[: pm.start()] + seg2 + s[pm.end() :]
        changed = True
    # sl-7 패널 점프 → sl-4 의 Day3 상세 카드 (동일 'Day 3 공연' 타임라인, JS 가 패널 전환)
    pm7 = re.search(r'<div class="sl-panel sl-7">.*', s, re.S)
    if pm7:
        seg = pm7.group(0)
        seg2 = seg.replace(
            'class="showday-jump" href="#showday-c0"',
            'class="showday-jump" href="#showday-s4"',
        )
        if seg2 != seg:
            s = s[: pm7.start()] + seg2 + s[pm7.end() :]
            changed = True
    # ①-b 죽은 빈 <p> 제거 (P1-7③): data-presale 빈 슬롯 — JS 가 채울 데이터 자체가 없음
    if '<p class="hero-presale" data-presale=""></p>' in s:
        s = s.replace('<p class="hero-presale" data-presale=""></p>', "", 1)
        changed = True
    # ② 점프 JS (숨은 탭 패널 라디오 전환 + details 오픈 + 스크롤) — 무동작 본질 봉쇄
    if "W4SHOWDAY" not in s and "showday-jump" in s:
        s = s.replace("</body>", SHOWDAY_JS + "</body>", 1)
        changed = True
    # ③ Day3 카드 시간 라벨 세로 깨짐: 체크박스 없는 lirow 가 30px 열에 lk 가 끼는 본질
    if "W4LKFIX" not in s and "day-card--show" in s:
        css = (
            "/*W4LKFIX*/.day-card--show .lirow:not(:has(.ckstep)){grid-template-columns:92px 1fr}"
            ".lirow .lk{word-break:keep-all}.lk .dur{white-space:nowrap}"
        )
        i = s.find("</style>")
        if i >= 0:
            s = s[:i] + css + s[i:]
            changed = True
    # ④ en: toc #sec-sources 깨진 앵커 — 실존 'Schedule source' 섹션에 id 부여 + toc 링크 복원
    if lang_dir == "en" and 'id="sec-sources"' not in s:
        # en 출처 박스 h2 가 본 일정 섹션과 중복 id="sec-schedule" 오기 — sec-sources 로 정정
        dup = '<h2 class="sec-hd" id="sec-schedule">Schedule source</h2>'
        if dup in s:
            s = s.replace(
                dup, '<h2 class="sec-hd" id="sec-sources">Schedule source</h2>', 1
            )
            changed = True
        m = re.search(r"<(h2|h3)([^>]*)>(\s*)(Schedule sources?|Sources)\b", s)
        if m and "id=" not in m.group(2):
            s = (
                s[: m.start()]
                + f'<{m.group(1)} id="sec-sources"{m.group(2)}>{m.group(3)}{m.group(4)}'
                + s[m.end() :]
            )
            changed = True
    if lang_dir == "en" and 'id="sec-sources"' in s and 'href="#sec-sources"' not in s:
        # 1차 sweep 이 제거했던 toc 링크 복원 (#sec-stays 링크 직후)
        anchor = '<a href="#sec-stays">Stays near the venue</a>'
        if anchor in s:
            s = s.replace(
                anchor, anchor + '<a href="#sec-sources">Schedule source</a>', 1
            )
            changed = True
    # ⑤ en 안전 항목 패리티 (대표 catch 2026-06-11 12:23) — ko ①→⑤ 의 안전 3종을
    # 'Book in the right order' 흐름에 비-아필리에이트 행으로 추가. 수치·시각은 본 페이지
    # 기존 검증 콘텐츠(showtbl 19:00/18:00/17:00 · last-train 22:55) verbatim — 신규 주장 0.
    if lang_dir == "en" and "W4SAFETY" not in s and "Book in the right order" in s:
        safety = (
            "<!--W4SAFETY-->"
            '<a class="prep-row" href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">'
            '<span class="prep-ico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M12 2l8 4v6c0 5-8 10-8 10S4 17 4 12V6z"/></svg></span>'
            '<span class="prep-main"><span class="prep-name">K-ETA / visa check</span>'
            '<span class="prep-sub">Visa-waiver nationals (US·Canada·EU…) may need K-ETA — rules change often. Confirm for your nationality at the official site</span></span>'
            '<span class="prep-when">Before you fly</span></a>'
            '<a class="prep-row" href="#sec-schedule">'
            '<span class="prep-ico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h6"/></svg></span>'
            '<span class="prep-main"><span class="prep-name">Show day — bring your physical passport</span>'
            '<span class="prep-sub">ID checks at entry — arrive early. MD sales in the morning. Shows: Fri 19:00 · Sat 18:00 · Sun 17:00</span></span>'
            '<span class="prep-when">Show day</span></a>'
            '<a class="prep-row" href="#last-train">'
            '<span class="prep-ico"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><rect x="4" y="3" width="16" height="13" rx="2"/><path d="M4 11h16M8 19l-2 2M16 19l2 2"/></svg></span>'
            '<span class="prep-main"><span class="prep-name">After the show — last trains</span>'
            '<span class="prep-sub">All 3 nights have margin, except Line 9 westbound (Gaehwa) ~22:55 on Sat·Sun. Line-by-line table →</span></span>'
            '<span class="prep-when">After the show</span></a>'
        )
        i = s.find("Book in the right order")
        m = None
        for m in re.finditer(r'<a class="prep-row".*?</a>', s[i:], re.S):
            pass  # 마지막 prep-row 탐색
        if m:
            ins = i + m.end()
            s = s[:ins] + safety + s[ins:]
            changed = True
    # ⑥ en TWICE Seoul 위치 패리티 (대표 catch 2026-06-12) — Local practical info + Safety가
    # ko처럼 최하단 알림 직전에 보여야 함. 기존 en은 sec-sources 앞에 있어 하단 화면에서 안전 영역이 누락됨.
    if (
        lang_dir == "en"
        and "W4SAFETYMOVE" not in s
        and "TWICE THIS IS FOR" in s
        and "world.nol.com/en/ticket/places/26000627/products/26007949" in s
    ):
        start_marker = '<div class="box linfo-box">\n  <div style="font-weight:600;font-size:14px;margin-bottom:6px">🧭 Local travel essentials</div>'
        end_marker = '\n<div class="box srcbox">'
        target_marker = '<div class="news-soon">'
        start = s.find(start_marker)
        end = s.find(end_marker, start)
        target = s.find(target_marker)
        if start >= 0 and end > start and target >= 0 and start < target:
            block = "<!--W4SAFETYMOVE-->\n" + s[start:end].strip() + "\n"
            s = s[:start] + s[end:]
            s = s.replace(target_marker, block + target_marker, 1)
            changed = True
    return s, changed


def process(path, lang_dir, is_index, is_course):
    s0 = path.read_text(encoding="utf-8")
    s = s0
    s = s.replace(CORRUPT, CORRUPT_FIX)
    s = inject_tokens(s)
    for a, b in COLOR_MAP:
        s = s.replace(a, b)
    s = fix_abadge(s)
    s = floor_12px(s)
    for a, b in FIXUPS_V2:
        s = s.replace(a, b)
    s = soften_tints(s)
    s = fix_phchips(s)
    if is_index:
        s = fix_index(s, lang_dir)
        s = tint_policy(s)
        s = group_artist_cards(s, lang_dir)
    if is_course:
        s, _ = fix_course(s, lang_dir)
    if s != s0:
        path.write_text(s, encoding="utf-8")
        return True
    return False


def main():
    changed = 0
    total = 0
    for ld in LANG_DIRS:
        d = DIST / ld if ld else DIST
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.html")):
            total += 1
            is_index = f.name == "index.html"
            is_course = f.name.startswith("twice-thisisfor-seoul")
            if process(f, ld, is_index, is_course):
                changed += 1
    print(f"wave4 sweep: {changed}/{total} files changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
