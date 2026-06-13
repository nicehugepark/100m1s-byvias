#!/usr/bin/env python3
"""Normalize small mobile touch targets on the TWICE Seoul pages."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "dist" / "twice-thisisfor-seoul.html",
    ROOT / "dist" / "en" / "twice-thisisfor-seoul.html",
]

REPLACEMENTS = [
    (
        ".jump-nav a{display:inline-flex;align-items:center;gap:5px;font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;padding:7px 12px;min-height:36px;border:1px solid var(--line);border-radius:999px;background:var(--card)}",
        ".jump-nav a{display:inline-flex;align-items:center;gap:5px;font-size:13px;font-weight:600;color:var(--accent);text-decoration:none;padding:9px 12px;min-height:44px;box-sizing:border-box;border:1px solid var(--line);border-radius:999px;background:var(--card)}",
    ),
    (
        ".ota-btn{display:inline-flex;align-items:center;min-height:36px;color:#C7396B;font-size:12px;font-weight:600;text-decoration:none}",
        ".ota-btn{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;color:#C7396B;font-size:12px;font-weight:600;text-decoration:none}",
    ),
    (
        ".steps5 .s5-go{display:inline-flex;align-items:center;min-height:32px;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none}",
        ".steps5 .s5-go{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none}",
    ),
    (
        ".langbar .lng{display:inline-flex;align-items:center;min-height:36px;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:8px}",
        ".langbar .lng{display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;color:var(--muted);text-decoration:none;padding:6px 10px;border-radius:8px}",
    ),
    (
        ".langpick>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;min-height:36px;padding:6px 12px;border:1px solid var(--line);border-radius:8px;font-size:12px;font-weight:600;color:var(--muted);background:var(--card)}",
        ".langpick>summary{list-style:none;cursor:pointer;display:inline-flex;align-items:center;gap:6px;min-height:44px;box-sizing:border-box;padding:6px 12px;border:1px solid var(--line);border-radius:8px;font-size:12px;font-weight:600;color:var(--muted);background:var(--card);min-width:140px;white-space:nowrap}",
    ),
    (
        ".langpick .langmenu .lng{display:flex;align-items:center;min-height:40px;padding:8px 12px;border-radius:6px;font-size:13px;color:var(--muted);text-decoration:none}",
        ".langpick .langmenu .lng{display:flex;align-items:center;min-height:44px;box-sizing:border-box;padding:8px 12px;border-radius:6px;font-size:13px;color:var(--muted);text-decoration:none}",
    ),
    (
        ".showday-jump{display:inline-flex;align-items:center;gap:6px;min-height:40px;margin:4px 0 8px;padding:6px 12px;font-size:13px;font-weight:600;color:#AD2E5C;text-decoration:none;background:var(--rose-soft);border:1px solid #F3B6CC;border-radius:10px}",
        ".showday-jump{display:inline-flex;align-items:center;gap:6px;min-height:44px;box-sizing:border-box;margin:4px 0 8px;padding:6px 12px;font-size:13px;font-weight:600;color:#AD2E5C;text-decoration:none;background:var(--rose-soft);border:1px solid #F3B6CC;border-radius:10px}",
    ),
    (
        ".stay-iglink{align-self:flex-start;font-size:12px;color:var(--muted);text-decoration:none;font-weight:500;min-height:36px;display:inline-flex;align-items:center;gap:5px;margin-top:0}",
        ".stay-iglink{align-self:flex-start;font-size:12px;color:var(--muted);text-decoration:none;font-weight:500;min-height:44px;box-sizing:border-box;display:inline-flex;align-items:center;gap:5px;margin-top:0}",
    ),
    (
        "display:inline-flex;align-items:center;min-height:32px;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none",
        "display:inline-flex;align-items:center;min-height:44px;box-sizing:border-box;padding:4px 0;margin-top:4px;font-size:12.5px;font-weight:600;color:var(--accent);text-decoration:none",
    ),
    (
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:6px 10px;'",
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'",
    ),
    (
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'\n  +'border:1px solid var(--line);border-radius:999px;background:transparent;min-height:32px;display:inline-flex;align-items:center;white-space:nowrap}'",
        "+'.affbar a{flex:0 0 auto;font-size:12px;font-weight:600;color:var(--accent);text-decoration:none;padding:10px 12px;min-height:44px;box-sizing:border-box;'\n  +'border:1px solid var(--line);border-radius:999px;background:transparent;display:inline-flex;align-items:center;white-space:nowrap}'",
    ),
    (
        "+'.affbar-x{flex:0 0 auto;border:0;background:transparent;color:var(--muted);font-size:18px;line-height:1;padding:4px 6px;cursor:pointer}';",
        "+'.affbar-x{flex:0 0 auto;border:0;background:transparent;color:var(--muted);font-size:18px;line-height:1;min-width:44px;min-height:44px;padding:0;cursor:pointer}';",
    ),
]


def patch_file(path: Path) -> bool:
    html = path.read_text(encoding="utf-8")
    before = html
    for old, new in REPLACEMENTS:
        html = html.replace(old, new)
    if html == before:
        return False
    path.write_text(html, encoding="utf-8")
    return True


def main() -> None:
    changed = [path for path in TARGETS if patch_file(path)]
    if changed:
        print("changed:", ", ".join(str(path.relative_to(ROOT)) for path in changed))
    else:
        print("unchanged")


if __name__ == "__main__":
    main()
