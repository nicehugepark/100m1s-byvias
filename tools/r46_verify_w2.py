#!/usr/bin/env python3
"""R46 W2 렌더 검증 — 390px 라이트/다크 ko·en, bbox 실측 + 동작 + 콘솔 + 캡처."""

import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SHOT = ROOT / "shots-r46"
SHOT.mkdir(exist_ok=True)
PORT = 8947


def serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(DIST), **k)

        def log_message(self, *a):
            pass

    srv = socketserver.TCPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


HOME_JS = """
() => {
  const out = {};
  // F4: 모든 dtkn 단일 라인 (줄쪼갬 0)
  const dt = [...document.querySelectorAll('.dtkn')];
  out.dtkn_total = dt.length;
  out.dtkn_multiline = dt.filter(s => s.getClientRects().length > 1).length;
  // F7: 이중 구조 0 — h2 지난 이벤트와 archive 사이 grid 없음 (DOM 검사)
  const arch = document.querySelector('details.w5-archive');
  out.archive = !!arch;
  out.archive_summary = arch ? arch.querySelector('summary').textContent.trim() : null;
  out.archive_cards = arch ? arch.querySelectorAll('.ecard').length : 0;
  let sib = arch ? arch.previousElementSibling : null;
  out.before_archive = sib ? (sib.tagName + '.' + sib.className) : null;
  out.visible_past_grid = sib && sib.classList.contains('grid') ? 1 : 0;
  out.scroll_h = document.documentElement.scrollHeight;
  // F9: 당일(오늘) 카드 — live-cta + dd-live
  const lc = [...document.querySelectorAll('.live-cta')];
  out.live_cta = lc.length;
  if (lc.length) {
    const r = lc[0].getBoundingClientRect();
    out.live_cta_box = {w: Math.round(r.width), h: Math.round(r.height)};
    out.live_cta_text = lc[0].textContent;
    out.live_cta_card = lc[0].closest('.ecard')?.getAttribute('href');
    out.live_cta_y = Math.round(r.top + scrollY);
  }
  out.dd_live = document.querySelectorAll('.dd-live').length;
  // F10: 회색 아바타 0
  out.gray_abadge = [...document.querySelectorAll('.abadge')]
    .filter(b => getComputedStyle(b).backgroundColor === 'rgb(138, 138, 138)').length;
  out.abadge_total = document.querySelectorAll('.abadge').length;
  return out;
}
"""

RICH_JS = """
() => {
  const out = {};
  // F6: tap44 bbox 실측
  out.tap44 = [...document.querySelectorAll('.tap44')].map(a => {
    const r = a.getBoundingClientRect();
    return {t: a.textContent.trim().slice(0, 28), w: Math.round(r.width), h: Math.round(r.height)};
  });
  // F8: 호텔 카드 예약 행(앵커) 1개
  out.stay_cards = [...document.querySelectorAll('.stay-card')].map(c => ({
    name: c.querySelector('.sname')?.textContent.trim().split(' ')[0],
    cta_anchors: c.querySelectorAll('.stay-cta a').length,
    ota_rows: c.querySelectorAll('.ota-row').length,
    vendor: c.querySelector('.stay-cta a')?.getAttribute('data-aff-vendor'),
  }));
  // F11: skyscanner href
  out.sky = [...document.querySelectorAll('a[href*="skyscanner"]')].map(a => a.getAttribute('href'));
  // F4
  const dt = [...document.querySelectorAll('.dtkn')];
  out.dtkn_total = dt.length;
  out.dtkn_multiline = dt.filter(s => s.getClientRects().length > 1).length;
  return out;
}
"""

LANG_JS = """
async () => {
  const d = document.querySelector('details.langpick');
  if (!d) return {found: false};
  d.setAttribute('open', '');
  await new Promise(r => setTimeout(r, 80));
  const openBefore = d.hasAttribute('open');
  document.querySelector('h1, .hero, body').dispatchEvent(
    new MouseEvent('click', {bubbles: true}));
  await new Promise(r => setTimeout(r, 120));
  return {found: true, openBefore, openAfter: d.hasAttribute('open')};
}
"""


def main():
    srv = serve()
    res = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for lang, home, rich in [
            ("ko", "/index.html", "/twice-thisisfor-seoul.html"),
            ("en", "/en/index.html", "/en/twice-thisisfor-seoul.html"),
        ]:
            for scheme in ("light", "dark"):
                ctx = b.new_context(
                    viewport={"width": 390, "height": 844},
                    color_scheme=scheme,
                    locale="ko-KR" if lang == "ko" else "en-US",
                )
                key = f"{lang}-{scheme}"
                page = ctx.new_page()
                errs = []
                page.on(
                    "console",
                    lambda m: errs.append(m.text) if m.type == "error" else None,
                )
                page.on("pageerror", lambda e: errs.append(str(e)))
                page.goto(
                    f"http://127.0.0.1:{PORT}{home}",
                    wait_until="networkidle",
                    timeout=30000,
                )
                page.wait_for_timeout(400)
                h = page.evaluate(HOME_JS)
                h["lang_dismiss"] = page.evaluate(LANG_JS)
                h["console"] = list(errs)
                res[f"home-{key}"] = h
                # 캡처: 당일 카드 + 아카이브 줄
                if h.get("live_cta_y"):
                    page.evaluate(f"scrollTo(0,{max(0, h['live_cta_y'] - 300)})")
                    page.wait_for_timeout(150)
                    page.screenshot(path=str(SHOT / f"w2-home-{key}-live.png"))
                page.evaluate(
                    "document.querySelector('details.w5-archive')?.scrollIntoView({block:'center'})"
                )
                page.wait_for_timeout(150)
                page.screenshot(path=str(SHOT / f"w2-home-{key}-archive.png"))
                errs.clear()
                page.goto(
                    f"http://127.0.0.1:{PORT}{rich}",
                    wait_until="networkidle",
                    timeout=30000,
                )
                page.wait_for_timeout(400)
                r = page.evaluate(RICH_JS)
                r["console"] = list(errs)
                res[f"rich-{key}"] = r
                page.evaluate(
                    "document.querySelector('.stay-card')?.scrollIntoView({block:'center'})"
                )
                page.wait_for_timeout(150)
                page.screenshot(path=str(SHOT / f"w2-rich-{key}-stay.png"))
                ctx.close()
        b.close()
    srv.shutdown()
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
