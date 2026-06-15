#!/usr/bin/env python3
"""R79 (A) fix — ja 역명 괄호 단일 정책 (4스타일 → 2tier 규칙화).

배경 (R78 미수렴 — 조니 2심 DOC-20260615-JDG-039 §3·§5 + 1심 guestpool/branding/kpop):
  R78 단일 SSOT 상속으로 P0(한글 원문 누락)는 전 layer 해소됐다(한글 prefix 전수 정합).
  그러나 ja-course 한 페이지에서 역명 괄호 *본문* 이 4스타일로 공존(P1):
    A(漢字駅 / カタカナ)  : 잠실·성수·올림픽공원·몽촌토성·강동 — 한자+가나 정착
    B(English Station)   : 경복궁·안국·종로5가 — 영어 역명
    C(Romaja駅)          : 삼성·을지로입구·압구정로데오 — 로마자+駅
    D(漢字駅 또는 가나駅) : 을지로·방이·송파나루(카페블록) — 한자만/가나만
  + 🔴 송파나루역 intra-page 2표기(동선블록 `(Songpanaru Station / ソンパナル駅)`
    vs 카페블록 `(松坡ナル駅)`) = 동일 역 2 distinct 괄호.
  본질(조니 §1): 역명 하나하나는 정직(폴백 0·한글 prefix 전수)하나, 4스타일 공존이
  일본인 팬에게 "다른 종류의 장소"라는 cross-card 거짓 구분을 만든다(②재료 정직성 +
  ④의도 명료성 동시 위반).

정책 (조니 §5 (A) + guestpool 권고 — 2tier 단일 규칙):
  ▸ tier A(한자 정착 역) → `한글역(漢字駅 / カタカナ)`
      한자·가나가 본문에 *둘 다* 정착된 역만. 신 한자/가나 창작 금지(FLR-AGT-002).
  ▸ tier C(한자 또는 가나 data 공백 역) → `한글역(Romaja駅)`
      한자 또는 가나가 본문에 없는 역. 기존 텍스트의 romaja 재사용(창작 0).
  B·D 스타일은 제거(A 또는 C로 흡수). 송파나루 2표기 → A 단일형 통일.

🔴 실데이터 grep 기반 tier 배정 (FLR-AGT-002 — 선언 아닌 실측, 2026-06-16 검증):
  [A 승격]
    · 경복궁역(Gyeongbokgung Station) → (景福宮駅 / キョンボックン)
        근거: 본문 `景福宮 / キョンボックン` 9회 정착(관광 명소 표기). 한자+가나 둘 다 present.
    · 송파나루역 2표기 → (松坡ナル駅 / ソンパナル駅) 단일형
        근거: `松坡` present + `ソンパナル` present. 동선/카페 블록 2표기 D→A 흡수.
  [C 정규화 — 한자 또는 가나 공백]
    · 안국역(Anguk Station) → (Anguk駅)        근거: 安國/安国 한자 present 0(조니 M6 일치).
    · 종로5가역(Jongno 5-ga Station) → (Jongno 5-ga駅)  근거: 5街+종로5가 가나(チョンノ-) 공백.
    · 방이역(バンギ駅) → 방이역(Bangi駅)        근거: 芳荑 한자 0. en 동형 `Bangi`. 순 가나 D→C.
    · 을지로역(乙支路駅) → 을지로역(Euljiro駅)   근거: 가나(ウルチロ) present 0. en 'Line 2 Euljiro'.
        을지로입구역(Euljiro-ipgu駅)과 cross-card 일관(同 '을지로' 계열 romaja 통일).
    · 압구정로데오역(Apgujeong-Rodeo 駅) → (Apgujeong-Rodeo駅)
        근거: 狎鷗亭 1건(거리명 ROAD)·역명 가나 0. 공백만 제거(C 정규화).
  [무변경 — 이미 정합]
    · A 5역: 강동(江東駅 / ガンドン)·몽촌토성(夢村土城駅 / モンチョントソン)×9·
             성수(聖水駅 / ソンス)×4·올림픽공원(オリンピック公園駅 / オルリムピックゴンウォン)×9·
             잠실(蚕室駅 / ジャムシル)×8
    · C 2역: 삼성(Samseong駅)×3·을지로입구(Euljiro-ipgu駅)×2

開化(かいか) — 일본 음독 제거 (조니 §5 + kpop 1심):
  `9号線 西行き(開化·金浦空港方面)` 와 `9号線の徐行(開化(かいか)駅周辺)` 의 開化 는
  9호선 西行き 金浦空港方面 directional terminus 라벨(보딩/환승 역 아님)이나, ja 음독
  '(かいか)' 가 ko 개화·en Gaehwa(한국어 읽기)와 cross-locale 비대칭 → ja 음독 제거하여
  한국어 읽기로 통일. `開化(かいか)駅周辺` → `開化(ケファ)駅周辺`(가나 음 통일), directional
  `開化·金浦空港方面` 은 한자 그대로(방면 라벨·en Gaehwa 괄호 동형, 읽기 가나 미부착).

을지로입구역 kana gloss — 반-번역 제거 (조니 §5):
  R78 SSOT canonical 이 이미 `을지로입구역(Euljiro-ipgu駅)` 로 통일(반-번역 `えるじろいりぐち`
  surface 는 R78 에서 소거됨). 본 라운드 라이브 재확인 — gloss 잔존 0 검증만(신규 치환 없음).

SoT/divergence (R75~R78 dev 보고 동형 — 구조적 확정):
  라이브 repo 는 generate.py 없음 + CI 가 dist verbatim 업로드. byvias_course_i18n.py
  (ko 마스터 번역 파이프라인)는 _NO_TRANS_RE 로 ASCII 고유명사 skip → SoT 경유 재생성
  시 병기 전부 소실. ∴ R75~R78 동형 dist 직접 패치 + 멱등 스크립트 박제.

전략 (R78 검증 엔진 verbatim 차용):
  - 본 라운드는 '정규형(한글 prefix present) → 정규형(2tier)' 치환. 4스타일 모두 한글-led
    이므로 R78 의 bare→한글 SSOT 가 아닌, 괄호 *본문* 통일.
  - 2-phase NUL sentinel + longest-first + 멱등(canonical 자기 잠금). 정규형 통째 매칭이라
    superstring/cross-variant 오염 구조적 차단.

게이트 (FLR-AGT-002 거짓 충실성 — 선언 아닌 실측 grep):
  - 송파나루역 distinct 괄호 표기 = 1형(2표기 0).
  - 역명 괄호 스타일 = 2tier(A/C)만. B(English Station)·D(漢字駅/kana駅) 0.
  - 開化(かいか) 음독 0. 開化(ケファ) directional gloss 통일.
  - 한글 prefix 전수 무회귀(R78 P0 해소 무손상). 막차/요약/IG/메인 layer bare 0.
  - 멱등(재실행 0 변경) · <div 균형(태그 무손상).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
PATH = WT / "dist/ja/twice-thisisfor-seoul.html"

# ──────────────────────────────────────────────────────────────────────────
# 4스타일(B/D) → 2tier(A/C) 정규형 치환. (old 정규형, new 정규형)
#   🔴 모두 한글 prefix present(한글-led 정합). 본 라운드 = 괄호 본문 통일만.
#   🔴 longest-first 자동(2-phase 엔진). new(2tier) 는 멱등 자기 잠금.
# ──────────────────────────────────────────────────────────────────────────

# [A 승격] 한자+가나 둘 다 본문 정착 — Style A 로 통일
TIER_A_PROMOTE: list[tuple[str, str]] = [
    # 경복궁: 景福宮(9회)+キョンボックン(본문 관광 표기) 정착 → A
    ("경복궁역(Gyeongbokgung Station)", "경복궁역(景福宮駅 / キョンボックン)"),
    # 송파나루 2표기 → A 단일형(松坡+ソンパナル 둘 다 present). 양형 모두 흡수.
    (
        "송파나루역(Songpanaru Station / ソンパナル駅)",
        "송파나루역(松坡ナル駅 / ソンパナル駅)",
    ),
    ("송파나루역(松坡ナル駅)", "송파나루역(松坡ナル駅 / ソンパナル駅)"),
]

# [C 정규화] 한자 또는 가나 data 공백 — Style C(Romaja駅) 로 통일. romaja 재사용(창작 0).
TIER_C_NORMALIZE: list[tuple[str, str]] = [
    # 안국: 安國 한자 0 → Romaja駅 (English 'Station' → '駅' 통일)
    ("안국역(Anguk Station)", "안국역(Anguk駅)"),
    # 종로5가: 5街 가나 공백 → Romaja駅
    ("종로5가역(Jongno 5-ga Station)", "종로5가역(Jongno 5-ga駅)"),
    # 방이: 芳荑 한자 0·순 가나 D → Romaja駅 (en 'Bangi' 동형)
    ("방이역(バンギ駅)", "방이역(Bangi駅)"),
    # 을지로: 가나 공백·한자만 D → Romaja駅 (을지로입구역과 'Euljiro' 계열 일관)
    ("을지로역(乙支路駅)", "을지로역(Euljiro駅)"),
    # 압구정로데오: 가나 0·공백 정규화 (Apgujeong-Rodeo 駅 → Apgujeong-Rodeo駅)
    ("압구정로데오역(Apgujeong-Rodeo 駅)", "압구정로데오역(Apgujeong-Rodeo駅)"),
]

# 開化 directional terminus 음독 제거 (한국어 읽기 통일). 보딩 역 아님 — 방면 라벨.
KAIKA_READING: list[tuple[str, str]] = [
    # 막차 경고 `9号線の徐行(開化(かいか)駅周辺)` 의 일본 음독 → 한국어 읽기 가나
    ("開化(かいか)駅", "開化(ケファ)駅"),
]


def _two_phase_replace(html: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """R78 검증 엔진: 멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    pairs = [(old, new), ...]. 매칭된 old → new 복원. new 는 자기 잠금(멱등).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)

    # 1) 멱등: 이미 적용된 new(final) 잠금 (longest-first)
    seen_finals = {f for _, f in pairs}
    for f in sorted(seen_finals, key=len, reverse=True):
        _lock(f)
    # 2) old 치환 (longest-first). 매칭 → sentinel + new 복원 큐 적재.
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if old not in html:
            continue
        n = html.count(old)
        sent = f"\x00L{len(locks)}\x00"
        html = html.replace(old, sent)
        locks.append(new)
        counts[old] = counts.get(old, 0) + n
    # 3) 복원: sentinel → old(멱등) / new
    for i, val in enumerate(locks):
        html = html.replace(f"\x00L{i}\x00", val)
    return html, counts


def _gate(html: str) -> list[str]:
    """게이트: 실측 grep. 위반 시 사유 리스트 반환(빈 리스트 = PASS)."""
    fails: list[str] = []

    # 1) 송파나루역 distinct 괄호 표기 = 1형
    sp = set(re.findall(r"송파나루역\([^)]*\)", html))
    if sp != {"송파나루역(松坡ナル駅 / ソンパナル駅)"}:
        fails.append(f"송파나루역 표기 {len(sp)}형(1형이어야): {sp}")

    # 2) B(English Station)·D 잔존 0 — 본 fix 대상 역만
    for bad in (
        "경복궁역(Gyeongbokgung Station)",
        "안국역(Anguk Station)",
        "종로5가역(Jongno 5-ga Station)",
        "방이역(バンギ駅)",
        "을지로역(乙支路駅)",
        "압구정로데오역(Apgujeong-Rodeo 駅)",  # 공백형
        "송파나루역(松坡ナル駅)",  # 단독 D형
        "송파나루역(Songpanaru Station / ソンパナル駅)",  # 단독 B형
    ):
        if bad in html:
            fails.append(f"구 스타일 잔존: {bad!r}")

    # 3) 開化 음독 제거
    if "開化(かいか)" in html:
        fails.append("開化(かいか) 일본 음독 잔존")

    # 4) 한글 prefix 무회귀 — 모든 역명 괄호가 한글역(...) 형 (bare 0)
    #    [Latin/漢字]+(駅|Station) 앞에 한글이 없는 bare 검출(false-positive 제외)
    bare = re.findall(r"(?<![가-힣（(])\b[A-Z][A-Za-z\- ]*(?:Station|Stn)\b", html)
    bare = [b for b in bare if b.strip() not in ("Seoul Metro Line",)]  # counter 제외
    if bare:
        fails.append(f"한글 prefix 부재 bare 역명 후보: {bare[:5]}")

    return fails


def run(write: bool) -> bool:
    if not PATH.exists():
        print(f"ERROR: {PATH} 없음")
        return False
    orig = PATH.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    html, c_a = _two_phase_replace(orig, TIER_A_PROMOTE)
    html, c_c = _two_phase_replace(html, TIER_C_NORMALIZE)
    html, c_k = _two_phase_replace(html, KAIKA_READING)

    # 게이트: <div 균형
    div_after = html.count("<div")
    if div_before != div_after:
        print(f"ABORT: <div 불균형 {div_before}→{div_after}")
        return False

    # 게이트: 실측 grep (적용 후 상태)
    fails = _gate(html)
    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = html != orig
    if changed and write:
        PATH.write_text(html, encoding="utf-8")

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== [ja] {PATH.name} ({state}) ===")
    print(f"  tier A 승격(경복궁·송파나루): {sum(c_a.values())}건")
    for tok, n in sorted(c_a.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(
        f"  tier C 정규화(안국·종로5가·방이·을지로·압구정로데오): {sum(c_c.values())}건"
    )
    for tok, n in sorted(c_c.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  開化 음독→한국어 읽기: {sum(c_k.values())}건")
    for tok, n in sorted(c_k.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print("  게이트: PASS (송파나루 1형·B/D 0·開化 음독 0·bare 0·<div 균형)")
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R79 (A) ja 역명 2tier 단일 정책 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
