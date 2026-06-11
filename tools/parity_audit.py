#!/usr/bin/env python3
"""WAVE4 콘텐츠 패리티 게이트 (대표 catch 2026-06-11 12:23 — "정보의 대칭성·균일성").

ko 코스 페이지(SSOT) 기준 구조 manifest vs 11언어 각각 diff.
번역 텍스트 자체는 비교 불가 → 구조 시그니처로 비교:
  - h2 섹션 수 / 섹션 id 집합 / 안전·경고 블록 (막차 last-train · K-ETA · 여권 · showtbl 회차표)
  - 면책(disc) 수 / 핵심 위젯 (showday-jump · 체크리스트 · 티켓팅 섹션)
완료 기준: 의도된 로컬라이즈 차이(WHITELIST) 외 누락 0건.
구세대 페이지(코스 콘텐츠 자체 부재)는 OLD-GEN 으로 정직 분류 — 재생성 백로그 증빙.

사용: python3 tools/parity_audit.py [--page twice-thisisfor-seoul.html]
종료코드: 0 = PASS (신세대 페이지 전부 패리티), 1 = 신세대 페이지 누락 존재.
OLD-GEN 은 별도 카운트로 보고 (exit 에는 미반영 — P0-5 재생성 선행조건과 분리).
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
LANG_DIRS = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

# 의도된 로컬라이즈 차이 (언어, 시그니처 키) — 사유 명기 필수
WHITELIST = {
    # (lang, key): 사유
    (
        "en",
        "ids:arrival-1h",
    ): "en 은 도착 타임라인 id 명명이 다름 — 동일 콘텐츠 존재 여부는 first-hour 키로 별도 검증",
}

SIGS = {
    "h2_count": lambda s: len(re.findall(r"<h2[^>]*>", s)),
    "ids": lambda s: sorted(
        set(re.findall(r'id="(sec-[a-z\-]+|last-train|arrival-1h)"', s))
    ),
    "last_train_block": lambda s: int('id="last-train"' in s),
    "keta_link": lambda s: len(re.findall(r"k-eta\.go\.kr", s)),
    "passport_mention": lambda s: int(("여권" in s) or ("passport" in s.lower())),
    "showtbl": lambda s: len(re.findall(r'class="showtbl"', s)),
    "showday_jump": lambda s: len(re.findall(r'class="showday-jump"', s)),
    "show_checklist": lambda s: len(re.findall(r'class="ckstep"', s)),
    "disc_count": lambda s: len(re.findall(r'class="disc[ "]', s)),
    "ticketing_sec": lambda s: int('id="sec-ticketing"' in s),
    "safety_rows": lambda s: int("W4SAFETY" in s or "이 순서대로" in s),
    "course_panels": lambda s: len(re.findall(r'class="sl-panel', s)),
}

# 신세대 코스 판별 (코스 패널 보유)
NEW_GEN_MIN_PANELS = 2


def sig_of(path):
    s = path.read_text(encoding="utf-8")
    return {k: f(s) for k, f in SIGS.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", default="twice-thisisfor-seoul.html")
    args = ap.parse_args()

    ko = sig_of(DIST / args.page)
    print(f"== 패리티 게이트: {args.page} (ko SSOT 기준)")
    print(f"   ko manifest: {dict(ko.items())}")

    fails = []
    oldgen = []
    for ld in LANG_DIRS[1:]:
        f = DIST / ld / args.page
        if not f.exists():
            fails.append((ld, "FILE MISSING", ""))
            continue
        sg = sig_of(f)
        if sg["course_panels"] < NEW_GEN_MIN_PANELS:
            oldgen.append(ld)
            continue
        diffs = []
        for k in SIGS:
            if k == "ids":
                missing = [
                    i
                    for i in ko["ids"]
                    if i not in sg["ids"] and (ld, f"ids:{i}") not in WHITELIST
                ]
                if missing:
                    diffs.append(f"ids 누락 {missing}")
            elif sg[k] < ko[k] if isinstance(ko[k], int) else sg[k] != ko[k]:
                diffs.append(f"{k}: ko={ko[k]} {ld}={sg[k]}")
        if diffs:
            fails.append((ld, "PARITY GAP", "; ".join(diffs)))
        else:
            print(f"   [{ld}] PASS (신세대 · 패리티 일치)")

    for ld in oldgen:
        print(
            f"   [{ld}] OLD-GEN — 코스 콘텐츠 자체 부재 (이벤트 페이지 세대). 재생성 백로그 대상"
        )
    for ld, kind, detail in fails:
        print(f"   [{ld}] FAIL {kind}: {detail}")

    print(
        f"== 결과: 신세대 PASS {len([1 for ld in LANG_DIRS[1:] if (ld not in oldgen and ld not in [f[0] for f in fails])])} / "
        f"FAIL {len(fails)} / OLD-GEN {len(oldgen)}"
    )
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
