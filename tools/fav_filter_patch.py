#!/usr/bin/env python3
"""최애 필터 1단계 (A안 칩 행 + 바텀 시트) wiring — Q-20260607-130 (대표 GO, SPEC.md 기준).

적용 범위: 탭(.tabs) 보유 페이지 = index 11언어 한정 (root + 10 locale 디렉토리).
  필터는 목록(index)의 개념 — 상세 페이지는 필터 무관 (SPEC §1). 847p 전수 주입 불필요.
필터 로직 = dist/assets/fav-filter.js 단일 모듈 (SSOT — 페이지별 복제 금지, jbar 동형).
페이지별 주입 = 설정 1줄 (로케일) + 모듈 로드, jbar-js 선례 동형:
  <script id="favf-js">window.__FAV={l:"ja"};</script><script src="../assets/fav-filter.js"></script>

매칭 키는 런타임 (fav-filter.js): 기존 .abadge[title] = events[].artist 원문 재사용
(ko/ja/ar 로케일 불변 실측) — 카드 마크업 무변경, 주입은 script 2태그뿐.

멱등: 'id="favf-js"' 존재 + 설정 일치 시 skip — 재실행 diff 0. 설정 불일치 시 자가치유 교체.
</body> 정확 1회 아니면 raise (원자적).
실행: python3 tools/fav_filter_patch.py        # 패치 + verify
      python3 tools/fav_filter_patch.py --verify-only
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARK = 'id="favf-js"'
LOCALES = [
    "en",
    "ja",
    "zh-cn",
    "zh-tw",
    "es",
    "th",
    "id",
    "pt",
    "ar",
    "vi",
]


def targets():
    """탭 보유 페이지 = index 11언어."""
    pages = [DIST / "index.html"]
    for lc in LOCALES:
        p = DIST / lc / "index.html"
        if p.exists():
            pages.append(p)
    return pages


def lang_of(path: Path) -> str:
    parent = path.parent.name
    return parent if parent in LOCALES else "ko"


def snippet_for(path: Path) -> str:
    lang = lang_of(path)
    rel = "assets/fav-filter.js" if lang == "ko" else "../assets/fav-filter.js"
    return (
        f'<script id="favf-js">window.__FAV={{l:"{lang}"}};</script>'
        f'<script src="{rel}"></script>'
    )


def patch(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    snippet = snippet_for(path)
    if MARK in html:
        if snippet in html:
            return "skip"
        # 자가치유: 설정 불일치 시 기존 주입부 교체
        html = re.sub(
            r'<script id="favf-js">[^<]*</script><script src="[^"]*fav-filter\.js"></script>',
            snippet.replace("\\", "\\\\"),
            html,
            count=1,
        )
        path.write_text(html, encoding="utf-8")
        return "heal"
    if html.count("</body>") != 1:
        raise SystemExit(f"FAIL [{path}] </body> count != 1")
    html = html.replace("</body>", snippet + "</body>", 1)
    path.write_text(html, encoding="utf-8")
    return "patch"


def verify() -> int:
    fails = 0
    js = DIST / "assets" / "fav-filter.js"
    if not js.exists():
        print("FAIL fav-filter.js 부재")
        fails += 1
    for p in targets():
        html = p.read_text(encoding="utf-8")
        if snippet_for(p) not in html:
            print(f"FAIL [{p.relative_to(ROOT)}] 주입 누락/불일치")
            fails += 1
        if html.count(MARK) != 1:
            print(f"FAIL [{p.relative_to(ROOT)}] marker count != 1")
            fails += 1
    return fails


def main():
    verify_only = "--verify-only" in sys.argv
    pages = targets()
    if not verify_only:
        counts = {"patch": 0, "skip": 0, "heal": 0}
        for p in pages:
            counts[patch(p)] += 1
        print(f"patched={counts['patch']} skipped={counts['skip']} healed={counts['heal']} / {len(pages)} pages")
    fails = verify()
    if fails:
        raise SystemExit(f"VERIFY FAIL {fails}건")
    print(f"VERIFY PASS — {len(pages)} pages")


if __name__ == "__main__":
    main()
