#!/usr/bin/env python3
"""R80 fix — ja 개화역 한자 오타(開花→開化(ケファ)) + 을지로입구 gloss 반-번역 제거.

배경 (R79 미수렴 — 조니 2심 DOC-20260616-JDG-006 §4·§5 (A)(B)(C) + kpop 1심 DOC-20260616-JDG-005):
  R79 에서 막차표 본문(s5-d) 개화역은 `開化(ケファ)` 로 fix 됐다(cross-locale 정합 회복).
  그러나 *같은 개화역* 이 다른 2 layer 에서 `開花`(벚꽃 개화·실재하지 않는 역) 한자로 오기:
    (a) img alt   : `終演から終電までの路線別タイムライン — 9号線開花行き…`
    (b) 終電 요약  : `<b>9号線西行(開花)+土・日</b>`(現地実用情報 lv 블록 가시 본문)
  en `Line 9 Gaehwa-bound`·`Line 9 westbound (Gaehwa)` / ko `9호선 개화행`·`9호선 서행(개화)`
  는 양 layer 정상. ja 만 開花 오기 (조니: layer 누락 양파가 아니라 ja source 1곳 한자 오타).

근본 진단 (조니 §4 — 4-layer 교차표 결정타):
  개화 = layer 누락 양파 아님. en/ko 는 終電 요약 + img alt *양 layer 이미 정상*.
  틀린 건 ja 의 source string — `開化`(개화역 정자)를 `開花`(꽃이 핀다)로 적은 ja 단일 오타.
  → ja source(dictionary) 점검 의무. 실측 결과:
    ▸ img alt source = tools/r68_ja_course_patch.py:79 사전 entry `9号線開花行き` (R80 동시 정정).
    ▸ 終電 요약 본문 = dist 직접 생성 (r68/r78 매핑 부재 = HTML 이 곧 SoT, dist 직접 치환).
  을지로입구만 진성 layer-갭: 첫 등장(동선 요약 line 730) `(Euljiro-ipgu駅)(約20分)` 정상,
  carousel slide(line 739) gloss `(えるじろいりぐちえき)` 만 반-번역(입구→入口=いりぐち iriguchi).

정책 (조니 §5 (A)(B)):
  ▸ (A) 開花 → 開化(ケファ) — 終電 요약 본문 <b> + img alt 양 layer. en Gaehwa·ko 개화 정합.
        막차표 본문 layer(line 616 `開化(ケファ)`)와 동일 SSOT 상속. 읽기 가나(ケファ) 부착
        (조니 의제 verbatim — en `(Gaehwa)`·`Gaehwa-bound` 동형 읽기 부착).
  ▸ (B) 을지로입구 gloss `(えるじろいりぐちえき)` 제거 → 첫 등장(line 730) gloss-less 형태와
        정합. kpop 1심은 `ウルチロイプク`(한국어 읽기) 도 허용 — gloss-less 통일이 첫 등장 SSOT
        상속이라 가장 안전(반-번역 신 가나 창작 0·FLR-AGT-002). 한글원문 `을지로입구역` +
        romaja `Euljiro-ipgu駅` present 유지(P0 무손상).

🔴 (C) 게이트 — fix *전* 4-layer 교차표 enumerate (조니 핵심 처방·양파 끊기):
  station-token(개화·을지로입구) × {본문·終電요약·img alt·i18n_cache(=dist)} × {ja·en·ko}
  를 코드가 fix 전에 표로 펼쳐 한 토큰이 전 layer 일관인지 검증(개별 layer 누락 0).
  을지로입구류 진성 layer-갭(한 layer 만 잔존)을 사전 봉쇄.

SoT/divergence (R75~R79 dev 보고 동형 — 구조적 확정):
  라이브 repo generate.py 없음 + CI 가 dist verbatim 업로드. byvias_course_i18n.py
  (_NO_TRANS_RE ASCII skip) 경유 재생성 시 병기/한자 소실. ∴ dist 직접 패치 + 멱등 박제.
  i18n_cache JSON 은 repo 부재(dist = SSOT) → 終電 요약·gloss 직접 dist 치환이 곧 cache override.
  img alt source 오타(r68:79)는 source 동시 정정(재발 방지·FLR-20260406-TEC-001 공통 모듈 검토).

게이트 (FLR-AGT-002 거짓 충실성 — 선언 아닌 실측 grep):
  - 開花 = 0 (전 layer). 開化(ケファ) 가 본문+終電요약+img alt 전 layer present.
  - 을지로입구 gloss `えるじろいりぐち` = 0. 한글원문+romaja present 유지.
  - R79 무회귀: 송파나루 1형 · ja 역명 2tier(B/D 0) · 개화 막차표 본문 line 616 무손상.
  - 멱등(재실행 0 변경) · <div 균형(태그 무손상) · 4-layer 교차표 클린.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
DIST_JA = WT / "dist/ja/twice-thisisfor-seoul.html"
SRC_R68 = WT / "tools/r68_ja_course_patch.py"

# ──────────────────────────────────────────────────────────────────────────
# (A) 開花(WRONG·벚꽃 개화) → 開化(ケファ)(개화역 정자+한국어 읽기). (old, new)
#   🔴 막차표 본문 line 616 `開化(ケファ)` 와 동일 SSOT 상속. en Gaehwa·ko 개화 정합.
#   🔴 directional 방면 라벨 line 694 `開化·金浦空港方面`(정자·이미 정상)은 비대상.
# ──────────────────────────────────────────────────────────────────────────
KAIHWA_FIX: list[tuple[str, str]] = [
    # (a) img alt: 9号線開花行き → 9号線開化(ケファ)行き
    ("9号線開花行き", "9号線開化(ケファ)行き"),
    # (b) 終電 요약 본문 <b>9号線西行(開花) → <b>9号線西行(開化(ケファ))
    ("9号線西行(開花)", "9号線西行(開化(ケファ))"),
]

# ──────────────────────────────────────────────────────────────────────────
# (B) 을지로입구 gloss 반-번역 제거 → 첫 등장 gloss-less 형태와 정합. (old, new)
#   🔴 한글원문 `을지로입구역` + romaja `(Euljiro-ipgu駅)` present 유지(P0 무손상).
#   🔴 반-번역 gloss `(えるじろいりぐちえき)` surface 만 소거(신 가나 창작 0).
#   🔴 new ⊂ old prefix (gloss 삭제) — 엔진 step1 잠금이 new 를 사전 격리하면 old 가
#      파괴되므로, 엔진은 "new 가 어느 old 의 substring 이면 사전 잠금 스킵"으로 일반 처리.
#   결과: `을지로입구역(Euljiro-ipgu駅) · …` = 첫 등장(line 730 gloss-less)과 동일 패턴.
EULJIRO_FIX: list[tuple[str, str]] = [
    (
        "을지로입구역(Euljiro-ipgu駅)(えるじろいりぐちえき)",
        "을지로입구역(Euljiro-ipgu駅)",
    ),
]

# img alt source 오타(재발 방지 — r68 사전 entry). (old, new)
SRC_FIX: list[tuple[str, str]] = [
    ("9号線開花行き", "9号線開化(ケファ)行き"),
]


def _two_phase_replace(html: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """R78/R79 검증 엔진: 멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    new 는 자기 잠금(멱등 — 재실행 시 0 변경).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)

    # 1) 멱등: 이미 적용된 new(final) 잠금 (longest-first).
    #    🔴 단 new 가 어느 old 의 substring 이면(예: gloss 삭제 = new ⊂ old prefix)
    #    사전 잠금 시 old 가 파괴되므로 스킵 — 멱등은 step2 longest-first 가 보장.
    olds = [o for o, _ in pairs]
    for f in sorted({f for _, f in pairs}, key=len, reverse=True):
        if any(f != o and f in o for o in olds):
            continue
        _lock(f)
    # 2) old 치환 (longest-first)
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if old not in html:
            continue
        counts[old] = counts.get(old, 0) + html.count(old)
        sent = f"\x00L{len(locks)}\x00"
        html = html.replace(old, sent)
        locks.append(new)
    # 3) 복원: sentinel → final / new
    for i, val in enumerate(locks):
        html = html.replace(f"\x00L{i}\x00", val)
    return html, counts


def _crosstable(html: str) -> str:
    """🔴 (C) 4-layer 교차표 enumerate — fix 전/후 공용. station-token × layer 표."""
    rows = []
    rows.append("  station-token × layer (ja course 실측):")
    # 개화: 막차표본문 / 終電요약 / img alt / 방면라벨(directional)
    kf_body = len(re.findall(r"開化\(ケファ\)駅周辺", html))  # line 616 막차표 본문
    kf_summary_ok = len(
        re.findall(r"9号線西行\(開化\(ケファ\)\)", html)
    )  # 終電 요약 fix
    kf_summary_bad = len(re.findall(r"9号線西行\(開花\)", html))  # 終電 요약 오타
    kf_alt_ok = len(re.findall(r"9号線開化\(ケファ\)行き", html))  # img alt fix
    kf_alt_bad = len(re.findall(r"9号線開花行き", html))  # img alt 오타
    kf_dir = len(re.findall(r"開化·金浦空港方面", html))  # 방면 라벨(정자·정상)
    kf_total_wrong = html.count("開花")
    rows.append(
        f"    [개화] 막차표본문 開化(ケファ)={kf_body} · 終電요약 OK={kf_summary_ok}/"
        f"BAD={kf_summary_bad} · img-alt OK={kf_alt_ok}/BAD={kf_alt_bad} · "
        f"방면라벨 開化(정자)={kf_dir} · 開花(전체 오타)={kf_total_wrong}"
    )
    # 을지로입구: 첫등장(gloss-less) / carousel(gloss)
    ej_plain = len(re.findall(r"을지로입구역\(Euljiro-ipgu駅\)\(約20分\)", html))
    ej_gloss = html.count("えるじろいりぐち")
    ej_target = html.count("ウルチロイプク")
    ej_kor = html.count("을지로입구역")
    rows.append(
        f"    [을지로입구] 첫등장(gloss-less)={ej_plain} · carousel gloss(えるじろ)="
        f"{ej_gloss} · ウルチロイプク={ej_target} · 한글원문 을지로입구역={ej_kor}"
    )
    return "\n".join(rows)


def _gate(html: str) -> list[str]:
    """게이트: 실측 grep. 위반 시 사유 리스트(빈 = PASS)."""
    fails: list[str] = []
    # 1) 開花 전 layer 0
    if "開花" in html:
        n = html.count("開花")
        ctx = re.findall(r".{0,12}開花.{0,12}", html)
        fails.append(f"開花(벚꽃 개화·오타) 잔존 {n}건: {ctx[:3]}")
    # 2) 開化(ケファ) 가 終電 요약 + img alt 양 layer present
    if "9号線西行(開化(ケファ))" not in html:
        fails.append("終電 요약 開化(ケファ) 부재 — (A) 미적용")
    if "9号線開化(ケファ)行き" not in html:
        fails.append("img alt 開化(ケファ) 부재 — (A) 미적용")
    # 3) 막차표 본문 line 616 무손상 (R79 SSOT)
    if "開化(ケファ)駅周辺" not in html:
        fails.append("막차표 본문 開化(ケファ)駅周辺 회귀 — R79 무손상 위반")
    # 4) 을지로입구 gloss 0 + 한글원문/romaja present
    if "えるじろいりぐち" in html:
        fails.append("을지로입구 gloss えるじろいりぐち 잔존 — (B) 미적용")
    if "을지로입구역(Euljiro-ipgu駅)" not in html:
        fails.append("을지로입구역 한글원문+romaja 회귀 — P0 위반")
    # 5) R79 무회귀: 송파나루 1형
    sp = set(re.findall(r"송파나루역\([^)]*\)", html))
    if sp != {"송파나루역(松坡ナル駅 / ソンパナル駅)"}:
        fails.append(f"송파나루역 표기 회귀 {len(sp)}형: {sp}")
    # 6) R79 무회귀: ja 역명 2tier B/D 잔존 0
    for bad in (
        "경복궁역(Gyeongbokgung Station)",
        "안국역(Anguk Station)",
        "을지로역(乙支路駅)",
        "송파나루역(松坡ナル駅)",
    ):
        if bad in html:
            fails.append(f"R79 2tier 회귀 — 구 스타일 잔존: {bad!r}")
    return fails


def run(write: bool) -> bool:
    if not DIST_JA.exists():
        print(f"ERROR: {DIST_JA} 없음")
        return False
    orig = DIST_JA.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    # 🔴 (C) fix *전* 4-layer 교차표 enumerate
    print("=== [BEFORE] 4-layer 교차표 (fix 전 enumerate) ===")
    print(_crosstable(orig))
    print()

    html, c_k = _two_phase_replace(orig, KAIHWA_FIX)
    html, c_e = _two_phase_replace(html, EULJIRO_FIX)

    # 게이트: <div 균형
    div_after = html.count("<div")
    if div_before != div_after:
        print(f"ABORT: <div 불균형 {div_before}→{div_after}")
        return False

    # 게이트: 실측 grep (적용 후)
    fails = _gate(html)
    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    # source 오타 정정 (img alt 재발 방지)
    src_changed = False
    c_s: dict[str, int] = {}
    if SRC_R68.exists():
        src_orig = SRC_R68.read_text(encoding="utf-8")
        src_html, c_s = _two_phase_replace(src_orig, SRC_FIX)
        src_changed = src_html != src_orig
        if src_changed and write:
            SRC_R68.write_text(src_html, encoding="utf-8")

    changed = html != orig
    if changed and write:
        DIST_JA.write_text(html, encoding="utf-8")

    print("=== [AFTER] 4-layer 교차표 (fix 후 검증) ===")
    print(_crosstable(html))
    print()

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== [ja] {DIST_JA.name} ({state}) ===")
    print(f"  (A) 開花→開化(ケファ): {sum(c_k.values())}건")
    for tok, n in sorted(c_k.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  (B) 을지로입구 gloss 제거: {sum(c_e.values())}건")
    for tok, n in sorted(c_e.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    src_state = (
        "WROTE" if (src_changed and write) else ("DRY" if not write else "변경없음")
    )
    print(f"  source 오타(r68:79) 정정 [{src_state}]: {sum(c_s.values())}건")
    print(
        "  게이트: PASS (開花 0·開化(ケファ) 양 layer·gloss 0·한글원문 유지·"
        "송파나루 1형·2tier 무회귀·<div 균형·4-layer 교차표 클린)"
    )
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R80 ja 개화 한자 오타 + 을지로입구 gloss [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
