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
HOME = "index.html"

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
    # ---- R45 (c7 동등화 — wave7 c4 패턴 동형) ----
    {
        "id": "r45-c7-equalized",  # c7 동등화 — c4 규격 (타임라인·스팟카드·경고박스·ckstep)
        "page": COURSE,
        "pattern": r'data-w7-c7="1"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재 — 9 locale은 경량 이벤트 페이지(코스 섹션 부재, 백로그)",
    },
    {
        "id": "r45-c7-spot-pair",  # c7 스팟 카드 맵 링크 (ko kakao+google 페어 — en은 google 단독)
        "page": COURSE,
        "pattern": r'class="sl-panel sl-7"[\s\S]*?class="psrc-row"[\s\S]*?<!-- /stay-len -->',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "r45-c7-showday-flat",  # c7 공연일 = flat day-card--show (c4 동형, 아코디언 아님)
        "page": COURSE,
        "pattern": r'<div class="day-card day-card--show" id="showday-s7">',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "r45-c7-ckstep",  # c7 showday ckstep 체크리스트
        "page": COURSE,
        "pattern": r'data-ck="showday-s7-0"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    # ---- WAVE7 (R44 2심 조니 확정) ----
    {
        "id": "w7-c4-equalized",  # #6 c4 동등화 — sl-2 규격 (스팟카드·맵페어·경고박스)
        "page": COURSE,
        "pattern": r'data-w7-c4="1"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재 — 9 locale은 경량 이벤트 페이지(코스 섹션 부재, 백로그)",
    },
    {
        "id": "w7-c4-spot-pair",  # #6 c4 스팟 카드 맵 링크 (kakao+google 페어 — en은 en sl-2 규격 google 단독)
        "page": COURSE,
        "pattern": r'class="sl-panel sl-4"[\s\S]*?class="psrc-row"[\s\S]*?class="sl-panel sl-7"',
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w7-no-fake-why",  # #7 'ptag · 주소' 가짜 why 잔존 0 (부정 체크 — pwhy=실사유만)
        "page": COURSE,
        "pattern": r'<div class="ptag">([^<]+)</div><div class="pwhy">\1',
        "locales": RICH,
        "negate": True,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w7-ckstep-44",  # #9 ckstep 레이아웃 박스 44 실측화
        "page": COURSE,
        "pattern": r"\.ckstep\{[^}]*width:44px;height:44px",
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w7-psrc-44",  # #9 psrc min-width 44
        "page": COURSE,
        "pattern": r"\.psrc\{[^}]*min-width:44px",
        "locales": RICH,
        "gap_note": "코스 리치 페이지 ko·en만 존재",
    },
    {
        "id": "w7-home-radius-tokens",  # #8 홈 radius 토큰 (이벤트 체계 8/12/999)
        "page": HOME,
        "pattern": r"--r-s:8px;--r-m:12px;--r-pill:999px",
        "locales": ALL,
    },
    {
        "id": "w7-logo-real-ratio",  # #12 로고 attr=실비율 87×38 (206:90)
        "page": HOME,
        "pattern": r'class="logo"[^>]*width="87" height="38"',
        "locales": ALL,
    },
    {
        "id": "w7-logo-stale-attr",  # #12 구 attr 119 잔존 0 (부정 체크)
        "page": HOME,
        "pattern": r'class="logo"[^>]*width="119"',
        "locales": ALL,
        "negate": True,
    },
    # ---- Trip.com 어필리에이트 (수익 마커 — 재생성 누락 = FAIL, tools/tripcom_affiliate_patch.py) ----
    {
        "id": "tripcom-stay-ota",  # 숙소 ota-row Trip.com 버튼 + 실 Allianceid 부착
        "page": COURSE,
        "pattern": r'href="[^"]*Allianceid=8661388[^"]*"[^>]*data-aff-surface="stay-ota" data-aff-vendor="Trip\.com"',
        "locales": RICH,
        "gap_note": "stay-ota는 코스 리치 stays 섹션 전용(ko·en) — 경량 9 locale은 lock-now 표면만 보유"
        " (generate.py 재생성으로 자동 포함되지 않음, 코스 다국어화 백로그)",
    },
    {
        "id": "tripcom-flights-locknow",  # lock-now Trip.com Flights prep-row 병렬 (Skyscanner 대체 금지)
        "page": COURSE,
        "pattern": r'data-aff-surface="lock-now" data-aff-vendor="Trip\.com"',
        # 9언어 재생성(feat/9lang-regen, generate.py d181e17c 포트)으로 lock-now 마커 11 locale 전수 확보
        # — RICH→ALL 승격(회귀 봉쇄). stay-ota는 코스 리치 전용이라 RICH 유지.
        "locales": ALL,
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
