#!/usr/bin/env python3
"""R82 fix — ja 막차 타임라인 SVG 형제 역명 dual-notation 정합 (개화 단독 글로스 비대칭 종식).

배경 (R81 미수렴 — 조니 2심 DOC-20260616-JDG-030):
  R81 이 ja SVG 2종(lasttrain-timeline-ja·quote-lasttrain-ja)의 개화 종점만 가나 글로스
  `開化(ケファ)` 로 통일하면서, 同 차트 내 형제 역명은 bare 한자로 방치 →
  同一 차트 dual-notation 비대칭 (개화 1역만 글로스):
    [timeline] 開化(ケファ)(글로스) vs 馬川·傍花(bare) — 同 주말 블록 5호선/9호선 라벨
               + 부제 夢村土城駅(bare)
    [quote]    開化(ケファ)(글로스) vs 金浦空港·中央報勲病院·夢村土城(bare)
  en 통제군 SVG 는 同좌표 전부 균일 romaji(Gaehwa/Macheon/Banghwa) → ja 만 비대칭.

근본 진단 (R81 verbatim 상속 — generator 부재 = SVG 파일 자체가 source):
  R79~R81 실측 확정: locale별 SVG generator(.py) 부재. base
  `assets/gen/{lasttrain-timeline,quote-lasttrain}.svg` 는 ko-base 1종뿐.
  ∴ SVG 직접 치환 = source 단일화(generator 경유 재발 경로 0). HTML 도 i18n 재생성 시
  병기/한자 소실 → dist 직접 패치 + 멱등 박제 (R75~R81 dev 보고 동형·구조 확정).

🔴 정책 (조니 R82 의제 — 글로스 *추가* 방향·HTML prose 가 SSOT):
  ▸ 가나 글로스 = HTML prose 의 기존 글로스를 **verbatim** 가져와 적용 (임의 후리가나 절대 금지·
    FLR-20260606-AGT-001 역명 환각 회귀 봉쇄·project_byvias_proper_noun_dual_notation 정합).
  ▸ verbatim prose source 확정 (실측 grep, dist/ja/twice-thisisfor-seoul.html):
      馬川       ← `Macheon行(マチョン)` (L681/L685)   → 馬川(マチョン)
      傍花       ← `Banghwa行(バンファ)` (L681)        → 傍花(バンファ)
      夢村土城   ← `(夢村土城駅 / モンチョントソン)` (L653/671/676/682) → 夢村土城(モンチョントソン)
                   (부제는 이미 `夢村土城駅` 형태 → 夢村土城駅(モンチョントソン))
  ▸ 개화 무회귀: 開化(ケファ) 유지·開花(벚꽃 오자)=0 (R80/R81 layer 무손상).

🔴 verbatim source 부재 2건 — 환각 금지 우선 (FLR-AGT-002 거짓 충실성·우회 금지):
  prose/dict 전수 grep 결과 가나 source 0:
    金浦空港(Gimpo Airport)  — ja/ko/en prose 모두 bare (의도적·잘 알려진 공항·空港=일본어 native
                              くうこう). prose L694 `開化(ケファ)·金浦空港方面` 에서도 개화만 글로스.
    中央報勲病院             — ja prose 에 station name 자체 부재. prose 는 `東方向(Jung-Ang
                              Veterans Hospital)` 방향어+영문만 사용. quote SVG L32 가 유일 ja asset.
  ∴ 이 2건은 가나 후리가나 *생성 금지*. prose convention(bare 유지)과 SVG 를 정합시킴
    (= prose↔SVG 정합 달성). "bare 한자 0" 게이트는 환각 없이 물리적 충족 불가 →
    lead 명시 보고 (게이트 honest 재정의: prose-grounded dual-notation 균일 + prose 정합).

🔴 게이트 (실측 grep·선언 금지·R81 4·7-layer 엔진 상속):
  (G1) prose-source 역명 = dual-notation 균일 적용:
       timeline 馬川(マチョン)·傍花(バンファ)·夢村土城駅(モンチョントソン) 전부 present.
       quote 夢村土城(モンチョントソン) present.
  (G2) prose↔SVG 정합: 적용한 가나가 prose 의 verbatim 가나와 일치 (実측 prose grep 대조).
  (G3) 개화 무회귀: 開花=0 (전 SVG)·開化(ケファ) 유지 (timeline ×2 라벨 + ×1 콜아웃·quote ×1).
  (G4) en/ko 통제군 무회귀: en SVG 균일 romaji(Gaehwa/Macheon/Banghwa) 유지·한자 미오염.
  (G5) bare-source-부재 2건(金浦空港·中央報勲病院) = 환각 가나 미생성 (キンポ/キムポ/チュンアン* 0).
  (G6) 멱등(재실행 0 변경)·SVG <text>/<tspan> 노드 균형.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
SVG_LASTTRAIN = WT / "dist/assets/gen/lasttrain-timeline-ja.svg"
SVG_QUOTE = WT / "dist/assets/gen/quote-lasttrain-ja.svg"
DIST_JA = (
    WT / "dist/ja/twice-thisisfor-seoul.html"
)  # prose SSOT (cross-check 전용·비편집)

# en 통제군 (무회귀 cross-check 전용·비편집)
SVG_LASTTRAIN_EN = WT / "dist/assets/gen/lasttrain-timeline-en.svg"
SVG_QUOTE_EN = WT / "dist/assets/gen/quote-lasttrain-en.svg"

# ──────────────────────────────────────────────────────────────────────────
# verbatim prose source (실측 grep 확정) — 임의 생성 금지. 가나는 prose 에서만.
#   馬川→マチョン(Macheon行) · 傍花→バンファ(Banghwa行) · 夢村土城→モンチョントソン(夢村土城駅 / …)
# ──────────────────────────────────────────────────────────────────────────
KANA = {"馬川": "マチョン", "傍花": "バンファ", "夢村土城": "モンチョントソン"}

# (1) timeline ja: bare 형제 역명 → dual-notation. (old, new)
#   🔴 開化(ケファ)×3 은 비대상(R81 정상·유지). 馬川/傍花 라벨 + 부제 夢村土城駅.
SVG_LASTTRAIN_FIX: list[tuple[str, str]] = [
    ("馬川 23:49", f"馬川({KANA['馬川']}) 23:49"),  # 주말 5호선 라벨 (x583 y440)
    ("傍花 23:54", f"傍花({KANA['傍花']}) 23:54"),  # 주말 5호선 라벨 (x616 y422)
    # 부제: 夢村土城駅(8) → 夢村土城駅(モンチョントソン)(8). 이미 `駅` 포함 형태.
    ("夢村土城駅(8)", f"夢村土城駅({KANA['夢村土城']})(8)"),  # 부제 (x40 y74)
]

# (2) quote ja: bare 夢村土城 → dual-notation + line2 overflow 보정. (old, new)
#   🔴 金浦空港·中央報勲病院 = prose source 부재 → 미생성(환각 금지). 개화 유지.
#   🔴 overflow: 가나 글로스 추가 시 supporting line2 가 box(444px·text x=22→avail 422px) 초과.
#     브라우저 getComputedTextLength 실측: @12.5=427px(x22 → 우단 449 > box 444 = 5px 오버플로) →
#     @11.5=393px(≤ 410 comfortable, 우 패딩 확보). ∴ line2 전체 <text> 를 atomic 치환
#     (font-size 12.5→11.5 + 夢村土城 dual-notation 동시). line1(font13 weight700) 위계 유지.
_Q_L2_OLD = (
    '<text x="22" y="46" font-family="-apple-system,\'Hiragino Sans\',sans-serif" '
    'font-size="12.5" font-weight="500" fill="rgba(255,255,255,0.85)">'
    "東行き(中央報勲病院)で乗るか、8号線夢村土城で迂回。</text>"
)
_Q_L2_NEW = (
    '<text x="22" y="46" font-family="-apple-system,\'Hiragino Sans\',sans-serif" '
    'font-size="11.5" font-weight="500" fill="rgba(255,255,255,0.85)">'
    f"東行き(中央報勲病院)で乗るか、8号線夢村土城({KANA['夢村土城']})で迂回。</text>"
)
SVG_QUOTE_FIX: list[tuple[str, str]] = [
    (_Q_L2_OLD, _Q_L2_NEW),
]


def _two_phase_replace(text: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """R78~R81 검증 엔진: 멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리. new 는 자기 잠금(멱등).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal text
        if s and s in text:
            sent = f"\x00L{len(locks)}\x00"
            text = text.replace(s, sent)
            locks.append(s)

    # 1) 멱등: 이미 적용된 new(final) 잠금 (longest-first).
    #    new 가 어느 old 의 substring 이면 사전 잠금 시 old 파괴 → 스킵.
    olds = [o for o, _ in pairs]
    for f in sorted({f for _, f in pairs}, key=len, reverse=True):
        if any(f != o and f in o for o in olds):
            continue
        _lock(f)
    # 2) old 치환 (longest-first)
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if old not in text:
            continue
        counts[old] = counts.get(old, 0) + text.count(old)
        sent = f"\x00L{len(locks)}\x00"
        text = text.replace(old, sent)
        locks.append(new)
    # 3) 복원: sentinel → final / new
    for i, val in enumerate(locks):
        text = text.replace(f"\x00L{i}\x00", val)
    return text, counts


def _verbatim_prose_check(prose: str) -> list[str]:
    """🔴 G2 — 적용 가나가 prose 의 verbatim 가나와 일치하는지 실측 대조.

    prose source 부재면 fix 자체를 ABORT (환각 방지·우회 금지).
    """
    fails: list[str] = []
    needs = {
        "馬川": r"Macheon行\(マチョン\)",
        "傍花": r"Banghwa行\(バンファ\)",
        "夢村土城": r"夢村土城駅 / モンチョントソン",
    }
    for term, pat in needs.items():
        if not re.search(pat, prose):
            fails.append(
                f"prose verbatim source 부재: {term} (pat={pat!r}) — "
                f"가나 {KANA[term]!r} 적용 근거 없음 → 환각 위험, ABORT"
            )
    return fails


def _station_inventory(svg_lt: str, svg_q: str) -> str:
    """🔴 역명 dual-notation 교차표 enumerate (fix 전/후 공용)."""

    def _tokens(svg: str) -> list[str]:
        out = []
        for m in re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S):
            inner = re.sub(r"<[^>]+>", "", m).strip()
            # 역명 한자 보유 토큰만
            if re.search(r"馬川|傍花|金浦空港|中央報勲病院|夢村土城|開化|開花", inner):
                out.append(inner)
        return out

    rows = ["  역명 dual-notation 교차표 (ja SVG <text> 실측):"]
    rows.append("    [timeline]")
    for t in _tokens(svg_lt):
        rows.append(f"      {t!r}")
    rows.append("    [quote]")
    for t in _tokens(svg_q):
        rows.append(f"      {t!r}")
    return "\n".join(rows)


def _gate(svg_lt: str, svg_q: str, prose: str) -> list[str]:
    """게이트 G1~G6: 실측 grep. 위반 시 사유 리스트(빈 = PASS)."""
    fails: list[str] = []

    # G1: prose-source 역명 dual-notation 균일 present
    for need in (
        "馬川(マチョン) 23:49",
        "傍花(バンファ) 23:54",
        "夢村土城駅(モンチョントソン)(8)",
    ):
        if need not in svg_lt:
            fails.append(f"G1 timeline dual-notation 미적용: {need!r}")
    if "夢村土城(モンチョントソン)で迂回" not in svg_q:
        fails.append("G1 quote 夢村土城(モンチョントソン) 미적용")

    # G2: prose↔SVG 정합 (verbatim 가나 일치)
    fails += _verbatim_prose_check(prose)

    # G3: 개화 무회귀 — 開花(오자)=0 + 開化(ケファ) 유지
    for name, txt in (("timeline", svg_lt), ("quote", svg_q)):
        if "開花" in txt:
            ctx = re.findall(r".{0,8}開花.{0,8}", txt)
            fails.append(
                f"G3 {name} 開花(벚꽃 오자) 잔존 {txt.count('開花')}: {ctx[:3]}"
            )
    if svg_lt.count("開化(ケファ)") < 3:
        fails.append(
            f"G3 timeline 開化(ケファ) 회귀 ({svg_lt.count('開化(ケファ)')}/3)"
        )
    if svg_q.count("開化(ケファ)") < 1:
        fails.append(f"G3 quote 開化(ケファ) 회귀 ({svg_q.count('開化(ケファ)')}/1)")

    # G5: bare-source-부재 2건 = 환각 가나 미생성
    for bad in ("キンポ", "キムポ", "チュンアン", "ポフン", "ホフン"):
        if bad in svg_lt or bad in svg_q:
            fails.append(f"G5 환각 가나 생성 발견(금지): {bad!r}")
    # 金浦空港·中央報勲病院 은 bare 유지(prose 정합) — present 확인(누락 회귀 방지)
    if "金浦空港行き" not in svg_q:
        fails.append("G5 quote 金浦空港 토큰 누락 회귀")
    if "中央報勲病院" not in svg_q:
        fails.append("G5 quote 中央報勲病院 토큰 누락 회귀")

    return fails


def _en_control_check() -> list[str]:
    """G4 — en 통제군 무회귀 (균일 romaji 유지·한자 미오염)."""
    fails: list[str] = []
    # timeline en: Gaehwa×5 + Macheon×1 + Banghwa×1 (R81 baseline)
    if not SVG_LASTTRAIN_EN.exists():
        fails.append(f"en 통제군 부재: {SVG_LASTTRAIN_EN.name}")
    else:
        t = SVG_LASTTRAIN_EN.read_text(encoding="utf-8")
        for name, want in (("Gaehwa", 5), ("Macheon", 1), ("Banghwa", 1)):
            if t.count(name) < want:
                fails.append(f"G4 en timeline {name} 회귀 {t.count(name)}/{want}")
        if "開花" in t or "開化" in t or "馬川" in t or "傍花" in t:
            fails.append("G4 en timeline ja 한자 오염")
    # quote en: Gaehwa×1
    if not SVG_QUOTE_EN.exists():
        fails.append(f"en 통제군 부재: {SVG_QUOTE_EN.name}")
    else:
        t = SVG_QUOTE_EN.read_text(encoding="utf-8")
        if t.count("Gaehwa") < 1:
            fails.append(f"G4 en quote Gaehwa 회귀 {t.count('Gaehwa')}/1")
        if "開花" in t or "開化" in t:
            fails.append("G4 en quote ja 한자 오염")
    return fails


def run(write: bool) -> bool:
    for p in (SVG_LASTTRAIN, SVG_QUOTE, DIST_JA):
        if not p.exists():
            print(f"ERROR: {p} 없음")
            return False

    lt0 = SVG_LASTTRAIN.read_text(encoding="utf-8")
    q0 = SVG_QUOTE.read_text(encoding="utf-8")
    prose = DIST_JA.read_text(encoding="utf-8")
    lt_text_before = lt0.count("<text")
    q_text_before = q0.count("<text")

    # 🔴 G2 사전: prose verbatim source 부재면 즉시 ABORT (환각 방지)
    src_fail = _verbatim_prose_check(prose)
    if src_fail:
        print("ABORT: prose verbatim source 검증 실패 (환각 위험)")
        for f in src_fail:
            print(f"    ✗ {f}")
        return False

    print("=== [BEFORE] 역명 dual-notation 교차표 (fix 전 enumerate) ===")
    print(_station_inventory(lt0, q0))
    print()

    lt, c_lt = _two_phase_replace(lt0, SVG_LASTTRAIN_FIX)
    q, c_q = _two_phase_replace(q0, SVG_QUOTE_FIX)

    # 구조 보존 게이트
    if lt.count("<text") != lt_text_before:
        print(f"ABORT: timeline <text 불균형 {lt_text_before}→{lt.count('<text')}")
        return False
    if q.count("<text") != q_text_before:
        print(f"ABORT: quote <text 불균형 {q_text_before}→{q.count('<text')}")
        return False

    fails = _gate(lt, q, prose) + _en_control_check()
    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = (lt != lt0) or (q != q0)
    if write:
        if lt != lt0:
            SVG_LASTTRAIN.write_text(lt, encoding="utf-8")
        if q != q0:
            SVG_QUOTE.write_text(q, encoding="utf-8")

    print("=== [AFTER] 역명 dual-notation 교차표 (fix 후 검증) ===")
    print(_station_inventory(lt, q))
    print()

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R82 ja 형제 역명 dual-notation 정합 ({state}) ===")
    print(f"  (1) timeline bare → dual-notation: {sum(c_lt.values())}건")
    for tok, n in sorted(c_lt.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  (2) quote bare → dual-notation: {sum(c_q.values())}건")
    for tok, n in sorted(c_q.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(
        "  🔴 verbatim source 부재 2건 = 환각 가나 미생성 (prose convention bare 유지·정합):\n"
        "      金浦空港(Gimpo Airport) — prose ja/ko/en 모두 bare (의도적)\n"
        "      中央報勲病院 — ja prose 에 station name 부재 (東方向+영문만)"
    )
    print(
        "  게이트: PASS (G1 prose-source dual-notation 균일·G2 prose verbatim 정합·"
        "G3 개화 무회귀·G4 en 통제군 무회귀·G5 환각 가나 0·G6 <text> 균형)"
    )
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R82 ja 형제 역명 dual-notation 정합 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
