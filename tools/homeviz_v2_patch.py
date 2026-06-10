#!/usr/bin/env python3
"""ByBias 홈 비주얼 2차 (HOMEVIZ-v2) — 11언어 일괄 패치.

R19 UGC 처방 "홈 = 상세의 예고편":
  1. [P0] 히어로 스포트라이트 — 가장 임박한 이벤트(min D-day)를 히어로 안에 대형 D-day +
     도시 스카이라인 실루엣 backdrop 으로 노출. (실사 이미지 0, CSS/SVG 그래픽만)
  2. [P0] 카드 비주얼 — .ecard 에 도시 스카이라인 실루엣 워터마크(공용 SVG, currentColor)
     + 기존 국기·키컬러 좌측 띠 유지. 이니셜 ghost 워터마크는 스카이라인으로 대체.
  3. [P0] 핫위크 긴급 톤 — D-day 칩·카드 좌측 띠를 붉은 계열로(기존 accent 파랑 → urgent red).

설계 원칙(트랩 회피):
  - 신규 AI 실사 0. 스카이라인은 비식별 일반 실루엣(FoP 안전) 단일 SVG.
  - 11언어 히어로 카피·핫위크 로컬라이즈 문자열 보존(추출 후 재사용).
  - 멱등(marker 가드): 재실행해도 중복 주입 0.
  - dist/ = 배포 SSOT. 자산은 dist/assets/gen + repo-root assets/gen 양쪽 동일(md5).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
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

# 히어로 스포트라이트 로컬라이즈 라벨 (eyebrow). D-day·아티스트·도시는 카드에서 추출되므로 무번역.
SPOTLIGHT_LABEL = {
    "ko": "가장 임박한 일정",
    "en": "Closing soonest",
    "ja": "締切が最も近い",
    "zh-cn": "最临近的日程",
    "zh-tw": "最臨近的行程",
    "es": "El más próximo",
    "th": "ใกล้ปิดที่สุด",
    "id": "Paling dekat",
    "pt": "Mais próximo",
    "ar": "الأقرب موعدًا",
    "vi": "Sắp đóng nhất",
}

# CSS (HOMEVIZ-v2) — </style> 직전 주입. 신규 색은 urgent red 1종만, 나머지 기존 토큰 재사용.
CSS_BLOCK = (
    "/* HOMEVIZ-v2 */"
    ":root{--urgent:#C62828;--urgent-bg:#FCE9E7;--sky:#11305a}"
    "@media(prefers-color-scheme:dark){:root{--urgent:#FF6B6B;--urgent-bg:#3a1f1d;--sky:#9ec3f0}}"
    # 카드 스카이라인 워터마크: 이니셜 ghost 대체. 좌하단, 키컬러(--stripe) 톤, 매우 옅게.
    ".ecard{padding-bottom:30px}"
    ".ecard .ghost{display:none}"  # 이니셜 워터마크 제거(스카이라인이 대체)
    ".ecard::after{content:'';position:absolute;left:0;right:0;bottom:0;height:30px;z-index:0;"
    "color:var(--stripe,var(--accent));opacity:.18;"
    "-webkit-mask:url(assets/gen/city-skyline.svg) bottom/auto 30px repeat-x;"
    "mask:url(assets/gen/city-skyline.svg) bottom/auto 30px repeat-x;"
    "background:currentColor}"
    "@media(prefers-color-scheme:dark){.ecard::after{opacity:.28}}"
    # 히어로 스카이라인 backdrop — 하단 풀블리드, sky 톤.
    ".hero::before{content:'';position:absolute;left:0;right:0;bottom:0;height:64px;z-index:0;"
    "color:var(--sky);opacity:.16;"
    "-webkit-mask:url(assets/gen/city-skyline.svg) bottom/auto 64px repeat-x;"
    "mask:url(assets/gen/city-skyline.svg) bottom/auto 64px repeat-x;"
    "background:currentColor;pointer-events:none}"
    # 히어로 스포트라이트 — 풀블리드 카드 느낌. 키컬러 좌측 굵은 띠 + 대형 D-day.
    ".hero-spot{display:none;margin:16px 0 0;border-radius:var(--r-md);background:var(--card);"
    "border:1px solid var(--line);border-inline-start:5px solid var(--stripe,var(--accent));"
    "padding:13px 15px;text-decoration:none;color:var(--ink);position:relative;overflow:hidden}"
    ".hero-spot.on{display:flex;align-items:center;gap:14px}"
    ".hero-spot:hover{border-color:var(--accent)}"
    ".hero-spot .hs-dd{flex:0 0 auto;display:flex;flex-direction:column;align-items:center;"
    "justify-content:center;min-width:62px;line-height:1;color:var(--urgent)}"
    ".hero-spot .hs-dd b{font-size:30px;font-weight:800;letter-spacing:-1px}"
    ".hero-spot .hs-dd small{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;"
    "color:var(--muted);margin-top:2px}"
    ".hero-spot .hs-body{min-width:0;flex:1}"
    ".hero-spot .hs-eye{font-size:11px;font-weight:700;color:var(--urgent);background:var(--urgent-bg);"
    "border-radius:var(--r-sm);padding:2px 8px;display:inline-block;margin:0 0 4px}"
    ".hero-spot .hs-art{font-weight:700;font-size:16px;margin:0;line-height:1.25}"
    ".hero-spot .hs-meta{color:var(--muted);font-size:13px;margin:1px 0 0}"
    ".hero-spot .hs-go{flex:0 0 auto;color:var(--muted);font-size:20px}"
    "[dir=rtl] .hero-spot .hs-go{transform:scaleX(-1)}"
    # 핫위크 긴급 톤 — D-day 칩·카드 좌측 띠를 붉은색으로(이번 주 임박 = 긴급).
    ".hotweek .dday-hot{background:var(--urgent)}"
    ".hotweek .hotcard{border-inline-start-color:var(--urgent)}"
    ".hotweek .hotcard:hover{border-color:var(--urgent)}"
    ".hotweek .hotweek-h{color:var(--urgent)}"
)

# 핫위크+스포트라이트 통합 스크립트. 기존 hotweek 스크립트를 대체.
# 로컬라이즈 문자열(__TITLE__/__UNIT__/__SPOT__)은 기존 파일에서 추출해 주입.
SCRIPT_TMPL = (
    "<script>(function(){function run(){try{"
    "var T=new Date();T.setHours(0,0,0,0);"
    "var cards=document.querySelectorAll('.tp-c .ecard');var L=[];"
    "for(var i=0;i<cards.length;i++){var c=cards[i];"
    "var dd=c.querySelector('.dday[data-date]');if(!dd)continue;"
    "var p=(dd.getAttribute('data-date')||'').split('-');if(p.length!==3)continue;"
    "var ev=new Date(+p[0],+p[1]-1,+p[2]);ev.setHours(0,0,0,0);"
    "var diff=Math.round((ev-T)/86400000);if(diff<0)continue;"
    "var art=(c.querySelector('.a')||{}).textContent||'';"
    "var meta=(c.querySelector('.c')||{}).textContent||'';"
    "L.push({href:c.getAttribute('href'),art:art.trim(),"
    "meta:meta.replace(/D-\\d+|D-DAY/,'').trim(),diff:diff});}"
    "L.sort(function(a,b){return a.diff-b.diff;});"
    "var dlabel=function(d){return d===0?'D-DAY':'D-'+d;};"
    "var esc=function(s){var t=document.createElement('div');t.textContent=s;return t.innerHTML;};"
    # 히어로 스포트라이트 = 가장 임박한 1건(미래 한정).
    "var spot=document.getElementById('hero-spot');"
    "if(spot&&L.length){var s0=L[0];"
    "spot.setAttribute('href',s0.href);"
    "spot.innerHTML='<span class=\"hs-dd\"><b dir=\"ltr\">'+dlabel(s0.diff)+'</b></span>'"
    '+\'<div class="hs-body"><span class="hs-eye">__SPOT__</span>\''
    "+'<p class=\"hs-art\">'+esc(s0.art)+'</p>'"
    "+'<p class=\"hs-meta\">'+esc(s0.meta)+'</p></div>'"
    '+\'<span class="hs-go" aria-hidden="true">\\u203a</span>\';'
    "spot.classList.add('on');}"
    # 핫위크 = 14일 이내 5건.
    "var box=document.getElementById('hotweek');if(!box)return;"
    "var H=[];for(var j=0;j<L.length;j++){if(L[j].diff<=14)H.push(L[j]);}H=H.slice(0,5);"
    "if(!H.length){return;}var rows='';"
    "for(var k=0;k<H.length;k++){var it=H[k];"
    "rows+='<a class=\"hotcard\" href=\"'+it.href+'\">'"
    "+'<span class=\"dday-hot\" dir=\"ltr\">'+dlabel(it.diff)+'</span>'"
    "+'<div class=\"hc-art\">'+esc(it.art)+'</div>'"
    "+'<div class=\"hc-meta\">'+esc(it.meta)+'</div></a>';}"
    "var unit='__UNIT__';"
    "box.innerHTML='<div class=\"hotweek-h\">'+'__TITLE__'"
    "+' <span class=\"hw-count\">'+H.length+unit+'</span></div>'"
    "+'<div class=\"hotrow\">'+rows+'</div>';box.style.display='block';"
    "}catch(e){}}"
    "if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',run);}"
    "else{run();}})();</script>"
)

# 기존 hotweek 스크립트(통째) 매칭 — 대체 대상.
OLD_SCRIPT_RE = re.compile(
    r"<script>\(function\(\)\{function run\(\)\{try\{var box=document\.getElementById\('hotweek'\).*?run\);\}else\{run\(\);\}\}\)\(\);</script>",
    re.DOTALL,
)
# 로컬라이즈 문자열 추출용.
TITLE_RE = re.compile(r"box\.innerHTML='<div class=\"hotweek-h\">'\+'([^']*)'")
UNIT_RE = re.compile(r"var unit='([^']*)';")


def lang_key(path: str) -> str:
    if path == "index.html":
        return "ko"
    return path.split("/")[0]


def patch(path: str) -> str:
    f = DIST / path
    html = f.read_text(encoding="utf-8")
    if "HOMEVIZ-v2" in html:
        return f"{path}: SKIP (이미 패치됨)"

    lk = lang_key(path)

    # 1) CSS 주입 (</style> 직전, 첫 번째만).
    if "</style>" not in html:
        return f"{path}: FAIL (</style> 없음)"
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

    # 2) 히어로 스포트라이트 앵커 주입 — </div> 닫는 hero 직후(<!-- HOTWEEK-v1 --> 직전).
    if "<!-- HOTWEEK-v1 -->" not in html:
        return f"{path}: FAIL (HOTWEEK 마커 없음)"
    spot_anchor = (
        '<a class="hero-spot" id="hero-spot" href="#" '
        'aria-label="' + SPOTLIGHT_LABEL.get(lk, SPOTLIGHT_LABEL["en"]) + '"></a>\n'
        "<!-- HOTWEEK-v1 -->"
    )
    html = html.replace("<!-- HOTWEEK-v1 -->", spot_anchor, 1)

    # 3) 기존 hotweek 스크립트 → 통합 스크립트 대체 (로컬라이즈 보존).
    m = OLD_SCRIPT_RE.search(html)
    if not m:
        return f"{path}: FAIL (기존 hotweek 스크립트 미발견)"
    old = m.group(0)
    title_m = TITLE_RE.search(old)
    unit_m = UNIT_RE.search(old)
    if not title_m:
        return f"{path}: FAIL (hotweek 타이틀 추출 실패)"
    title = title_m.group(1)
    unit = unit_m.group(1) if unit_m else ""
    spot = SPOTLIGHT_LABEL.get(lk, SPOTLIGHT_LABEL["en"])
    new_script = (
        SCRIPT_TMPL.replace("__TITLE__", title)
        .replace("__UNIT__", unit)
        .replace("__SPOT__", spot)
    )
    html = html[: m.start()] + new_script + html[m.end() :]

    f.write_text(html, encoding="utf-8")
    return f"{path}: OK (title={title!r} unit={unit!r} spot={spot!r})"


if __name__ == "__main__":
    results = [patch(p) for p in LANGS]
    for r in results:
        print(r)
    fails = [r for r in results if "FAIL" in r]
    sys.exit(1 if fails else 0)
