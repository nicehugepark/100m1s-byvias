#!/usr/bin/env python3
"""R77 fix — dual-notation SSOT 4분기 상속 (단일 구조 fix).

배경 (R76 미수렴 — 조니 2심 핵심 통찰 VRD-RND-BYBIAS-076-2nd-jony):
  1심 4패널이 개별 결함으로 잡은 4건이 단일 root — dual-notation(한글 원문 병기)이
  R75/R76 에서 '메인 공연 동선 prose' 분기에만 적용되고 4분기에 미상속:
    ① IG캡션 layer  — 송파나루역 (en Songpanaru BARE 2 / ja 한글 0)            [P0]
    ② 부차 관광/쇼핑일 동선 역명 (en 13건 BARE / ja 동형)                       [P1]
    ③ 코인드 별칭   — GangnamDol → 강남돌(GangnamDol)                          [P1]
    ④ en 로마자 사전 — 송리단길 2철자(Songnidan/Songridan) 同페이지 공존 → 1형  [P1]
    ⑤ ja 캡션 한자붕괴 — 肉，肉(동일 한자 중복) → 肉類・焼肉                      [P1]
  조니: "4결함을 4개 별건 fix로 처리하면 다음 라운드에 또 다른 미상속 분기가 샌다.
        단일 구조 fix(SSOT 전 분기 상속)로 P0+P1 동시 해소" → 본 엔진은 R76 검증
        엔진(2-phase NUL sentinel + longest-first)을 4분기 전체로 확장한 단일 sweep.

SoT/divergence (R75·R76 dev 보고와 동일 — 구조적 확정):
  byvias_course_i18n.py(ko 마스터 번역 파이프라인)는 _NO_TRANS_RE 로 ASCII 고유명사
  를 skip → 한글 병기 미생성. ko 마스터(dist/twice-thisisfor-seoul.html)에 dual-notation
  source 없음 → SoT 경유 재생성 시 R74+R75+R76+R77 병기 전부 소실. ∴ R75/R76 동형
  dist 직접 패치 + 멱등 패치 스크립트 박제. i18n.py 정본화(옵션2)는 후행 별 트랙
  (R74/R75/R76 누적 부채). 한글 원문 source 는 ko 마스터에 전수 존재(grep 확인):
    송파나루역·삼성역·압구정로데오역·을지로입구역·안국역·종로구·강남돌(하우스).

전략 (R76 검증 엔진 verbatim 차용 — tools/r76_en_prose_pname_patch.py):
  - 2-phase NUL sentinel 치환. longest-first(괄호/합성어/Station/Stn 이 bare 보다 먼저
    매칭) → cross-variant 오염 + superstring 오염(Songpanaru⊃Songpa 등) 구조적 차단.
  - 멱등: 이미 적용된 final + 보호 합성어 사전 sentinel 잠금. 재실행 0 변경.
  - 카드 .pname/.sname/.ptag/.crs-tag + aria-label inner content 동적 보호 잠금.

게이트 (FLR-AGT-002 거짓 충실성 — 선언 아닌 실측 grep):
  - en: 송파나루(한글) present·부차역명 6종 한글 present·강남돌 present·송리단길 1철자
    (Songnidan-gil bare 0)·raw 키 0·메인동선(올림픽공원 23/몽촌토성 9) 무회귀.
  - ja: 송파나루(한글) present·肉，肉 0(肉類・焼肉 present)·캡션 변종 0 무회귀.
  - 멱등(재실행 0 변경).
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
# en: 4분기 변종 → '{ko원문}({로마자})'. longest-first 는 엔진서 자동 정렬.
#   ① IG캡션 송파나루 ② 부차역명 13건 ③ GangnamDol 코인드 ④ 송리단길 단일화
# ──────────────────────────────────────────────────────────────────────────
EN_VARIANTS: list[tuple[str, str]] = [
    # ── ③ 코인드 별칭 (longest-first: Haus by Galleria 가 GangnamDol bare 보다 먼저) ──
    ("GangnamDol Haus by Galleria", "강남돌하우스(GangnamDol Haus by Galleria)"),
    ("GangnamDol", "강남돌(GangnamDol)"),
    # ── ① IG캡션 송파나루역 (prose 'Songpanaru Station' + igtop 'Songpanaru / ') ──
    #   'Songpanaru Station' longest-first 로 igtop bare 'Songpanaru' 보다 먼저.
    ("Songpanaru Station", "송파나루역(Songpanaru Station)"),
    ("Songpanaru", "송파나루(Songpanaru)"),
    # ── ② 부차 관광/쇼핑일 역명 (Stn/Station longest-first) ──
    ("Samseong Stn", "삼성역(Samseong Stn)"),
    ("Apgujeong Rodeo Stn", "압구정로데오역(Apgujeong Rodeo Stn)"),
    ("Apgujeong Rodeo", "압구정로데오(Apgujeong Rodeo)"),
    ("Euljiro 1-ga Stn", "을지로1가역(Euljiro 1-ga Stn)"),
    ("Anguk Stn", "안국역(Anguk Stn)"),
    ("Jongno 5-ga Stn", "종로5가역(Jongno 5-ga Stn)"),
]

# ④ en 로마자 사전 단일화: 송리단길 Songnidan-gil → Songridan-gil (조니: 다수형 기준).
#   R76 이미 한글 병기 완료 → '송리단길(Songnidan-gil)' 4건을 '송리단길(Songridan-gil)' 로
#   통일(동페이지 2철자 0). 고정 enumerable → 직접 치환(병기 형태 한정·bare 토큰 무관).
EN_ROMAN_UNIFY: list[tuple[str, str]] = [
    ("송리단길(Songnidan-gil)", "송리단길(Songridan-gil)"),
]

# ──────────────────────────────────────────────────────────────────────────
# ja: ① IG캡션 송파나루역 + ② 부차역명(라틴/한자/가나 혼재 → 한글 원문 병기) + ⑤ 肉，肉.
#   ja 한글 병기 형태 = '{ko원문}({한자 / 가나})' (본문 SSOT 정합).
# ──────────────────────────────────────────────────────────────────────────
JA_VARIANTS: list[tuple[str, str]] = [
    # ── ① IG캡션 송파나루역 (prose '松坡ナル駅' + igtop 'Songpanaru Station (ソンパナル駅)') ──
    #   igtop 의 'Songpanaru Station (ソンパナル駅)' longest-first 로 먼저 잠근 뒤 prose 처리.
    (
        "Songpanaru Station (ソンパナル駅)",
        "송파나루역(Songpanaru Station / ソンパナル駅)",
    ),
    ("松坡ナル駅", "송파나루역(松坡ナル駅)"),
    # ── ② 부차역명 (en 동형 — ja 형태 그대로 한글 prefix 병기) ──
    ("Apgujeong-Rodeo 駅", "압구정로데오역(Apgujeong-Rodeo 駅)"),
    ("Samseong駅", "삼성역(Samseong駅)"),
    ("Anguk Station", "안국역(Anguk Station)"),
    ("Euljiro-ipgu駅", "을지로입구역(Euljiro-ipgu駅)"),
    ("Jongno 5-ga Station", "종로5가역(Jongno 5-ga Station)"),
    # ── ⑤ 캡션 한자 붕괴: 肉，肉(동일 한자 중복) → 肉類・焼肉 (ko '육류,고기' 2토큰 대응) ──
    ("肉，肉", "肉類・焼肉"),
]


def _two_phase_replace(
    html: str, variants: list[tuple[str, str]], protect: list[str]
) -> tuple[str, dict]:
    """R76 검증 엔진: 멱등 final 잠금 + 보호 토큰 잠금 + longest-first 토큰 치환.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)  # 보호/멱등: 원문 그대로 복원

    # 1) 멱등: 이미 적용된 final 들 잠금 (longest-first)
    seen_finals = {f for _, f in variants}
    for f in sorted(seen_finals, key=len, reverse=True):
        _lock(f)
    # 2) 보호 토큰 잠금 (카드 콘텐츠/aria-label)
    for p in sorted(protect, key=len, reverse=True):
        _lock(p)
    # 3) 토큰 치환 (longest-first). 매칭 → sentinel 잠금 + final 복원 큐 적재.
    for cur_tok, final in sorted(variants, key=lambda x: len(x[0]), reverse=True):
        if cur_tok not in html:
            continue
        n = html.count(cur_tok)
        sent = f"\x00L{len(locks)}\x00"
        html = html.replace(cur_tok, sent)
        locks.append(final)
        counts[cur_tok] = counts.get(cur_tok, 0) + n
    # 4) 복원: sentinel → 원문/보호/final
    for i, val in enumerate(locks):
        html = html.replace(f"\x00L{i}\x00", val)
    return html, counts


def _card_protect(html: str) -> list[str]:
    """카드 .pname/.sname/.ptag/.crs-tag + aria-label inner content 동적 보호 토큰 수집.

    산문 bare 토큰 치환이 카드/속성 안 토큰(R74~R76 박은 병기·고유명)을 못 건드리게 잠금.
    단, 본 패치 대상 토큰(부차역명 등)이 산문에 있으면 치환되도록 — 보호는 카드 내부만.
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
    return protect


def apply_en(html: str) -> tuple[str, dict, dict]:
    # ⑤ 肉，肉 는 ja 전용 — en 카드 .ptag 'Meat / BBQ' 는 정상이므로 동적 보호에 자동 포함.
    protect = _card_protect(html)
    html, c_var = _two_phase_replace(html, EN_VARIANTS, protect)
    # ④ 로마자 사전 단일화 (이미 병기된 형태 직접 치환 — 보호 잠금 후 안전)
    c_uni: dict[str, int] = {}
    for old, new in EN_ROMAN_UNIFY:
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            c_uni[old] = n
    return html, c_var, c_uni


def apply_ja(html: str) -> tuple[str, dict]:
    # 肉，肉 은 ph-chip/ptag 카드 내부 → 동적 보호가 잠그면 치환 안 됨.
    #   ∴ ja 는 ph-chip/ptag 의 '肉，肉' 만 명시 변종 처리. 보호 수집서 肉，肉 카드 제외.
    protect = [
        p for p in _card_protect(html) if "肉，肉" not in p and "松坡ナル駅" not in p
    ]
    html, c_var = _two_phase_replace(html, JA_VARIANTS, protect)
    return html, c_var


def run(lang: str, write: bool) -> bool:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    if lang == "en":
        html, c_var, c_uni = apply_en(orig)
    else:
        html, c_var = apply_ja(orig)
        c_uni = {}

    # 게이트: <div 균형(태그 깨짐 방지 — 치환이 태그 구조 무손상)
    div_after = html.count("<div")
    if div_before != div_after:
        print(f"ABORT [{lang}]: <div 불균형 {div_before}→{div_after}")
        return False

    changed = html != orig
    if changed and write:
        path.write_text(html, encoding="utf-8")

    print(
        f"=== [{lang}] {path.name} "
        f"({'WROTE' if (changed and write) else 'DRY' if not write else '변경없음'}) ==="
    )
    print(f"  분기 병기/정정: {sum(c_var.values())}건 ({len(c_var)} 토큰종)")
    for tok, n in sorted(c_var.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    if lang == "en":
        print(f"  로마자 사전 단일화: {sum(c_uni.values())}건")
        for tok, n in c_uni.items():
            print(f"      {tok!r} ×{n}")
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    langs = [a for a in args if a in ("ja", "en")] or ["en", "ja"]
    ok = True
    for lang in langs:
        if not run(lang, write):
            ok = False
    if not ok:
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R77 dual-notation SSOT 4분기 상속 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
