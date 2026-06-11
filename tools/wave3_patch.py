#!/usr/bin/env python3
"""wave3 patch — R26 판정 P0 3건 + P1 6건 + 조니 권고 (멱등).

대상: dist/ 11언어 home + ko/en 코스(twice-thisisfor-seoul) + 9언어 langbar→langpick.
근거: R26 판정단·조니 캡처 (/tmp/bybias-r26, /tmp/jony-r26).
CR 토큰 (WCAG): today #C8295F/white=5.33, past dark #2a2820/#9c998f=5.18,
                light #eeece5/#6b6a64=4.59, warn dark #FF8A8A/card=7.26.
"""

import json
import re
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"
LANG_DIRS = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]
MARK_HOME = "/* WAVE3-HOME-v1 */"
MARK_COURSE = "/* WAVE3-COURSE-v1 */"

# ── P0-A① 스카이라인 잔존 — wave2가 .ecard::after만 제거, .hero::before 별개 셀렉터 잔존 ──
SKY_V2 = (
    ".hero::before{content:'';position:absolute;left:0;right:0;bottom:0;height:64px;"
    "z-index:0;color:var(--sky);opacity:.16;"
    "-webkit-mask:url(/assets/gen/city-skyline.svg) bottom/auto 64px repeat-x;"
    "mask:url(/assets/gen/city-skyline.svg) bottom/auto 64px repeat-x;"
    "background:currentColor;pointer-events:none}"
)
SKY_V3 = ".hero::before{color:#fff !important;opacity:.22 !important}"

# ── P1① 티켓팅 hero 승격 라벨 (11언어) ──
TK_LABEL = {
    "": ("오늘 티켓팅 오픈", "티켓팅 오픈 임박"),
    "en": ("Tickets open today", "Tickets opening soon"),
    "ja": ("本日チケット発売", "チケット発売間近"),
    "zh-cn": ("今日开票", "即将开票"),
    "zh-tw": ("今日開票", "即將開票"),
    "es": ("Entradas a la venta hoy", "Venta de entradas inminente"),
    "th": ("เปิดจองบัตรวันนี้", "ใกล้เปิดจองบัตร"),
    "id": ("Tiket dibuka hari ini", "Tiket segera dibuka"),
    "pt": ("Ingressos à venda hoje", "Venda de ingressos em breve"),
    "ar": ("التذاكر تُفتح اليوم", "فتح التذاكر قريبًا"),
    "vi": ("Mở bán vé hôm nay", "Sắp mở bán vé"),
}

HOME_CSS = (
    f"{MARK_HOME}"
    # P0-A② 종료 badge — 인라인 #eeece5를 var(--pastbg)로 치환 + 다크 토큰
    ":root{--pastbg:#eeece5}"
    # P0-A① 홈 .disc — 기존 다크 override가 라이트 정의보다 앞이라 캐스케이드 패배 → 말미 재선언
    "@media(prefers-color-scheme:dark){:root{--pastbg:#2a2820}"
    ".disc{background:#1d1c15;border-color:var(--line);color:var(--muted)}}"
    # P1② 종료 카드 desaturate — 키컬러 tint 제거(위계 역전 해소)
    '.grid .ecard:has(.badge[style*="--pastbg"])'
    "{background:var(--card)!important;border-inline-start-color:var(--line)!important}"
    '.grid .ecard:has(.badge[style*="--pastbg"]) .abadge{filter:grayscale(.85);opacity:.7}'
    '.grid .ecard:has(.badge[style*="--pastbg"]) .ghost{display:none}'
    # P1⑥ badge↔D-chip 중심 Δy 정렬 — 둘 다 absolute, 수직 중심 일치(badge h≈22, dday h≈15)
    ".grid .ecard{padding-bottom:44px}"
    ".grid .ecard>.badge{position:absolute;bottom:13px;inset-inline-start:14px;margin:0;z-index:2}"
    ".grid .ecard .dday{bottom:17px}"
    # 조니③ 월별 위계 구분 divider
    ".mdiv{grid-column:1/-1;font-size:12px;font-weight:700;color:var(--muted);"
    "letter-spacing:.3px;margin:8px 0 -4px}"
    # P1③ 1280 임박 레일 — 우측 페이드(넘김 affordance) + thin scrollbar 복원
    "@media(min-width:1024px){.hotweek .hotrow{scrollbar-width:thin;"
    "-webkit-mask:linear-gradient(90deg,#000 calc(100% - 56px),transparent);"
    "mask:linear-gradient(90deg,#000 calc(100% - 56px),transparent)}"
    "[dir=rtl] .hotweek .hotrow{"
    "-webkit-mask:linear-gradient(270deg,#000 calc(100% - 56px),transparent);"
    "mask:linear-gradient(270deg,#000 calc(100% - 56px),transparent)}}"
)

# 조니③ 월별 divider — Intl로 11언어 자동 로컬라이즈, 종료 그리드 제외
MONTH_JS = (
    "<script>(function(){try{"
    "var fmt=new Intl.DateTimeFormat(document.documentElement.lang||'en',"
    "{month:'short',year:'numeric'});"
    "document.querySelectorAll('.tp-c .grid').forEach(function(g){"
    "if(g.querySelector('.badge[style*=\"--pastbg\"]'))return;"
    "var cards=g.querySelectorAll(':scope>.ecard');if(cards.length<5)return;"
    "var cur='';cards.forEach(function(c){"
    "var dd=c.querySelector('.dday[data-date]');if(!dd)return;"
    "var d=(dd.getAttribute('data-date')||'').slice(0,7);if(!d||d===cur)return;cur=d;"
    "var p=d.split('-');var el=document.createElement('div');el.className='mdiv';"
    "el.textContent=fmt.format(new Date(+p[0],+p[1]-1,1));g.insertBefore(el,c);});});"
    "}catch(e){}})();</script>"
)

COURSE_CSS = (
    f"{MARK_COURSE}"
    ":root{--pastbg:#eeece5}"
    "@media(prefers-color-scheme:dark){:root{--pastbg:#2a2820}"
    # P0-A④ .warn 막차 경고 — 다크 #A32D2D 2.97 → #FF8A8A 7.26 (.tldr li .warn 동일 specificity)
    ".tldr li .warn,.warn{color:#FF8A8A}}"
)

# 코스 toc 14개 id (h2 순서 기준 — ko/en 동일 구조)
H2_IDS = [
    "sec-arrive",
    "sec-venue",
    "sec-schedule",
    "sec-staytips",
    "sec-return",
    "sec-c2",
    "sec-c4",
    "sec-c7",
    "sec-stays",
    "sec-sources",
    "sec-tourstops",
    "sec-videos",
    "sec-official",
    "sec-ticketing",
]

# toc 클릭 시 radio-hidden 코스 패널(.sl-panel) 자동 활성
TOC_JS = (
    "<script>(function(){var t=document.querySelector('nav.toc');if(!t)return;"
    "t.addEventListener('click',function(ev){var a=ev.target.closest('a');if(!a)return;"
    "var id=(a.getAttribute('href')||'').slice(1);var el=id&&document.getElementById(id);"
    "if(!el)return;var p=el.closest('.sl-panel');if(!p)return;"
    "var m=p.className.match(/sl-(\\d)/);if(!m)return;"
    "var r=document.getElementById('sl-'+m[1]);if(r&&!r.checked)r.checked=true;});})();"
    "</script>"
)

EMOJI_RE = re.compile("[\U0001f000-\U0001fbff☀-➿️⬀-⯿]+")


def collect_ticketing():
    """루트(ko) 이벤트 페이지에서 data-tkdate 수집 — 하드코딩 금지, 데이터 유도."""
    out = []
    for f in sorted(DIST.glob("*.html")):
        h = f.read_text()
        dates = sorted(set(re.findall(r'data-tkdate="(\d{4}-\d{2}-\d{2})"', h)))
        if dates:
            out.append((f.name, dates))
    return out


def tk_entries(html, lang, tk_pages):
    """해당 언어 home의 ecard에서 art/meta를 추출해 TKO 배열 생성."""
    e0, e1 = TK_LABEL.get(lang, TK_LABEL["en"])
    entries = []
    for slug, dates in tk_pages:
        # 서브디렉토리 언어도 이벤트 페이지는 동일 디렉토리 상대경로 (../ 불필요) — 양쪽 허용
        m = re.search(
            rf'<a class="ecard" href="((?:\.\./)?{re.escape(slug)})"[^>]*>.*?<div class="a"><bdi>([^<]*)</bdi></div>'
            r".*?<div class=\"c\">(.*?)<span class=\"dday\"",
            html,
            re.S,
        )
        if not m:
            continue
        href, art, meta = (
            m.group(1),
            m.group(2),
            re.sub(r"<[^>]+>", "", m.group(3)).strip(" ·"),
        )
        for d in dates:
            entries.append(
                {
                    "h": href + "#sec-ticketing",
                    "d": d,
                    "a": art,
                    "m": meta.strip(),
                    "e0": e0,
                    "e1": e1,
                }
            )
    return entries


def patch_home(path, lang, tk_pages):
    h = path.read_text()
    if MARK_HOME in h:
        return False
    orig = h
    # ① 스카이라인 제거 (P0 회귀 — .hero::before 양 레이어)
    h = h.replace(SKY_V2, "").replace(SKY_V3, "")

    # ② 조니① 히어로 본문 문단 제거 — 헤드라인만
    def hero_strip(m):
        inner = re.sub(r'<p class="sub"[^>]*>.*?</p>\s*', "", m.group(1), flags=re.S)
        return '<div class="hero">' + inner + "</div>"

    h = re.sub(r'<div class="hero">(.*?)</div>', hero_strip, h, count=1, flags=re.S)
    # ③ 종료 badge 인라인 → 다크 변수
    h = h.replace("background:#eeece5", "background:var(--pastbg,#eeece5)")
    # ④ P1① 티켓팅 hero 승격 (D-day 기반 동적)
    tko = tk_entries(h, lang, tk_pages)
    anchor = "var spot=document.getElementById('hero-spot');if(spot&&L.length){var s0=L[0];spot.setAttribute("
    if tko and anchor in h:
        inject = (
            "var TKO=" + json.dumps(tko, ensure_ascii=False) + ";var tkb=null;"
            "for(var q=0;q<TKO.length;q++){var tp=TKO[q].d.split('-');"
            "var te=new Date(+tp[0],+tp[1]-1,+tp[2]);te.setHours(0,0,0,0);"
            "var tdf=Math.round((te-T)/86400000);"
            "if(tdf>=0&&tdf<=2&&(tkb===null||tdf<tkb.df))tkb={df:tdf,o:TKO[q]};}"
            "var spot=document.getElementById('hero-spot');"
            "if(spot&&tkb){var o=tkb.o;spot.setAttribute('href',o.h);"
            "spot.innerHTML='<span class=\"hs-dd\"><b dir=\"ltr\">'+dlabel(tkb.df)+'</b></span>'"
            "+'<div class=\"hs-body\"><span class=\"hs-eye\">'+esc(tkb.df===0?o.e0:o.e1)+'</span>'"
            "+'<p class=\"hs-art\">'+esc(o.a)+'</p>'+'<p class=\"hs-meta\">'+esc(o.m)+'</p></div>'"
            '+\'<span class="hs-go" aria-hidden="true">\\u203a</span>\';'
            "spot.classList.add('on');}"
            "else if(spot&&L.length){var s0=L[0];spot.setAttribute("
        )
        h = h.replace(anchor, inject)
        h = h.replace(
            "var hs=(spot&&L.length)?1:0;", "var hs=(spot&&!tkb&&L.length)?1:0;"
        )
    # ⑤ CSS + 월별 divider JS
    h = h.replace("</style>", HOME_CSS + "</style>", 1)
    h = h.replace("</body>", MONTH_JS + "</body>", 1)
    if h != orig:
        path.write_text(h)
        return True
    return False


def patch_course(path):
    h = path.read_text()
    if MARK_COURSE in h:
        return False
    orig = h
    # P0-B 오늘 오픈 칩 3.67 → 5.33
    h = h.replace(
        ".tk-badge--today{color:#fff;background:#E84A7F}",
        ".tk-badge--today{color:#fff;background:#C8295F}",
    )
    # P0-A②③ past/cat 칩 다크 변수화
    h = h.replace("background:#eeece5", "background:var(--pastbg,#eeece5)")
    # P1⑤ 10.5px → 12px (dur·badge--cat·igmeta·ig-disc 클래스 정의 4건 → 인스턴스 35개)
    h = h.replace("font-size:10.5px", "font-size:12px")
    # P0-C IG embed — iframe 흰 블록 제거(placeholder 그라데이션 노출) + crop 완화(400→326=IG 최소폭)
    h = h.replace(
        ".ig-embed iframe{position:absolute;top:-54px;left:50%;width:400px;max-width:none;"
        "height:540px;transform:translateX(-50%);border:0;display:block;background:#fff}",
        ".ig-embed iframe{position:absolute;top:-54px;left:50%;width:326px;max-width:none;"
        "height:540px;transform:translateX(-50%);border:0;display:block;background:transparent}",
    )
    # 조니② toc 5 → h2 14 전체
    h2s = list(re.finditer(r"<h2([^>]*)>(.*?)</h2>", h, re.S))
    if len(h2s) == len(H2_IDS):
        new_h, off = h, 0
        labels = []
        for i, m in enumerate(h2s):
            attrs, text = m.group(1), m.group(2)
            label = EMOJI_RE.sub("", re.sub(r"<[^>]+>", "", text)).split("—")[0].strip()
            labels.append(label)
            if "id=" not in attrs:
                ins = m.start(1) + off
                new_h = new_h[:ins] + f' id="{H2_IDS[i]}"' + new_h[ins:]
                off += len(f' id="{H2_IDS[i]}"')
        h = new_h
        toc = "".join(
            f'<a href="#{H2_IDS[i]}">{labels[i]}</a>' for i in range(len(H2_IDS))
        )
        h = re.sub(
            r'(<nav class="toc"[^>]*>).*?(</nav>)',
            r"\1" + toc + r"\2",
            h,
            count=1,
            flags=re.S,
        )
        h = h.replace("</body>", TOC_JS + "</body>", 1)
    # CSS 토큰
    h = h.replace("</style>", COURSE_CSS + "</style>", 1)
    if h != orig:
        path.write_text(h)
        return True
    return False


def langbar_to_langpick(path, lang):
    """P1④ 구세대 langbar → ko/en과 동일 langpick 드롭다운 (빌드 세대 통일)."""
    h = path.read_text()
    if "langbar" not in h:
        return False
    if "langpick" in h:
        # ko/en 신세대: 마크업은 langpick인데 구 .langbar CSS 잔재 → CSS만 제거
        h2 = re.sub(r'(?:\[dir="?rtl"?\] )?\.langbar[^{}]*\{[^}]*\}', "", h)
        if h2 != h:
            path.write_text(h2)
            return True
        return False
    m = re.search(r'<div class="langbar">(.*?)</div>', h, re.S)
    if not m:
        return False
    links = m.group(1)
    cur = re.search(r'<a class="lng"[^>]*aria-current="true"[^>]*>([^<]*)</a>', links)
    cur_name = cur.group(1) if cur else "Language"
    pick = (
        f'<details class="langpick"><summary aria-label="Language — {cur_name}">{cur_name}</summary>'
        f'<div class="langmenu">{links}</div></details>'
    )
    h = h.replace(m.group(0), pick, 1)
    # langbar CSS 제거 + langpick CSS 주입 (ko 빌드와 동일 룰)
    h = re.sub(r'(?:\[dir="?rtl"?\] )?\.langbar[^{}]*\{[^}]*\}', "", h)
    pick_css = (
        "/* WAVE3-LANGPICK */"
        ".langpick{margin:0 0 10px;display:flex;justify-content:flex-end}"
        ".langpick>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;"
        "gap:6px;min-height:36px;padding:6px 12px;border:1px solid var(--line);border-radius:8px;"
        "font-size:12px;font-weight:600;color:var(--muted);background:var(--card)}"
        ".langpick>summary::-webkit-details-marker{display:none}"
        '.langpick>summary::after{content:"▾";font-size:10px;color:var(--muted);'
        "transition:transform .2s cubic-bezier(0.16,1,0.3,1)}"
        ".langpick[open]>summary::after{transform:rotate(180deg)}"
        ".langpick>summary:hover{border-color:#c9c7bd}"
        ".langpick>summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
        ".langpick .langmenu{display:none;position:absolute;right:16px;margin-top:6px;z-index:5;"
        "flex-direction:column;min-width:160px;background:var(--card);border:1px solid var(--line);"
        "border-radius:10px;padding:6px;box-shadow:0 8px 24px rgba(0,0,0,.12)}"
        ".langpick[open] .langmenu{display:flex}"
        ".langpick .langmenu .lng{display:flex;align-items:center;min-height:40px;padding:8px 12px;"
        "border-radius:6px;font-size:13px;color:var(--muted);text-decoration:none}"
        '.langpick .langmenu .lng[aria-current="true"]{color:var(--accent);font-weight:600;background:#eef4fb}'
        ".langpick .langmenu .lng:hover{background:#f0eee6}"
        ".langpick .langmenu .lng:focus-visible{outline:2px solid var(--accent);outline-offset:-2px}"
        "@media(prefers-color-scheme:dark){.langpick .langmenu{box-shadow:0 8px 24px rgba(0,0,0,.5)}"
        '.langpick .langmenu .lng[aria-current="true"]{background:#1e2b3d}'
        ".langpick>summary:hover,.langpick .langmenu .lng:hover{background:#222}}"
        "[dir=rtl] .langpick{justify-content:flex-start}"
        "[dir=rtl] .langpick .langmenu{right:auto;left:16px}"
    )
    h = h.replace("</style>", pick_css + "</style>", 1)
    path.write_text(h)
    return True


def main():
    tk_pages = collect_ticketing()
    print("ticketing pages:", tk_pages)
    changed = []
    for lang in LANG_DIRS:
        idx = DIST / lang / "index.html" if lang else DIST / "index.html"
        if patch_home(idx, lang, tk_pages):
            changed.append(str(idx))
        if langbar_to_langpick(idx, lang):
            changed.append(str(idx) + " (langpick)")
    for f in [
        DIST / "twice-thisisfor-seoul.html",
        DIST / "en" / "twice-thisisfor-seoul.html",
    ]:
        if patch_course(f):
            changed.append(str(f))
    print(f"changed {len(changed)} files:")
    for c in changed:
        print(" ", c)


if __name__ == "__main__":
    main()
