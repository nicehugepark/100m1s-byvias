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


def _move_base_jump_after_summary(s: str, panel: str, href: str) -> str:
    start = s.find(f'<div class="crs-panel {panel}">')
    if start < 0:
        return s
    a_start = s.find(f'<a class="showday-jump" href="{href}"', start)
    p_start = s.find('<p class="crs-sum">', start)
    if a_start < 0 or p_start < 0 or a_start > p_start:
        return s
    a_end = s.find("</a>", a_start)
    if a_end < 0:
        return s
    a_end += len("</a>")
    jump = s[a_start:a_end]
    s = s[:a_start] + s[a_end:]
    p_start = s.find('<p class="crs-sum">', start)
    p_end = s.find("</p>", p_start)
    if p_start < 0 or p_end < 0:
        return s
    p_end += len("</p>")
    return s[:p_end] + jump + s[p_end:]


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


def _remove_inner_jump(s: str, panel: str, target_id: str) -> str:
    span = _panel_span(s, panel)
    if not span:
        return s
    start, end = span
    seg = s[start:end]
    marker = f'id="{target_id}"'
    body_start = seg.find(marker)
    if body_start < 0:
        return s
    m = re.search(r'<a class="showday-jump" href="#showday-s[47]">.*?</a>', seg[body_start:], re.S)
    if not m:
        return s
    cut_start = body_start + m.start()
    cut_end = body_start + m.end()
    seg = seg[:cut_start] + seg[cut_end:]
    return s[:start] + seg + s[end:]


def fix(s: str, lang: str) -> str:
    if "W6COURSE" not in s:
        s = s.replace("</style>", W6_CSS + "</style>", 1)
    s = _move_base_jump_after_summary(s, "cp-0", "#showday-c0")
    s = _move_base_jump_after_summary(s, "cp-1", "#showday-c1")
    s = _ensure_sl7_target(s)
    s = _insert_top_jump(s, lang, "sl-4", "#showday-s4")
    s = _insert_top_jump(s, lang, "sl-7", "#showday-s7")
    s = _remove_inner_jump(s, "sl-4", "showday-s4")
    s = _remove_inner_jump(s, "sl-7", "showday-s7")
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
