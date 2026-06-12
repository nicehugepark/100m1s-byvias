#!/usr/bin/env python3
"""여정 상주 바 검증 게이트 실측 (R46 P1-5 시안 B) — Playwright 390px, 로컬 http.

게이트: (a) 4모드 캡처 홈·리치·이벤트 (라이트/다크 x 풀/미니)
        (b) 44→28 축소 실측 + 미니 탭 확장 + 단계 점등 스크롤 연동 실측 (리치 5단계)
        (c) toast 겹침 0 (공유 버튼 실탭 — toast bottom vs 바 top)
        (d) 푸터 최하단 가림 0 (footer bottom <= 하단 바 union top)
        (h) 콘솔 0 (pageerror + 로컬 리소스 실패. 외부 도메인(GA)은 샌드박스 차단 제외)
        (i) 빨강 임박 전유: D-8+ 빨강 0건 + D-0(LIVE) 빨강·펄스 확인
        (f) locale 표본: ko 홈·리치(한국어 점등) + ja 이벤트 + ar 이벤트(RTL)
        (-) 과거 공연(아카이브) = 바 무렌더 negative + affbar 공존 (z40 < z60)

주의: 사이트 언어 라우터가 브라우저 locale 로 자동 redirect — 컨텍스트 locale 을 페이지 언어로 고정.

R2 캡처 절차 (P0-1 — 증거 자기모순 재발 차단):
  1) 모든 스크롤 후 settle() = scroll → rAF 2프레임 대기 → 측정/캡처 (직후 캡처 race 봉쇄)
  2) 미니 캡처 = zone 앵커 scrollIntoView — 고정 y=700 캡처는 섹션이 프레임에 보이면서
     top이 40% 점등 기준선(vh*0.4) 미달인 "본문 단계3 / 바 1/5" 자기모순 프레임을 만들었음
  3) 이벤트 = affbar yield(P1-1) 실측 후 해제하고 jbar 단독 상태에서 미니/탭 실측
  4) 데스크탑(1280px) rich light/dark 2장 추가 (.wrap 960 변형)
실행: python3 tools/journey_bar_verify.py   (종료 0=ALL PASS)
"""

import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "tools" / "jb-captures"
OUT.mkdir(exist_ok=True)

PORT = 8941
BASE = f"http://127.0.0.1:{PORT}"
VP = {"width": 390, "height": 844}
IMM = {"rgb(198, 40, 40)", "rgb(255, 107, 107)"}  # C62828 / FF6B6B

# (페이지, locale) — locale 라우터 고정용. 이벤트 = 2026-11-19 D-160 (D-8+ 표본)
CAPTURE = {
    "home": ("index.html", "ko-KR"),
    "rich": ("twice-thisisfor-seoul.html", "ko-KR"),
    "event": ("bts-arirang-kaohsiung-1119.html", "ko-KR"),
}

BAR_METRICS = """()=>{const b=document.getElementById('jbar');if(!b)return null;
 const row=b.querySelector('.row').getBoundingClientRect();
 const d=document.getElementById('jbDnum');
 return {rowH:Math.round(row.height),navTop:b.getBoundingClientRect().top,
  z:getComputedStyle(b).zIndex,mini:b.classList.contains('mini'),
  dnum:d.textContent,dColor:getComputedStyle(d).color,
  pulse:!!d.querySelector('.pulse'),
  lit:(function(e){return e?e.textContent.replace(/\\s+/g,' ').trim():''})(document.getElementById('jbLit')),
  miniTxt:(function(e){return e?e.textContent.replace(/\\s+/g,' ').trim():''})(document.getElementById('jbMini')),
  cta:document.getElementById('jbCta').textContent,
  dir:getComputedStyle(b).direction,
  bodyPad:getComputedStyle(document.body).paddingBottom,
  hasCls:document.body.classList.contains('has-jbar')};}"""

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


def dismiss_affbar(pg):
    x = pg.query_selector(".affbar-x")
    if x:
        x.click()
        pg.wait_for_timeout(300)


def settle(pg, ms=120):
    """P0-1 캡처 절차: scroll → rAF 1프레임+ 대기 → 측정/캡처 (스크롤 직후 캡처 race 봉쇄)."""
    pg.evaluate("()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r())))")
    pg.wait_for_timeout(ms)


def main():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), Quiet)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for mode in ("light", "dark"):
                for name, (rel, loc) in CAPTURE.items():
                    ctx = browser.new_context(
                        viewport=VP, color_scheme=mode, locale=loc
                    )
                    pg = ctx.new_page()
                    errors = watch(pg)
                    pg.goto(f"{BASE}/{rel}", wait_until="load")
                    pg.wait_for_timeout(600)

                    # (a) 풀 캡처 + 바 존재 (+f: ko 점등 한국어)
                    m = pg.evaluate(BAR_METRICS)
                    gate(
                        f"a/{name}/{mode}/bar-render",
                        bool(m),
                        f"{m and m['dnum']} | {m and m['lit']}",
                    )
                    if not m:
                        pg.close()
                        ctx.close()
                        continue
                    pg.screenshot(path=str(OUT / f"{name}-{mode}-full.png"))
                    gate(
                        f"b/{name}/{mode}/full-44px",
                        m["rowH"] == 44,
                        f"rowH={m['rowH']}",
                    )
                    gate(f"-/{name}/{mode}/z40", m["z"] == "40", f"z={m['z']}")
                    gate(
                        f"d/{name}/{mode}/body-pad",
                        m["hasCls"] and m["bodyPad"] != "0px",
                        m["bodyPad"],
                    )
                    if mode == "light":
                        if name == "home":
                            # 제거-1: 홈 = 점·점등 라벨 무렌더 (D-num + CTA만)
                            nostage = pg.evaluate(
                                "()=>!document.querySelector('#jbar .stage')"
                                "&&!document.querySelector('#jbar .mininfo')"
                            )
                            gate("f/home/no-stage", nostage, "홈 stage/mininfo DOM 0건")
                        else:
                            gate(
                                f"f/{name}/ko-lit",
                                "인지" in m["lit"] and "1/5" in m["lit"],
                                f"lit='{m['lit']}'",
                            )

                    # (i) 빨강 게이트
                    if name in ("rich", "event"):  # D-28 / D-160 = D-8+
                        gate(
                            f"i/{name}/{mode}/no-red-D8plus",
                            m["dColor"] not in IMM,
                            f"{m['dnum']} {m['dColor']}",
                        )
                    if name == "home":  # 최근접 = 2026-06-12 = D-0 (P1-2: 당일 어휘 D-DAY 통일)
                        gate(
                            f"i/home/{mode}/live-red",
                            m["dnum"] == "D-DAY" and m["dColor"] in IMM and m["pulse"],
                            f"{m['dnum']} {m['dColor']} pulse={m['pulse']}",
                        )
                        href = pg.evaluate(
                            "()=>document.getElementById('jbCta').getAttribute('href')"
                        )
                        gate(
                            f"-/home/{mode}/cta-href",
                            href == "bts-arirang-busan-0612.html",
                            href,
                        )

                    # (b) 축소: 스크롤 다운 → 28px 미니 + 캡처
                    # P1-1: 이벤트 = affbar yield 실측(표시 중 jbar visibility hidden +
                    # 연산 중지) 후 해제 — 미니/탭 실측은 jbar 단독 상태에서.
                    if name == "event":
                        pg.evaluate(
                            "()=>scrollTo(0,Math.round((document.documentElement"
                            ".scrollHeight-innerHeight)*0.25))"
                        )
                        settle(pg, 300)
                        yld = pg.evaluate(
                            """()=>{const a=document.querySelector('.affbar.show');
                            const b=document.getElementById('jbar');
                            return {aff:!!a, vis:b?getComputedStyle(b).visibility:null};}"""
                        )
                        gate(
                            f"-/event/{mode}/affbar-yield",
                            (not yld["aff"]) or yld["vis"] == "hidden",
                            f"{yld}",
                        )
                        dismiss_affbar(pg)
                        pg.evaluate("()=>scrollTo(0,0)")
                        settle(pg, 200)
                    # P0-1: 미니 캡처 = zone 앵커 스크롤 — 고정 y=700은 섹션이 프레임에
                    # 보이면서 top이 40% 점등선 미달인 자기모순 프레임 생성 (구 rich-light-mini)
                    anchor = {"rich": ".steps5", "event": ".btns"}.get(name)
                    if anchor:
                        pg.evaluate(
                            f"()=>document.querySelector('{anchor}').scrollIntoView()"
                        )
                    else:
                        pg.evaluate("()=>scrollTo(0,700)")
                    settle(pg, 300)
                    m2 = pg.evaluate(BAR_METRICS)
                    gate(
                        f"b/{name}/{mode}/mini-28px",
                        m2 and m2["mini"] and m2["rowH"] == 28,
                        f"rowH={m2 and m2['rowH']} miniTxt={m2 and m2['miniTxt']}",
                    )
                    pg.screenshot(path=str(OUT / f"{name}-{mode}-mini.png"))
                    # 늦은 레이아웃 시프트가 scroll 재발화 → 탭 직후 재축소 가능 — settle 후 탭
                    pg.wait_for_function(
                        "()=>new Promise(r=>{const y=scrollY;"
                        "setTimeout(()=>r(scrollY===y),120)})"
                    )
                    pg.mouse.click(195, 830)
                    # height transition .18s — 중간 측정 아티팩트 방지: 클래스 해제 + 44px 도달 대기
                    try:
                        pg.wait_for_function(
                            "()=>{const b=document.getElementById('jbar');"
                            "return !b.classList.contains('mini')&&"
                            "Math.round(b.querySelector('.row').getBoundingClientRect().height)===44}",
                            timeout=1500,
                        )
                        expanded = True
                    except Exception:
                        expanded = False
                    m3 = pg.evaluate(BAR_METRICS)
                    gate(
                        f"b/{name}/{mode}/tap-expand",
                        expanded,
                        f"rowH={m3 and m3['rowH']} mini={m3 and m3['mini']}",
                    )

                    # (b) 단계 점등 스크롤 연동 (리치 5존: 1→3→5→4→2 문서 순)
                    if name == "rich":
                        seq = [
                            (".steps5", "3/5"),
                            ("#sec-arrive", "5/5"),
                            ("#sec-stays", "4/5"),
                            ("#sec-ticketing", "2/5"),
                        ]
                        for sel, want in seq:
                            pg.evaluate(
                                f"()=>document.querySelector('{sel}').scrollIntoView()"
                            )
                            settle(pg, 250)
                            got = pg.evaluate(BAR_METRICS)
                            txt = (
                                (got["miniTxt"] if got["mini"] else got["lit"])
                                if got
                                else ""
                            )
                            gate(
                                f"b/rich/{mode}/stage@{sel}",
                                want in txt,
                                f"got='{txt}'",
                            )
                        pg.evaluate("()=>scrollTo(0,0)")
                        settle(pg, 300)
                        got = pg.evaluate(BAR_METRICS)
                        gate(
                            f"b/rich/{mode}/stage@top",
                            got and "1/5" in got["lit"] and not got["mini"],
                            f"lit='{got and got['lit']}'",
                        )

                    # (c) toast 겹침: 공유 실탭 → toast bottom vs 바 top
                    pg.evaluate("()=>scrollTo(0,0)")
                    settle(pg, 300)
                    share = pg.query_selector("#shareBtn")
                    if share:
                        share.click()
                        pg.wait_for_timeout(350)
                        t = pg.evaluate("""()=>{const t=document.querySelector('.share-toast');
                            const b=document.getElementById('jbar');if(!t||!b)return null;
                            return {tb:t.getBoundingClientRect().bottom,
                                    bt:b.getBoundingClientRect().top,
                                    shown:t.classList.contains('show')};}""")
                        gate(
                            f"c/{name}/{mode}/toast-clear",
                            bool(t) and t["shown"] and t["tb"] <= t["bt"] + 0.5,
                            f"{t}",
                        )
                        pg.wait_for_timeout(1900)
                    else:
                        gate(
                            f"c/{name}/{mode}/share-btn-found",
                            name == "home",
                            "no #shareBtn",
                        )

                    # (d) 푸터 가림 0
                    pg.evaluate("()=>scrollTo(0,document.documentElement.scrollHeight)")
                    settle(pg, 400)
                    f = pg.evaluate("""()=>{const cand=[...document.querySelectorAll('.disc-hub,.foot,footer')].pop();
                        if(!cand)return null;
                        const jb=document.getElementById('jbar');
                        const ab=document.querySelector('.affbar.show');
                        const tops=[jb&&jb.getBoundingClientRect().top, ab&&ab.getBoundingClientRect().top]
                          .filter(v=>typeof v==='number');
                        return {fb:cand.getBoundingClientRect().bottom, barTop:Math.min(...tops),
                                affbar:!!ab};}""")
                    gate(
                        f"d/{name}/{mode}/footer-clear",
                        bool(f) and f["fb"] <= f["barTop"] + 1,
                        f"{f}",
                    )

                    # (h) 콘솔 0
                    gate(
                        f"h/{name}/{mode}/console-0", not errors, "; ".join(errors[:3])
                    )
                    pg.close()
                    ctx.close()

            # 과거 공연 negative + locale 표본 (라이트 1회)
            ctx = browser.new_context(viewport=VP, color_scheme="light", locale="ko-KR")
            pg = ctx.new_page()
            pg.goto(f"{BASE}/blackpink-deadline-tokyo.html", wait_until="load")
            pg.wait_for_timeout(400)
            gone = pg.evaluate(
                "()=>({bar:!!document.getElementById('jbar'),"
                "cls:document.body.classList.contains('has-jbar'),"
                "pad:getComputedStyle(document.body).paddingBottom})"
            )
            gate("-/past-event/no-bar", not gone["bar"] and not gone["cls"], f"{gone}")
            pg.close()
            ctx.close()

            for rel, loc, want, wantdir in (
                ("ja/twice-thisisfor-seoul.html", "ja-JP", "発見", "ltr"),
                ("ar/bts-arirang-kaohsiung-1119.html", "ar-SA", "اكتشف", "rtl"),
            ):
                ctx = browser.new_context(viewport=VP, color_scheme="light", locale=loc)
                pg = ctx.new_page()
                errors = watch(pg)
                pg.goto(f"{BASE}/{rel}", wait_until="load")
                pg.wait_for_timeout(600)
                m = pg.evaluate(BAR_METRICS)
                tag = rel.split("/")[0]
                gate(
                    f"f/{tag}/locale-lit",
                    bool(m) and want in m["lit"],
                    f"lit='{m and m['lit']}' dir={m and m['dir']}",
                )
                if wantdir == "rtl":
                    gate(
                        "f/ar/rtl-dir",
                        bool(m) and m["dir"] == "rtl",
                        f"dir={m and m['dir']}",
                    )
                gate(f"h/{tag}/console-0", not errors, "; ".join(errors[:2]))
                pg.screenshot(path=str(OUT / f"locale-{tag}.png"))
                pg.close()
                ctx.close()

            # R2: 데스크탑(>=760px) 캡처 — rich .wrap 960 변형 포함, light/dark
            for mode in ("light", "dark"):
                ctx = browser.new_context(
                    viewport={"width": 1280, "height": 900},
                    color_scheme=mode,
                    locale="ko-KR",
                )
                pg = ctx.new_page()
                errors = watch(pg)
                pg.goto(f"{BASE}/twice-thisisfor-seoul.html", wait_until="load")
                pg.wait_for_timeout(600)
                settle(pg, 200)
                md = pg.evaluate(BAR_METRICS)
                gate(
                    f"a/rich-desktop/{mode}/bar-render",
                    bool(md) and md["rowH"] == 44,
                    f"{md and md['dnum']} rowH={md and md['rowH']}",
                )
                gate(f"h/rich-desktop/{mode}/console-0", not errors, "; ".join(errors[:2]))
                pg.screenshot(path=str(OUT / f"rich-desktop-{mode}.png"))
                pg.close()
                ctx.close()
            browser.close()
    finally:
        srv.shutdown()

    print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + str(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
