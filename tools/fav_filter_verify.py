#!/usr/bin/env python3
"""최애 필터 1단계 검증 게이트 실측 (Q-20260607-130 A안) — 조니 시각 8항목 자동 캡처.

journey_bar_verify.py 동형: Playwright + 로컬 http(dist) + rAF 2프레임 settle + 게이트/캡처.
산출: tools/ff-captures/*.png, 종료 0 = 전 게이트 PASS.

8항목 (조니 시각 verbatim):
  ITEM-1 칩 행 390px      — ko index 390×844 칩 행 클립 (flex line 수 게이트: 1줄 기대)
  ITEM-2 다크 칩 ON       — prefers-color-scheme:dark + localStorage byvias_fav 선 주입
                            (아티스트 1명·filterOn) → 칩 ON 클립
  ITEM-3 dim 0.45 다크    — 다크 + 필터 ON에서 festival dim(.favf-tbd) 카드 포함 프레임
  ITEM-4 /ar/ RTL         — ar index 390px 칩 행 클립 + 시트 오픈 (X 버튼 = 좌측 기대)
  ITEM-5 데스크탑 시트    — ko index 1280×900 시트 오픈 (560px 다이얼로그 센터)
  ITEM-6 체크마크 확대    — 시트 내 선택 셀(.favf-cell) 단독 클립 캡처
  ITEM-7 시트-스크림-jbar — 390px 시트 오픈 풀프레임 (scrim 전면 피복 + z 40<45 서열)
  ITEM-8 빈 상태+fest dim — 최애 = 콘서트 0건 아티스트(festival-only 'WATERBOMB SEOUL
                            2026') 주입 → 빈 상태 박스 + dim 카드 동거 프레임

절차 의무:
  - scroll/상태 변경 후 settle() = rAF 2프레임 + 대기 (journey_bar_verify:98-101 동형)
  - affbar 무관 (index 한정 — affbar는 이벤트 페이지 전유)
  - localStorage 주입 = context.add_init_script (페이지 로드 전 선 주입)
  - 시트 열기 = #favf-chip 실클릭 (실 사용자 경로 — DOM 직접 조작 없음)
  - 사이트 언어 라우터 = 컨텍스트 locale 고정 (ko-KR / ar-SA)

본 작성 환경 chromium 부재 — 실행 검증 불가. 실행은 대표 로컬:
  cd <repo> && python3 tools/fav_filter_verify.py   (종료 0=ALL PASS / 2=환경 부재)
"""

import http.server
import socketserver
import sys
import threading
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("환경 부재 — playwright 미설치. 실행은 대표 로컬에서:")
    print("  pip install playwright && playwright install chromium")
    print("  python3 tools/fav_filter_verify.py")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "tools" / "ff-captures"
OUT.mkdir(exist_ok=True)

PORT = 8947
BASE = f"http://127.0.0.1:{PORT}"
VP = {"width": 390, "height": 844}
KEY = "byvias_fav"
# 콘서트 보유 아티스트 (dist/index.html .abadge[title] 실측: BTS 3건)
ARTIST = "BTS"
# festival-only 키 (🎪 배지 카드 — 비 festival 콘서트 0건 → 빈 상태 유도, ITEM-8)
FEST_ONLY = "WATERBOMB SEOUL 2026"

fails = []


def gate(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'} [{name}] {detail}")
    if not ok:
        fails.append(name)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(DIST), **kw)

    def log_message(self, *a):
        pass


def watch(pg):
    """pageerror + 로컬 리소스 실패만 수집 (외부 도메인 = 샌드박스 차단 제외)."""
    errs = []
    pg.on("pageerror", lambda x, e=errs: e.append(f"js:{x}"))
    pg.on(
        "requestfailed",
        lambda r, e=errs: e.append(f"res:{r.url}") if r.url.startswith(BASE) else None,
    )
    return errs


def settle(pg, ms=120):
    """scroll/상태 변경 → rAF 2프레임 대기 → 측정/캡처 (직후 캡처 race 봉쇄)."""
    pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())))")
    pg.wait_for_timeout(ms)


def inject_fav(ctx, artists, filter_on=True):
    """localStorage v1 레코드 로드 전 선 주입 (fav-filter.js sRead 스키마 동형)."""
    import json
    rec = {"v": 1, "artists": artists, "filterOn": filter_on,
           "updatedAt": "2026-06-12T00:00:00.000Z"}
    ctx.add_init_script(
        f"try{{localStorage.setItem({json.dumps(KEY)},{json.dumps(json.dumps(rec, ensure_ascii=False))})}}catch(e){{}}"
    )


ROW_LINES = """()=>{const r=document.getElementById('favf-row');if(!r)return null;
 const ch=[...r.children].filter(c=>getComputedStyle(c).display!=='none');
 let lines=0,bot=null;const rects=[];
 for(const c of ch){const b=c.getBoundingClientRect();rects.push([Math.round(b.top),Math.round(b.bottom)]);
  if(bot===null||b.top>=bot-1){lines++;bot=b.bottom;}else{bot=Math.max(bot,b.bottom);}}
 const rr=r.getBoundingClientRect();
 return {lines,n:ch.length,rects,rowRect:{x:rr.x,y:rr.y,w:rr.width,h:rr.height},
  pressed:document.getElementById('favf-chip').getAttribute('aria-pressed'),
  on:document.body.classList.contains('favf-on')};}"""

SHEET_METRICS = """()=>{const s=document.getElementById('favf-sheet');const sc=document.getElementById('favf-scrim');
 const x=document.getElementById('favf-x');const jb=document.getElementById('jbar');
 if(!s)return null;const sr=s.getBoundingClientRect();const xr=x.getBoundingClientRect();
 const scs=getComputedStyle(sc);const ss=getComputedStyle(s);
 const scr=sc.getBoundingClientRect();
 return {open:document.body.classList.contains('favf-open'),
  vis:ss.visibility,dir:ss.direction,z:ss.zIndex,
  rect:{x:sr.x,y:sr.y,w:sr.width,h:sr.height},
  xCenter:xr.x+xr.width/2,
  scrim:{op:+scs.opacity,pe:scs.pointerEvents,x:scr.x,y:scr.y,w:scr.width,h:scr.height},
  jbar:jb?{z:getComputedStyle(jb).zIndex,top:jb.getBoundingClientRect().top}:null,
  bodyOv:document.body.style.overflow};}"""


def clip_of(rect, pad, vw, vh):
    """rect dict(x/y/w/h) → 패딩 포함 viewport 내 클립."""
    x = max(0, rect["x"] - pad)
    y = max(0, rect["y"] - pad)
    return {"x": x, "y": y,
            "width": min(vw - x, rect["w"] + pad * 2),
            "height": min(vh - y, rect["h"] + pad * 2)}


def open_sheet(pg):
    """실 사용자 경로 — 칩 클릭 → favf-open 대기 → transform .26s + 포커스 60ms 정착."""
    pg.click("#favf-chip")
    pg.wait_for_function("()=>document.body.classList.contains('favf-open')")
    pg.wait_for_timeout(420)
    settle(pg)


def main():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.launch()
            except Exception as e:
                print(f"환경 부재 — chromium 실행 불가({e}). 실행은 대표 로컬.")
                return 2

            # ══ ITEM-1 칩 행 390px + ITEM-7 시트-스크림-jbar (ko 390 light, 저장 없음) ══
            ctx = browser.new_context(viewport=VP, color_scheme="light", locale="ko-KR")
            pg = ctx.new_page()
            errors = watch(pg)
            pg.goto(f"{BASE}/index.html", wait_until="load")
            pg.wait_for_timeout(600)
            settle(pg)
            m = pg.evaluate(ROW_LINES)
            gate("item1/row-render", bool(m), f"{m and m['n']}개 자식")
            if m:
                gate("item1/row-1line", m["lines"] == 1,
                     f"lines={m['lines']} rects={m['rects']}")
                pg.screenshot(path=str(OUT / "item1-chip-row-390.png"),
                              clip=clip_of(m["rowRect"], 12, 390, 844))
            # ITEM-7: 같은 컨텍스트에서 칩 실클릭 → 시트 오픈 풀프레임
            open_sheet(pg)
            s = pg.evaluate(SHEET_METRICS)
            gate("item7/sheet-open", bool(s) and s["open"] and s["vis"] == "visible",
                 f"{s and s['vis']}")
            if s:
                gate("item7/scrim-cover",
                     s["scrim"]["op"] == 1 and s["scrim"]["pe"] == "auto"
                     and s["scrim"]["x"] <= 0 and s["scrim"]["y"] <= 0
                     and s["scrim"]["w"] >= 390 and s["scrim"]["h"] >= 844,
                     f"scrim={s['scrim']}")
                gate("item7/z-order-jbar40-sheet45",
                     bool(s["jbar"]) and s["jbar"]["z"] == "40" and s["z"] == "45",
                     f"jbar={s['jbar']} sheetZ={s['z']}")
                gate("item7/scroll-lock", s["bodyOv"] == "hidden", f"ov='{s['bodyOv']}'")
            pg.screenshot(path=str(OUT / "item7-sheet-scrim-jbar-390.png"))
            gate("h/ko-390/console-0", not errors, "; ".join(errors[:3]))
            pg.close()
            ctx.close()

            # ══ ITEM-2 다크 칩 ON + ITEM-3 dim 0.45 다크 (ko 390 dark, BTS·filterOn) ══
            ctx = browser.new_context(viewport=VP, color_scheme="dark", locale="ko-KR")
            inject_fav(ctx, [ARTIST], True)
            pg = ctx.new_page()
            errors = watch(pg)
            pg.goto(f"{BASE}/index.html", wait_until="load")
            pg.wait_for_timeout(600)
            settle(pg)
            m = pg.evaluate(ROW_LINES)
            gate("item2/chip-on-dark",
                 bool(m) and m["pressed"] == "true" and m["on"],
                 f"pressed={m and m['pressed']} favf-on={m and m['on']}")
            if m:
                pg.screenshot(path=str(OUT / "item2-chip-on-dark-390.png"),
                              clip=clip_of(m["rowRect"], 12, 390, 844))
            # ITEM-3: festival dim 카드(.favf-tbd) 프레임 — ehead opacity 0.45 실측
            dim = pg.evaluate(
                """()=>{const c=document.querySelector('.tp-c .ecard.favf-tbd');
                if(!c)return null;const h=c.querySelector('.ehead');
                return {op:h?getComputedStyle(h).opacity:null,
                 cap:(function(e){return e?getComputedStyle(e).display:null})(c.querySelector('.favf-cap'))};}"""
            )
            gate("item3/fest-dim-045", bool(dim) and dim["op"] == "0.45",
                 f"opacity={dim and dim['op']} cap={dim and dim['cap']}")
            pg.evaluate(
                "()=>{const c=document.querySelector('.tp-c .ecard.favf-tbd');"
                "if(c)c.scrollIntoView({block:'center'});}"
            )
            settle(pg, 300)
            pg.screenshot(path=str(OUT / "item3-fest-dim-dark-390.png"))
            gate("h/ko-dark/console-0", not errors, "; ".join(errors[:3]))
            pg.close()
            ctx.close()

            # ══ ITEM-4 /ar/ RTL — 칩 행 + 시트 오픈 (X 버튼 위치) ══
            ctx = browser.new_context(viewport=VP, color_scheme="light", locale="ar-SA")
            pg = ctx.new_page()
            errors = watch(pg)
            pg.goto(f"{BASE}/ar/index.html", wait_until="load")
            pg.wait_for_timeout(600)
            settle(pg)
            m = pg.evaluate(ROW_LINES)
            gate("item4/ar-row-render", bool(m), f"{m and m['n']}개 자식")
            if m:
                pg.screenshot(path=str(OUT / "item4-chip-row-ar-390.png"),
                              clip=clip_of(m["rowRect"], 12, 390, 844))
            open_sheet(pg)
            s = pg.evaluate(SHEET_METRICS)
            gate("item4/ar-sheet-rtl", bool(s) and s["open"] and s["dir"] == "rtl",
                 f"dir={s and s['dir']}")
            if s:
                # margin-inline-start:auto → RTL에서 X = 시트 좌측 절반 기대
                mid = s["rect"]["x"] + s["rect"]["w"] / 2
                gate("item4/ar-x-left-half", s["xCenter"] < mid,
                     f"xCenter={s['xCenter']:.0f} sheetMid={mid:.0f}")
            pg.screenshot(path=str(OUT / "item4-sheet-ar-390.png"))
            gate("h/ar-390/console-0", not errors, "; ".join(errors[:3]))
            pg.close()
            ctx.close()

            # ══ ITEM-5 데스크탑 시트 + ITEM-6 체크마크 확대 (ko 1280×900, BTS 선택) ══
            ctx = browser.new_context(viewport={"width": 1280, "height": 900},
                                      color_scheme="light", locale="ko-KR",
                                      device_scale_factor=2)
            inject_fav(ctx, [ARTIST], True)
            pg = ctx.new_page()
            errors = watch(pg)
            pg.goto(f"{BASE}/index.html", wait_until="load")
            pg.wait_for_timeout(600)
            settle(pg)
            open_sheet(pg)
            s = pg.evaluate(SHEET_METRICS)
            ok_w = bool(s) and 558 <= s["rect"]["w"] <= 564  # 560 + 보더 box-sizing 변량
            ok_c = bool(s) and abs((s["rect"]["x"] + s["rect"]["w"] / 2) - 640) <= 3
            gate("item5/desktop-560-center", ok_w and ok_c,
                 f"w={s and round(s['rect']['w'])} center={s and round(s['rect']['x'] + s['rect']['w'] / 2)}")
            pg.screenshot(path=str(OUT / "item5-sheet-desktop-1280.png"))
            # ITEM-6: 선택 셀 — 정렬 ① 선택됨 우선 → 첫 셀 = checked 기대
            ck = pg.evaluate(
                """()=>{const c=document.querySelector('#favf-list .favf-cell');
                if(!c)return null;const i=c.querySelector('input');
                const k=c.querySelector('.favf-ck');
                return {checked:i.checked,ckDisp:k?getComputedStyle(k).display:null};}"""
            )
            gate("item6/cell-checked-ckmark",
                 bool(ck) and ck["checked"] and ck["ckDisp"] == "flex",
                 f"{ck}")
            cell = pg.query_selector("#favf-list .favf-cell")
            if cell:
                cell.screenshot(path=str(OUT / "item6-checkmark-cell-zoom.png"))
            gate("h/ko-desktop/console-0", not errors, "; ".join(errors[:3]))
            pg.close()
            ctx.close()

            # ══ ITEM-8 빈 상태 + festival dim 동거 (ko 390, festival-only 키 주입) ══
            ctx = browser.new_context(viewport=VP, color_scheme="light", locale="ko-KR")
            inject_fav(ctx, [FEST_ONLY], True)
            pg = ctx.new_page()
            errors = watch(pg)
            pg.goto(f"{BASE}/index.html", wait_until="load")
            pg.wait_for_timeout(600)
            settle(pg)
            em = pg.evaluate(
                """()=>{const e=document.querySelector('.tp-c .favf-empty');
                const t=document.querySelectorAll('.tp-c .ecard.favf-tbd');
                if(!e)return null;
                return {disp:getComputedStyle(e).display,nTbd:t.length,
                 on:document.body.classList.contains('favf-on')};}"""
            )
            gate("item8/empty-visible",
                 bool(em) and em["on"] and em["disp"] == "block",
                 f"{em}")
            gate("item8/fest-dim-coexist", bool(em) and em["nTbd"] >= 1,
                 f"nTbd={em and em['nTbd']}")
            pg.evaluate(
                "()=>{const e=document.querySelector('.tp-c .favf-empty');"
                "if(e)e.scrollIntoView({block:'start'});}"
            )
            settle(pg, 300)
            frame = pg.evaluate(
                """()=>{const e=document.querySelector('.tp-c .favf-empty');
                const t=document.querySelector('.tp-c .ecard.favf-tbd');
                if(!e||!t)return null;const er=e.getBoundingClientRect(),tr=t.getBoundingClientRect();
                return {emBot:er.bottom,tbdTop:tr.top,coexist:er.bottom<844&&tr.top<844&&tr.bottom>0};}"""
            )
            gate("item8/same-frame", bool(frame) and frame["coexist"], f"{frame}")
            pg.screenshot(path=str(OUT / "item8-empty-plus-festdim-390.png"))
            gate("h/ko-empty/console-0", not errors, "; ".join(errors[:3]))
            pg.close()
            ctx.close()

            browser.close()
    finally:
        srv.shutdown()

    print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + str(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
