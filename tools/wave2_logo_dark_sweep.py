#!/usr/bin/env python3
"""다크모드 로고 'by' 소실 fix (WAVE2-LOGO-v1) — 전 페이지 멱등 스윕.

logo.svg 'by' tspan fill #23272F(네이비) vs 다크 배경 #211F18 대비 1.2:1 → 소실.
처방: 다크 전용 변형 logo-dark.svg('by'=#ECE9E0 잉크 톤, 'bias'=#E84A7F 유지) 생성
+ 전 페이지 <img class="logo"> 를 <picture> + prefers-color-scheme source 로 래핑.
CSS filter 핵 대신 정직한 다크 변형 자산 (브랜드 핑크 보존).

dist/ = 라이브 SSOT (FLR-20260611-TEC-001). repo-root logo-dark.svg 도 동기 생성.

실행: python3 tools/wave2_logo_dark_sweep.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

LOGO_DARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 206 90" width="206" height="90" role="img" aria-label="ByBias">
  <title>ByBias</title>
  <text x="14" y="66" font-family="-apple-system,BlinkMacSystemFont,'Apple SD Gothic Neo','Segoe UI',Roboto,Helvetica,Arial,sans-serif" font-size="60" font-weight="700" letter-spacing="-1.5">
    <tspan fill="#ECE9E0">by</tspan><tspan fill="#E84A7F">bias</tspan>
  </text>
</svg>
"""

IMG_RE = re.compile(r'<img class="logo" src="((?:\.\./)?)logo\.svg"([^>]*)>')


def wrap(m):
    prefix = m.group(1)
    return (
        f'<picture><source srcset="{prefix}logo-dark.svg" '
        'media="(prefers-color-scheme: dark)">'
        f'<img class="logo" src="{prefix}logo.svg"{m.group(2)}></picture>'
    )


def main():
    (DIST / "logo-dark.svg").write_text(LOGO_DARK, encoding="utf-8")
    (ROOT / "logo-dark.svg").write_text(LOGO_DARK, encoding="utf-8")
    n_files = 0
    n_imgs = 0
    for f in sorted(DIST.rglob("*.html")):
        html = f.read_text(encoding="utf-8")
        if "logo-dark.svg" in html:
            continue  # 멱등
        html2, n = IMG_RE.subn(wrap, html)
        if n:
            f.write_text(html2, encoding="utf-8")
            n_files += 1
            n_imgs += n
    print(f"logo-dark sweep: files={n_files} imgs={n_imgs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
