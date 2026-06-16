#!/usr/bin/env python3
"""R89 fix — zh-cn/zh-tw 메인 index 검색·국가필터·푸터 네비 복원 (ko parity).

배경 (검증 verdict byvias-zh-content-eye-audit P0-2/P1-4, LIVE perl 실측 확정):
  메인 index 가 ko 만 hubfilter(검색창 hf-search + 국가 필터칩 hf-chips + #events 앵커)
  + 푸터 네비 5종(소개/연락처/개인정보처리방침/이용약관/제휴 고지) 보유. zh-cn/zh-tw 는
  HTML·CSS·JS 전부 부재(LIVE: hubfilter 0 · hf-search 0 · affiliate-disclosure/ 0).
  → 다국어 사용자 국가별 거르기·검색 불가 + 법무 링크 부재 + 히어로 CTA #events 앵커 깨짐.

원인: hubfilter/푸터는 generate.py(빌더) 가 아닌 *post-build* 로 ko 에만 주입됨
  (home_redesign_patch.py L113-116 가 "ko=hubfilter, 그 외=tabs 바로" 를 전제로 함).
  → zh 는 한 번도 주입 안 됨. dist 가 라이브 SSOT(FLR-20260611-TEC-001) → dist 직접 패치.

🔴 form (FLR-AGT-002·환각 금지):
  - 국가 필터칩 COUNTRIES = 카드 .c 라인 실측 zh 국가명(韩国/日本/台湾…) verbatim 기반.
    ko 18종을 zh 표준 국가명으로 매핑(표준 국명·환각 아님). 칩은 카드에서 동적 생성이라
    하드코딩 0(카드 추가 시 자동 동기화) — COUNTRIES 는 .c 토큰 매칭 SSOT 일 뿐.
  - UI 문구(placeholder/empty/count/푸터 라벨) = 페이지 기존 zh 용어 정합(艺人·城市·场·联盟).
  - 푸터 법무 링크 = 루트 전용(/about·/privacy 등, zh 전용 페이지 부재) → `../` prefix
    (zh-cn/ 에서 ../about/ = /about/ 200). zh 법무 페이지 신설은 별건(현재 ko 페이지로 연결).

전략 (home_redesign_patch.py dist-direct 멱등 패치 precedent):
  - 멱등 마커 HF_MARK/FOOT_MARK. 재실행 0 변경.
  - CSS: ko .hf-*/.hubfilter 26 rule 을 zh <style> 말미 주입(언어 무관·verbatim).
  - HTML: hubfilter 블록을 <div class="tabs"> 직전 주입(placeholder/aria 번역).
  - JS: 독립 IIFE(검색·칩 로직, ko 7KB 중 hubfilter 부분만 추출 + COUNTRIES/문구 zh) 를
    </body> 직전 주입. 기존 minified JS 미surgery(자족 IIFE).
  - 푸터: <div class="foot"> 의 'byvias.100m1s.com' 뒤에 nav span 주입(../ 경로·zh 라벨).

게이트 (FLR-AGT-002 — 실측 grep, --verify):
  (G1) hubfilter 1 + hf-search 1 + #hf-q 1 + hf-chips 1 present.
  (G2) 푸터 법무 링크 5종 present(../about ~ ../affiliate-disclosure).
  (G3) #events 앵커 present(히어로 CTA 타겟).
  (G4) CSS .hf-chip rule present(스타일 무손실).
  (G5) <div> 균형 + 멱등(재실행 0).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
LANGS = ["zh-cn", "zh-tw"]

HF_MARK = "<!-- HF-PARITY-R89 -->"
FOOT_MARK = "<!-- FOOT-NAV-R89 -->"
CSS_MARK = "/* HF-PARITY-R89 */"

# ── CSS (ko .hubfilter/.hf-* verbatim — 언어 무관) ──────────────────────────
HF_CSS = (
    ".hubfilter{margin:0 0 16px}"
    ".hf-search{position:relative;display:flex;align-items:center}"
    ".hf-search svg{position:absolute;inset-inline-start:12px;color:var(--muted);pointer-events:none;flex:0 0 auto}"
    ".hf-search input{width:100%;min-height:46px;box-sizing:border-box;padding:11px 40px 11px 40px;border:1px solid var(--line);border-radius:var(--r-s);background:var(--card);color:var(--ink);font-size:15px;font-family:inherit}"
    ".hf-search input::placeholder{color:var(--muted)}"
    ".hf-search input:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(24,95,165,.12)}"
    ".hf-clear{position:absolute;inset-inline-end:6px;display:none;align-items:center;justify-content:center;width:38px;height:38px;border:0;background:none;color:var(--muted);cursor:pointer;border-radius:8px;font-size:20px;line-height:1}"
    ".hf-clear:hover{background:var(--line);color:var(--ink)}"
    ".hf-search.has-val .hf-clear{display:inline-flex}"
    ".hf-chips{display:flex;flex-wrap:nowrap;gap:7px;overflow-x:auto;scrollbar-width:none;padding:10px 0 2px;margin:0 -2px;scroll-padding-inline:2px}"
    ".hf-chips::-webkit-scrollbar{display:none}"
    ".hf-chip{flex:0 0 auto;display:inline-flex;align-items:center;gap:5px;min-height:44px;box-sizing:border-box;padding:7px 13px;border:1px solid var(--line);border-radius:var(--r-s);background:var(--card);color:var(--ink);font-size:13px;font-weight:500;cursor:pointer;white-space:nowrap;font-family:inherit;transition:border-color .2s,background .2s}"
    ".hf-chip:hover{border-color:#c9c7bd}"
    '.hf-chip[aria-pressed="true"]{background:var(--sun-chip-bg);color:var(--sun-chip-ink);border-color:var(--sun-chip-ink)}'
    ".hf-chip .cnt{color:var(--muted);font-weight:400;font-size:12px}"
    '.hf-chip[aria-pressed="true"] .cnt{color:var(--sun-chip-ink);opacity:.75}'
    ".hf-empty{display:none;text-align:center;color:var(--muted);font-size:14px;padding:30px 16px;line-height:1.6}"
    ".hf-empty b{color:var(--ink);font-weight:600}"
    ".hf-allhidden .hf-empty{display:block}"
    ".hf-count{display:none;font-size:13px;color:var(--muted);margin:2px 0 12px}"
    ".hf-count.on{display:block}"
    ".hf-count b{color:var(--accent);font-weight:600}"
)

# ── 언어별 문자열 (페이지 기존 zh 용어 정합) ────────────────────────────────
L10N = {
    "zh-cn": {
        "ph": "艺人 · 国家 · 城市搜索",
        "aria_search": "按艺人·国家·城市搜索日程",
        "aria_clear": "清除搜索词",
        "aria_chips": "按国家筛选",
        "all": "全部",
        "empty": "没有符合搜索·筛选的日程。<br>请选择<b>其他国家</b>或清除搜索词。",
        "count_label": "搜索",  # activeCountry 없을 때 fallback
        "count_unit": "场",
        # ko COUNTRIES 18 → zh-cn 표준 국명 (카드 .c 토큰 매칭 SSOT)
        "countries": [
            "韩国",
            "日本",
            "台湾",
            "美国",
            "新加坡",
            "香港",
            "泰国",
            "英国",
            "墨西哥",
            "澳门",
            "菲律宾",
            "印度尼西亚",
            "德国",
            "中国",
            "越南",
            "加拿大",
            "澳大利亚",
            "马来西亚",
        ],
        # 푸터 라벨 (../ 경로·ko 법무 페이지 연결)
        "foot": [
            ("../about/", "介绍"),
            ("../contact/", "联系"),
            ("../privacy/", "隐私政策"),
            ("../terms/", "使用条款"),
            ("../affiliate-disclosure/", "联盟告知"),
        ],
    },
    "zh-tw": {
        "ph": "藝人 · 國家 · 城市搜尋",
        "aria_search": "依藝人·國家·城市搜尋日程",
        "aria_clear": "清除搜尋詞",
        "aria_chips": "依國家篩選",
        "all": "全部",
        "empty": "沒有符合搜尋·篩選的日程。<br>請選擇<b>其他國家</b>或清除搜尋詞。",
        "count_label": "搜尋",
        "count_unit": "場",
        "countries": [
            "韓國",
            "日本",
            "台灣",
            "美國",
            "新加坡",
            "香港",
            "泰國",
            "英國",
            "墨西哥",
            "澳門",
            "菲律賓",
            "印尼",
            "德國",
            "中國",
            "越南",
            "加拿大",
            "澳洲",
            "馬來西亞",
        ],
        "foot": [
            ("../about/", "介紹"),
            ("../contact/", "聯絡"),
            ("../privacy/", "隱私政策"),
            ("../terms/", "使用條款"),
            ("../affiliate-disclosure/", "聯盟告知"),
        ],
    },
}


def _hub_html(lang: str) -> str:
    s = L10N[lang]
    return (
        f"{HF_MARK}\n"
        '<div class="hubfilter" id="events">\n'
        '  <label class="hf-search">\n'
        '    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>\n'
        f'    <input id="hf-q" type="search" inputmode="search" autocomplete="off" placeholder="{s["ph"]}" aria-label="{s["aria_search"]}">\n'
        f'    <button type="button" class="hf-clear" id="hf-clear" aria-label="{s["aria_clear"]}">&times;</button>\n'
        "  </label>\n"
        f'  <div class="hf-chips" id="hf-chips" role="group" aria-label="{s["aria_chips"]}"></div>\n'
        "</div>\n"
        '<div class="hf-count" id="hf-count" aria-live="polite"></div>\n'
    )


def _hub_js(lang: str) -> str:
    s = L10N[lang]
    countries = "[" + ",".join(f'"{c}"' for c in s["countries"]) + "]"
    # ko hubfilter IIFE 의 검색·칩 로직 verbatim + COUNTRIES/문구 zh. 자족 IIFE.
    #   🔴 지연 실행: tabpanel/카드는 선행 favorite-filter 스크립트가 DOMContentLoaded 에
    #   채운다. </body> 동기 실행 시점엔 비어 있어 if(!panels.length)return 조기 종료 →
    #   칩 0 (실측 사고). run() 으로 분리 후 DOMContentLoaded + rAF 2틱 지연 실행.
    return (
        f"<script>/* {HF_MARK[4:-3].strip()} */\n"
        "(function(){function run(){try{\n"
        " var qEl=document.getElementById('hf-q'),clearEl=document.getElementById('hf-clear'),"
        "chipsEl=document.getElementById('hf-chips'),countEl=document.getElementById('hf-count'),"
        "searchWrap=qEl&&qEl.closest('.hf-search');\n"
        " if(!qEl||!chipsEl)return;\n"
        " var panels=[].slice.call(document.querySelectorAll('.tabs .tabpanel'));\n"
        " if(!panels.length)return;\n"
        f" var COUNTRIES={countries};\n"
        " function norm(s){return (s||'').toLowerCase().replace(/\\s+/g,' ').trim();}\n"
        " var index=[],countryCount={};\n"
        " panels.forEach(function(panel){\n"
        "  var grid=panel.querySelector('.grid');if(!grid)return;\n"
        "  var cards=[].slice.call(grid.querySelectorAll('.ecard'));\n"
        "  cards.forEach(function(card){\n"
        "   var a=card.querySelector('.a'),c=card.querySelector('.c');\n"
        "   var artist=a?a.textContent:'', cline=c?c.textContent:'';\n"
        "   var ctrys=COUNTRIES.filter(function(k){return cline.indexOf(k)>=0;});\n"
        "   ctrys.forEach(function(k){countryCount[k]=(countryCount[k]||0)+1;});\n"
        "   index.push({card:card,panel:panel,hay:norm(artist+' '+cline),countries:ctrys});\n"
        "  });\n"
        "  var empty=document.createElement('div');empty.className='hf-empty';\n"
        f"  empty.innerHTML='{s['empty']}';\n"
        "  grid.appendChild(empty);\n"
        " });\n"
        " var order=Object.keys(countryCount).sort(function(x,y){return countryCount[y]-countryCount[x];});\n"
        " var activeCountry='';\n"
        " function makeChip(label,key,cnt){\n"
        "  var b=document.createElement('button');b.type='button';b.className='hf-chip';\n"
        "  b.setAttribute('aria-pressed',key===activeCountry?'true':'false');b.setAttribute('data-k',key);\n"
        "  b.innerHTML=label+(cnt!=null?' <span class=\"cnt\">'+cnt+'</span>':'');\n"
        "  b.addEventListener('click',function(){activeCountry=(activeCountry===key)?'':key;syncChips();apply();});\n"
        "  return b;\n"
        " }\n"
        f" chipsEl.appendChild(makeChip('{s['all']}','',null));\n"
        " order.forEach(function(k){chipsEl.appendChild(makeChip(k,k,countryCount[k]));});\n"
        " function syncChips(){[].forEach.call(chipsEl.children,function(b){\n"
        "  b.setAttribute('aria-pressed',(b.getAttribute('data-k')||'')===activeCountry?'true':'false');});}\n"
        " function activePanel(){\n"
        "  var r=document.querySelector('.tabs>input:checked');\n"
        "  if(!r)return panels[0];\n"
        "  var p=document.querySelector('.tabpanel.tp-'+r.id.replace('tab-',''));\n"
        "  return p||panels[0];\n"
        " }\n"
        " function apply(){\n"
        "  var q=norm(qEl.value), cur=activePanel(), shownInCur=0;\n"
        "  index.forEach(function(it){\n"
        "   var ok=(!q||it.hay.indexOf(q)>=0)&&(!activeCountry||it.countries.indexOf(activeCountry)>=0);\n"
        "   it.card.hidden=!ok;\n"
        "   if(ok&&it.panel===cur)shownInCur++;\n"
        "  });\n"
        "  panels.forEach(function(p){\n"
        "   var vis=p.querySelectorAll('.ecard:not([hidden])').length;\n"
        "   p.classList.toggle('hf-allhidden',vis===0);\n"
        "  });\n"
        "  if(searchWrap)searchWrap.classList.toggle('has-val',!!qEl.value);\n"
        "  if(q||activeCountry){\n"
        f"   countEl.innerHTML=(activeCountry?activeCountry+' · ':'')+'<b>'+shownInCur+'</b>{s['count_unit']}';\n"
        "   countEl.classList.add('on');\n"
        "  }else{countEl.classList.remove('on');countEl.textContent='';}\n"
        " }\n"
        " qEl.addEventListener('input',apply);\n"
        " if(clearEl)clearEl.addEventListener('click',function(){qEl.value='';qEl.focus();apply();});\n"
        " document.querySelectorAll('.tabs>input').forEach(function(r){r.addEventListener('change',apply);});\n"
        " apply();return true;\n"
        "}catch(e){return true;}}\n"
        # panels 미준비(선행 스크립트 후행)면 재시도. 최대 ~20틱(rAF) 후 포기.
        " var tries=0;function tryRun(){var panels=document.querySelectorAll('.tabs .tabpanel');\n"
        "  if(panels.length&&document.getElementById('hf-chips')){run();return;}\n"
        "  if(tries++<20){(window.requestAnimationFrame||function(f){setTimeout(f,16);})(tryRun);}}\n"
        " if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',tryRun);}else{tryRun();}\n"
        "})();\n"
        "</script>\n"
    )


def _foot_nav(lang: str) -> str:
    s = L10N[lang]
    links = "".join(
        f'<a href="{href}" style="color:var(--muted);text-decoration:none">{label}</a>'
        for href, label in s["foot"]
    )
    return (
        f'{FOOT_MARK}<br><span style="display:inline-flex;flex-wrap:wrap;gap:0 8px;margin-top:4px">'
        f"{links}</span>"
    )


def apply_lang(lang: str, write: bool) -> tuple[bool, str, str]:
    """반환: (성공, 메시지, 적용후 HTML). dry-run 도 적용후 HTML 로 게이트."""
    p = DIST / lang / "index.html"
    if not p.exists():
        return False, f"{p} 없음", ""
    h = p.read_text(encoding="utf-8")
    orig = h
    div0 = h.count("<div")

    # 멱등: 이미 적용?
    already = HF_MARK in h and FOOT_MARK in h

    # 1) CSS 주입 (</style> 직전, 마지막 style 블록)
    if CSS_MARK not in h:
        idx = h.rfind("</style>")
        if idx < 0:
            return False, "</style> 앵커 부재", ""
        h = h[:idx] + CSS_MARK + HF_CSS + h[idx:]

    # 2) hubfilter HTML 주입 (<div class="tabs" 직전)
    if HF_MARK not in h:
        m = re.search(r'<div class="tabs"', h)
        if not m:
            return False, '<div class="tabs"> 앵커 부재', ""
        h = h[: m.start()] + _hub_html(lang) + h[m.start() :]

    # 3) hubfilter JS 주입 (</body> 직전)
    if f"{HF_MARK[4:-3].strip()}" not in h or "getElementById('hf-q')" not in h:
        idx = h.rfind("</body>")
        if idx < 0:
            return False, "</body> 앵커 부재", ""
        h = h[:idx] + _hub_js(lang) + h[idx:]

    # 4) 푸터 nav 주입 (foot div 의 byvias.100m1s.com 뒤)
    if FOOT_MARK not in h:
        m = re.search(r'(<div class="foot">[^<]*byvias\.100m1s\.com)', h)
        if not m:
            return False, "foot div byvias.100m1s.com 앵커 부재", ""
        h = h[: m.end()] + _foot_nav(lang) + h[m.end() :]

    div1 = h.count("<div")
    # 신규 div = hubfilter + hf-chips + hf-count = +3 (hf-search=label·foot nav=span, div 아님)
    if div1 - div0 not in (0, 3):
        return False, f"<div> 비정상 증가 {div0}→{div1} (기대 +0/+3)", ""

    changed = h != orig
    if write and changed:
        p.write_text(h, encoding="utf-8")
    msg = "WROTE" if (changed and write) else ("멱등(변경없음)" if already else "DRY")
    return True, msg, h


def gate(html: str, lang: str) -> list[str]:
    h = html
    fails = []

    def cnt(tok):
        return len(re.findall(re.escape(tok), h))

    if cnt('class="hubfilter"') < 1:
        fails.append("G1 hubfilter 부재")
    if cnt('class="hf-search"') < 1:
        fails.append("G1 hf-search 부재")
    if cnt('id="hf-q"') < 1:
        fails.append("G1 #hf-q 부재")
    if cnt('id="hf-chips"') < 1:
        fails.append("G1 hf-chips 부재")
    for href, _ in L10N[lang]["foot"]:
        if cnt(f'href="{href}"') < 1:
            fails.append(f"G2 푸터 링크 부재 {href}")
    if cnt('id="events"') < 1:
        fails.append("G3 #events 앵커 부재")
    if ".hf-chip{" not in h:
        fails.append("G4 .hf-chip CSS 부재")
    return fails


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    verify = "--verify" in args
    langs = [a for a in args if a in LANGS] or LANGS
    ok = True
    for lang in langs:
        if verify:
            disk = (DIST / lang / "index.html").read_text(encoding="utf-8")
            f = gate(disk, lang)
            if f:
                print(f"[{lang}] 게이트 FAIL ({len(f)}):")
                for x in f:
                    print(f"    ✗ {x}")
                ok = False
            else:
                print(
                    f"[{lang}] 게이트 PASS (G1 hubfilter·검색·칩 · G2 푸터5 · G3 #events · G4 CSS)"
                )
            continue
        good, msg, html = apply_lang(lang, write)
        if not good:
            print(f"[{lang}] ABORT: {msg}")
            ok = False
            continue
        f = gate(html, lang)
        if f:
            print(f"[{lang}] ABORT 게이트 FAIL ({len(f)}): {f}")
            ok = False
            continue
        print(f"[{lang}] {msg} — 게이트 PASS (hubfilter+검색+국가칩+#events+푸터5종)")
    if not ok:
        sys.exit(2)
    mode = "VERIFY" if verify else ("WRITE" if write else "DRY-RUN")
    print(f"OK: R89 zh 메인 hubfilter+푸터 [{mode}] ({' '.join(langs)})")


if __name__ == "__main__":
    main()
