#!/usr/bin/env python3
"""R88 fix — zh-cn/zh-tw 코스 *비역명* 고유명사 dual-notation 복원 (양파 종결 연장).

배경 (검증 verdict byvias-zh-content-eye-audit P1-2/P1-3 + R85 station 적용 후):
  R85 가 역명 13종을 `한글역(中文站)` 로 복원했으나, **역명 외 명소·지역·거리명**은
  여전히 완전현지어화(한글 원문 탈락) 또는 다중표기로 잔존:
    - 仁寺洞(Insadong)·北村·蚕室(area)·景福宫(궁)·石村湖 = 한글 원문 0 (룰 위반)
    - 成寿(area, ×8)·城水 = R85 가 station 만 圣水 로 통일 → area 는 음역 오역 잔존
    - 松梨灯街/松里坛街/松里坦街 = 한 거리 3가지 한자 (松里坦街 坦≠坛 오자)

🔴 대표 고유명사 규칙 (project_byvias_proper_noun_dual_notation, 2026-06-15/16):
  twice 서울 = 한국 공연 → 외국어 페이지 고유명사 = **한국어 원문 + (독자 언어 뜻)**.
  완전현지어화 금지. ja 코스(verified precedent)가 동일 비역명을 처리한 형태를 zh 동형 적용:
    ja: 잠실(蚕室 / ジャムシル) · 성수(聖水 / ソンス) · 석촌호수(石村湖 / ソクチョノス)
        송파(松坡 / ソンパ) · 강남(江南 / カンナム) · 경복궁(景福宮 / キョンボックン)
        송리단길(ソンリダンギル)  ← **한자 없음** (coined 지명 = 한자 신설 금지)

🔴 form 결정 (FLR-AGT-002·FLR-20260606-AGT-001 환각 금지 — 핵심):
  - 공식 한자 확실: 한글 원문 + 公식 한자. 圣水(area)는 R85 station 과 동일 canonical
    (成寿=음역 오역 → 圣水 공식 의미명, ja 聖水 정합).
  - 송리단길 = **coined 지명, 공식 한자 부재** → 한글 원문만 (松梨灯街/松里坛街 등은 LLM
    환각 한자, 통일 대상이 아니라 제거 대상). ja r75 가 동일 결정(한자 신설 금지·가나만).
    중국어 독자는 한글 원문으로 표지판 대조 + romaji(Songridan-gil) 로 발음. 한자 폐기.
  - romaji(Latin) 읽는법은 빌드 내 verbatim 존재분만 fold-in. 신생성 0.

전략 (R85 검증 엔진 verbatim 재사용 — 2-phase NUL sentinel + longest-first + idempotent):
  - R85 *이후* 실행 전제. station final(`잠실역(蚕室站)` 등)을 protect 에 편입 → area
    bare `蚕室`/`景福宫` 치환이 station 형태를 오염 불가.
  - longest-first: romaji 보유형(`蚕室(Jamsil)`)이 bare `蚕室` 보다 먼저 매칭.
  - 멱등: 이미 적용된 `한글(...)` final 사전 잠금. 재실행 0 변경.

게이트 (FLR-AGT-002 — 선언 아닌 실측 grep, --verify):
  (G1) 비역명 한글 원문 ≥ 6종 present (인사동·북촌·잠실·경복궁·성수·석촌호수…).
  (G2) dual-notation 형태 `한글(漢字)` 표본 present (잠실(蚕室)·성수(圣水)·석촌호수(石村湖)).
  (G3) 음역 오역 0 (area 成寿/城水 잔존 0 → 圣水 통일).
  (G4) 송리단길 다중 한자 0 (松梨灯街/松里坛街/松里坦街 잔존 0).
  (G5) R85 station 무회귀 (잠실역(蚕室站) 등 13종 present 유지).
  (G6) 중첩 괄호 오류 0 + <div> 균형.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
PATHS = {
    "zh-cn": WT / "dist/zh-cn/twice-thisisfor-seoul.html",
    "zh-tw": WT / "dist/zh-tw/twice-thisisfor-seoul.html",
}

# R85 검증 엔진(_two_phase_replace) verbatim 재사용 (양파 종결: 엔진 단일).
#   ⚠ _card_protect 는 사용 안 함: R85 는 카드가 이미 dual-noted 라 보호했으나, 본 패치는
#   카드 label 내부의 *bare* area 한자(`Onion 成寿`·`石村湖·松里坦街`·`Godosik蚕室分店`)도
#   교정 대상 → 카드 보호 시 미적용. 대신 R85 station final 만 protect(역명 회귀 차단).
_r85_path = Path(__file__).parent / "r85_zh_station_dual_notation_patch.py"
_spec = importlib.util.spec_from_file_location("r85", _r85_path)
_r85 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_r85)
_two_phase_replace = _r85._two_phase_replace
KO_STATION_NAMES = _r85.KO_STATION_NAMES

# ──────────────────────────────────────────────────────────────────────────
# 비역명 고유명사 dual-notation pairs. (cur_token, final). longest-first 자동 정렬.
#   final = 한글(漢字) 또는 한글(漢字 / romaji). romaji = verbatim 존재분만 fold-in.
#   canonical 한자 = ja 코스 verified precedent + 공식 표기 (음역 오역 교정).
# ──────────────────────────────────────────────────────────────────────────
# zh-cn (간체)
ZHCN_AREA: list[tuple[str, str]] = [
    # 인사동 (공식 한자 仁寺洞)
    ("仁寺洞(Insadong)", "인사동(仁寺洞 / Insadong)"),
    ("仁寺洞", "인사동(仁寺洞)"),
    # 북촌 (공식 한자 北村)
    ("北村(Bukchon)", "북촌(北村 / Bukchon)"),
    ("北村", "북촌(北村)"),
    # 잠실 area (蚕室 — station 과 동일 canonical, ja 정합). station 형태는 protect.
    ("蚕室(Jamsil)", "잠실(蚕室 / Jamsil)"),
    ("蚕室洞", "잠실동(蚕室洞)"),
    ("蚕室", "잠실(蚕室)"),
    # 경복궁 (景福宫). 경복궁역(景福宫站) station 형태는 protect.
    ("景福宫(Gyeongbokgung Palace)", "경복궁(景福宫 / Gyeongbokgung Palace)"),
    ("景福宫", "경복궁(景福宫)"),
    # 성수 area (成寿/城水 음역 오역 → 圣水 공식, station 정합·ja 聖水 정합)
    ("成寿洞", "성수동(圣水)"),
    ("成寿(Seongsu)", "성수(圣水 / Seongsu)"),
    ("城水(Seongsu)", "성수(圣水 / Seongsu)"),
    ("成寿", "성수(圣水)"),
    ("城水", "성수(圣水)"),
    # 석촌호수 (石村湖)
    ("石村湖(Seokchon Lake)", "석촌호수(石村湖 / Seokchon Lake)"),
    ("石村湖", "석촌호수(石村湖)"),
    # 송리단길 (coined 지명 = 공식 한자 부재 → 한글 원문만, 한자 폐기·ja r75 정합)
    ("松梨灯街(Songridan-gil)", "송리단길(Songridan-gil)"),
    ("松里坛街(Songridan-gil)", "송리단길(Songridan-gil)"),
    ("松梨灯街", "송리단길"),
    ("松里坛街", "송리단길"),
    ("松里坦街", "송리단길"),
]

# zh-tw (번체) — 번체 canonical + 동일 romaji fold-in. 송리단길 한자 폐기 동일.
ZHTW_AREA: list[tuple[str, str]] = [
    ("仁寺洞(Insadong)", "인사동(仁寺洞 / Insadong)"),
    ("仁寺洞", "인사동(仁寺洞)"),
    ("北村(Bukchon)", "북촌(北村 / Bukchon)"),
    ("北村", "북촌(北村)"),
    ("蠶室(Jamsil)", "잠실(蠶室 / Jamsil)"),
    ("蠶室洞", "잠실동(蠶室洞)"),
    ("蠶室", "잠실(蠶室)"),
    ("景福宮(Gyeongbokgung Palace)", "경복궁(景福宮 / Gyeongbokgung Palace)"),
    ("景福宮", "경복궁(景福宮)"),
    ("成壽洞", "성수동(聖水)"),
    ("成壽(Seongsu)", "성수(聖水 / Seongsu)"),
    ("城水(Seongsu)", "성수(聖水 / Seongsu)"),
    ("成壽", "성수(聖水)"),
    ("城水", "성수(聖水)"),
    ("石村湖(Seokchon Lake)", "석촌호수(石村湖 / Seokchon Lake)"),
    ("石村湖", "석촌호수(石村湖)"),
    ("松梨燈街(Songridan-gil)", "송리단길(Songridan-gil)"),
    ("松裡坦街(Songridan-gil)", "송리단길(Songridan-gil)"),
    ("松裡壇街(Songridan-gil)", "송리단길(Songridan-gil)"),
    ("松梨燈街", "송리단길"),
    ("松裡坦街", "송리단길"),
    ("松裡壇街", "송리단길"),
    ("松里坦街", "송리단길"),
]

AREA = {"zh-cn": ZHCN_AREA, "zh-tw": ZHTW_AREA}

# G1 검증용 비역명 한글 원문 종수
KO_AREA_NAMES = [
    "인사동",
    "북촌",
    "잠실",
    "경복궁",
    "성수",
    "석촌호수",
    "송리단길",
]

# G5: R85 station final 무회귀 표본 (protect 대상이기도).
#   ⚠ romaji fold-in 형(`성수역(圣水站 / Seongsu)`)이 있어 닫는 괄호 없는 prefix 로 검증.
STATION_FINALS_CN = [
    "잠실역(蚕室站",
    "경복궁역(景福宫站",
    "성수역(圣水站",
    "올림픽공원역(奥林匹克公园站",
    "蚕室站",
    "景福宫站",
]
STATION_FINALS_TW = [
    "잠실역(蠶室站",
    "경복궁역(景福宮站",
    "성수역(聖水站",
    "올림픽공원역(奧林匹克公園站",
    "蠶室站",
    "景福宮站",
]
STATION_FINALS = {"zh-cn": STATION_FINALS_CN, "zh-tw": STATION_FINALS_TW}

# G3/G4 잔존 금지 토큰 (음역 오역 + 송리단길 다중 한자)
FORBIDDEN_CN = ["成寿", "城水", "松梨灯街", "松里坛街", "松里坦街"]
FORBIDDEN_TW = ["成壽", "城水", "松梨燈街", "松裡坦街", "松裡壇街", "松里坦街"]
FORBIDDEN = {"zh-cn": FORBIDDEN_CN, "zh-tw": FORBIDDEN_TW}


def _gate(html: str, lang: str) -> list[str]:
    fails: list[str] = []
    # G1: 비역명 한글 원문 ≥ 6종
    present = [s for s in KO_AREA_NAMES if s in html]
    if len(present) < 6:
        missing = [s for s in KO_AREA_NAMES if s not in html]
        fails.append(f"G1 비역명 한글 원문 부족 {len(present)}/7 (누락 {missing})")
    # G2: dual-notation 표본
    samples = (
        ["잠실(蚕室", "성수(圣水", "석촌호수(石村湖"]
        if lang == "zh-cn"
        else ["잠실(蠶室", "성수(聖水", "석촌호수(石村湖"]
    )
    for s in samples:
        if s not in html:
            fails.append(f"G2 dual-notation 미적용 {s!r}")
    # G3+G4: 음역 오역 + 송리단길 다중 한자 잔존 0
    for tok in FORBIDDEN[lang]:
        if tok in html:
            fails.append(f"G3/G4 금지 토큰 잔존 {tok!r} ×{html.count(tok)}")
    # G5: R85 station 무회귀
    for s in STATION_FINALS[lang]:
        if s not in html:
            fails.append(f"G5 R85 station 회귀 {s!r} 소실")
    # G6: 중첩 괄호 오류 (역명 station 이 또 station 안 / 역(( 중첩). raw (( 는 JS 존재 → 제외.
    bad_nest = re.findall(r"站\)\([^)]*站\)", html)
    if bad_nest:
        fails.append(f"G6 站)(站) 중첩 {len(bad_nest)}: {bad_nest[:3]}")
    if "역((" in html or "洞((" in html or "湖((" in html:
        fails.append("G6 역((/洞((/湖(( 중첩")
    return fails


def _inventory(html: str, lang: str) -> str:
    rows = ["  비역명 한글 원문 종수 (실측):"]
    present = [s for s in KO_AREA_NAMES if s in html]
    rows.append(f"    present {len(present)}/7: {present}")
    rows.append("  잔존 음역/다중표기 (0 목표):")
    for tok in FORBIDDEN[lang]:
        n = html.count(tok)
        if n:
            rows.append(f"    {tok!r} ×{n}")
    return "\n".join(rows)


def run(lang: str, write: bool, verify_only: bool = False) -> bool:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    if verify_only:
        print(f"=== [{lang}] 비역명 dual-notation 현 상태 (verify) ===")
        print(_inventory(orig, lang))
        fails = _gate(orig, lang)
        if fails:
            print(f"\n  게이트 FAIL ({len(fails)}건):")
            for f in fails:
                print(f"    ✗ {f}")
            return False
        print("\n  게이트 PASS (G1~G6)")
        return True

    print(f"=== [BEFORE] {lang} 비역명 교차표 ===")
    print(_inventory(orig, lang))
    print()

    # protect = R85 station final 만 (카드 보호 X — 카드 내 bare area 한자도 교정 대상).
    protect = list(STATION_FINALS[lang])

    html, counts = _two_phase_replace(orig, AREA[lang], protect)

    if html.count("<div") != div_before:
        print(f"ABORT: <div 불균형 {div_before}→{html.count('<div')}")
        return False

    fails = _gate(html, lang)
    if fails:
        print(f"ABORT: 게이트 FAIL ({len(fails)}건)")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = html != orig
    if write and changed:
        path.write_text(html, encoding="utf-8")

    print(f"=== [AFTER] {lang} 비역명 교차표 ===")
    print(_inventory(html, lang))
    print()
    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R88 {lang} 비역명 dual-notation 복원 ({state}) ===")
    print(f"  비역명 dual-notation 치환 {sum(counts.values())}건:")
    for tok, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {tok!r} ×{n}")
    print(
        "  🔴 송리단길 = coined 지명·공식 한자 부재 → 한글 원문만 (한자 폐기·ja r75 정합·"
        "FLR-20260606-AGT-001 환각 회피). 성수 area 成寿→圣水 (station canonical 정합)."
    )
    print(
        "  게이트: PASS (G1 한글원문 · G2 dual-notation · G3/4 음역·다중표기0 · G5 station무회귀 · G6 구조)"
    )
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    verify = "--verify" in args
    langs = [a for a in args if a in PATHS]
    if not langs:
        langs = list(PATHS.keys())
    ok = True
    for lang in langs:
        if not run(lang, write, verify_only=verify):
            ok = False
        print()
    if not ok:
        sys.exit(2)
    mode = "VERIFY" if verify else ("WRITE" if write else "DRY-RUN (--write 로 적용)")
    print(f"OK: R88 zh 비역명 dual-notation [{mode}] ({' '.join(langs)})")


if __name__ == "__main__":
    main()
