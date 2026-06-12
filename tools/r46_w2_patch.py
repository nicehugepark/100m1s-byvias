#!/usr/bin/env python3
"""R46 2심 확정 W2 패치 — 디테일·단순화 (홈 11언어 + 리치 ko·en + F10 전 dist 스윕).

F4  날짜 토큰 nowrap 전사 규칙화: 텍스트 노드의 YYYY-MM-DD 를 .dtkn(white-space:nowrap)으로 래핑
    (script/style 블록 보호 — JS·JSON-LD 내 날짜 무접촉). 홈 11 + 리치 ko·en.
F5  언어 메뉴 light-dismiss: 바깥 탭/클릭 시 details.langpick 닫힘 (capture phase). 홈 11 + 리치 ko·en.
F6  sub-44 터치 타겟: 항공 인라인 링크 2종 + NOL 예매처 링크 .tap44 (시각 비변형 패딩+네거티브 마진,
    bbox h>=44). ota-btn 은 F8 의 ota-row 제거로 구조 해소. 리치 ko·en.
F7  지난 이벤트 이중 구조 → 단일 아카이브: 풀사이즈 종료 grid 를 w5-archive grid 로 병합,
    summary (N) 합산 갱신. 홈 11.
F8  호텔 카드 벤더 3중 행 → 단일 CTA 1행: ota-row 제거, primary 를 Trip.com(실수익) 승격
    (기존 ota-row 의 Trip.com href 재사용 — trip_sub1 stay{i} 유지). 리치 ko·en.
F9  당일 공연 카드 액션화: D-DAY 카드에 펄스 도트(.dd-live) + 행동 1버튼(.live-cta, 카드 상세 직링크
    시각 버튼). reduced-motion 대응. 홈 11 (ko 외 영어 fallback — home_redesign_patch 선례).
F10 회색 이니셜 아바타(#8A8A8A) → 해시 기반 브랜드 팔레트 자동 배정 (전 dist 스윕, title 키 —
    페이지 간 동일 아티스트 동일 색, 전 페어 CR>=4.5 사전 assert).
F11 Skyscanner 비표준 ?destination=Seoul → 공식 path 딥링크 /flights-to/sela/cheap-flights-to-seoul.html
    (2026-06-12 curl 200 + 서울 페이지 title 실측, WebSearch 2회 corroborate). 리치 ko·en 4곳.

멱등: 홈/리치 = R46-W2 CSS 마커로 파일 단위 skip. F10 = 치환 자체가 소진형(잔존 0이면 no-op).
실행: python3 tools/r46_w2_patch.py
"""

import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARK = "/* R46-W2 */"
LANGS = ["ko", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]
NOL = "https://world.nol.com/en/ticket/places/26000627/products/26007949"

SKY_OLD = {
    "ko": "https://www.skyscanner.co.kr/flights/?destination=Seoul",
    "en": "https://www.skyscanner.com/flights/?destination=Seoul",
}
SKY_NEW = {
    "ko": "https://www.skyscanner.co.kr/flights-to/sela/cheap-flights-to-seoul.html",
    "en": "https://www.skyscanner.com/flights-to/sela/cheap-flights-to-seoul.html",
}

LIVE_TXT = {
    "ko": "오늘 공연 · 상세 보기 ›"
}  # 그 외 로케일 = 영어 fallback (선례: home_redesign_patch)
LIVE_TXT_EN = "Live today · details ›"


def home_path(lang):
    return (DIST if lang == "ko" else DIST / lang) / "index.html"


def rich_path(lang):
    return (DIST if lang == "ko" else DIST / lang) / "twice-thisisfor-seoul.html"


# ── 색 유틸 (F10 팔레트 CR assert) ──────────────────────────
def _lum(hexc):
    r, g, b = (int(hexc[i : i + 2], 16) / 255 for i in (1, 3, 5))

    def f(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def cr(a, b):
    la, lb = _lum(a), _lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# (bg, ink) — 기존 브랜드 무드 정합 (BTS 보라·BP 핑크 동형 채도), 전 페어 CR>=4.5
PALETTE = [
    ("#6B3FA0", "#ffffff"),  # 보라 (purple 토큰)
    ("#185FA5", "#ffffff"),  # 블루 (accent-bg 토큰)
    ("#0F6E56", "#ffffff"),  # 그린 (ok 토큰)
    ("#A32D2D", "#ffffff"),  # 레드 (warn 토큰)
    ("#B32E5C", "#ffffff"),  # 로즈 (rose-deep 토큰)
    ("#11305A", "#ffffff"),  # 네이비 (sky 토큰)
    ("#7A5A12", "#ffffff"),  # 골드 딥 (sun-chip-ink 토큰)
    ("#4A5D23", "#ffffff"),  # 올리브
]
for bg, ink in PALETTE:
    assert cr(bg, ink) >= 4.5, f"PALETTE CR FAIL {bg}/{ink} = {cr(bg, ink):.2f}"


def pick_color(title):
    h = int(hashlib.md5(title.encode("utf-8")).hexdigest(), 16)
    return PALETTE[h % len(PALETTE)]


# ── F4: 텍스트 노드 날짜 nowrap ─────────────────────────────
DATE_RX = re.compile(r"(\d{4}-\d{2}-\d{2})")
PROTECT_RX = re.compile(r"(<script\b.*?</script>|<style\b.*?</style>)", re.S)


def f4_nowrap(html):
    # <head> 전체 보호 — <title> 텍스트 노드에 마크업 주입 방지 (meta/og/JSON-LD 포함)
    head_end = html.find("</head>")
    if head_end > 0:
        head_end += len("</head>")
        head, body = html[:head_end], html[head_end:]
    else:
        head, body = "", html
    parts = PROTECT_RX.split(body)
    out, n = [head], 0
    for i, part in enumerate(parts):
        if i % 2 == 1:  # script/style 블록 — 무접촉
            out.append(part)
            continue
        toks = re.split(r"(<[^>]*>)", part)
        for j, t in enumerate(toks):
            if j % 2 == 0 and t.strip():
                t2, c = DATE_RX.subn(r'<span class="dtkn">\1</span>', t)
                if c:
                    toks[j] = t2
                    n += c
        out.append("".join(toks))
    return "".join(out), n


# ── F5 + F9 JS / CSS ────────────────────────────────────────
LD_JS = (
    "/*R46-W2-LD*/document.addEventListener('click',function(e){"
    "var ds=document.querySelectorAll('details.langpick[open]');"
    "for(var i=0;i<ds.length;i++){if(!ds[i].contains(e.target))ds[i].removeAttribute('open');}},true);"
)


def live_js(txt):
    return (
        "/*R46-W2-LIVE*/(function(){try{var T=new Date();T.setHours(0,0,0,0);"
        "var ds=document.querySelectorAll('.grid .ecard .dday[data-date]');"
        "for(var i=0;i<ds.length;i++){var p=(ds[i].getAttribute('data-date')||'').split('-');"
        "if(p.length!==3)continue;var ev=new Date(+p[0],+p[1]-1,+p[2]);ev.setHours(0,0,0,0);"
        "if(Math.round((ev-T)/86400000)!==0)continue;"
        "var card=ds[i].closest('.ecard');if(!card||card.querySelector('.live-cta'))continue;"
        "ds[i].classList.add('dd-live');var c=card.querySelector('.c');"
        "if(c)c.insertAdjacentHTML('afterend','<span class=\"live-cta\">"
        + txt
        + "</span>');"
        "}}catch(e){}})();"
    )


CSS_COMMON = (
    MARK + ".dtkn{white-space:nowrap}"
    '.dd-live::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;'
    "background:currentColor;margin-inline-end:4px;vertical-align:1px;"
    "animation:ddpulse 1.2s ease-in-out infinite}"
    "@keyframes ddpulse{0%,100%{opacity:.35}50%{opacity:1}}"
    "@media(prefers-reduced-motion:reduce){.dd-live::before{animation:none}}"
    ".live-cta{display:inline-flex;align-items:center;justify-content:center;min-height:36px;"
    "box-sizing:border-box;margin:8px 0 0;padding:7px 14px;font-size:13px;font-weight:700;"
    "color:var(--on-accent,#fff);background:var(--urgent,#C62828);border-radius:8px;width:fit-content}"
    # 다크: --urgent(#FF6B6B)는 라이트 레드 — 흰 글자 bg 로 쓰면 CR 2.78. dday-hot 동형(urgent-bg 필 + urgent 잉크)
    "@media(prefers-color-scheme:dark){.live-cta{color:var(--urgent,#FF6B6B);"
    "background:var(--urgent-bg,#3a1f1d);border:1px solid var(--urgent,#FF6B6B)}}"
)
CSS_RICH_EXTRA = (
    ".tap44{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;"
    "padding:12px 3px;margin:-12px -3px;vertical-align:middle}"
)


# ── F7: 지난 이벤트 grid → 아카이브 병합 ────────────────────
def f7_merge_past(html, lang):
    arch_pos = html.find('<details class="w5-archive"')
    if arch_pos < 0:
        raise SystemExit(f"FAIL [{lang}/F7] w5-archive 부재")
    head = html[:arch_pos]
    grid_start = head.rfind('<div class="grid">')
    if grid_start < 0:
        raise SystemExit(f"FAIL [{lang}/F7] visible past grid 부재")
    seg = html[grid_start:arch_pos]
    seg_strip = seg.rstrip()
    if not seg_strip.endswith("</div>"):
        raise SystemExit(f"FAIL [{lang}/F7] past grid 종단 형식 상이")
    cards = seg_strip[len('<div class="grid">') : -len("</div>")]
    n_moved = cards.count('class="ecard"')
    if n_moved < 1:
        raise SystemExit(f"FAIL [{lang}/F7] 이동 카드 0")
    # visible grid 제거
    html = html[:grid_start] + html[arch_pos:]
    # 아카이브 grid 선두에 prepend (최근 종료분이 위)
    anchor = '<div class="grid" style="margin-top:8px"'
    a_pos = html.find(anchor, html.find('<details class="w5-archive"'))
    if a_pos < 0:
        raise SystemExit(f"FAIL [{lang}/F7] archive grid 부재")
    insert_at = html.find(">", a_pos) + 1
    html = html[:insert_at] + cards + html[insert_at:]

    # summary (N) 합산
    def bump(m):
        return m.group(1) + str(int(m.group(2)) + n_moved) + m.group(3)

    html, c = re.subn(
        r'(<details class="w5-archive"[^>]*><summary[^>]*>[^<]*\()(\d+)(\))',
        bump,
        html,
        count=1,
    )
    if c != 1:
        raise SystemExit(f"FAIL [{lang}/F7] summary (N) 갱신 실패")
    return html, n_moved


# ── F8: 호텔 단일 CTA ───────────────────────────────────────
def f8_single_cta(html, lang):
    label = "예약하기 · Trip.com ↗" if lang == "ko" else "Book · Trip.com ↗"
    n = [0]

    def fix(m):
        block = m.group(0)
        trip = re.search(
            r'<a class="ota-btn" href="(https://www\.trip\.com/hotels/[^"]+)"[^>]*data-aff-pos="(\d+)"[^>]*>',
            block,
        )
        if not trip:
            raise SystemExit(
                f"FAIL [{lang}/F8] stay-cta 내 Trip.com 부재: {block[:120]}"
            )
        href, pos = trip.group(1), trip.group(2)
        n[0] += 1
        return (
            '<div class="stay-cta"><a class="postlink stay22-btn" href="' + href + '" '
            'rel="sponsored nofollow" target="_blank" data-aff="1" data-aff-surface="stay-cta-single" '
            'data-aff-vendor="Trip.com" data-aff-event="twice-thisisfor-seoul" data-aff-pos="'
            + pos
            + '">'
            + label
            + "</a></div>"
        )

    # 매치 = stay-cta 전체 블록(개행 없는 1라인 구조): stay-cta open + primary a + ota-row(open/close) + stay-cta close
    # → 치환도 균형 블록 (open 1 + close 1). 여분 </div> 추가 금지 (div 균형).
    html = re.sub(
        r'<div class="stay-cta">.*?</div></div>',
        lambda m: fix(m),
        html,
        flags=re.S,
    )
    if n[0] != 4:
        raise SystemExit(f"FAIL [{lang}/F8] stay-cta 4곳 기대, {n[0]}곳 치환")
    return html


# ── 메인 패치 ───────────────────────────────────────────────
def patch_home(lang):
    path = home_path(lang)
    html = path.read_text(encoding="utf-8")
    if MARK in html:
        print(f"[home/{lang}] already — skip")
        return
    html, n4 = f4_nowrap(html)
    html, n7 = f7_merge_past(html, lang)
    txt = LIVE_TXT.get(lang, LIVE_TXT_EN)
    html = html.replace(
        "</body>", "<script>" + LD_JS + live_js(txt) + "</script></body>", 1
    )
    html = html.replace("</style>", CSS_COMMON + "</style>", 1)
    path.write_text(html, encoding="utf-8")
    print(f"[home/{lang}] F4 dtkn={n4} F7 moved={n7} F5+F9 injected")


def patch_rich(lang):
    path = rich_path(lang)
    html = path.read_text(encoding="utf-8")
    if MARK in html:
        print(f"[rich/{lang}] already — skip")
        return
    # F11 (스카이스캐너 2곳: steps5 + prep-list)
    cnt = html.count(SKY_OLD[lang])
    if cnt != 2:
        raise SystemExit(f"FAIL [{lang}/F11] skyscanner 구 URL 2곳 기대, {cnt}곳")
    html = html.replace(SKY_OLD[lang], SKY_NEW[lang])
    # F6: 항공 인라인 2 + NOL 2 (ligrid 예매처 + W1 인트로 잔여석)
    sky_a = f'<a href="{SKY_NEW[lang]}" rel="nofollow" target="_blank">'
    if html.count(sky_a) != 1:
        raise SystemExit(f"FAIL [{lang}/F6] steps5 skyscanner 앵커 식별 실패")
    html = html.replace(sky_a, sky_a.replace("<a ", '<a class="tap44" '), 1)
    html = re.sub(
        r'<a (href="https://www\.trip\.com/flights/[^"]*steps5_flight"[^>]*>)',
        r'<a class="tap44" \1',
        html,
        count=1,
    )
    n_nol = [0]

    def nol_fix(m):
        tag = m.group(0)
        if 'class="' in tag:
            tag = re.sub(r'class="([^"]*)"', r'class="\1 tap44"', tag, count=1)
        else:
            tag = tag.replace("<a ", '<a class="tap44" ', 1)
        n_nol[0] += 1
        return tag

    # disc-hub(밀집 고지 텍스트) 내 NOL 링크는 제외 — ±12px 히트영역 확장이 인접 본문 오탭 유발.
    # F6 스코프 = 인트로 잔여석 + ligrid 예매처 (audit 명단 NOL Ticket 152×17 승계).
    hub_pos = html.find('class="disc-hub"')
    if hub_pos < 0:
        raise SystemExit(f"FAIL [{lang}/F6] disc-hub 부재 (W1 선행 필요)")
    pre, post = html[:hub_pos], html[hub_pos:]
    pre = re.sub(r'<a href="' + re.escape(NOL) + r'"[^>]*>', nol_fix, pre)
    html = pre + post
    # F8
    html = f8_single_cta(html, lang)
    # F4
    html, n4 = f4_nowrap(html)
    # F5
    html = html.replace("</body>", "<script>" + LD_JS + "</script></body>", 1)
    html = html.replace("</style>", CSS_COMMON + CSS_RICH_EXTRA + "</style>", 1)
    path.write_text(html, encoding="utf-8")
    print(
        f"[rich/{lang}] F11 x2 F6 tap44(sky+trip+NOLx{n_nol[0]}) F8 x4 F4 dtkn={n4} F5 injected"
    )


def patch_f10_all():
    rx = re.compile(r'style="background:#8A8A8A;color:#1a1a18" title="([^"]*)"')
    total_files, total_hits = 0, 0
    for p in sorted(DIST.rglob("*.html")):
        html = p.read_text(encoding="utf-8")
        if "#8A8A8A" not in html:
            continue

        def repl(m):
            import html as ihtml

            title = ihtml.unescape(m.group(1))
            bg, ink = pick_color(title)
            return f'style="background:{bg};color:{ink}" title="{m.group(1)}"'

        new, c = rx.subn(repl, html)
        if c:
            p.write_text(new, encoding="utf-8")
            total_files += 1
            total_hits += c
    print(f"[F10] {total_files} files, {total_hits} avatars recolored")
    left = sum(
        1
        for p in DIST.rglob("*.html")
        if "background:#8A8A8A;color:#1a1a18" in p.read_text(encoding="utf-8")
    )
    if left:
        raise SystemExit(f"FAIL [F10] 회색 abadge 잔존 {left} files")


def verify():
    bad = 0
    for lang in LANGS:
        h = home_path(lang).read_text(encoding="utf-8")
        arch = h.find('<details class="w5-archive"')
        # h2 지난 이벤트 ~ archive 사이 visible grid 0 확인
        h2 = h.rfind("<h2", 0, arch)
        if '<div class="grid">' in h[h2:arch]:
            print(f"VERIFY FAIL [home/{lang}] 이중 구조 잔존")
            bad += 1
        if "live-cta" not in h or "dd-live" not in h:
            print(f"VERIFY FAIL [home/{lang}] F9 JS 부재")
            bad += 1
        if "R46-W2-LD" not in h:
            print(f"VERIFY FAIL [home/{lang}] F5 부재")
            bad += 1
    for lang in ("ko", "en"):
        r = rich_path(lang).read_text(encoding="utf-8")
        if "?destination=Seoul" in r:
            print(f"VERIFY FAIL [rich/{lang}] F11 구 URL 잔존")
            bad += 1
        if r.count('class="ota-row"') != 0:
            print(f"VERIFY FAIL [rich/{lang}] F8 ota-row 잔존")
            bad += 1
        if r.count("stay-cta-single") != 4:
            print(
                f"VERIFY FAIL [rich/{lang}] F8 단일 CTA {r.count('stay-cta-single')}/4"
            )
            bad += 1
    print("VERIFY", "FAIL" if bad else "OK")
    return bad


if __name__ == "__main__":
    for lang in LANGS:
        patch_home(lang)
    for lang in ("ko", "en"):
        patch_rich(lang)
    patch_f10_all()
    sys.exit(1 if verify() else 0)
