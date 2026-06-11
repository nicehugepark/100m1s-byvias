#!/usr/bin/env python3
"""WAVE6 course CTA alignment for the TWICE Seoul guide.

Fixes the component drift where the show-day jump CTA appears near the top of
the 2N3D course, but only inside the Day 3 card for longer courses.
"""

from pathlib import Path
import re
from typing import Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ("", ROOT / "dist" / "twice-thisisfor-seoul.html"),
    ("en", ROOT / "dist" / "en" / "twice-thisisfor-seoul.html"),
]

SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.8" aria-hidden="true">'
    '<path d="M3 7l9-4 9 4v6c0 5-9 8-9 8s-9-3-9-8V7z"/>'
    '<path d="M9 12l2 2 4-4"/></svg>'
)

LABEL = {
    "": "공연 당일(Day 3) 한눈에 보기 →",
    "en": "Show day (Day 3) at a glance →",
}

W6_CSS = "/*W6COURSE*/.showday-jump{min-height:44px;box-sizing:border-box}"


def _panel_span(s: str, panel: str) -> Optional[Tuple[int, int]]:
    start = s.find(f'<div class="sl-panel {panel}">')
    if start < 0:
        return None
    if panel == "sl-4":
        end = s.find('<div class="sl-panel sl-7">', start)
    else:
        end = s.find("</div><!-- /stay-len -->", start)
    if end < 0:
        end = len(s)
    return start, end


def _jump(href: str, lang: str) -> str:
    return (
        f'<a class="showday-jump" data-w6-course-jump="1" href="{href}">'
        f"{SVG}{LABEL[lang]}</a>"
    )


def _insert_top_jump(s: str, lang: str, panel: str, href: str) -> str:
    span = _panel_span(s, panel)
    if not span:
        return s
    start, end = span
    seg = s[start:end]
    marker = f'data-w6-course-jump="1" href="{href}"'
    if marker in seg:
        return s
    m = re.search(r'<p class="crs-sum">.*?</p>', seg, re.S)
    if not m:
        return s
    insert_at = start + m.end()
    return s[:insert_at] + _jump(href, lang) + s[insert_at:]


def _ensure_sl7_target(s: str) -> str:
    span = _panel_span(s, "sl-7")
    if not span:
        return s
    start, end = span
    seg = s[start:end]
    if 'id="showday-s7"' in seg:
        return s
    seg2 = re.sub(
        r'<details class="day-card day-acc"><summary>Day 3\b',
        '<details class="day-card day-acc" id="showday-s7"><summary>Day 3',
        seg,
        count=1,
    )
    if seg2 == seg:
        return s
    return s[:start] + seg2 + s[end:]


def fix(s: str, lang: str) -> str:
    if "W6COURSE" not in s:
        s = s.replace("</style>", W6_CSS + "</style>", 1)
    s = _ensure_sl7_target(s)
    s = _insert_top_jump(s, lang, "sl-4", "#showday-s4")
    s = _insert_top_jump(s, lang, "sl-7", "#showday-s7")
    return s


def main() -> None:
    changed = []
    for lang, path in FILES:
        s0 = path.read_text(encoding="utf-8")
        s = fix(s0, lang)
        if s != s0:
            path.write_text(s, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print("changed:", ", ".join(changed) if changed else "none")


if __name__ == "__main__":
    main()
