#!/usr/bin/env python3
"""WAVE4 CR 자동 측정 게이트 (R27 P0-4 완료 기준 산출물 — 재발 차단).

Playwright 렌더 기반 실측: 페이지를 라이트/다크 양 모드로 렌더 → 모든 가시 텍스트 노드의
실제 computed color vs 실효 배경(조상 체인 합성) WCAG CR 계산.
- 텍스트 CR >= 4.5 (단, 18.66px+bold 또는 24px+ 대형 텍스트는 3.0)
- 비텍스트(보더 있는 컨트롤 필) >= 3.0 은 토큰 설계 단계에서 검증 (본 게이트는 텍스트 전수)
- 제외: aria-hidden, .ghost 워터마크(장식), opacity<.4 장식, 투명 텍스트

사용: python3 tools/cr_audit.py [--pages page1.html,page2.html] [--full]
기본 = 대표 셋 (index 11언어 + 코스 ko/en/ja/zh-cn + 이벤트 표본). --full = 847 전수(느림).
종료코드 0=PASS, 1=FAIL(위반 목록 출력).
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

JS_AUDIT = r"""
() => {
  function parseColor(c){
    const m = c.match(/rgba?\(([^)]+)\)/);
    if(!m) return null;
    const p = m[1].split(',').map(parseFloat);
    return {r:p[0],g:p[1],b:p[2],a:p.length>3?p[3]:1};
  }
  function blend(top, bot){
    const a = top.a + bot.a*(1-top.a);
    if(a===0) return {r:255,g:255,b:255,a:0};
    return {
      r:(top.r*top.a + bot.r*bot.a*(1-top.a))/a,
      g:(top.g*top.a + bot.g*bot.a*(1-top.a))/a,
      b:(top.b*top.a + bot.b*bot.a*(1-top.a))/a, a:a};
  }
  function gradAt(bi, frac){
    // linear-gradient 1개의 frac(0~1) 지점 색 보간. 스톱 % 명시 없으면 균등 분배.
    const inner = bi.slice(bi.indexOf('(')+1, bi.lastIndexOf(')'));
    // 콤마 분리 (괄호 중첩 보호)
    const parts = []; let d=0, cur='';
    for(const ch of inner){
      if(ch==='(')d++; if(ch===')')d--;
      if(ch===','&&d===0){parts.push(cur.trim());cur='';}else cur+=ch;
    }
    if(cur.trim())parts.push(cur.trim());
    let stops=[];
    for(const p of parts){
      const cm = p.match(/rgba?\([^)]+\)|#[0-9a-fA-F]{3,8}\b|\btransparent\b/);
      if(!cm) continue; // 각도/방향 토큰
      let col;
      if(cm[0]==='transparent') col={r:0,g:0,b:0,a:0};
      else if(cm[0][0]==='#'){
        let h=cm[0].slice(1);
        if(h.length===3)h=h.split('').map(c=>c+c).join('');
        col={r:parseInt(h.slice(0,2),16),g:parseInt(h.slice(2,4),16),b:parseInt(h.slice(4,6),16),a:h.length>=8?parseInt(h.slice(6,8),16)/255:1};
      } else col=parseColor(cm[0]);
      const pm = p.match(/([\d.]+)%/);
      stops.push({c:col, pos: pm?parseFloat(pm[1])/100:null});
    }
    if(!stops.length) return null;
    if(stops[0].pos===null)stops[0].pos=0;
    if(stops[stops.length-1].pos===null)stops[stops.length-1].pos=1;
    for(let i=1;i<stops.length-1;i++) if(stops[i].pos===null){
      // 직전 명시~다음 명시 사이 균등
      let j=i; while(stops[j].pos===null)j++;
      const prev=stops[i-1].pos, next=stops[j].pos, span=j-(i-1);
      for(let k=i;k<j;k++) stops[k].pos = prev + (next-prev)*(k-(i-1))/span;
    }
    if(frac<=stops[0].pos) return stops[0].c;
    for(let i=1;i<stops.length;i++){
      if(frac<=stops[i].pos){
        const t=(frac-stops[i-1].pos)/Math.max(1e-6,stops[i].pos-stops[i-1].pos);
        const a=stops[i-1].c, b=stops[i].c;
        return {r:a.r+(b.r-a.r)*t, g:a.g+(b.g-a.g)*t, b:a.b+(b.b-a.b)*t, a:a.a+(b.a-a.a)*t};
      }
    }
    return stops[stops.length-1].c;
  }
  function gradFrac(bi, box, cx, cy){
    // 그라데이션 축 위 (cx,cy)의 진행도. 각도 미지정 = to bottom(180deg).
    let ang = 180;
    const am = bi.match(/linear-gradient\(\s*([\d.]+)deg/);
    if(am) ang = parseFloat(am[1]);
    else {
      const dm = bi.match(/linear-gradient\(\s*to\s+([a-z ]+),/);
      if(dm){const d=dm[1].trim();
        ang = d==='top'?0:d==='right'?90:d==='bottom'?180:d==='left'?270:
              d==='top right'||d==='right top'?45:d==='bottom right'||d==='right bottom'?135:
              d==='bottom left'||d==='left bottom'?225:315;}
    }
    const rad = ang*Math.PI/180;
    const dx = Math.sin(rad), dy = -Math.cos(rad); // 화면좌표(y 아래) 진행 벡터
    const corners = [[box.left,box.top],[box.right,box.top],[box.left,box.bottom],[box.right,box.bottom]];
    const proj = c => c[0]*dx + c[1]*dy;
    const ps = corners.map(proj);
    const mn = Math.min(...ps), mx = Math.max(...ps);
    return Math.min(1, Math.max(0, (cx*dx+cy*dy - mn) / Math.max(1e-6, mx-mn)));
  }
  function effBg(el){
    let chain = [];
    for(let n=el;n;n=n.parentElement) chain.push(n);
    const docBg = parseColor(getComputedStyle(document.documentElement).backgroundColor);
    const bodyBg = parseColor(getComputedStyle(document.body).backgroundColor);
    let base = (bodyBg && bodyBg.a>0)?bodyBg:((docBg&&docBg.a>0)?docBg:{r:255,g:255,b:255,a:1});
    chain.reverse(); // 루트→자신 순 합성
    let cur = {...base, a:1};
    const er = el.getBoundingClientRect();
    const cx = er.left+er.width/2, cy = er.top+er.height/2;
    for(const n of chain){
      const st = getComputedStyle(n);
      const bg = parseColor(st.backgroundColor);
      if(bg && bg.a>0) cur = blend(bg, cur);
      const bi = st.backgroundImage;
      if(bi && bi !== 'none'){
        // 다중 background 레이어: 마지막 레이어부터(아래) 순서로 합성
        const layers = []; let d=0, curs='';
        for(const ch of bi){ if(ch==='(')d++; if(ch===')')d--;
          if(ch===','&&d===0){layers.push(curs.trim());curs='';} else curs+=ch; }
        if(curs.trim())layers.push(curs.trim());
        const nb = n.getBoundingClientRect();
        for(let li=layers.length-1; li>=0; li--){
          const L = layers[li];
          if(L.includes('linear-gradient')){
            const frac = gradFrac(L, nb, cx, cy);
            const col = gradAt(L, frac);
            if(col && col.a>0) cur = blend(col, cur);
          }
          // url(사진) 레이어: CSS 만으로 색 미상 — 픽셀 실측 영역 (별도 마킹)
          else if(L.includes('url(')) cur.photo = true;
        }
      }
    }
    return cur;
  }
  function srgb(v){v/=255;return v<=0.03928? v/12.92 : Math.pow((v+0.055)/1.055,2.4);}
  function lum(c){return 0.2126*srgb(c.r)+0.7152*srgb(c.g)+0.0722*srgb(c.b);}
  function cr(a,b){const la=lum(a),lb=lum(b);const hi=Math.max(la,lb),lo=Math.min(la,lb);return (hi+0.05)/(lo+0.05);}
  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const seen = new Set();
  while(walker.nextNode()){
    const t = walker.currentNode; const txt = t.textContent.trim();
    if(!txt || txt.length<2) continue;
    const el = t.parentElement; if(!el || seen.has(el)) continue; seen.add(el);
    if(el.closest('[aria-hidden="true"],script,style,noscript,svg,.ghost')) continue;
    const st = getComputedStyle(el);
    if(st.display==='none'||st.visibility!=='visible') continue;
    const r = el.getBoundingClientRect();
    if(r.width<2||r.height<2) continue;
    const op = parseFloat(st.opacity);
    const fg0 = parseColor(st.color); if(!fg0) continue;
    let fgA = fg0.a * (isNaN(op)?1:op);
    // 조상 opacity 합성
    for(let n=el.parentElement;n;n=n.parentElement){
      const o = parseFloat(getComputedStyle(n).opacity); if(!isNaN(o)&&o<1) fgA*=o;
    }
    if(fgA < 0.4) continue; // 장식적 저불투명 제외
    const bg = effBg(el);
    const fg = blend({...fg0,a:fgA}, bg);
    const ratio = cr(fg,bg);
    const fs = parseFloat(st.fontSize); const fw = parseInt(st.fontWeight)||400;
    const large = fs>=24 || (fs>=18.66 && fw>=700);
    const need = large?3.0:4.5;
    if(ratio < need){
      out.push({text:txt.slice(0,40), sel:(el.className&&el.className.toString?el.className.toString():'')||el.tagName,
                fs:fs, ratio:Math.round(ratio*100)/100, need:need,
                photo:!!bg.photo, fgc:[fg.r,fg.g,fg.b],
                rect:[r.left,r.top,r.width,r.height]});
    }
  }
  return out;
}
"""


def photo_recheck(page, viols):
    """사진(url) 배경 요소 — CSS 만으로 색 미상. 요소 영역 스크린샷 픽셀 평균으로 실측 재판정.
    한계: 텍스트 픽셀 포함 평균(텍스트 면적 소수 가정) — 근사치. 문서화된 정책."""
    import io

    from PIL import Image

    confirmed = []
    for v in viols:
        if not v.get("photo"):
            confirmed.append(v)
            continue
        x, y, w, h = v["rect"]
        if w < 4 or h < 4:
            continue
        try:
            png = page.screenshot(
                clip={"x": max(0, x), "y": max(0, y), "width": w, "height": h}
            )
            im = Image.open(io.BytesIO(png)).convert("RGB")
            px = list(im.getdata())
            n = len(px)
            mr = sum(p[0] for p in px) / n
            mg = sum(p[1] for p in px) / n
            mb = sum(p[2] for p in px) / n

            def srgb(c):
                c /= 255
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            def lum(r, g, b):
                return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)

            lf = lum(*v["fgc"])
            lb = lum(mr, mg, mb)
            hi, lo = max(lf, lb), min(lf, lb)
            ratio = (hi + 0.05) / (lo + 0.05)
            if ratio < v["need"]:
                v = dict(v, ratio=round(ratio, 2), method="pixel")
                confirmed.append(v)
        except Exception:
            confirmed.append(v)
    return confirmed


DEFAULT_PAGES = (
    [
        f"{d}/index.html" if d else "index.html"
        for d in ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]
    ]
    + [
        f"{d}/twice-thisisfor-seoul.html" if d else "twice-thisisfor-seoul.html"
        for d in ["", "en", "ja", "zh-cn", "es", "th"]
    ]
    + [
        "kim-junsu-gravity-osaka-d1.html",
        "en/ive-showwhatiam-tokyo.html",
        "ja/kai-kaion-yokohama-d2.html",
        "zh-cn/gdragon-ubermensch-macau.html",
        "ar/bts-arirang-seoul.html",
        "seoul-live-idol-festival-2026-07-18-19-kintex.html",
    ]
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", default="")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--out", default="/tmp/w4_cr_results.json")
    args = ap.parse_args()

    if args.full:
        pages = sorted(str(p.relative_to(DIST)) for p in DIST.rglob("*.html"))
    elif args.pages:
        pages = args.pages.split(",")
    else:
        pages = DEFAULT_PAGES

    from playwright.sync_api import sync_playwright

    fails = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for scheme in ("light", "dark"):
            ctx = browser.new_context(
                color_scheme=scheme, viewport={"width": 390, "height": 844}
            )
            page = ctx.new_page()
            for rel in pages:
                f = DIST / rel
                if not f.exists():
                    continue
                page.goto(f.as_uri(), wait_until="load")
                # 탭 패널 전수: 모든 라디오 탭 체크 상태 순회 대신 기본 패널 + 전 패널 강제 노출 1회
                page.add_style_tag(
                    content=".tabpanel,.sl-panel,.crs-panel{display:block!important}details{open:true}"
                )
                page.evaluate(
                    "()=>{document.querySelectorAll('details').forEach(d=>d.open=true)}"
                )
                viols = page.evaluate(JS_AUDIT)
                viols = photo_recheck(page, viols)
                if viols:
                    fails[f"{scheme}:{rel}"] = viols
            ctx.close()
        browser.close()

    Path(args.out).write_text(json.dumps(fails, ensure_ascii=False, indent=1))
    n = sum(len(v) for v in fails.values())
    if fails:
        print(
            f"CR AUDIT FAIL — {n} violations on {len(fails)} page-modes (see {args.out})"
        )
        for k, v in list(fails.items())[:12]:
            for x in v[:4]:
                print(
                    f"  {k} :: {x['sel'][:40]} '{x['text']}' CR {x['ratio']} < {x['need']} ({x['fs']}px)"
                )
        return 1
    print(f"CR AUDIT PASS — {len(pages)} pages x light/dark, 0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
