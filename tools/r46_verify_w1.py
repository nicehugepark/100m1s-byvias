#!/usr/bin/env python3
"""R46 W1 렌더 검증 — 390px 라이트/다크, 콘솔 0, 칩 bbox, tk-badge 상태, 캡처."""

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
PORT = 8946


def serve():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=str(DIST), **k)

        def log_message(self, *a):
            pass

    srv = socketserver.TCPServer(("127.0.0.1", PORT), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


JS = """
() => {
  const out = {};
  const affs = [...document.querySelectorAll('a[data-aff="1"]')];
  out.aff_count = affs.length;
  const vendors = [...new Set(affs.map(a => a.getAttribute('data-aff-vendor')))];
  out.vendors = vendors;
  if (affs.length) {
    const r = affs[0].getBoundingClientRect();
    out.first_aff = {vendor: affs[0].getAttribute('data-aff-vendor'),
                     y: Math.round(r.top + window.scrollY), text: affs[0].textContent.trim().slice(0,40)};
    const st = getComputedStyle(affs[0], '::after');
    out.first_aff_chip = {content: st.content, display: st.display, bg: st.backgroundColor, color: st.color};
  }
  out.hub = document.querySelectorAll('.disc-hub').length;
  out.mini = document.querySelectorAll('.disc-mini').length;
  const hubR = document.querySelector('.disc-hub');
  out.hub_y = hubR ? Math.round(hubR.getBoundingClientRect().top + window.scrollY) : null;
  const mini = document.querySelector('.disc-mini');
  out.mini_y = mini ? Math.round(mini.getBoundingClientRect().top + window.scrollY) : null;
  const prep = document.querySelector('.prep-list');
  out.prep_y = prep ? Math.round(prep.getBoundingClientRect().top + window.scrollY) : null;
  const tk = document.querySelector('.tk-badge[data-tkdate="2026-06-11"]');
  out.tk_general = tk ? {text: tk.textContent, cls: tk.className} : null;
  const tk9 = document.querySelector('.tk-badge[data-tkdate="2026-06-09"]');
  out.tk_presale = tk9 ? {text: tk9.textContent, cls: tk9.className} : null;
  // 동종 고지 중복 본문 grep
  const body = document.body.innerText;
  out.dup = {};
  for (const p of ['알림 기능은 없습니다','정보 최종 확인','비공식','rough market rates','unofficial','last verified']) {
    out.dup[p] = (body.match(new RegExp(p.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&'),'gi'))||[]).length;
  }
  return out;
}
"""


def main():
    srv = serve()
    results = {}
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for lang, path in [
            ("ko", "/twice-thisisfor-seoul.html"),
            ("en", "/en/twice-thisisfor-seoul.html"),
        ]:
            for scheme in ("light", "dark"):
                ctx = b.new_context(
                    viewport={"width": 390, "height": 844},
                    color_scheme=scheme,
                    locale="ko-KR" if lang == "ko" else "en-US",
                )
                page = ctx.new_page()
                errors = []
                page.on(
                    "console",
                    lambda m: errors.append(m.text) if m.type == "error" else None,
                )
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.goto(
                    f"http://127.0.0.1:{PORT}{path}",
                    wait_until="networkidle",
                    timeout=30000,
                )
                page.wait_for_timeout(400)
                data = page.evaluate(JS)
                data["console_errors"] = errors
                results[f"{lang}-{scheme}"] = data
                # 캡처: 인트로(첫 어필 영역) / OTA 군집 / 허브
                if data.get("first_aff"):
                    page.evaluate(
                        f"window.scrollTo(0,{max(0, data['first_aff']['y'] - 200)})"
                    )
                    page.wait_for_timeout(150)
                    page.screenshot(path=str(SHOT / f"w1-{lang}-{scheme}-firstaff.png"))
                if data.get("mini_y"):
                    page.evaluate(f"window.scrollTo(0,{max(0, data['mini_y'] - 150)})")
                    page.wait_for_timeout(150)
                    page.screenshot(path=str(SHOT / f"w1-{lang}-{scheme}-ota.png"))
                if data.get("hub_y"):
                    page.evaluate(f"window.scrollTo(0,{max(0, data['hub_y'] - 60)})")
                    page.wait_for_timeout(150)
                    page.screenshot(path=str(SHOT / f"w1-{lang}-{scheme}-hub.png"))
                ctx.close()
        b.close()
    srv.shutdown()
    print(json.dumps(results, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
