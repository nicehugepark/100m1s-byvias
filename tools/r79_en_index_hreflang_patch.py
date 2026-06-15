#!/usr/bin/env python3
"""R79 (B) fix — en index(/en/) hreflang 상대경로 → 절대경로.

배경 (R78 미수렴 — 조니 2심 DOC-20260615-JDG-039 §4 + 1심 tech-cynic P1-R78-TC-001):
  `/en/` index 의 `<head>` hreflang 이 `../` 없는 상대경로(`href="en/index.html"` 등)라
  브라우저/크롤러가 `/en/` 기준 해석 → 라이브 404:
    en        → /en/en/index.html      (HTTP 404)
    ja        → /en/ja/index.html      (HTTP 404)
    zh-Hans   → /en/zh-cn/index.html   (HTTP 404)
    zh-Hant   → /en/zh-tw/index.html   (HTTP 404)
    ko        → /en/index.html         (자기 자신 가리킴 = 오지정)
  대조군 ko-index·ja-index 는 절대경로(정상). en-course 는 `../` 상대(정상 해석).
  결손은 en-index 1페이지 `<head>` 템플릿 전용(R74 잠복·R78 회귀 아님).

정책 (조니 §5 (B) + tech-cynic 권고):
  en-index `<head>` hreflang 을 ko-index 와 동일 절대경로로 교체.
  cross-page 상호 정합: ko-index 가 en 을 `/en/index.html` 로 참조하므로 en-index 자기참조
  도 `/en/index.html`. 5 hreflang(ko/en/ja/zh-Hans/zh-Hant) + x-default 전수 절대경로.
  🔴 langpick `<details>` 메뉴(line 311 부근)의 `../` 상대경로는 정상(가시 링크) — 무터치.

🔴 ko/ja index 동형 점검 (조니 §5 (B) '동형 점검'):
  ko-index·ja-index head hreflang 은 이미 절대경로(검증됨) → 신규 치환 0. 게이트 재확인만.

전략:
  en-index head hreflang 5줄(line 43~47) 정규형 통째 치환 → 절대경로. 멱등(이미 절대형
  잠금). x-default(line 48)는 이미 절대경로 → 무변경. canonical(line 42)도 무변경.
  langpick `<details>` 내부 `../` href 는 치환 대상서 제외(head <link> 만 매칭).

게이트 (FLR-AGT-002 — 선언 아닌 실측 grep):
  - en-index head hreflang 5종 전수 절대경로(https://byvias.100m1s.com/...).
  - 상대 hreflang(`href="en/index.html"` 식·../없는) 0.
  - langpick `<details>` 내 `../` 무손상(가시 링크 회귀 0).
  - ko-index·ja-index head 절대경로 무회귀.
  - 멱등(재실행 0 변경).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
EN_INDEX = WT / "dist/en/index.html"
KO_INDEX = WT / "dist/index.html"
JA_INDEX = WT / "dist/ja/index.html"

BASE = "https://byvias.100m1s.com"

# en-index head hreflang: 상대경로 → 절대경로. (old <link>, new <link>)
#   🔴 verbatim 매칭(head <link rel="alternate">). langpick <details> 내부는 형식 상이(class="lng")
#      라 매칭되지 않음 — 구조적 격리.
EN_HREFLANG_FIX: list[tuple[str, str]] = [
    (
        '<link href="index.html" hreflang="ko" rel="alternate"/>',
        f'<link href="{BASE}/index.html" hreflang="ko" rel="alternate"/>',
    ),
    (
        '<link href="en/index.html" hreflang="en" rel="alternate"/>',
        f'<link href="{BASE}/en/index.html" hreflang="en" rel="alternate"/>',
    ),
    (
        '<link href="ja/index.html" hreflang="ja" rel="alternate"/>',
        f'<link href="{BASE}/ja/index.html" hreflang="ja" rel="alternate"/>',
    ),
    (
        '<link href="zh-cn/index.html" hreflang="zh-Hans" rel="alternate"/>',
        f'<link href="{BASE}/zh-cn/index.html" hreflang="zh-Hans" rel="alternate"/>',
    ),
    (
        '<link href="zh-tw/index.html" hreflang="zh-Hant" rel="alternate"/>',
        f'<link href="{BASE}/zh-tw/index.html" hreflang="zh-Hant" rel="alternate"/>',
    ),
]


def _gate_en(html: str) -> list[str]:
    """en-index 게이트: head hreflang 전수 절대 + langpick `../` 무손상."""
    fails: list[str] = []

    # head <link rel="alternate"> 영역만 추출 (langpick <a class="lng"> 제외)
    head_links = re.findall(
        r'<link [^>]*hreflang="[^"]*"[^>]*rel="alternate"[^>]*/>'
        r'|<link [^>]*rel="alternate"[^>]*hreflang="[^"]*"[^>]*/>',
        html,
    )
    for link in head_links:
        href_m = re.search(r'href="([^"]*)"', link)
        if not href_m:
            continue
        href = href_m.group(1)
        if not href.startswith("https://"):
            fails.append(f"en-index head hreflang 비절대: {href!r}")

    # 상대 hreflang 패턴 0 (../없는 'en/index.html' 식 <link>)
    if re.search(
        r'<link href="(?:en|ja|zh-cn|zh-tw|index)\.?[^"]*\.html" hreflang=', html
    ):
        fails.append("en-index 상대 hreflang <link> 잔존")
    if re.search(r'<link href="index\.html" hreflang=', html):
        fails.append("en-index ko 자기참조 상대 <link> 잔존")

    # langpick <details> 내 ../ 가시 링크 무손상 (회귀 가드)
    if 'href="../index.html"' not in html or 'href="../en/index.html"' not in html:
        fails.append("langpick <details> ../ 가시 링크 회귀(무손상이어야)")

    return fails


def _gate_other(html: str, name: str) -> list[str]:
    """ko/ja index 동형 점검: head hreflang 이미 절대(무회귀)."""
    fails: list[str] = []
    head_links = re.findall(
        r'<link rel="alternate" hreflang="[^"]*" href="[^"]*">', html
    )
    for link in head_links:
        href_m = re.search(r'href="([^"]*)"', link)
        if href_m and not href_m.group(1).startswith("https://"):
            fails.append(f"{name} head hreflang 비절대: {href_m.group(1)!r}")
    return fails


def run(write: bool) -> bool:
    ok = True

    # en-index 치환
    if not EN_INDEX.exists():
        print(f"ERROR: {EN_INDEX} 없음")
        return False
    orig = EN_INDEX.read_text(encoding="utf-8")
    html = orig
    counts: dict[str, int] = {}
    for old, new in EN_HREFLANG_FIX:
        if old == new:
            continue
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            counts[old] = n

    fails = _gate_en(html)
    if fails:
        print("ABORT [en-index]: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = html != orig
    if changed and write:
        EN_INDEX.write_text(html, encoding="utf-8")
    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== [en-index] {EN_INDEX.name} ({state}) ===")
    print(f"  hreflang 상대→절대: {sum(counts.values())}건")
    for tok, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print("  게이트: PASS (head hreflang 전수 절대·상대 0·langpick ../ 무손상)")

    # ko/ja index 동형 점검(무회귀 — 신규 치환 0)
    for idx, nm in ((KO_INDEX, "ko-index"), (JA_INDEX, "ja-index")):
        if not idx.exists():
            print(f"    경고: {idx} 없음 — 점검 skip")
            continue
        f2 = _gate_other(idx.read_text(encoding="utf-8"), nm)
        if f2:
            print(f"ABORT [{nm}]: 동형 점검 FAIL")
            for f in f2:
                print(f"    ✗ {f}")
            ok = False
        else:
            print(f"  [{nm}] 동형 점검: PASS (head hreflang 이미 절대·무회귀)")

    return ok


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R79 (B) en-index hreflang 절대경로 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
