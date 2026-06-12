#!/usr/bin/env python3
"""Locale parity gate (P0-2, R43) — 모든 fix의 완료 조건 게이트.

모든 체크는 11 locale 각각에 대해 대상 요소 존재를 grep으로 검사한다.
locale 페이지 구조가 다른 경우(예: 코스 리치 페이지는 ko·en만 존재, 9 locale은
경량 이벤트 페이지)는 `locales` 필드로 기대 범위를 *명시*해야 하며, 기대 범위 밖
locale은 GAP으로 별도 출력(침묵 금지 — 9 locale 미적용 3회째 재발 차단 본질).

사용: python3 tools/locale_parity_gate.py            # 전체 체크
      python3 tools/locale_parity_gate.py --list     # 체크 목록
종료코드: 0=PASS, 1=FAIL(기대 locale에서 패턴 부재).

새 wave의 fix 추가 시 CHECKS에 entry 추가만 하면 된다:
  {"id": ..., "page": 파일명, "pattern": 정규식, "locales": ALL 또는 부분집합,
   "gap_note": 부분집합인 이유(필수 — 명시 없는 부분집합 금지)}
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

ALL = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]
RICH = ["", "en"]  # 코스 리치 페이지 보유 locale
COURSE = "twice-thisisfor-seoul.html"

CHECKS = [
    # ---- WAVE8 (R43 2심 조니 확정) ----
    {
        "id": "w8-home-touch-css",
        "page": "index.html",
        "pattern": r"/\*W8R43H\*/",
        "locales": ALL,
    },
    {
        "id": "w8-course-css",
        "page": COURSE,
        "pattern": r"/\*W8R43C\*/",
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재 — 9 locale은 경량 이벤트 페이지(코스 섹션 자체 부재, 백로그)",
    },
    {
        "id": "w8-jump-chip-s4-unified",  # P0-1: s4 점프가 base 칩(override CSS 부재)
        "page": COURSE,
        "pattern": r'data-w6-course-jump="1" href="#showday-s4"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-jump-chip-s7-unified",
        "page": COURSE,
        "pattern": r'data-w6-course-jump="1" href="#showday-s7"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-no-underline-override",  # P0-1: underline override CSS 제거 확인 (부정 체크)
        "page": COURSE,
        "pattern": r'\[data-w6-course-jump="1"\]\{min-height:32px',
        "locales": RICH,
        "negate": True,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-fold-jump",  # ⑦ above-the-fold 공연일 점프
        "page": COURSE,
        "pattern": r'data-w8-fold="1"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-disc-merged",  # ⑥ 면책 1건 통합
        "page": COURSE,
        "pattern": r'data-w8-disc="1"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-disc-no-residue",  # ⑥ 잔여 면책 제거 확인 (부정 체크)
        "page": COURSE,
        "pattern": r'class="(?:ig-disc|disc disc-aff)"',
        "locales": RICH,
        "negate": True,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-ph-variation",  # ⑤ 모노그램 변주
        "page": COURSE,
        "pattern": r'data-ph-var="1"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w8-radius-token",  # ④ radius 토큰
        "page": COURSE,
        "pattern": r"--r-m:12px",
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
]


def run() -> int:
    fails, gaps = [], []
    for c in CHECKS:
        expected = c["locales"]
        negate = c.get("negate", False)
        marks = []
        for loc in ALL:
            p = (DIST / loc / c["page"]) if loc else (DIST / c["page"])
            tag = loc or "ko"
            if loc not in expected:
                gaps.append((c["id"], tag, c.get("gap_note", "사유 미명시!")))
                marks.append(f"{tag}:GAP")
                continue
            if not p.exists():
                fails.append((c["id"], tag, "파일 부재"))
                marks.append(f"{tag}:FAIL(no-file)")
                continue
            hit = re.search(c["pattern"], p.read_text(encoding="utf-8"))
            ok = (not hit) if negate else bool(hit)
            if not ok:
                fails.append((c["id"], tag, "패턴 잔존" if negate else "패턴 부재"))
            marks.append(f"{tag}:{'PASS' if ok else 'FAIL'}")
        n_pass = sum(1 for m in marks if m.endswith("PASS"))
        print(f"[{c['id']}] {n_pass}/{len(expected)} PASS | {' '.join(marks)}")
    if gaps:
        seen = set()
        print("\n-- GAP (기대 범위 밖 locale — 명시 사유) --")
        for cid, _tag, note in gaps:
            if cid in seen:
                continue
            seen.add(cid)
            locs = sorted({t for i, t, _ in gaps if i == cid})
            print(f"  {cid}: {','.join(locs)} — {note}")
    if fails:
        print(f"\nGATE FAIL ({len(fails)}):")
        for cid, tag, why in fails:
            print(f"  {cid} @ {tag}: {why}")
        return 1
    print("\nGATE PASS (전 체크 기대 locale 충족)")
    return 0


if __name__ == "__main__":
    if "--list" in sys.argv:
        for c in CHECKS:
            print(c["id"], "→", c["page"], "| locales:", len(c["locales"]))
        sys.exit(0)
    sys.exit(run())
