#!/usr/bin/env python3
"""ByVias SEO 기반 산출물 생성 — canonical 주입 + sitemap.xml + robots.txt.

원칙 (발명 금지):
  - 각 페이지의 canonical / sitemap loc 은 그 페이지가 이미 보유한
    <meta property="og:url"> 값에서 추출한다. URL 을 새로 조합하지 않는다.
  - lastmod 는 파일별 git 최종 commit 일자(YYYY-MM-DD). git 이력 없으면 생략.
  - canonical 주입은 멱등(idempotent): 이미 있으면 건드리지 않는다.

사용자 노출 페이지 전수(847) 대상. dist/og/ 의 이미지·CNAME 등 비-HTML 은 제외.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"
BASE = "https://bybias.100m1s.com"

OG_URL_RE = re.compile(r'<meta property="og:url" content="([^"]+)"')
CANONICAL_RE = re.compile(r'<link rel="canonical"')
ICON_RE = re.compile(r'(<link rel="icon"[^>]*>)')


def og_url(html: str) -> str | None:
    m = OG_URL_RE.search(html)
    return m.group(1) if m else None


def git_lastmod(path: Path) -> str | None:
    """파일의 git 최종 commit 일자(YYYY-MM-DD). 이력 없으면 None."""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", str(path)],
            cwd=DIST.parent,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return out or None
    except subprocess.CalledProcessError:
        return None


def inject_canonical(path: Path) -> tuple[str | None, bool]:
    """canonical 주입(멱등). (loc_url, changed) 반환."""
    html = path.read_text(encoding="utf-8")
    loc = og_url(html)
    if loc is None:
        print(f"  SKIP (og:url 부재): {path}", file=sys.stderr)
        return None, False
    if CANONICAL_RE.search(html):
        return loc, False  # 이미 존재 — 무간섭
    tag = f'\n<link rel="canonical" href="{loc}">'
    new = ICON_RE.sub(lambda m: m.group(1) + tag, html, count=1)
    if new == html:
        print(f"  SKIP (icon 앵커 부재): {path}", file=sys.stderr)
        return loc, False
    path.write_text(new, encoding="utf-8")
    return loc, True


def main() -> int:
    pages = sorted(DIST.rglob("*.html"))
    if not pages:
        print("dist/*.html 0건 — 중단", file=sys.stderr)
        return 1

    entries: list[tuple[str, str | None]] = []  # (loc, lastmod)
    injected = 0
    for path in pages:
        loc, changed = inject_canonical(path)
        if loc is None:
            continue
        injected += int(changed)
        entries.append((loc, git_lastmod(path)))

    # sitemap.xml — loc 정렬, lastmod 있으면 포함
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, lastmod in sorted(entries):
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        if lastmod:
            lines.append(f"    <lastmod>{lastmod}</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # robots.txt — AI 검색엔진 포함 전체 허용 (ByVias 는 SEO 유입이 생명)
    robots = f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n"
    (DIST / "robots.txt").write_text(robots, encoding="utf-8")

    print(
        f"pages={len(entries)} canonical_injected={injected} "
        f"sitemap_urls={len(entries)} robots=1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
