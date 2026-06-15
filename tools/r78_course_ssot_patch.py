#!/usr/bin/env python3
"""R78 fix — ja 전 layer dual-notation 단일 SSOT 상속 (양파 패턴 종결).

배경 (R77 미수렴 — 조니 2심 VRD-RND-BYBIAS-077-2nd-jony):
  R75(메인 prose)→R76(IG캡션 해소·부차역명)→R77(IG캡션·송리단길·en GangnamDol) 은
  매 라운드 '적발된 layer' 만 패치 → 다음 라운드에 또 다른 미측정 layer 가 노출되는
  양파(onion) 패턴. R77 라이브에서 막차(終電)표 + 일자별 동선요약(dsum) layer 에 ja
  역명 12 instance 가 한글 원문 없이 bare (Mongtoseong駅·Samsung 駅·乙支路駅·
  狎鷗亭ロデオ駅·Mongchon-toseong Station·Gyeongbokgung Station 등) — 同 ja 페이지
  메인 길안내는 同역명 한글-우선(몽촌토성역·삼성역·을지로입구역·압구정로데오역)인데
  막차표/요약 layer 만 갈림 = 同페이지 同역명 거짓 구분(P0).

조니 진단 (R78 단일 fix 설계):
  "layer 를 하나씩 패치하지 말고, 모든 생성 분기가 같은 원문 규칙을 상속하게 하라."
  → 본 패치는 R77 의 'layer 별 변종 enumerate(JA_VARIANTS 하드코딩)' 를 폐기하고,
    **역(station) 단위 단일 SSOT 사전** 1개 + **전 layer 공통 함수 1개** 로 재설계.
    SSOT 는 '정규 한글-우선 형(canonical)' 1개 + 그 역의 모든 표면 변종(surface)
    리스트(layer 무관 — 막차/dsum/IG캡션/메인 prose 전부). 새 layer 가 알려진 표면
    변종을 내보내면 자동으로 잡힌다(R79 양파 차단).

🔴 거짓 구분(false-distinction) 봉쇄 — 역 disambiguation (라이브 verbatim grep 확정):
  乙支路駅(을지로역, 청계천 day '2号線 乙支路駅 → 잠실') 와 을지로입구역(Euljiro-ipgu,
  굿즈샵 day) 는 **다른 역**. 무차별 blanket 치환 금지 — 각 표면 변종을 정확한 ko 역에만
  매핑. ko 마스터(dist/twice-thisisfor-seoul.html) + en 본문 cross-check 로 확정:
    · 청계천 day: ko '2호선 을지로' / en 'Line 2, Euljiro → 잠실'  → 을지로역(乙支路駅)
    · 굿즈샵 day: ko '2호선 을지로입구' / en '을지로1가역'        → 을지로입구역
  (을지로입구 vs 을지로1가 는 ja dsum 에선 'Euljiro Entrance(...)駅' = 을지로입구역
   문맥 — ja 본문 정규형 '을지로입구역(Euljiro-ipgu駅)' 와 동일 역으로 통합.)

🔴 over-fix 회피 — 開化(かいか)駅 는 의도적 비대상 (FLR-AGT-002 거짓 구조 신설 회피):
  '9号線 西行き(開化·金浦空港方面)' / '9号線の徐行(開化駅周辺)' 의 開化 는 막차 경고용
  **노선 방면(direction terminus)** 참조이지 팬이 이동하는 목적지 역이 아님. en 도 동형으로
  '(Gaehwa)' / '(Gaehwa / Gimpo Airport)' 괄호 방면 라벨로 처리(hangul-led 역명 아님) +
  ko 'ターミナル' = '9호선 개화행'(방면). ∴ en 통제군(bare 0) 과 정합 유지 위해 開化 는
  한글-우선 강제 비대상. (역명으로 강제 시 en 과 divergence + 방면→역 의미 왜곡.)

🔴 Mongtoseong → Mongchontoseong 철자 정정:
  '몽촌토성' 의 정규 로마자는 Mongchontoseong. 막차표 'Mongtoseong駅' 는 철자 누락.
  한글-우선 형(몽촌토성역(夢村土城駅 / モンチョントソン)) 상속으로 bare 로마자 자체 소멸
  → 'Mongtoseong' 토큰 0 (한글 정규형엔 로마자 미포함, 가나 reading 만).

SoT/divergence (R75~R77 dev 보고 동형 — 구조적 확정):
  라이브 repo 는 generate.py 없음 + CI 가 dist verbatim 업로드. byvias_course_i18n.py
  (ko 마스터 번역 파이프라인)는 _NO_TRANS_RE 로 ASCII 고유명사 skip → SoT 경유 재생성
  시 R74~R78 병기 전부 소실. ∴ R75~R77 동형 dist 직접 패치 + 멱등 스크립트 박제.
  i18n.py 정본화(옵션2)는 후행 별 트랙(누적 부채).

전략 (R76/R77 검증 엔진 verbatim 차용):
  - 2-phase NUL sentinel 치환. longest-first(정규형/괄호/합성어가 bare 보다 먼저 매칭)
    → cross-variant 오염 + superstring 오염 구조적 차단 + 멱등.
  - 단일 공통 함수 apply_station_dual_notation() 를 en·ja 양 locale 이 호출.

게이트 (FLR-AGT-002 거짓 충실성 — 선언 아닌 실측 grep):
  - ja: 전 layer(막차/dsum/IG캡션/메인) bare 역명 0 · 한글 원문 병기 전수 ·
    'Mongtoseong' 철자 0 · intra-page 2표기(同역명 한글 유/무 갈림) 0 · 'Gangnam-Dol'/
    'Gangnam Idols' 0 (강남돌(GangnamDol) 단일) · ja Station 로마자 누출 0(駅 통제군).
  - en: ' Station' 1형(다수 Stn 으로 통일·양형 0) · GangnamDol 정합 무회귀.
  - 멱등(재실행 0 변경) · <div 균형(태그 무손상).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
PATHS = {
    "ja": WT / "dist/ja/twice-thisisfor-seoul.html",
    "en": WT / "dist/en/twice-thisisfor-seoul.html",
}

# ──────────────────────────────────────────────────────────────────────────
# 단일 SSOT — 역(station) 단위. layer 무관. (양파 패턴 종결 핵심)
#   각 항목: canonical = 정규 한글-우선 형(전 layer 출력 목표)
#            surfaces  = 라이브에서 발견된 모든 표면 변종(전 layer — 막차/dsum/IG/메인)
#   엔진이 surface → canonical 치환 + canonical 자기 잠금(멱등). longest-first 자동.
#
#   🔴 surface 는 '한글 prefix 가 없는' bare 형만 등록(정규형은 canonical 이 자기 잠금).
#   🔴 disambiguation: 을지로역(乙支路駅) ≠ 을지로입구역 — 표면 변종 분리 등록.
# ──────────────────────────────────────────────────────────────────────────
STATION_SSOT_JA: list[dict] = [
    # 몽촌토성역 — 막차표 'Mongtoseong駅(모...)' + dsum 'Mongchon-toseong Station/駅'
    #   철자 정정(Mongtoseong→Mongchontoseong)은 canonical 한글-우선 상속으로 자동(로마자 소멸).
    {
        "canonical": "몽촌토성역(夢村土城駅 / モンチョントソン)",
        "surfaces": [
            "Mongtoseong駅(モンチョントソン)",  # 막차표 ×2
            "Mongchon-toseong Station",  # dsum (8号線1駅 …Station)
            "Mongchon-toseong 駅",  # dsum (Ktown4u COEX …駅から)
            "モンチョントソン駅",  # 게스트하우스 카드 (8号線でモンチョントソン駅へ) — 순 가나 bare
        ],
    },
    # 강동역 — 막차표 'Gangdong駅(가...)で分岐'
    {
        "canonical": "강동역(江東駅 / ガンドン)",
        "surfaces": ["Gangdong駅(ガンドン)"],
    },
    # 삼성역 — dsum 'Samsung 駅 5・6番出口' + 'Samsung 駅から'
    {
        "canonical": "삼성역(Samseong駅)",
        "surfaces": ["Samsung 駅"],
    },
    # 을지로입구역 — dsum 'Euljiro Entrance(우...)駅'. 🔴 canonical = 同페이지 메인 prose 정규형
    #   '을지로입구역(Euljiro-ipgu駅)' verbatim 상속 (intra-page 2표기 0 — 괄호 내 형식 동일).
    {
        "canonical": "을지로입구역(Euljiro-ipgu駅)",
        "surfaces": ["Euljiro Entrance(ウルチロイングク)駅"],
    },
    # 방이역 — 방이동 먹자골목(저녁) dsum '徒歩(バンギ駅・올림픽공원역…)' (en '방이(Bangi) Stn' 동형)
    #   조니 12-instance sweep 아래였으나 同 class(dsum 名 역명 bare) — 양파 종결 위해 SSOT 편입.
    {
        "canonical": "방이역(バンギ駅)",
        "surfaces": ["バンギ駅"],
    },
    # 🔴 을지로역(≠을지로입구역) — 청계천 day '2号線 乙支路駅 → 잠실'
    {
        "canonical": "을지로역(乙支路駅)",
        "surfaces": ["乙支路駅"],
    },
    # 압구정로데오역 — dsum/관광 '스인분당선 狎鷗亭ロデオ駅'
    {
        "canonical": "압구정로데오역(Apgujeong-Rodeo 駅)",
        "surfaces": ["狎鷗亭ロデオ駅"],
    },
    # 경복궁역 — dsum '8号線→3号線 Gyeongbokgung Station'
    {
        "canonical": "경복궁역(Gyeongbokgung Station)",
        "surfaces": ["Gyeongbokgung Station"],
    },
]

# en: SSOT 는 R77 에서 이미 한글-우선 병기 완료(BARE 0 — 조니 독립 grep). 본 라운드 en 작업은
#   '역 접미사 1형 통일'(P1-4·branding 이월)만. ' Station' bracket form 5건 → ' Stn'(다수형).
#   🔴 정규형(역(... Station)) 안의 ' Station' 만 ' Stn' 으로(괄호 닫힘 직전). 한글-우선 무손상.
EN_SUFFIX_UNIFY: list[tuple[str, str]] = [
    ("올림픽공원역(Olympic Park Station)", "올림픽공원역(Olympic Park Stn)"),
    ("몽촌토성역(Mongchontoseong Station)", "몽촌토성역(Mongchontoseong Stn)"),
    ("송파나루역(Songpanaru Station)", "송파나루역(Songpanaru Stn)"),
]

# ja: 코인드 거리명 — 'Gangnam-Dol'/'Gangnam Idols' 2종 혼재 → '강남돌(GangnamDol)' 단일(en 동형).
#   거리명(표지판 아님)이라 P1. House(시작지점)는 'GangnamDol Haus' 표기 통일.
JA_GANGNAMDOL: list[tuple[str, str]] = [
    ("Gangnam-Dol House", "강남돌(GangnamDol) House"),
    ("Gangnam-Dol", "강남돌(GangnamDol)"),
    ("Gangnam Idols", "강남돌(GangnamDol)"),
]


def _two_phase_replace(
    html: str, pairs: list[tuple[str, str]], protect: list[str]
) -> tuple[str, dict]:
    """R76/R77 검증 엔진: 멱등 final 잠금 + 보호 토큰 잠금 + longest-first 치환.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    pairs = [(surface, canonical), ...]. 매칭된 surface → canonical 복원.
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)  # 보호/멱등: 원문 그대로 복원

    # 1) 멱등: 이미 적용된 canonical(final) 들 잠금 (longest-first)
    seen_finals = {f for _, f in pairs}
    for f in sorted(seen_finals, key=len, reverse=True):
        _lock(f)
    # 2) 보호 토큰 잠금 (카드 콘텐츠/aria-label inner — 산문 치환이 카드 못 건드리게)
    for p in sorted(protect, key=len, reverse=True):
        _lock(p)
    # 3) surface 치환 (longest-first). 매칭 → sentinel 잠금 + canonical 복원 큐 적재.
    for surface, final in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if surface not in html:
            continue
        n = html.count(surface)
        sent = f"\x00L{len(locks)}\x00"
        html = html.replace(surface, sent)
        locks.append(final)
        counts[surface] = counts.get(surface, 0) + n
    # 4) 복원: sentinel → 원문/보호/canonical
    for i, val in enumerate(locks):
        html = html.replace(f"\x00L{i}\x00", val)
    return html, counts


def _card_protect(html: str, exclude: list[str]) -> list[str]:
    """카드 .pname/.sname/.ptag/.crs-tag + aria-label inner content 보호 토큰 수집.

    산문 bare 토큰 치환이 카드/속성 안 토큰(R74~R77 박은 병기·고유명)을 못 건드리게 잠금.
    exclude 안 부분문자열을 포함한 inner 는 보호서 제외(해당 카드 내부 surface 도 치환 대상일 때).
    """
    protect: list[str] = []
    for cls in ("pname", "sname", "ptag", "crs-tag"):
        for m in re.finditer(rf'class="{cls}">(.*?)</', html, flags=re.DOTALL):
            inner = m.group(1)
            if inner and inner not in protect:
                protect.append(inner)
    for m in re.finditer(r'aria-label="([^"]*)"', html):
        inner = m.group(1)
        if inner and inner not in protect:
            protect.append(inner)
    if exclude:
        protect = [p for p in protect if not any(x in p for x in exclude)]
    return protect


def apply_station_dual_notation(
    html: str, ssot: list[dict], protect_exclude: list[str]
) -> tuple[str, dict]:
    """🔴 전 layer 공통 함수 (조니 단일 SSOT 명시 요구).

    역 단위 SSOT(canonical + surfaces)를 (surface→canonical) pair 로 flatten 후
    단일 2-phase sweep. layer(막차/dsum/IG/메인) 무관 — 표면 변종이 어느 layer 에
    있든 동일 함수가 잡는다. en·ja 양 locale 이 본 함수를 호출(중복 패치 로직 0).
    """
    pairs: list[tuple[str, str]] = []
    for st in ssot:
        for surface in st["surfaces"]:
            pairs.append((surface, st["canonical"]))
    protect = _card_protect(html, exclude=protect_exclude)
    return _two_phase_replace(html, pairs, protect)


def apply_ja(html: str) -> tuple[str, dict, dict]:
    # surface 토큰이 카드 내부에 있을 수 있으므로(예: 狎鷗亭ロデオ駅 ph-chip), 해당 surface
    #   부분문자열을 보호 수집서 제외 → 카드 내부도 정규형으로 통일.
    surface_excludes: list[str] = []
    for st in STATION_SSOT_JA:
        surface_excludes.extend(st["surfaces"])
    html, c_st = apply_station_dual_notation(html, STATION_SSOT_JA, surface_excludes)
    # 코인드 거리명 단일화 (강남돌). 본문/카드 무관 enumerable → 2-phase 동일 엔진.
    html, c_gd = _two_phase_replace(html, JA_GANGNAMDOL, protect=[])
    return html, c_st, c_gd


def apply_en(html: str) -> tuple[str, dict]:
    # en 역명 한글-우선 BARE 0(R77 확정). 본 라운드 = 접미사 1형 통일만(정규형 직접 치환).
    c: dict[str, int] = {}
    for old, new in EN_SUFFIX_UNIFY:
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            c[old] = n
    return html, c


def run(lang: str, write: bool) -> bool:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    if lang == "ja":
        html, c_st, c_gd = apply_ja(orig)
    else:
        html, c_suffix = apply_en(orig)

    # 게이트: <div 균형(치환이 태그 구조 무손상)
    div_after = html.count("<div")
    if div_before != div_after:
        print(f"ABORT [{lang}]: <div 불균형 {div_before}→{div_after}")
        return False

    changed = html != orig
    if changed and write:
        path.write_text(html, encoding="utf-8")

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== [{lang}] {path.name} ({state}) ===")
    if lang == "ja":
        print(
            f"  역명 dual-notation 상속(전 layer): {sum(c_st.values())}건 ({len(c_st)} surface)"
        )
        for tok, n in sorted(c_st.items(), key=lambda x: -x[1]):
            print(f"      {tok!r} ×{n}")
        print(f"  강남돌 단일화: {sum(c_gd.values())}건")
        for tok, n in sorted(c_gd.items(), key=lambda x: -x[1]):
            print(f"      {tok!r} ×{n}")
    else:
        print(f"  en 역 접미사 1형(Station→Stn): {sum(c_suffix.values())}건")
        for tok, n in sorted(c_suffix.items(), key=lambda x: -x[1]):
            print(f"      {tok!r} ×{n}")
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    langs = [a for a in args if a in ("ja", "en")] or ["ja", "en"]
    ok = True
    for lang in langs:
        if not run(lang, write):
            ok = False
    if not ok:
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R78 전 layer dual-notation 단일 SSOT 상속 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
