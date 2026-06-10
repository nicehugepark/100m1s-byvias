#!/usr/bin/env python3
"""ByBias 홈(메인) 재설계 패치 — DOC-20260611-DSN-001 집행.

dist/<lang>/index.html (11언어) 에 다음을 멱등(idempotent) 적용:
  P0 ① 첫화면 hero 재구성 (eyebrow 칩 + 햇살 무드 배경) — §1
  P0 ② 이번 주 임박 핫이벤트 모듈 (client-side, D-day 임박 3~5건) — §2
  P1 ③ 고스트 워터마크 강등(.10→.06, 64→52px) — §3.1
  P1 ④ 홈 토큰 1벌 (radius 3단·폰트 5단·햇살 토큰) + 신규 컴포넌트 적용 — §4

dist HTML이 라이브 SSOT (FLR-20260611-TEC-001: HTML은 dist 단일 SSOT 확인).
generate.py 는 stale → dist 직접 패치. 멱등 마커로 재실행 안전.

구조·CSS·JS = 11언어 공통. hero eyebrow·비팬 카피 = ko/en 만 (DSN §5.3),
나머지 9언어는 영어 fallback (구조는 동일, 텍스트만 후속 번역).

실행: python3 tools/home_redesign_patch.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

LANGS = ["ko", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

# ── 멱등 마커 ──────────────────────────────────────────────
CSS_MARK = "/* HOME-REDESIGN-v1 */"
HERO_MARK = "<!-- HERO-REDESIGN-v1 -->"
HOTWEEK_MARK = "<!-- HOTWEEK-v1 -->"

# ── §4 토큰 + 신규 컴포넌트 CSS (전 언어 공통) ──────────────
# :root 에 추가할 토큰 (라이트). 다크는 별도 블록.
ROOT_TOKENS = (
    "--r-sm:6px;--r-md:10px;--r-lg:16px;"
    "--fs-cap:12px;--fs-sm:13px;--fs-base:14px;--fs-lg:16px;--fs-h1:28px;"
    "--sun-1:#FFF4D1;--sun-2:#FFF9E8;--sun-deep:#E8C063;"
    "--chip-info:#185FA5;--chip-info-bg:#E6F1FB;"
    "--chip-purple:#6B3FA0;--chip-purple-bg:#F0E9F9;"
    "--chip-green:#0F6E56;--chip-green-bg:#E1F5EE;"
    "--chip-red:#A32D2D;--chip-red-bg:#FCEBEB;"
)
ROOT_TOKENS_DARK = "--sun-1:#3a2e12;--sun-2:#2a2210;--sun-deep:#6b5320;"

# 라이브/소스의 첫 :root{} 가 풀페이지 컨텍스트에서 --accent 이후로 잘리는
# 선존 버그(라이브 confirm: --sun-chip-bg/--sun-chip-ink 미해결, rule0 len=108)가 있어
# 첫 :root 에 토큰을 덧붙이면 함께 드롭된다. 따라서 토큰은 style 말미에 별도 :root{} 로 주입한다.
# (별도 rule 은 정상 파싱됨 — .hero/.ghost 컴포넌트 규칙 적용 confirm.)
# eyebrow 가 쓰는 --sun-chip-ink 라이트값도 여기서 재선언(선존 버그 우회 겸 fix).
COMPONENT_ROOT = ":root{--sun-chip-ink:#7A5A12;" + ROOT_TOKENS + "}"
COMPONENT_ROOT_DARK = (
    "@media(prefers-color-scheme:dark){:root{--sun-chip-ink:#F2D58A;"
    + ROOT_TOKENS_DARK
    + "}}"
)

# 신규 컴포넌트 규칙 (style 블록 말미에 1회 주입). RTL 미러 1줄 포함.
COMPONENT_CSS = (
    CSS_MARK
    + COMPONENT_ROOT
    + COMPONENT_ROOT_DARK
    # hero
    + ".hero{position:relative;overflow:hidden;border-radius:var(--r-lg);"
    "padding:30px 22px 24px;margin:8px 0 14px;"
    "background:radial-gradient(120% 80% at 80% 0%,var(--sun-1) 0%,var(--sun-2) 42%,var(--bg) 74%)}"
    ".hero::after{content:'';position:absolute;inset:0;pointer-events:none;z-index:0;"
    "background:repeating-radial-gradient(circle at 88% -10%,transparent 0 38px,rgba(232,192,99,.05) 38px 40px)}"
    "[dir=rtl] .hero{background:radial-gradient(120% 80% at 20% 0%,var(--sun-1) 0%,var(--sun-2) 42%,var(--bg) 74%)}"
    "[dir=rtl] .hero::after{background:repeating-radial-gradient(circle at 12% -10%,transparent 0 38px,rgba(232,192,99,.05) 38px 40px)}"
    ".hero>*{position:relative;z-index:1}"
    ".hero h1{font-size:var(--fs-h1);line-height:1.25;margin:8px 0 4px}"
    ".eyebrow{display:inline-block;font-size:var(--fs-cap);font-weight:600;"
    "background:var(--sun-2);border:1px solid var(--sun-deep);color:var(--sun-chip-ink);"
    "border-radius:var(--r-sm);padding:3px 10px;margin:0}"
    # hotweek
     + ".hotweek{margin:0 0 18px}"
    ".hotweek-h{display:flex;align-items:baseline;gap:8px;font-size:var(--fs-lg);font-weight:600;margin:0 0 10px}"
    ".hotweek-h .hw-count{color:var(--muted);font-size:var(--fs-sm);font-weight:400}"
    ".hotrow{display:flex;gap:10px;overflow-x:auto;scroll-snap-type:x mandatory;padding-bottom:4px;"
    "-webkit-overflow-scrolling:touch}"
    ".hotcard{flex:0 0 78%;max-width:300px;scroll-snap-align:start;position:relative;text-decoration:none;"
    "color:var(--ink);border:1px solid var(--line);border-radius:var(--r-md);padding:13px 14px;"
    "background:var(--card);border-inline-start:4px solid var(--stripe,var(--accent))}"
    ".hotcard:hover{border-color:var(--accent)}"
    ".hotcard .hc-art{font-weight:600;font-size:var(--fs-base);margin:0 0 2px}"
    ".hotcard .hc-meta{color:var(--muted);font-size:var(--fs-sm);margin:0}"
    ".dday-hot{display:inline-flex;align-items:center;font-size:var(--fs-cap);font-weight:700;"
    "color:#fff;background:var(--accent);border-radius:var(--r-sm);padding:2px 8px;margin:0 0 8px}"
    "@media(min-width:640px){.hotrow{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));overflow:visible}"
    ".hotcard{flex:initial;max-width:none}}"
    # §3.1 고스트 강등
     + ".ghost{opacity:.06;font-size:52px;bottom:-10px}"
)


def patch_css(html: str) -> str:
    if CSS_MARK in html:
        return html  # 멱등
    # 토큰(:root 라이트/다크) + 컴포넌트 규칙을 한 덩어리로 </style> 직전 주입.
    # 첫 :root 덧붙이기는 선존 truncation 버그로 함께 드롭되므로 사용 안 함(상단 주석).
    return html.replace("</style>", COMPONENT_CSS + "</style>", 1)


# ── §1 hero 래핑 + eyebrow ────────────────────────────────
EYEBROW = {
    "ko": "K-pop 투어 · 항공·숙소 타이밍",
    "en": "K-pop tours · flight &amp; stay timing",
}
EYEBROW_FALLBACK = EYEBROW["en"]  # 9언어 후속 번역 전까지 영어 fallback (DSN §5.3)


def _content_anchor(html: str) -> int:
    """hero 본문 끝 = 본격 콘텐츠 시작점.
    ko = <div class="hubfilter"> (검색/필터 UI 존재).
    그 외 9언어 = hubfilter 없이 바로 <div class="tabs"> .
    둘 중 먼저 나오는 위치를 앵커로 사용 (못 찾으면 -1)."""
    cands = [html.find('<div class="hubfilter">'), html.find('<div class="tabs"')]
    cands = [i for i in cands if i >= 0]
    return min(cands) if cands else -1


def patch_hero(html: str, lang: str) -> str:
    if HERO_MARK in html:
        return html
    # hero 블록 = <div class="top">...</div> 다음의 <h1>...sub들... 을 .hero 로 감싼다.
    # top div 닫힘 직후 ~ 콘텐츠 앵커(hubfilter|tabs) 직전을 hero 본문으로 본다.
    top_close = "<span>bybias.100m1s.com</span></div>"
    i_top = html.find(top_close)
    i_hub = _content_anchor(html)
    if i_top < 0 or i_hub < 0 or i_hub < i_top:
        return html
    i_body = i_top + len(top_close)
    inner = html[i_body:i_hub]  # \n<h1>..</h1>\n<p class=sub>..</p>(..) \n
    eyebrow = EYEBROW.get(lang, EYEBROW_FALLBACK)
    eyebrow_html = f'<span class="eyebrow">{eyebrow}</span>'
    hero = (
        f'\n{HERO_MARK}\n<div class="hero">\n{eyebrow_html}'
        + inner.rstrip("\n ")
        + "\n</div>\n"
    )
    return html[:i_body] + hero + html[i_hub:]


# ── §2 hotweek 모듈 (client-side) ─────────────────────────
# hubfilter 직전에 빈 컨테이너 + 스크립트 삽입. 스크립트가 콘서트탭 카드에서
# D-day 임박 3~5건을 골라 채운다. 0건이면 컨테이너 자체 미표시(빈 박스 금지).
HOTWEEK_TITLE = {
    "ko": "이번 주 임박",
    "en": "Closing this week",
}
HOTWEEK_TITLE_FALLBACK = HOTWEEK_TITLE["en"]
# {n}건 / {n} — 단순 카운트. 복수 규칙 회피 위해 숫자만 + 라벨.
HOTWEEK_UNIT = {
    "ko": "건",
    "en": "",  # en: "{n}" 단독
}


def hotweek_block(lang: str) -> str:
    title = HOTWEEK_TITLE.get(lang, HOTWEEK_TITLE_FALLBACK)
    unit = HOTWEEK_UNIT.get(lang, "")
    # JS: 콘서트 그리드(.tp-c .ecard)에서 data-date 미래·임박순 정렬 후 상위 5건.
    # 카드 텍스트에서 아티스트(.a) + 메타(.c) 추출, D-day 계산. 0건이면 숨김.
    # 스크립트가 카드(하단)보다 먼저 위치하므로 DOM 완성 후 실행(DOMContentLoaded).
    js = (
        "(function(){function run(){try{"
        "var box=document.getElementById('hotweek');if(!box)return;"
        "var T=new Date();T.setHours(0,0,0,0);"
        "var cards=document.querySelectorAll('.tp-c .ecard');var L=[];"
        "for(var i=0;i<cards.length;i++){var c=cards[i];"
        "var dd=c.querySelector('.dday[data-date]');if(!dd)continue;"
        "var p=(dd.getAttribute('data-date')||'').split('-');if(p.length!==3)continue;"
        "var ev=new Date(+p[0],+p[1]-1,+p[2]);ev.setHours(0,0,0,0);"
        "var diff=Math.round((ev-T)/86400000);if(diff<0||diff>14)continue;"
        "var art=(c.querySelector('.a')||{}).textContent||'';"
        "var meta=(c.querySelector('.c')||{}).textContent||'';"
        "L.push({href:c.getAttribute('href'),art:art.trim(),meta:meta.replace(/D-\\d+|D-DAY/,'').trim(),diff:diff});}"
        "L.sort(function(a,b){return a.diff-b.diff;});L=L.slice(0,5);"
        "if(!L.length){return;}"  # 0건 → 모듈 생략
        "var dlabel=function(d){return d===0?'D-DAY':'D-'+d;};"
        "var esc=function(s){var t=document.createElement('div');t.textContent=s;return t.innerHTML;};"
        "var rows='';for(var k=0;k<L.length;k++){var it=L[k];"
        "rows+='<a class=\"hotcard\" href=\"'+it.href+'\">'"
        "+'<span class=\"dday-hot\" dir=\"ltr\">'+dlabel(it.diff)+'</span>'"
        "+'<div class=\"hc-art\">'+esc(it.art)+'</div>'"
        "+'<div class=\"hc-meta\">'+esc(it.meta)+'</div></a>';}"
        "var unit=" + repr(unit) + ";"
        "box.innerHTML='<div class=\"hotweek-h\">'+"
        + repr(title)
        + "+' <span class=\"hw-count\">'+L.length+unit+'</span></div>'"
        "+'<div class=\"hotrow\">'+rows+'</div>';"
        "box.style.display='block';"
        "}catch(e){}}"
        "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',run);}else{run();}"
        "})();"
    )
    return (
        f"{HOTWEEK_MARK}\n"
        '<section class="hotweek" id="hotweek" style="display:none" aria-label="'
        + title
        + '"></section>\n'
        f"<script>{js}</script>\n"
    )


def patch_hotweek(html: str, lang: str) -> str:
    if HOTWEEK_MARK in html:
        return html
    # 콘텐츠 앵커(hubfilter|tabs) 직전에 hotweek 모듈 삽입.
    i_hub = _content_anchor(html)
    if i_hub < 0:
        return html
    return html[:i_hub] + hotweek_block(lang) + html[i_hub:]


def unpatch(html: str) -> str:
    """주입된 3블록(CSS/hero/hotweek)을 마커 기준으로 제거 → 원본 복구.
    --repatch 시 stale 버전(예: 동시세션이 구버전 흡수 commit)을 깨끗이 재적용하기 위함.
    멱등: 마커 없으면 무변경."""
    import re

    # 1) hero 언랩: <!-- HERO-REDESIGN-v1 -->\n<div class="hero">\n<eyebrow> ... </div>
    #    eyebrow 삽입 + 래퍼만 제거하고 안쪽 h1/sub 들은 보존.
    m = re.search(
        r"\n?"
        + re.escape(HERO_MARK)
        + r'\n<div class="hero">\n<span class="eyebrow">[^<]*</span>',
        html,
    )
    if m:
        # 래퍼 시작 제거
        html = html[: m.start()] + "\n" + html[m.end() :]
        # 대응하는 hero 닫는 </div>\n 제거 (hotweek 마커 또는 콘텐츠 앵커 직전의 </div>)
        # hero 본문 끝 = 다음 HOTWEEK_MARK 또는 앵커 직전 "\n</div>\n"
        html = html.replace("\n</div>\n" + HOTWEEK_MARK, "\n" + HOTWEEK_MARK, 1)
    # 2) hotweek 블록 제거: 마커 + section + script (한 줄씩)
    html = re.sub(
        re.escape(HOTWEEK_MARK)
        + r'\n<section class="hotweek"[^>]*></section>\n<script>.*?</script>\n',
        "",
        html,
        flags=re.S,
    )
    # 3) CSS 블록 제거: CSS_MARK 부터 </style> 직전까지
    i = html.find(CSS_MARK)
    if i >= 0:
        j = html.find("</style>", i)
        if j >= 0:
            html = html[:i] + html[j:]
    return html


def process(lang: str, repatch: bool = False) -> str:
    f = DIST / "index.html" if lang == "ko" else DIST / lang / "index.html"
    html = f.read_text(encoding="utf-8")
    before = html
    if repatch:
        html = unpatch(html)
    html = patch_css(html)
    html = patch_hero(html, lang)
    html = patch_hotweek(html, lang)
    if html != before:
        f.write_text(html, encoding="utf-8")
        return f"patched  {lang}"
    return f"skip(idempotent)  {lang}"


def main():
    import sys

    repatch = "--repatch" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    langs = only if only else LANGS
    for lang in langs:
        print(process(lang, repatch=repatch))


if __name__ == "__main__":
    main()
