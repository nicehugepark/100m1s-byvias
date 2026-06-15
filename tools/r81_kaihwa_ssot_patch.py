#!/usr/bin/env python3
"""R81 fix — ja 개화 종점 전 asset 단일 SSOT 통일 (양파 종결·SVG 포함).

배경 (R80 미수렴 — 조니 2심 DOC-20260616-JDG-014 §1·§4·§5 + 1심 3패널 교차):
  R79·R80 이 개화 종점을 HTML *일부* layer 만 fix 하고 SVG·tldr·bare instance 를 누락 →
  ja 단일 페이지에서 동일 9호선 개화 종점(西行·막차 ~22:55 경고)이 6 표기로 분기:
    [HTML] 開化(ケファ)×4(정상) · bare 開化×1(L694 막차경고 prose) · ゲファ×1(L593 tldr) ·
           Gaehwa(romaji)×2(L677/L683 li timeline — romaji layer 정책 유지)
    [SVG]  lasttrain-timeline-ja.svg 開花×3 + quote-lasttrain-ja.svg 開花×1 = 開花(벚꽃 오자)×4
  en SVG = 同좌표 Gaehwa×6(통제군 정상) · ko HTML = 개화×7 단일 · ko SVG 부재 →
  ja 만 SSOT 부재. 정합 가능한 데이터(정직한 부재 아님).

근본 진단 (조니 §4 — SVG generator source 단일화가 양파 종결 핵심):
  실측 결과 SVG generator(.py) 부재 — locale 별 SVG(`-ja.svg`/`-en.svg`)는 수작업 산출물이고
  base `assets/gen/{lasttrain-timeline,quote-lasttrain}.svg` 는 ko-base(개화=한글) 1종뿐.
  ∴ SVG 파일 자체 = source. SVG 직접 치환 = source 단일화(generator 경유 재발 경로 0).
  en SVG 가 同좌표(x607/y316·x403/y520·x54/y43)에 Gaehwa 를 박은 것이 동일 수작업 산출물 증거.
  HTML 도 byvias_course_i18n.py(_NO_TRANS_RE ASCII skip) 경유 재생성 시 병기/한자 소실 →
  dist 직접 패치 + 멱등 박제 (R75~R80 dev 보고 동형·구조적 확정).

정책 (조니 §5·§4.2 — 표준 표기 1종):
  ▸ 표준 = `開化(ケファ)` 1종 (한자 정자 + 한국어 표준 발음 음독.
    개화 어두 무성 [k] → `ケ` 정확, 濁音 `ゲ` 부정확). romaji layer(li timeline)는 `Gaehwa` 유지.
  ▸ HTML 미정정 2종:
      L593 tldr `<span class="warn">9号線ゲファ方面` → `9号線開化(ケファ)方面`
      L694 막차경고 prose bare `(開化·金浦空港方面)` → `(開化(ケファ)·金浦空港方面)`
    (조니 §3 #4 guest-pool: bare 開化 ↔ 開化(ケファ) 262byte 인접 = split 극대화 →
     단일 SSOT 위해 bare 도 開化(ケファ) 통일. bare 0 목표.)
  ▸ SVG 2종 開花×4 → 開化(ケファ):
      lasttrain-timeline-ja.svg: `開花 23:56`·`開花 22:55`·`西行き(開花行き)` (×3)
      quote-lasttrain-ja.svg:    `9号線開花行き` (×1)

🔴 게이트 (조니 §4.3 — 4→7 layer 확장·FLR-AGT-002 실측 grep·선언 금지):
  개화 token × {본문 prose · 終電요약 · tldr · img alt · li(romaji) · SVG <text> · dict source}
  전 asset 교차표 enumerate (fix 전/후):
    開花 = 0 (전 asset 전 layer) · 開化(ケファ) 통일 · ゲファ = 0 · bare 開化 = 0 ·
    Gaehwa(romaji li) 유지 · en SVG Gaehwa 무회귀 · R80 무회귀(송파나루·gloss·2tier).
  멱등(재실행 0 변경) · <div 균형 · SVG <text> 노드 균형.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
DIST_JA = WT / "dist/ja/twice-thisisfor-seoul.html"
SVG_LASTTRAIN = WT / "dist/assets/gen/lasttrain-timeline-ja.svg"
SVG_QUOTE = WT / "dist/assets/gen/quote-lasttrain-ja.svg"

# en SVG 통제군 (무회귀 cross-check 전용·비편집)
SVG_LASTTRAIN_EN = WT / "dist/assets/gen/lasttrain-timeline-en.svg"
SVG_QUOTE_EN = WT / "dist/assets/gen/quote-lasttrain-en.svg"

STD = "開化(ケファ)"  # 표준 표기 (한자 정자 + 한국어 음독)

# ──────────────────────────────────────────────────────────────────────────
# (1) HTML 미정정 2종 → 開化(ケファ) 통일. (old, new)
#   🔴 L616/L697/L833 開化(ケファ)×4·L677/L683 Gaehwa(romaji)×2 는 비대상(정상·유지).
# ──────────────────────────────────────────────────────────────────────────
HTML_FIX: list[tuple[str, str]] = [
    # L593 tldr `終電の罠` span: ゲファ(濁音·한자無) → 開化(ケファ)
    ("9号線ゲファ方面", f"9号線{STD}方面"),
    # L694 막차경고 prose bare: 開化·金浦空港 → 開化(ケファ)·金浦空港
    #   🔴 멱등: 이미 정정된 `開化(ケファ)` 는 `開化(` 뒤가 `·` 아님 → 충돌 0.
    ("(開化·金浦空港方面)", f"({STD}·金浦空港方面)"),
]

# ──────────────────────────────────────────────────────────────────────────
# (2) SVG 開花(벚꽃 오자·실재않는 역)×4 → 開化(ケファ). (old, new)
#   🔴 lasttrain ×3 + quote ×1. en SVG 同좌표 Gaehwa 가 정합 가능 입증(통제군).
# ──────────────────────────────────────────────────────────────────────────
SVG_LASTTRAIN_FIX: list[tuple[str, str]] = [
    ("開花 23:56", f"{STD} 23:56"),  # Line9 평일 라벨 (x607 y316)
    ("開花 22:55", f"{STD} 22:55"),  # Line9 주말 라벨·트랩 (x403 y520)
    ("西行き(開花行き)", f"西行き({STD}行き)"),  # 트랩 콜아웃 본문 (x54 y43)
]
SVG_QUOTE_FIX: list[tuple[str, str]] = [
    ("9号線開花行き", f"9号線{STD}行き"),  # quote (x22 y25)
]


def _two_phase_replace(text: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """R78/R79/R80 검증 엔진: 멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    new 는 자기 잠금(멱등 — 재실행 시 0 변경).
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
    #    new 가 어느 old 의 substring 이면 사전 잠금 시 old 파괴 → 스킵
    #    (멱등은 step2 longest-first 가 보장).
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


def _crosstable(html: str, svg_lt: str, svg_q: str) -> str:
    """🔴 7-layer 교차표 enumerate — fix 전/후 공용.

    개화 token × {본문 prose · 終電요약 · tldr · img alt · li(romaji) · SVG <text> · dict}.
    """
    rows = ["  개화 종점 × 7 layer (ja 전 asset 실측):"]
    # HTML layer
    h_body_prose = len(
        re.findall(r"西行き\(開化\(ケファ\)·金浦空港", html)
    )  # L694 본문
    h_body_bare = len(re.findall(r"西行き\(開化·金浦空港", html))  # L694 bare(오류)
    h_summary = len(
        re.findall(r"9号線西行\(開化\(ケファ\)\)", html)
    )  # L616/L833 終電요약
    h_step5 = len(re.findall(r"開化\(ケファ\)駅周辺", html))  # L616 step5 막차표
    h_tldr_ok = len(re.findall(r"9号線開化\(ケファ\)方面", html))  # L593 tldr fix
    h_tldr_bad = html.count("ゲファ")  # L593 tldr 오류
    h_alt = len(re.findall(r"9号線開化\(ケファ\)行き", html))  # L697 img alt
    h_li_romaji = len(
        re.findall(r"西方向\(Gaehwa\)", html)
    )  # L677/L683 li(romaji 유지)
    h_bad_kanji = html.count("開花")  # 開花(오자) — 전 HTML
    rows.append(
        f"    [HTML] 본문prose 開化(ケファ)={h_body_prose}/BARE={h_body_bare} · "
        f"終電요약={h_summary} · step5막차표={h_step5} · "
        f"tldr OK={h_tldr_ok}/ゲファ={h_tldr_bad} · img-alt={h_alt} · "
        f"li(romaji Gaehwa)={h_li_romaji} · 開花(오자)={h_bad_kanji}"
    )
    # SVG layer
    lt_bad = svg_lt.count("開花")
    lt_ok = svg_lt.count(STD)
    q_bad = svg_q.count("開花")
    q_ok = svg_q.count(STD)
    rows.append(
        f"    [SVG]  lasttrain 開花(오자)={lt_bad}/開化(ケファ)={lt_ok} · "
        f"quote 開花(오자)={q_bad}/開化(ケファ)={q_ok}"
    )
    # dict source
    rows.append(
        "    [dict] SVG generator(.py) 부재 = SVG 파일 자체가 source "
        "(직접 치환 = source 단일화·generator 재발 경로 0)"
    )
    return "\n".join(rows)


def _gate(html: str, svg_lt: str, svg_q: str) -> list[str]:
    """게이트 7-layer: 실측 grep. 위반 시 사유 리스트(빈 = PASS)."""
    fails: list[str] = []

    # 1) 開花(벚꽃 오자) = 0 (전 asset 전 layer)
    for name, txt in (("HTML", html), ("SVG-lasttrain", svg_lt), ("SVG-quote", svg_q)):
        if "開花" in txt:
            ctx = re.findall(r".{0,10}開花.{0,10}", txt)
            fails.append(
                f"{name} 開花(벚꽃 오자) 잔존 {txt.count('開花')}건: {ctx[:3]}"
            )

    # 2) ゲファ(濁音·부정확) = 0 (HTML tldr)
    if "ゲファ" in html:
        fails.append(
            f"HTML ゲファ(濁音·부정확) 잔존 {html.count('ゲファ')}건 — tldr 미정정"
        )

    # 3) bare 開化 = 0 (本文 prose). `開化` not followed by `(`
    bare = re.findall(r"開化(?!\()", html)
    if bare:
        ctx = re.findall(r".{0,10}開化(?!\().{0,10}", html)
        fails.append(f"HTML bare 開化(gloss無) 잔존 {len(bare)}건: {ctx[:3]}")

    # 4) 開化(ケファ) 통일 — 전 가시 layer present
    if "9号線開化(ケファ)方面" not in html:
        fails.append("HTML tldr 開化(ケファ)方面 부재 — (1) 미적용")
    if "西行き(開化(ケファ)·金浦空港方面)" not in html:
        fails.append("HTML 본문prose 開化(ケファ)·金浦空港 부재 — (1) 미적용")
    if STD not in svg_lt:
        fails.append("SVG lasttrain 開化(ケファ) 부재 — (2) 미적용")
    if STD not in svg_q:
        fails.append("SVG quote 開化(ケファ) 부재 — (2) 미적용")

    # 5) R80 무회귀: 개화 막차표 본문·終電요약·img alt 開化(ケファ) 무손상
    for need in (
        "開化(ケファ)駅周辺",
        "9号線西行(開化(ケファ))",
        "9号線開化(ケファ)行き",
    ):
        if need not in html:
            fails.append(f"R80 開化(ケファ) layer 회귀 — 무손상 위반: {need!r}")

    # 6) Gaehwa(romaji) li layer 유지 (정책 — 정정 대상 아님)
    if html.count("西方向(Gaehwa)") < 2:
        fails.append(
            f"li(romaji) Gaehwa 회귀 — romaji layer 정책 위반 "
            f"(현재 {html.count('西方向(Gaehwa)')}/2)"
        )

    # 7) R80 무회귀: 송파나루 1형 + 을지로입구 gloss 0 + 2tier
    sp = set(re.findall(r"송파나루역\([^)]*\)", html))
    if sp != {"송파나루역(松坡ナル駅 / ソンパナル駅)"}:
        fails.append(f"송파나루역 표기 회귀 {len(sp)}형: {sp}")
    if "えるじろいりぐち" in html:
        fails.append("을지로입구 gloss えるじろいりぐち 회귀 — R80 위반")
    if "을지로입구역(Euljiro-ipgu駅)" not in html:
        fails.append("을지로입구역 한글원문+romaja 회귀 — P0 위반")
    for bad in (
        "안국역(Anguk Station)",
        "을지로역(乙支路駅)",
        "송파나루역(松坡ナル駅)",
    ):
        if bad in html:
            fails.append(f"R79 2tier 회귀 — 구 스타일 잔존: {bad!r}")

    return fails


def _en_control_check() -> list[str]:
    """en SVG 통제군 무회귀 cross-check (Gaehwa 유지·開花/開化 미오염)."""
    fails: list[str] = []
    for f, want_gaehwa in ((SVG_LASTTRAIN_EN, 5), (SVG_QUOTE_EN, 1)):
        if not f.exists():
            fails.append(f"en 통제군 SVG 부재: {f.name}")
            continue
        t = f.read_text(encoding="utf-8")
        g = t.count("Gaehwa")
        if g < want_gaehwa:
            fails.append(f"en {f.name} Gaehwa 회귀 {g}/{want_gaehwa}")
        if "開花" in t or "開化" in t:
            fails.append(f"en {f.name} ja 한자 오염(開花/開化) 발생")
    return fails


def run(write: bool) -> bool:
    for p in (DIST_JA, SVG_LASTTRAIN, SVG_QUOTE):
        if not p.exists():
            print(f"ERROR: {p} 없음")
            return False

    html0 = DIST_JA.read_text(encoding="utf-8")
    lt0 = SVG_LASTTRAIN.read_text(encoding="utf-8")
    q0 = SVG_QUOTE.read_text(encoding="utf-8")
    div_before = html0.count("<div")
    lt_text_before = lt0.count("<text")
    q_text_before = q0.count("<text")

    # 🔴 fix *전* 7-layer 교차표 enumerate
    print("=== [BEFORE] 7-layer 교차표 (fix 전 enumerate) ===")
    print(_crosstable(html0, lt0, q0))
    print()

    html, c_h = _two_phase_replace(html0, HTML_FIX)
    lt, c_lt = _two_phase_replace(lt0, SVG_LASTTRAIN_FIX)
    q, c_q = _two_phase_replace(q0, SVG_QUOTE_FIX)

    # 구조 보존 게이트
    if html.count("<div") != div_before:
        print(f"ABORT: <div 불균형 {div_before}→{html.count('<div')}")
        return False
    if lt.count("<text") != lt_text_before:
        print(f"ABORT: lasttrain <text 불균형 {lt_text_before}→{lt.count('<text')}")
        return False
    if q.count("<text") != q_text_before:
        print(f"ABORT: quote <text 불균형 {q_text_before}→{q.count('<text')}")
        return False

    # 7-layer 게이트 (적용 후)
    fails = _gate(html, lt, q) + _en_control_check()
    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = (html != html0) or (lt != lt0) or (q != q0)
    if write:
        if html != html0:
            DIST_JA.write_text(html, encoding="utf-8")
        if lt != lt0:
            SVG_LASTTRAIN.write_text(lt, encoding="utf-8")
        if q != q0:
            SVG_QUOTE.write_text(q, encoding="utf-8")

    print("=== [AFTER] 7-layer 교차표 (fix 후 검증) ===")
    print(_crosstable(html, lt, q))
    print()

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R81 ja 개화 종점 SSOT 통일 ({state}) ===")
    print(f"  (1) HTML ゲファ/bare → 開化(ケファ): {sum(c_h.values())}건")
    for tok, n in sorted(c_h.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  (2) SVG lasttrain 開花 → 開化(ケファ): {sum(c_lt.values())}건")
    for tok, n in sorted(c_lt.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  (2) SVG quote 開花 → 開化(ケファ): {sum(c_q.values())}건")
    for tok, n in sorted(c_q.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(
        "  게이트 7-layer: PASS (開花 0 전 asset·ゲファ 0·bare 開化 0·"
        "開化(ケファ) 통일·Gaehwa romaji li 유지·en SVG 통제군 무회귀·"
        "R80 무회귀·<div/<text> 균형)"
    )
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R81 ja 개화 종점 전 asset SSOT 통일 [{mode}] (7-layer 게이트 통과)")


if __name__ == "__main__":
    main()
