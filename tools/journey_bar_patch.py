#!/usr/bin/env python3
"""여정 상주 바 (시안 B 스테이지 라이트) 전 페이지 주입 — R46 P1-5 (대표 채택 2026-06-12 18:24).

적용 범위 (대표 12:52 확정): 홈 11언어 + 리치 ko/en + 이벤트 페이지 전체.
주의: twice-thisisfor-seoul 의 9언어판은 이벤트 템플릿 (ehead-detail, sec-* 없음 — 실측) → t:"event".
바 로직 = dist/assets/jbar.js 단일 모듈 (SSOT — 페이지별 복제 금지, fix 누락 재발 차단).
페이지별 주입 = 설정 2줄 (유형 + 로케일) + 모듈 로드:
  <script id="jbar-js">window.__JB={t:"event",l:"ja"};</script><script src="../assets/jbar.js"></script>

날짜 게이트는 런타임 (jbar.js): 페이지 내 기존 D-DAY 데이터(.dday/.hero-dd-num[data-date]) 재사용,
부재·과거(아카이브) = 바 무렌더 (가짜 값 금지). 따라서 주입 자체는 전 페이지 일괄.

멱등: 'id="jbar-js"' 존재 + 설정 일치 시 skip — 재실행 diff 0. 설정 불일치 시 자가치유 교체.
</body> 정확 1회 아니면 raise (원자적).
실행: python3 tools/journey_bar_patch.py        # 패치 + verify
      python3 tools/journey_bar_patch.py --verify-only
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARK = 'id="jbar-js"'
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
]  # ko = dist 루트
RICH_NAME = "twice-thisisfor-seoul.html"


def page_type(path: Path) -> str:
    if path.name == "index.html":
        return "home"
    # 진짜 리치 템플릿(sec-*/steps5/hero-dd-num)은 ko/en 만 — 9언어판은 이벤트 템플릿 (실측)
    if path.name == RICH_NAME and page_lang(path) in ("ko", "en"):
        return "rich"
    return "event"


def page_lang(path: Path) -> str:
    parent = path.parent.name
    return parent if parent in LOCALES else "ko"


def asset_rel(path: Path) -> str:
    return "assets/jbar.js" if path.parent == DIST else "../assets/jbar.js"


def snippet_for(path: Path) -> str:
    t, lang, rel = page_type(path), page_lang(path), asset_rel(path)
    return (
        f'<script id="jbar-js">window.__JB={{t:"{t}",l:"{lang}"}};</script>'
        f'<script src="{rel}"></script>'
    )


def inject(path: Path) -> str:
    html = path.read_text(encoding="utf-8")
    snippet = snippet_for(path)
    if MARK in html:
        if snippet in html:
            return "skip"
        # 자가치유: 기존 주입분 설정 불일치 → 현행 snippet 으로 교체
        new_html = re.sub(
            r'<script id="jbar-js">[^<]*</script><script src="[^"]*jbar\.js"></script>',
            lambda _: snippet,
            html,
            count=1,
        )
        if new_html == html:
            raise SystemExit(
                f"FAIL [{path}] jbar-js marker present but snippet unmatched"
            )
        path.write_text(new_html, encoding="utf-8")
        return "fix"
    if html.count("</body>") != 1:
        raise SystemExit(f"FAIL [{path}] </body> count != 1")
    html = html.replace("</body>", snippet + "</body>", 1)
    path.write_text(html, encoding="utf-8")
    return page_type(path)


def all_pages():
    pages = sorted(DIST.glob("*.html"))
    for lc in LOCALES:
        pages += sorted((DIST / lc).glob("*.html"))
    return pages


def verify() -> int:
    bad = 0
    pages = all_pages()
    stats = {"home": 0, "rich": 0, "event": 0}
    for p in pages:
        html = p.read_text(encoding="utf-8")
        n = html.count(MARK)
        if n != 1:
            print(f"VERIFY FAIL [{p.relative_to(DIST)}] jbar-js x{n}")
            bad += 1
            continue
        t, lang = page_type(p), page_lang(p)
        stats[t] += 1
        if f'window.__JB={{t:"{t}",l:"{lang}"}}' not in html:
            print(
                f"VERIFY FAIL [{p.relative_to(DIST)}] config mismatch (want t={t},l={lang})"
            )
            bad += 1
        if f'src="{asset_rel(p)}"' not in html:
            print(f"VERIFY FAIL [{p.relative_to(DIST)}] asset path")
            bad += 1
    js = DIST / "assets" / "jbar.js"
    if not js.exists():
        print("VERIFY FAIL assets/jbar.js missing")
        bad += 1
    else:
        src = js.read_text(encoding="utf-8")
        for lang in ["ko"] + LOCALES:
            if f"'{lang}':" not in src and f"{lang}:" not in src.replace("'", ""):
                print(f"VERIFY FAIL jbar.js locale table missing: {lang}")
                bad += 1
    print(
        f"VERIFY pages={len(pages)} home={stats['home']} rich={stats['rich']} "
        f"event={stats['event']} | expect pages=847 home=11 rich=2 event=834"
    )
    if len(pages) != 847 or stats["home"] != 11 or stats["rich"] != 2:
        bad += 1
    return bad


if __name__ == "__main__":
    if "--verify-only" not in sys.argv:
        counts = {"home": 0, "rich": 0, "event": 0, "skip": 0, "fix": 0}
        for p in all_pages():
            counts[inject(p)] += 1
        print(f"PATCH {counts}")
    sys.exit(1 if verify() else 0)
