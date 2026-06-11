#!/usr/bin/env python3
"""WAVE5 (R28 2심 조니 확정) — 다크 라이트박스 봉쇄 + 컴포넌트 bg 토큰 강제 + P1 6종. 멱등 (마커 W5-v1).

본질: R27 W4 토큰화 이후에도 컴포넌트 bg raw hex 잔존 (day-note·ytfacade·step-img 외)
→ "단발 패치만 하고 끝내면 R29에서 5라운드째" (조니 verbatim) — 잔존 컴포넌트 bg 전수 토큰화.

포함 fix:
- P0-1: 다크 라이트박스 3셀렉터 (.day-note #FEF3F2 / .ytfacade UA 기본 bg / .step-img #ece9e0)
  + 컴포넌트 bg 하드코딩 전수 토큰화 (rose 계열 신규 토큰 + 기존 warn/surface 토큰 정합)
- P0-2: 다크 임박 틴트 — 인라인 rgba 알파 고정 → --tr 채널 + --ta1/--ta2 알파 토큰
  (라이트 .08/.16 유지, 다크 .26/.42 신설 — 정보 손실 0)
- P1-①: 체류일 상태 보존 — sl-7→showday-s4 점프 시 이전 선택 기록 + 명시 복귀 칩 (무언 전환 금지)
- P1-②: prep-name <small> 11.67px → 13px
- P1-③: en 코스 탭 crs-tag 11.2px 어긋남 — 탭 컬럼 정렬 + tag 하단 고정 (양 탭 동일 y)
- P1-④: 홈 카드 이니셜 폴백 전 카드 적용 (abadge 누락 24장 주입, CR>=4.5 보정)
- P1-⑤: 종료 후 180일+ 이벤트 (2024 aespa·NewJeans) → 하단 아카이브 details 이동
- P1-⑥: 코스 히어로 공연 정보 칩(hero-finale) ↔ D-day pill(hero-cd) 높이·수직 중심·radius 통일
- 템플릿①: 2박3일(sl-2) 히어로 사진 제거 ②: 4박5일·7박8일 intro '잠실 베이스 기준' 1줄
  ③: 'day 3일 이하 flat / 4일+ 아코디언' 임계 룰 — sl-4 아코디언 전환 + 룰 주석 박제
- 제거: 헤더 자기 주소 라벨 <span>bybias.100m1s.com</span> / hf-count 빈 <p> → <div> (aria-live)
- P2: '이번 주 임박'(실 윈도우 14일) → '다가오는 14일' 정직 표기 11개 언어 / 음방 카드 임박 틴트

소스 정합: 메인 repo projects/bybias/site/generate.py 에 동치 변경 포트
(topbar span 제거 / ytfacade bg / card_visual --tr 토큰 / 아카이브 분리). 코스 페이지(ko·en)는
generate.py 비관리 — 본 sweep 이 단일 레이어.

검증: tools/cr_audit.py + tools/parity_audit.py + 컴포넌트 bg grep + 멱등 2회 diff 0.
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
MARK = "/*W5-v1*/"
ARCHIVE_DAYS = 180  # 종료 후 180일+ → 아카이브 (2024 사례 일반화)

LANG_DIRS = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

# ---------- W5 토큰 (generate.py W5 포트와 동일 값 — SSOT 정합) ----------
# rose 계열: 코스 핑크 컴포넌트 (라이트 raw hex + 다크 산발 오버라이드 → 단일 토큰 레이어).
# 다크 값은 기존 다크 오버라이드 실측값 승계 (정보 손실 0). --ta1/--ta2: 임박 틴트 알파 채널.
TOKEN_BLOCK = (
    MARK + ":root{--rose:#E84A7F;--rose-cta:#C73364;--rose-deep:#B32E5C;"
    "--rose-badge:#C8295F;--rose-soft:#FCEAF1;--rose-hov:#F9DCE7;"
    "--rose-ink:#A32B5A;--rose-line:#F6CBDC;--ta1:.08;--ta2:.16}"
    "@media(prefers-color-scheme:dark){:root{"
    "--rose-soft:#2E1620;--rose-hov:#3A1622;--rose-ink:#F6B8CF;--rose-line:#4A2233;"
    "--ta1:.26;--ta2:.42}}"
)

# ---------- 단순 치환 (전 페이지) — 치환 후 원 패턴 소멸 = 멱등 ----------
REPLACES = [
    # 제거①: 헤더 자기 주소 라벨 (전 페이지 topbar)
    ("<span>bybias.100m1s.com</span>", ""),
    # P0-1 .day-note / 인덱스 .wait-note: 라이트 적색 노트 → warn 토큰 (다크 자동)
    (
        "color:#B42318;background:#FEF3F2",
        "color:var(--warn);background:var(--warn-soft)",
    ),
    # P0-1 .step-img / .stay-card .simg / .spot-card .pimg 이미지 플레이스홀더
    ("background:#ece9e0", "background:var(--surface-2)"),
    # ytfacade hover play — generate.py L214 와 동일 토큰 (소스 정합)
    (
        ".ytfacade:hover .ytplay{background:#A32D2D}",
        ".ytfacade:hover .ytplay{background:var(--warn)}",
    ),
    # 코스 tk-badge: soon 라이트 핑크 → warn-soft / today 솔리드 → rose-badge
    (
        "tk-badge--soon{color:var(--warn);background:#FBE3E3}",
        "tk-badge--soon{color:var(--warn);background:var(--warn-soft)}",
    ),
    (
        "tk-badge--today{color:#fff;background:#C8295F",
        "tk-badge--today{color:#fff;background:var(--rose-badge)",
    ),
    # 코스 wait-note (핑크 변형) — rose 토큰 3종
    (
        "color:#A32B5A;background:#FCEAF1;border:1px solid #F6CBDC",
        "color:var(--rose-ink);background:var(--rose-soft);border:1px solid var(--rose-line)",
    ),
    # 코스 wait-note 다크 오버라이드 — 토큰 캐스케이드로 대체 (값 동일 승계, 룰 제거)
    (".wait-note{color:#F6B8CF;background:#2E1620;border-color:#4A2233}", ""),
    # showday-jump 라이트 + hover → rose 토큰
    (
        "text-decoration:none;background:#FCEAF1",
        "text-decoration:none;background:var(--rose-soft)",
    ),
    (
        ".showday-jump:hover{background:#F9DCE7;color:#AD2E5C}",
        ".showday-jump:hover{background:var(--rose-hov);color:#AD2E5C}",
    ),
    # showday-jump 다크 오버라이드 bg → 토큰 캐스케이드 (#2A1019→#2E1620 동계 플럼 승계, fg 유지)
    (
        ".showday-jump{color:#F6B8CF;background:#2A1019;border-color:#4A2233}",
        ".showday-jump{color:#F6B8CF;border-color:var(--rose-line)}",
    ),
    (
        ".showday-jump:hover{background:#3A1622;color:#FBD0E0}",
        ".showday-jump:hover{color:#FBD0E0}",
    ),
    # ckstep 체크 핑크 (UI 컨트롤, 비텍스트 CR>=3)
    ("ckstep:checked{background:#E84A7F", "ckstep:checked{background:var(--rose)"),
    (
        ".ckstep:checked{border-color:#E84A7F;background:#E84A7F",
        ".ckstep:checked{border-color:var(--rose);background:var(--rose)",
    ),
    # stay22 / hero CTA 솔리드 핑크 (흰 글자 CR 5.14 — W4 검증값 유지)
    ("background:#C73364;color:#fff", "background:var(--rose-cta);color:#fff"),
    ("hero-cta{background:#C73364", "hero-cta{background:var(--rose-cta)"),
    ("background:#B32E5C", "background:var(--rose-deep)"),
    # outlook 다크 오버라이드 — gold 토큰 캐스케이드 대체 (#241d10≈#2a2410 승계, 룰 제거)
    (".outlook{background:#241d10;border-color:#4a3d1f}", ""),
    # P0-2 본질: W2-era 다크 ecard 틴트 전면 봉쇄(!important) 해제 — sheen 원인이던 라이트 mid 는
    # --ehead-mid 다크 토큰(#211f18)으로 이미 해소, 틴트는 --ta1/--ta2 다크 알파(.26/.42)로 복원
    (
        "@media(prefers-color-scheme:dark){.ecard{background:var(--card)!important}.ecard:hover{border-color:#4a4840}}",
        "@media(prefers-color-scheme:dark){.ecard:hover{border-color:var(--hoverline)}}",
    ),
    # 제거②: hf-count 빈 <p> → <div> (aria-live 컨테이너 — 단락 의미 제거)
    (
        '<p class="hf-count" id="hf-count" aria-live="polite"></p>',
        '<div class="hf-count" id="hf-count" aria-live="polite"></div>',
    ),
]

# 정규식 치환: srcbox/maplink 라이트 #fff → var(--card)
SRCBOX_RE = re.compile(r"(\.(?:srcbox|maplink)\{[^}]*?)background:#fff")

# ---------- P2: '이번 주 임박' → '다가오는 14일' (실 윈도우 diff<=14 정직 표기) ----------
HOTWEEK_LABEL = {
    "": ("이번 주 임박", "다가오는 14일"),
    "en": ("Closing this week", "Next 14 days"),
    "ja": ("今週締切間近", "今後14日"),
    "zh-cn": ("本周即将截止", "未来14天"),
    "zh-tw": ("本週即將截止", "未來14天"),
    "es": ("Cierran esta semana", "Próximos 14 días"),
    "th": ("ปิดรับสัปดาห์นี้", "14 วันข้างหน้า"),
    "id": ("Tutup minggu ini", "14 hari ke depan"),
    "pt": ("Encerram esta semana", "Próximos 14 dias"),
    "ar": ("تنتهي هذا الأسبوع", "الـ14 يومًا القادمة"),
    "vi": ("Đóng trong tuần này", "14 ngày tới"),
}

# P1-⑤ 아카이브 라벨
ARCHIVE_TITLE = {
    "": "지난 일정 아카이브",
    "en": "Past events archive",
    "ja": "過去イベントのアーカイブ",
    "zh-cn": "往期活动存档",
    "zh-tw": "往期活動存檔",
    "es": "Archivo de eventos pasados",
    "th": "คลังอีเวนต์ที่ผ่านมา",
    "id": "Arsip acara lampau",
    "pt": "Arquivo de eventos passados",
    "ar": "أرشيف الفعاليات السابقة",
    "vi": "Lưu trữ sự kiện đã qua",
}

# ---------- WCAG 유틸 (wave4 와 동일 — abadge CR 보정) ----------


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
    """이니셜 칩 (bg, fg) CR>=4.5 보장 — generate.py _badge_colors 동일 로직."""
    for _ in range(10):
        ink, wht = _cr("#1a1a18", bg), _cr("#ffffff", bg)
        if max(ink, wht) >= 4.5:
            return bg, ("#1a1a18" if ink >= wht else "#ffffff")
        bg = _mix_black(bg, 0.08)
    return bg, "#ffffff"


# ---------- 인덱스: P0-2 틴트 --tr 토큰화 + 틴트 정책 재평가 (음방 포함) ----------
TINT_INLINE_RE = re.compile(
    r"background:linear-gradient\(var\(--ga,135deg\),"
    r"rgba\((\d+),(\d+),(\d+),[0-9.]+\) 0%,var\(--ehead-mid,#ffffff\) 42%,"
    r"rgba\(\d+,\d+,\d+,[0-9.]+\) 100%\)"
)
DDATE_RE = re.compile(r'data-date="(\d{4})-(\d{2})-(\d{2})"')
STRIPE_RE = re.compile(r"--stripe:(#[0-9A-Fa-f]{6})")
CARD_RE = re.compile(r'<a class="ecard".*?</a>', re.S)


def _tint_style(hexcolor):
    h = hexcolor.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    return (
        f"--tr:{r},{g},{b};background:linear-gradient(var(--ga,135deg),"
        "rgba(var(--tr),var(--ta1,.08)) 0%,var(--ehead-mid,#ffffff) 42%,"
        "rgba(var(--tr),var(--ta2,.16)) 100%)"
    )


def retoken_tints(s):
    """기존 인라인 rgba 고정 알파 → --tr 채널 + --ta 알파 토큰 (다크 임박 틴트 복원)."""

    def rep(m):
        return _tint_style(
            f"#{int(m.group(1)):02x}{int(m.group(2)):02x}{int(m.group(3)):02x}"
        )

    return TINT_INLINE_RE.sub(rep, s)


def _days_until(card, today):
    dm = DDATE_RE.search(card)
    if not dm:
        return None
    try:
        return (date(int(dm.group(1)), int(dm.group(2)), int(dm.group(3))) - today).days
    except ValueError:
        return None


def tint_policy(s):
    """임박(D-7 이내) 카드 = 틴트 (음방 포함 — P2 누락 봉쇄), 그 외 var(--card). 멱등 재평가."""
    today = date.today()
    out, last = [], 0
    for m in CARD_RE.finditer(s):
        card = m.group(0)
        dd = _days_until(card, today)
        imminent = dd is not None and 0 <= dd <= 7
        has_tint = "--tr:" in card or "linear-gradient(var(--ga" in card
        if imminent and not has_tint:
            stripe = STRIPE_RE.search(card)
            color = stripe.group(1) if stripe else "#8A8A8A"
            card = card.replace("background:var(--card)", _tint_style(color), 1)
        elif not imminent and has_tint:
            card = re.sub(
                r"(?:--tr:\d+,\d+,\d+;)?background:linear-gradient\(var\(--ga[^;\"]*\)",
                "background:var(--card)",
                card,
            )
        out.append(s[last : m.start()])
        out.append(card)
        last = m.end()
    out.append(s[last:])
    return "".join(out)


# ---------- P1-④ 이니셜 폴백 전 카드 적용 ----------
GHOST_RE = re.compile(r'<span class="ghost"[^>]*>([^<]*)</span>')
EHEAD_NOBADGE_RE = re.compile(r'(<div class="ehead">)(<div class="a">)')


def inject_abadges(s):
    """abadge 없는 카드 → ghost 이니셜 + --stripe(없으면 #8A8A8A) 기반 칩 주입 (CR>=4.5 보정).
    x=163 vs 68 리듬 해소 — 전 카드 동일 시작점."""
    out, last = [], 0
    for m in CARD_RE.finditer(s):
        card = m.group(0)
        if 'class="abadge"' not in card:
            g = GHOST_RE.search(card)
            a = re.search(r'<div class="a">(?:<bdi>)?([^<]*)', card)
            label = (
                g.group(1) if g else (a.group(1)[:3].upper() if a else "?")
            ).strip()
            artist = (a.group(1) if a else label).strip()
            stripe = STRIPE_RE.search(card)
            bg, fg = badge_colors(stripe.group(1) if stripe else "#8A8A8A")
            badge = (
                f'<span class="abadge" style="background:{bg};color:{fg}" '
                f'title="{artist}"><bdi>{label}</bdi></span>'
            )
            card = EHEAD_NOBADGE_RE.sub(
                lambda mm: mm.group(1) + badge + mm.group(2), card, count=1
            )
        out.append(s[last : m.start()])
        out.append(card)
        last = m.end()
    out.append(s[last:])
    return "".join(out)


# ---------- P1-⑤ 종료 180일+ → 아카이브 details ----------


def archive_old_past(s, lang_dir):
    if "w5-archive" in s:
        # 멱등 2회차: 신규 노후 카드만 재평가 (이미 섹션 존재 시 그대로)
        return s
    today = date.today()
    foot = s.find('<div class="foot">')
    if foot < 0:
        return s
    # 지난 이벤트 그리드 = foot 직전 마지막 grid
    grids = list(re.finditer(r'<div class="grid">', s[:foot]))
    if not grids:
        return s
    g_start = grids[-1].end()
    s.find("</div>", g_start)
    # grid 내 카드 균형 추적: 카드에는 중첩 div 가 있으므로 카드 단위로 스캔
    seg_end = foot
    old_cards, kept, _last = [], [], g_start
    seg = s[g_start:seg_end]
    pos = 0
    for m in CARD_RE.finditer(seg):
        card = m.group(0)
        dd = _days_until(card, today)
        kept.append(seg[pos : m.start()])
        if dd is not None and dd < -ARCHIVE_DAYS:
            old_cards.append(card)
        else:
            kept.append(card)
        pos = m.end()
    kept.append(seg[pos:])
    if not old_cards:
        return s
    label = ARCHIVE_TITLE.get(lang_dir, ARCHIVE_TITLE["en"])
    archive = (
        '<details class="w5-archive" style="margin:14px 0 0">'
        f'<summary style="cursor:pointer;font-size:13px;font-weight:600;color:var(--muted);'
        f'min-height:36px;display:flex;align-items:center">{label} ({len(old_cards)})</summary>'
        f'<div class="grid" style="margin-top:8px">{"".join(old_cards)}</div></details>'
    )
    return s[:g_start] + "".join(kept) + archive + s[seg_end:]


# ---------- 코스 페이지 (ko/en) ----------
COURSE_CSS = (
    "/*W5COURSE*/"
    # P1-②: prep-name <small> 11.67px → 13px (CTA 보조 라벨 가독)
    ".prep-name small{font-size:13px}"
    # P1-③: en 탭 crs-tag 11.2px 어긋남 — 타이틀 상단·tag 하단 고정 (양 탭 동일 y, 라벨 stretch 등고)
    ".crs-tabs .crs-tabbar label{justify-content:flex-start}"
    ".crs-tabs .crs-tabbar label .crs-tag{margin-top:auto}"
    # P1-⑥: hero 공연 정보 칩 ↔ D-day pill — radius 12px·min-height 54px·수직 중심 통일
    ".hero-finale{display:inline-flex;align-items:center;vertical-align:middle;"
    "border-radius:12px;min-height:54px;box-sizing:border-box}"
    ".hero-cd{border-radius:12px;vertical-align:middle;min-height:54px;box-sizing:border-box;align-items:center}"
    # 와이드(>=700px) 한 줄 배치 시 margin 동일화 — 수직 중심 오프셋 0px (390 스택 레이아웃 불변)
    "@media(min-width:700px){.hero-finale,.hero-cd{margin:12px 10px 4px 0}}"
    ".hero-cd .hero-dd-num{align-self:baseline}.hero-cd .hero-dd-label,.hero-cd .hero-dd-unit{align-self:baseline}"
)

# 템플릿③ 룰 주석 (박제)
RULE_COMMENT = (
    "<!--W5RULE: day 카드 임계 룰 — 총 3일 이하 코스 flat / 4일+ 코스 day-acc 아코디언. "
    "공연 당일 상세(day-card--show)는 길이 무관 항상 flat 노출-->"
)

BASE_NOTE = {"": "잠실 베이스 기준", "en": "Jamsil base reference"}

# P1-① 복귀 칩 JS — W4SHOWDAY 의 라디오 전환을 캡처 단계에서 감지, 명시 복귀 동선 제공
RETURN_JS = """<script>/*W5RETURN*/(function(){
function slLabel(id){var l=document.querySelector('label[for="'+id+'"]');if(!l)return id;
var t=l.childNodes[0]&&l.childNodes[0].textContent||l.textContent;return t.trim();}
document.addEventListener('click',function(ev){
var a=ev.target.closest&&ev.target.closest('a.showday-jump');if(!a)return;
var prev=document.querySelector('input[name="stay-len"]:checked');var prevId=prev?prev.id:null;
setTimeout(function(){
var now=document.querySelector('input[name="stay-len"]:checked');if(!now||!prevId||now.id===prevId)return;
var sel=a.getAttribute('href')||'';var t=sel.charAt(0)==='#'&&document.getElementById(sel.slice(1));if(!t)return;
var old=document.getElementById('w5-return');if(old)old.remove();
var ko=(document.documentElement.lang||'ko').indexOf('ko')===0;
var btn=document.createElement('button');btn.type='button';btn.id='w5-return';
btn.textContent=ko?('\\u2190 '+slLabel(prevId)+' \\ucf54\\uc2a4\\ub85c \\ub3cc\\uc544\\uac00\\uae30')
:('\\u2190 Back to '+slLabel(prevId)+' course');
btn.style.cssText='display:flex;align-items:center;gap:6px;min-height:44px;margin:0 0 8px;padding:8px 14px;'
+'font-size:13px;font-weight:700;color:var(--accent);background:var(--accent-soft);'
+'border:1px solid var(--accent-line);border-radius:12px;cursor:pointer';
btn.addEventListener('click',function(){var r=document.getElementById(prevId);
if(r){r.checked=true;}btn.remove();
requestAnimationFrame(function(){a.scrollIntoView({behavior:'smooth',block:'center'});});});
t.parentNode.insertBefore(btn,t);},60);},true);})();</script>"""


def _dsumline(body):
    """day-acc summary 한 줄 요약 — 본문 lv 선두 텍스트 2개 결합 (신규 주장 0, 본문 verbatim)."""
    items = []
    for m in re.finditer(
        r'<div class="lv">(.*?)(?:<span class="badge|<div class="dsum|</div>)',
        body,
        re.S,
    ):
        t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        t = re.sub(r"\s+", " ", t)
        if t:
            items.append(t)
        if len(items) >= 2:
            break
    line = " · ".join(items)
    return (line[:64] + "…") if len(line) > 65 else line


def _find_balanced_div(s, start):
    """start = '<div' 시작 인덱스. 균형 닫힘 직후 인덱스 반환."""
    depth = 0
    for m in re.finditer(r"<div\b|</div>", s[start:]):
        depth += 1 if m.group(0) == "<div" else -1
        if depth == 0:
            return start + m.end()
    return -1


def convert_sl4_accordion(s):
    """템플릿③ — sl-4 (5일 코스) flat day-card → day-acc 아코디언. show 카드는 유지."""
    pm = re.search(r'<div class="sl-panel sl-4">', s)
    if not pm:
        return s
    nxt = re.search(r'<div class="sl-panel sl-7">', s)
    p_start, p_end = pm.start(), (nxt.start() if nxt else len(s))
    seg = s[p_start:p_end]
    if "day-acc" in seg:  # 이미 전환됨 (멱등)
        if RULE_COMMENT not in seg:
            seg = seg.replace(
                '<div class="sl-panel sl-4">',
                '<div class="sl-panel sl-4">' + RULE_COMMENT,
                1,
            )
            return s[:p_start] + seg + s[p_end:]
        return s
    out = []
    pos = 0
    first = True
    while True:
        i = seg.find('<div class="day-card">', pos)
        if i < 0:
            break
        j = _find_balanced_div(seg, i)
        if j < 0:
            break
        card = seg[i:j]
        hm = re.search(r'<div class="dhead">(.*?)</div>', card, re.S)
        if not hm:
            out.append(seg[pos:j])
            pos = j
            continue
        head = hm.group(1)
        body = card[hm.end() : -6]  # 마지막 </div> 제외
        summary = _dsumline(body)
        acc = (
            f'<details class="day-card day-acc"{" open" if first else ""}><summary>{head}'
            f'<span class="dsumline">{summary}</span></summary>'
            f'<div class="day-acc-body">{body}</div></details>'
        )
        first = False
        out.append(seg[pos:i])
        out.append(acc)
        pos = j
    out.append(seg[pos:])
    seg = "".join(out)
    if RULE_COMMENT not in seg:
        seg = seg.replace(
            '<div class="sl-panel sl-4">',
            '<div class="sl-panel sl-4">' + RULE_COMMENT,
            1,
        )
    return s[:p_start] + seg + s[p_end:]


def fix_course(s, lang_dir):
    # 템플릿①: sl-2 히어로 사진 (sec-media) 제거 — 한 코스만의 장식 = 리듬 붕괴
    pm = re.search(r'<div class="sl-panel sl-2">', s)
    if pm:
        zone = s[pm.start() : pm.start() + 3000]
        zone2 = re.sub(r'<div class="sec-media"><img[^>]*></div>', "", zone, count=1)
        if zone2 != zone:
            s = s[: pm.start()] + zone2 + s[pm.start() + 3000 :]
    # 템플릿②: sl-4·sl-7 intro '잠실 베이스 기준' 1줄
    note = BASE_NOTE.get(lang_dir, BASE_NOTE["en"])
    for pid in ("sl-4", "sl-7"):
        pm = re.search(r'<div class="sl-panel ' + pid + r'">.{0,600}?</p>', s, re.S)
        if pm and "w5-basenote" not in s[pm.start() : pm.end() + 120]:
            ins = pm.end()
            s = (
                s[:ins]
                + f'<p class="scap w5-basenote" style="margin:2px 0 0;font-weight:600">{note}</p>'
                + s[ins:]
            )
    # 템플릿③: sl-4 아코디언 전환
    s = convert_sl4_accordion(s)
    # P1-① 복귀 칩 JS
    if "W5RETURN" not in s and "showday-jump" in s:
        s = s.replace("</body>", RETURN_JS + "</body>", 1)
    # 코스 CSS (P1-②③⑥)
    if "W5COURSE" not in s:
        i = s.find("</style>")
        if i >= 0:
            s = s[:i] + COURSE_CSS + s[i:]
    # R38 P0 — 모바일 hero CTA가 긴 문구에서 우측 clipping 되지 않도록 폭 상한과 래핑 보장.
    if "W5HEROMOBILE" not in s and ".hero-cta{" in s:
        s = s.replace(
            "letter-spacing:.01em;text-decoration:none;border-radius:14px;\n  border:",
            "letter-spacing:.01em;text-decoration:none;border-radius:14px;\n"
            "  max-width:100%;box-sizing:border-box;white-space:normal;text-align:center;line-height:1.25;\n"
            "  border:",
            1,
        )
        s = s.replace(
            ".hero-cta svg{flex:0 0 auto}",
            ".hero-cta svg{flex:0 0 auto}\n"
            "/*W5HEROMOBILE*/@media (max-width:900px){.hero{display:flex;flex-direction:column;align-items:stretch}"
            ".hero-finale,.hero-cd,.hero-cta{display:flex;width:100%;max-width:100%;margin:8px 0 0}"
            ".hero-cd{justify-content:center}.hero-cta{padding:0 16px}}",
            1,
        )
    return s


# ---------- 파일 단위 처리 ----------


def process(path, lang_dir, is_index, is_course):
    s0 = path.read_text(encoding="utf-8")
    s = s0
    # 토큰 주입 (첫 <style> 닫기 직전, 멱등)
    if MARK not in s:
        i = s.find("</style>")
        if i >= 0:
            s = s[:i] + TOKEN_BLOCK + s[i:]
    for a, b in REPLACES:
        s = s.replace(a, b)
    s = SRCBOX_RE.sub(r"\1background:var(--card)", s)
    # ytfacade UA 기본 bg 봉쇄 (P0-1) — 마커 가드 멱등
    if "background-color:var(--surface-2);background-size:cover" not in s:
        s = s.replace(
            "background-size:cover;background-position:center;cursor:pointer;padding:0}",
            "background-color:var(--surface-2);background-size:cover;background-position:center;cursor:pointer;padding:0}",
        )
    if is_index:
        old, new = HOTWEEK_LABEL.get(lang_dir, HOTWEEK_LABEL["en"])
        s = s.replace(old, new)
        s = retoken_tints(s)
        s = tint_policy(s)
        s = inject_abadges(s)
        s = archive_old_past(s, lang_dir)
    if is_course:
        s = fix_course(s, lang_dir)
    if s != s0:
        path.write_text(s, encoding="utf-8")
        return True
    return False


def main():
    changed = total = 0
    for ld in LANG_DIRS:
        d = DIST / ld if ld else DIST
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.html")):
            total += 1
            if process(
                f,
                ld,
                f.name == "index.html",
                f.name.startswith("twice-thisisfor-seoul"),
            ):
                changed += 1
    print(f"wave5 sweep: {changed}/{total} files changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
