#!/usr/bin/env python3
"""R77 fix — hero-spot 'gestalt' 모순 해소: 첫 진열장을 K-pop(주력)으로 필터.

배경 (R76 미수렴 — 조니 2심 P1-4·fable 1심 채택):
  K-pop 사이트인데 hero 'Most imminent schedule' 카드가 D-3 축구(월드컵 South Korea
  National Team)를 최상단에 진열 → brand↔content gestalt 모순(간판과 첫 진열장이 다른
  장사). R74 D-3/D-5 자기모순 fix를 '전 종류 최단 통일'로 푼 trade-off의 역효과.
  조니/fable 권고: "hero-spot 은 K-pop(주력 카테고리) 최단으로 필터하라(1순위).
  jbar(하단 보조)·hotweek 는 전 종류 최단 유지 가능(브랜드 충돌 약함)."

구현 (dist/{ko,en,ja,zh-cn,zh-tw}/index.html 인라인 JS — R75 d419ba07 동형 dist 패치):
  hero-spot 선택 로직만 K-pop 필터. hotweek(다가오는 14일)·jbar 는 무손상(전 종류 유지).
  1) L.push 에 wc 플래그 추가 — href 가 'wc2026-' prefix 면 스포츠(월드컵) 카드.
     (⚽ 배지 카드 = 전부 wc2026- href·실측 확인. href 패턴이 텍스트 파싱보다 견고.)
  2) hero else-if: L[0] → 첫 非-wc(K-pop) 카드 s0 선택. K-pop 0건이면 L[0] fallback
     (graceful — TKO 티켓팅 우선 분기는 무손상). hero 가 집은 인덱스 hsIdx 기록.
  3) hotweek offset: 기존 hs=...?1:0 (L[0] 제외) → hsIdx 항목만 skip (hero 가 L[0] 이
     아닐 수 있으므로). hotweek 는 K-pop·축구 전 종류 유지 — hero 중복분만 제외.

ES5 호환 (기존 JS 스타일 — var/no-arrow). 멱등: 이미 패치된 마커(R77HERO) 존재 시 skip.

게이트 (실측):
  - 5 locale 각 1건 치환 (L.push·hero·hotweek 3 anchor 전수 매칭).
  - 멱등(재실행 0 변경). hotweek/jbar 로직 무손상(전 종류 유지 — wc 필터는 hero 한정).
"""

from __future__ import annotations

import sys
from pathlib import Path

WT = Path(__file__).parent.parent
INDEX_PATHS = [
    WT / "dist/index.html",
    WT / "dist/en/index.html",
    WT / "dist/ja/index.html",
    WT / "dist/zh-cn/index.html",
    WT / "dist/zh-tw/index.html",
]

# 1) L.push: wc(월드컵·스포츠) 플래그 추가. href prefix 'wc2026-' 판별.
PUSH_OLD = (
    "L.push({href:c.getAttribute('href'),art:art.trim(),"
    "meta:meta.replace(/D-\\d+|D-DAY/,'').trim(),diff:diff});"
)
PUSH_NEW = (
    "L.push({href:c.getAttribute('href'),art:art.trim(),"
    "meta:meta.replace(/D-\\d+|D-DAY/,'').trim(),diff:diff,"
    "wc:((c.getAttribute('href')||'').indexOf('wc2026-')===0)});/*R77HERO*/"
)

# 2) hero else-if: L[0] → 첫 非-wc(K-pop) 카드. K-pop 0건이면 L[0] fallback. hsIdx 기록.
HERO_OLD = "else if(spot&&L.length){var s0=L[0];"
HERO_NEW = (
    "else if(spot&&L.length){var hsIdx=0;for(var hi=0;hi<L.length;hi++){"
    "if(!L[hi].wc){hsIdx=hi;break;}}var s0=L[hsIdx];"
)

# 3) hotweek offset: hsIdx 항목만 skip (hero 중복 제거). 전 종류(축구 포함) 유지.
HOT_OLD = (
    "var hs=(spot&&!tkb&&L.length)?1:0;var H=[];"
    "for(var j=hs;j<L.length;j++){if(L[j].diff<=14)H.push(L[j]);}"
)
HOT_NEW = (
    "var hsUsed=(spot&&!tkb&&L.length);var H=[];"
    "for(var j=0;j<L.length;j++){if(hsUsed&&j===hsIdx)continue;"
    "if(L[j].diff<=14)H.push(L[j]);}"
)


def run(path: Path, write: bool) -> bool:
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")

    if "/*R77HERO*/" in orig:
        print(f"=== [{path.parent.name}/{path.name}] 이미 적용 (멱등 skip) ===")
        return True

    # 3 anchor 전수 매칭 검증 (선언 아닌 실측 — 누락 시 ABORT)
    missing = [
        name
        for name, tok in (
            ("L.push", PUSH_OLD),
            ("hero", HERO_OLD),
            ("hotweek", HOT_OLD),
        )
        if tok not in orig
    ]
    if missing:
        print(f"ABORT [{path.parent.name}/{path.name}]: anchor 누락 — {missing}")
        return False

    html = orig.replace(PUSH_OLD, PUSH_NEW)
    html = html.replace(HERO_OLD, HERO_NEW)
    html = html.replace(HOT_OLD, HOT_NEW)

    # 게이트: 각 anchor 1건씩 치환됐는지 (중복/0건 방지)
    if html.count("/*R77HERO*/") != 1 or HERO_NEW not in html or HOT_NEW not in html:
        print(f"ABORT [{path.parent.name}/{path.name}]: 치환 카운트 이상")
        return False

    changed = html != orig
    if changed and write:
        path.write_text(html, encoding="utf-8")
    print(
        f"=== [{path.parent.name}/{path.name}] "
        f"({'WROTE' if (changed and write) else 'DRY'}) — hero K-pop 필터 3 anchor 치환 ==="
    )
    return True


def main() -> None:
    write = "--write" in sys.argv[1:]
    ok = all(run(p, write) for p in INDEX_PATHS)
    if not ok:
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R77 hero-spot K-pop 필터 [{mode}] (hotweek/jbar 전 종류 무손상)")


if __name__ == "__main__":
    main()
