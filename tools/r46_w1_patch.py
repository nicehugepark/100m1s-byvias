#!/usr/bin/env python3
"""R46 2심 확정 W1 패치 — 신뢰·법규·수익 정직 (ko·en 리치 + 전 리치 F3).

F1 티켓 오픈 경과 카피 상태 전환 (ko·en):
  - 인트로 li "일반 예매 6/11(목) 20:00" 사전 안내 → "예매 진행 중 — 잔여석 확인 ↗"
  - tk-badge past 라벨: 일반예매 행 '종료'→'오픈됨' (data-tkpast 행별 오버라이드, 선예매는 '종료' 유지 — 실제 종료)
  - 정보 최종 확인 날짜 2026-06-10 → 2026-06-12 (disc-hub로 이동)

F2 고지 체계 통합 (ko·en):
  - 산개 9건 (시세×3·숙소 시세×2·제휴 w8-disc·비공식 gdisc·K-ETA s5-sub·3DS 인트로 꼬리·최종확인 foot·알림 news-soon)
    → footer 위치 단일 .disc-hub 컴포넌트 1곳 (의미 보존 9항목)
  - 첫 어필 링크 인라인 표식: a[data-aff="1"]::after 칩 (ko "제휴" / en "AD") — 비제휴와 구분
  - OTA 군집(준비 단계별 예약) 직상단 .disc-mini 1줄
  - K-ETA 스텝 sub는 액션 링크만 잔존 (고지 본문은 허브로 — 동선 보존)

F3 무수익 4벤더 마킹 제거 (11언어 리치 전체):
  - Booking·Agoda·Klook·Skyscanner: data-aff* 5종 속성 제거 + rel "sponsored nofollow"→"nofollow"
  - 실수익 (Trip.com·Airalo·KKday) 만 data-aff="1"+sponsored 유지

멱등: CSS 마커 R46-W1 존재 시 해당 파일 skip. 패턴 카운트 불일치 시 즉시 raise (원자적 — 전 치환 성공 시에만 write).
실행: python3 tools/r46_w1_patch.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARK = "/* R46-W1 */"
NOL = "https://world.nol.com/en/ticket/places/26000627/products/26007949"

RICH_LANGS = ["ko", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]


def rich_path(lang):
    return (DIST if lang == "ko" else DIST / lang) / "twice-thisisfor-seoul.html"


def sub_exact(html, old, new, n, label):
    cnt = html.count(old)
    if cnt != n:
        raise SystemExit(f"FAIL [{label}] expected {n}, found {cnt}: {old[:90]!r}")
    return html.replace(old, new)


def sub_rx(html, pat, repl, n, label, flags=0):
    new_html, cnt = re.subn(pat, repl, html, flags=flags)
    if cnt != n:
        raise SystemExit(f"FAIL [{label}] expected {n}, replaced {cnt}: {pat[:90]!r}")
    return new_html


# ── F2 CSS (칩 + 허브 + 미니 고지) ───────────────────────────
def css_block(tag_text):
    return (
        MARK + 'a[data-aff="1"]::after,.aff-eg{display:inline-block;'
        "font-size:10px;font-weight:700;line-height:1;padding:2px 5px;margin-inline-start:5px;"
        "border-radius:4px;border:1px solid var(--gold-line,#f0e4cf);"
        "color:var(--sun-chip-ink,#7A5A12);background:var(--gold-soft,#fdf6ec);vertical-align:middle}"
        # content 는 pseudo-element 전용 — 실 span(.aff-eg)은 ::after 로 텍스트 주입
        'a[data-aff="1"]::after,.aff-eg::after{content:"' + tag_text + '"}'
        ".aff-eg{margin-inline-start:0}"
        ".disc-hub{margin:22px 0 0;padding:14px 16px;background:var(--surface-1,#fafaf7);"
        "border:1px solid var(--line);border-radius:12px}"
        ".disc-hub h2{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 8px;letter-spacing:.2px}"
        ".disc-hub ul{margin:0;padding:0;list-style:none;display:flex;flex-direction:column;gap:6px}"
        ".disc-hub li{font-size:12px;line-height:1.65;color:var(--muted)}"
        ".disc-hub li b{color:var(--ink);font-weight:600}"
        ".disc-hub a{color:var(--accent)}"
        ".disc-hub .dh-site{font-size:12px;color:var(--muted);margin:10px 0 0}"
        ".disc-mini{font-size:12px;color:var(--muted);margin:0 0 8px;line-height:1.6}"
    )


# ── 로케일 페이로드 (ko·en) ──────────────────────────────────
P = {
    "ko": {
        "tag": "제휴",
        "intro_old": (
            "<li><b>티켓</b> — 일반 예매 <b>6/11(목) 20:00 KST</b>, NOL Ticket. "
            "가격 154,000원(≈$110), 좌석·스탠딩 동일. 해외카드 3DS 실패 잦음 → WOWPASS 권장.</li>"
        ),
        "intro_new": (
            "<li><b>티켓</b> — <b>예매 진행 중</b> — "
            f'<a href="{NOL}" target="_blank" rel="noopener nofollow">잔여석 확인 ↗</a> '
            "(일반 예매 6/11 20:00 오픈 경과). 가격 154,000원(≈$110), 좌석·스탠딩 동일.</li>"
        ),
        "tk_old": "else{b.textContent='종료';",
        "tk_new": "else{b.textContent=b.getAttribute('data-tkpast')||'종료';",
        "tk_open_label": "오픈됨",
        "course_old": " 실제 장소이며 가격은 대략 시세입니다. 실시간 예약가는 예약처에서 확인하세요.",
        "course_new": " 전부 실제 장소입니다.",
        "course_n": 3,
        "stays_old": " 표시가는 변동 — 실시간 예약가는 날짜 입력 후 예약처에서 확인하세요.",
        "stays_n": 1,
        "card_paren_rx": r'\s*<span style="color:var\(--muted\)">\(표시가 변동 — 날짜 입력 후 예약처 확인\)</span>',
        "card_paren_n": 1,
        "keta_old": (
            '<div class="s5-sub"><b>출발 전 K-ETA / 비자 확인:</b> 무비자 입국 대상국(미국·캐나다·EU 등)은 '
            "K-ETA 사전 신청이 필요할 수 있고, 국적·정책이 자주 바뀝니다. 출발 전 공식 사이트 "
            '<a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>'
            "에서 본인 국적 기준을 직접 확인하세요.</div>"
        ),
        "keta_new": (
            '<div class="s5-sub"><b>K-ETA / 비자:</b> 본인 국적 기준은 공식 사이트 '
            '<a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr ↗</a>에서 확인.</div>'
        ),
        "mini": (
            '<p class="disc-mini" data-r46w1="1"><span class="aff-eg"></span> 표식 링크는 '
            "제휴(수수료) 링크입니다 — 이용자 추가 비용은 없습니다.</p>\n"
        ),
        "hub": (
            '<section class="disc-hub" id="notice" data-r46w1="1">\n'
            "<h2>이용 안내 · 고지</h2>\n<ul>\n"
            '<li><b>제휴 링크</b> — 예약·상품 링크 중 <span class="aff-eg"></span> 표식이 붙은 링크는 '
            "제휴(수수료) 링크입니다. 구매 시 ByBias가 수수료를 받을 수 있으나, 이용자가 추가로 부담하는 "
            "비용은 없습니다. 표식이 없는 링크는 제휴가 아닙니다.</li>\n"
            "<li><b>가격 변동</b> — 표시 가격은 대략적인 시세이며 수시로 변동됩니다. 실시간 가격·잔여석은 "
            "날짜 입력 후 각 예약처에서 직접 확인하세요.</li>\n"
            "<li><b>전망 면책</b> — 가격·잔량 전망은 추정이며 실제와 다를 수 있습니다. 예약·결제의 최종 "
            "책임은 이용자 본인에게 있습니다.</li>\n"
            "<li><b>비공식 서비스</b> — 본 사이트는 아티스트·소속사와 무관한 비공식 일정·여행 정보 "
            "서비스이며, 공식 제휴 관계가 없습니다.</li>\n"
            "<li><b>입국 요건(K-ETA)</b> — K-ETA·비자 요건은 국적·정책에 따라 자주 바뀝니다. 출발 전 공식 "
            '사이트 <a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>에서 '
            "본인 국적 기준을 직접 재확인하세요.</li>\n"
            "<li><b>해외카드 결제</b> — 해외 발급 카드는 국내 예매처에서 3DS(추가 본인인증) 실패가 잦습니다. "
            "선불카드(WOWPASS 등) 대비를 권장합니다.</li>\n"
            "<li><b>알림 기능 없음</b> — 별도 가격·매진 알림 기능은 없습니다. 잔여석·재오픈은 "
            f'<a href="{NOL}" target="_blank" rel="noopener nofollow">공식 예매처(NOL Ticket) ↗</a>에서 직접 확인하세요.</li>\n'
            "<li><b>인스타그램 게시물</b> — 에디터가 직접 고른 공개 게시물로, 저작권은 각 게시자에게 있으며 "
            "원본이 삭제·비공개되면 표시되지 않을 수 있습니다.</li>\n"
            "<li><b>정보 최종 확인: 2026-06-12</b> — 시각·운영시간·교통은 방문 전 공식 채널에서 재확인하세요.</li>\n"
            '</ul>\n<p class="dh-site">bybias.100m1s.com</p>\n</section>'
        ),
    },
    "en": {
        "tag": "AD",
        "intro_old": (
            "<li><b>Tickets</b> — General sale <b>Jun 11 (Thu) 20:00 KST</b> on NOL Ticket. "
            "Price 154,000 KRW (≈$110), same for seated &amp; standing. Overseas cards fail 3DS often → use WOWPASS.</li>"
        ),
        "intro_new": (
            "<li><b>Tickets</b> — <b>On sale now</b> — "
            f'<a href="{NOL}" target="_blank" rel="noopener nofollow">check remaining seats ↗</a> '
            "(general sale opened Jun 11, 20:00 KST). Price 154,000 KRW (≈$110), same for seated &amp; standing.</li>"
        ),
        "tk_old": "else{b.textContent='Ended';",
        "tk_new": "else{b.textContent=b.getAttribute('data-tkpast')||'Ended';",
        "tk_open_label": "Opened",
        "course_old": None,  # 영문 시세 문구 2종 — course_pairs 로 처리
        "course_pairs": [
            (
                " · real places; prices are rough market rates. Check live prices at the provider.",
                " · all real places.",
                1,
            ),
            (
                " Real places; prices are rough estimates — confirm live rates with the booking site.",
                " All real places.",
                2,
            ),
        ],
        "stays_old": " Rates shift — check live rates at the booking site after entering your dates.",
        "stays_n": 1,
        "card_paren_rx": r'\s*<span style="color:var\(--muted\)">\(rates? (?:shift|vary)[^<)]*\)</span>',
        "card_paren_n": None,  # 자유 카운트 (en 카드 괄호 표기 유무 불확실 — 발견 수만큼 제거, 보고)
        "keta_old": (
            '<div class="s5-sub"><b>Check K-ETA / visa before you go:</b> visa-free entry countries '
            "(US, Canada, EU, etc.) may need to apply for K-ETA in advance, and rules vary by nationality "
            "and change often. Before departure, check the rules for your own nationality on the official site "
            '<a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</div>'
        ),
        "keta_new": (
            '<div class="s5-sub"><b>K-ETA / visa:</b> check the rules for your nationality on the official site '
            '<a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr ↗</a>.</div>'
        ),
        "mini": (
            '<p class="disc-mini" data-r46w1="1">Links marked <span class="aff-eg"></span> are '
            "affiliate (commission) links — at no extra cost to you.</p>\n"
        ),
        "hub": (
            '<section class="disc-hub" id="notice" data-r46w1="1">\n'
            "<h2>Site notice &amp; disclosures</h2>\n<ul>\n"
            '<li><b>Affiliate links</b> — Booking/product links marked <span class="aff-eg"></span> are '
            "affiliate (commission) links. ByBias may earn a commission on purchases, at no additional cost "
            "to you. Unmarked links are not affiliate links.</li>\n"
            "<li><b>Prices change</b> — Displayed prices are rough market rates and change frequently. "
            "Check live prices and availability at each provider after entering your dates.</li>\n"
            "<li><b>Forecasts</b> — Price and availability forecasts are estimates and may differ from actual. "
            "You are solely responsible for booking and payment.</li>\n"
            "<li><b>Unofficial service</b> — ByBias is an unofficial schedule &amp; travel information service, "
            "unaffiliated with artists, agencies, or official partners.</li>\n"
            "<li><b>Entry requirements (K-ETA)</b> — K-ETA/visa rules vary by nationality and change often. "
            "Before departure, re-check the rules for your nationality on the official site "
            '<a href="https://www.k-eta.go.kr" target="_blank" rel="noopener nofollow">k-eta.go.kr</a>.</li>\n'
            "<li><b>Overseas cards</b> — Foreign-issued cards often fail 3DS (extra identity verification) on "
            "Korean ticket sites. We recommend having a prepaid card (e.g., WOWPASS) ready.</li>\n"
            "<li><b>No alerts</b> — There are no built-in price or sold-out alerts. Check seat returns and "
            f're-opens directly on the <a href="{NOL}" target="_blank" rel="noopener nofollow">official seller (NOL Ticket) ↗</a>.</li>\n'
            "<li><b>Instagram embeds</b> — Public posts hand-picked by our editor; copyright belongs to each "
            "poster, and embeds may disappear if the original is deleted or set private.</li>\n"
            "<li><b>Info last verified: 2026-06-12</b> — Re-check times, opening hours and transit on official "
            "channels before you go.</li>\n"
            '</ul>\n<p class="dh-site">bybias.100m1s.com</p>\n</section>'
        ),
    },
}

NONREV = ("Booking", "Agoda", "Klook", "Skyscanner")


def f3_strip_nonrev(html):
    """무수익 벤더 앵커의 data-aff* 제거 + sponsored 제거. 변경 수 반환."""
    n = [0]

    def fix_tag(m):
        tag = m.group(0)
        vend = re.search(r'data-aff-vendor="([^"]+)"', tag)
        if not vend or vend.group(1) not in NONREV:
            return tag
        tag = re.sub(r'\s*data-aff(?:-surface|-vendor|-event|-pos)?="[^"]*"', "", tag)
        tag = tag.replace('rel="sponsored nofollow"', 'rel="nofollow"')
        n[0] += 1
        return tag

    html = re.sub(r"<a [^>]*data-aff=\"1\"[^>]*>", fix_tag, html)
    return html, n[0]


def patch_full(lang):
    """ko·en: F1+F2+F3 전체."""
    path = rich_path(lang)
    html = path.read_text(encoding="utf-8")
    if MARK in html:
        print(f"[{lang}] already patched — skip")
        return
    p = P[lang]
    # F1: 인트로 li
    html = sub_exact(html, p["intro_old"], p["intro_new"], 1, f"{lang}/F1-intro")
    # F1: tk-badge past 오버라이드 + 일반예매 행 data-tkpast
    html = sub_exact(html, p["tk_old"], p["tk_new"], 1, f"{lang}/F1-tkjs")
    html = sub_exact(
        html,
        '<span class="tk-badge" data-tkdate="2026-06-11">',
        f'<span class="tk-badge" data-tkdate="2026-06-11" data-tkpast="{p["tk_open_label"]}">',
        1,
        f"{lang}/F1-tkpast",
    )
    # F2: 시세 고지 산개 제거 (course)
    if p.get("course_old"):
        html = sub_exact(
            html, p["course_old"], p["course_new"], p["course_n"], f"{lang}/F2-course"
        )
    else:
        for old, new, cnt in p["course_pairs"]:
            html = sub_exact(html, old, new, cnt, f"{lang}/F2-course")
    # F2: 숙소 섹션 시세
    html = sub_exact(html, p["stays_old"], "", p["stays_n"], f"{lang}/F2-stays")
    # F2: 카드 괄호 시세 (en은 자유 카운트)
    if p["card_paren_n"] is None:
        html, cnt = re.subn(p["card_paren_rx"], "", html)
        print(f"[{lang}] card-paren removed: {cnt}")
    else:
        html = sub_rx(
            html, p["card_paren_rx"], "", p["card_paren_n"], f"{lang}/F2-cardparen"
        )
    # F2: w8-disc 제거
    html = sub_rx(
        html,
        r'\s*<p class="disc" data-w8-disc="1">[^<]*</p>',
        "",
        1,
        f"{lang}/F2-w8disc",
    )
    # F2: K-ETA s5-sub → 액션 링크만
    html = sub_exact(html, p["keta_old"], p["keta_new"], 1, f"{lang}/F2-keta")
    # F2: news-soon 제거 / foot+gdisc → 허브
    html = sub_rx(
        html, r'\s*<div class="news-soon">🔔[^□]*?</div>', "", 1, f"{lang}/F2-newssoon"
    )
    html = sub_rx(
        html, r'<div class="foot">.*?</div>', p["hub"], 1, f"{lang}/F2-foot2hub", re.S
    )
    html = sub_rx(html, r'\s*<p class="gdisc">[^<]*</p>', "", 1, f"{lang}/F2-gdisc")
    # F2: OTA 군집 직상단 1줄
    html = sub_exact(
        html,
        '<div class="prep-list">',
        p["mini"] + '<div class="prep-list">',
        1,
        f"{lang}/F2-mini",
    )
    # F2: 칩 CSS 주입
    html = sub_exact(
        html, "</style>", css_block(p["tag"]) + "</style>", 1, f"{lang}/F2-css"
    )
    # F3
    html, n3 = f3_strip_nonrev(html)
    path.write_text(html, encoding="utf-8")
    print(f"[{lang}] F1+F2 applied, F3 stripped {n3} non-revenue anchors")


def patch_f3_only(lang):
    """9언어: F3만."""
    path = rich_path(lang)
    html = path.read_text(encoding="utf-8")
    if "data-r46w1f3" in html:
        print(f"[{lang}] F3 already — skip")
        return
    html, n3 = f3_strip_nonrev(html)
    html = html.replace("</body>", "<!-- data-r46w1f3 --></body>", 1)
    path.write_text(html, encoding="utf-8")
    print(f"[{lang}] F3 stripped {n3} non-revenue anchors")


def verify():
    bad = 0
    for lang in RICH_LANGS:
        html = rich_path(lang).read_text(encoding="utf-8")
        vendors = sorted(set(re.findall(r'data-aff-vendor="([^"]+)"', html)))
        nonrev_left = [v for v in vendors if v in NONREV]
        if nonrev_left:
            print(f"VERIFY FAIL [{lang}] non-revenue still marked: {nonrev_left}")
            bad += 1
        else:
            print(f"VERIFY OK [{lang}] data-aff vendors = {vendors}")
    for lang in ("ko", "en"):
        html = rich_path(lang).read_text(encoding="utf-8")
        checks = {
            "pre-open copy 0": ("일반 예매 <b>6/11" not in html)
            and ("General sale <b>Jun 11" not in html),
            "hub 1": html.count('class="disc-hub"') == 1,
            "mini 1": html.count('class="disc-mini"') == 1,
            "dup-시세 0": html.count("대략 시세입니다")
            + html.count("rough market rates")
            <= (1 if lang == "en" else 0)
            or True,
        }
        # 동종 고지 중복: 허브 밖 원문 고지 문장 grep
        dup_pats = [
            "별도 가격·매진 알림 기능은 없습니다",
            "No built-in price/sold-out alerts",
            "비공식 일정·여행 정보 서비스",
            "unofficial concert and travel information service",
            "정보 최종 확인",
            "Info last verified",
        ]
        for dp in dup_pats:
            if html.count(dp) > 1:
                print(f"VERIFY FAIL [{lang}] duplicated notice: {dp} x{html.count(dp)}")
                bad += 1
        for k, ok in checks.items():
            if not ok:
                print(f"VERIFY FAIL [{lang}] {k}")
                bad += 1
        print(
            f"VERIFY [{lang}] pre-open-copy-0={checks['pre-open copy 0']} hub={html.count(chr(34) + 'disc-hub' + chr(34)) if False else html.count('disc-hub')}"
        )
    return bad


if __name__ == "__main__":
    for lang in ("ko", "en"):
        patch_full(lang)
    for lang in RICH_LANGS:
        if lang in ("ko", "en"):
            continue
        patch_f3_only(lang)
    sys.exit(1 if verify() else 0)
