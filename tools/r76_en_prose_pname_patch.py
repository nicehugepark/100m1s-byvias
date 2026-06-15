#!/usr/bin/env python3
"""R76 fix — en 코스 본문 산문 고유명사 한국어 원문 병기(P0) + ja 캡션 layer SSOT 상속(P1).

배경 (R75 미수렴 — kpop-fan-translator 1심 P0 + 조니 2심 P0 확정):
  P0 (en): R75 ja 본문은 고유명사 한글 원문 병기 land(잠실/송파/강남/몽촌토성…) 했으나,
    en 본문 transit/area prose 는 한글 0 잔존. 라이브 grep — Olympic Park(Latin 26/한글 0)·
    Gangnam(11/0)·Songpa(5/0)·Mongchontoseong(9/0)·길안내 station명 Olympic Park Station(3)·
    Mongchontoseong Station(1)·Olympic Park Stn(6)·Mongchontoseong Stn(7) 전부 한글 0.
    verbatim: 'Olympic Park Station (Lines 5 & 9) / Mongchontoseong Station (Line 8).' ·
    'From Jamsil: 1 stop on Subway Line 8 (to Mongchontoseong Stn)'.
    대표 정책(REQ-BYBIAS-20260615-001): "en도 원문-우선·원문 누락=P0·관광객이 한글 표지판과
    눈으로 대조". 영어권 관광객은 한글 역명을 못 읽어 원문 대조가 ja 독자보다 더 절실.
    + en 카드 aria-label 역순(Latin(한글)) 정정: 'Bongpiyang Bangi (봉피양)' → '봉피양(Bongpiyang Bangi)'.

  P1 (ja): R75 본문은 표기 단일화됐으나 IG 해시태그/숙소 access 캡션에 변종 잔존.
    본문 ソクチョノス(4)↔캡션 セクチョン湖(4) / 본문 ソンリダンギル(2)↔캡션 ソングリダンギル /
    숙소 access チャムシル(4·한글 잠실 원문 0·ジャムシル↔チャ 2읽기). 본문 SSOT 상속 → 화면당 1읽기.
    ⚠ R75 패치는 해시태그(#セクチョン湖グルメ)를 "SNS 키워드 → 유지" 로 PROTECT 했으나,
    R76 verdict(kpop+조니 양 패널)는 캡션 변종을 결함으로 명시 정정 지시 → R76 instruction 우선.

en 정책 (R74/R75 ja 정합): '{ko원문}({로마자})'. 한글 원문 prefix + 괄호(로마자).
  scope = R75 ja fix 가 ja 본문에 병기한 14 지명 집합과 동일(원문 누락=P0 정책 보편 적용):
    올림픽공원·잠실·석촌호수·송리단길·강남·송파·몽촌토성·성수·명동·경복궁·홍대·방이·성내·천호.
  out-of-scope(ja fix 도 미병기·verdict 미측정 → en 도 Latin 유지): Inwangsan·Apgujeong·
    Namsan·KSPO Dome·Peace Gate·Cheonho(ja=0). over-translation = 거짓 P0 회피.

전략 (R75 검증 엔진 verbatim 차용 — tools/r75_course_pname_patch.py):
  - 2-phase NUL sentinel 치환. longest-first(괄호/합성어/Station/Stn 이 bare 보다 먼저 매칭)
    → cross-variant 오염 + GangnamDol/Songpanaru/Banghwa 등 superstring 오염 구조적 차단.
  - 멱등: 이미 적용된 final 들 + 보호 합성어 사전 sentinel 잠금. 재실행 0 변경.
  - 카드 .pname/.sname/.ptag/.crs-tag + aria-label inner content 동적 보호 잠금
    (산문 bare 토큰이 카드/속성 안 토큰을 못 건드림).

재현성 부채 (R75 동일): dist 직접 치환. byvias_course_i18n.py(ko 마스터 번역 파이프라인)는
  ASCII 고유명사를 skip(_NO_TRANS_RE) → 한글 병기 미생성. ko 마스터(dist/twice-thisisfor-seoul.html)
  에 dual-notation source 없음 → SoT 경유 재생성 시 R74+R75+R76 병기 전부 소실.
  ∴ R75 동형 dist 직접 패치. i18n.py 정본화(옵션2)는 후행 별 트랙. lead 보고에 divergence 명시.

게이트 (FLR-AGT-002 거짓 충실성 — 선언 아닌 실측 grep):
  - en: 14 지명 한글 원문 present(>0) · aria-label 역순(Latin(한글)) 0 · raw 키({{}}/undefined/
    NaN/[object) 0 · 카드 .pname 무손상 · 보호 합성어(GangnamDol/Songpanaru) 무손상.
  - ja: 캡션 변종(セクチョン湖·ソングリダンギル·チャムシル) 0 · 본문 SSOT 회귀 0 · 카드 무손상.
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
# 보호 합성어 (지명 아님 / 별개 역명 / 숙소 고유명). 사전 sentinel 잠금 → 치환 격리.
#   longest-first 로 잠그면 bare 토큰 규칙이 이 superstring 을 못 건드림.
# ──────────────────────────────────────────────────────────────────────────
PROTECT_TOKENS: dict[str, list[str]] = {
    "en": [
        # 강남돌 합성 브랜드 (K-STAR ROAD 아트토이 — 지명 아님). en 실측 = 하이픈 無 'GangnamDol'.
        "GangnamDol Haus by Galleria",
        "GangnamDol Haus",
        "GangnamDol",
        # 송파나루역 = 송파(松坡)와 별개 역명 → bare 'Songpa' 치환서 격리.
        "Songpanaru Station",
        "Songpanaru",
        # 별개 역명/지명 (bare 'Bangi' superstring 오염 차단 — Banghwa 는 방화역, 방이 아님).
        "Banghwa",
        # 숙소 고유명(영문) — 지명 아님. bare 토큰 치환서 격리.
        "Seoul Olympic Parktel",
        "Olympic Parktel",
        # 올림픽공원 인접 랜드마크 (verdict 미측정·ja fix 미병기 → Latin 유지·bare 'Olympic Park'
        #   치환서 격리). 'Olympic Park Peace Gate' / 'Olympic Park / KSPO Dome'.
        "Olympic Park Peace Gate",
        "Olympic Park / KSPO Dome",
    ],
    "ja": [
        # 해시태그 합성어 — グルメ 접미 유지(검색 키워드 형태). 단 セクチョン/ソングリ 변종 음은
        #   본문 SSOT 로 교정해야 하므로 PROTECT 가 아니라 VARIANTS 에서 처리(아래).
        #   별개 역명 보호.
        "Songpanaru Station (ソンパナル駅)",
        "Songpanaru",
    ],
}

# ──────────────────────────────────────────────────────────────────────────
# en 본문 산문 변종 → '{ko원문}({로마자})'. longest-first 는 코드서 자동 정렬.
#   현 토큰(en 실측 철자) → 최종. Station/Stn 변종 각각 명시(누락 방지).
# ──────────────────────────────────────────────────────────────────────────
EN_BODY_VARIANTS: list[tuple[str, str]] = [
    # ── 올림픽공원 (Station/Stn/area/bare). PROTECT(Peace Gate·KSPO·Parktel) 격리됨 ──
    ("Olympic Park Station", "올림픽공원역(Olympic Park Station)"),
    ("Olympic Park Stn", "올림픽공원역(Olympic Park Stn)"),
    ("Olympic Park area", "올림픽공원(Olympic Park) area"),
    ("Olympic Park", "올림픽공원(Olympic Park)"),
    # ── 몽촌토성 (Station/Stn/bare) ──
    ("Mongchontoseong Station", "몽촌토성역(Mongchontoseong Station)"),
    ("Mongchontoseong Stn", "몽촌토성역(Mongchontoseong Stn)"),
    ("Mongchontoseong", "몽촌토성(Mongchontoseong)"),
    # ── 석촌호수 (Lake — longest-first 로 'Seokchon' bare 보다 먼저) ──
    ("Seokchon Lake", "석촌호수(Seokchon Lake)"),
    ("Seokchon", "석촌호수(Seokchon)"),
    # ── 송리단길 (en 실측 = Songnidan-gil 4 + Songridan-gil 12 두 철자 혼재) ──
    ("Songnidan-gil", "송리단길(Songnidan-gil)"),
    ("Songridan-gil", "송리단길(Songridan-gil)"),
    # ── 송파(구) — Songpa-gu longest-first. 'Songpanaru' 는 PROTECT 격리 ──
    ("Songpa-gu", "송파구(Songpa-gu)"),
    ("Songpa", "송파(Songpa)"),
    # ── 강남 — 'GangnamDol*' 합성 브랜드는 PROTECT 격리됨 ──
    ("Gangnam", "강남(Gangnam)"),
    # ── 잠실 — 숙소 고유명/카드는 동적 보호 격리. bare 'Jamsil' 본문만 ──
    ("Jamsil", "잠실(Jamsil)"),
    # ── 성수 — Yeonmujang-gil 등 합성은 카드 보호. bare 'Seongsu' 본문 ──
    ("Seongsu", "성수(Seongsu)"),
    # ── 명동 ──
    ("Myeongdong", "명동(Myeongdong)"),
    # ── 경복궁 ──
    ("Gyeongbokgung", "경복궁(Gyeongbokgung)"),
    # ── 홍대 ──
    ("Hongdae", "홍대(Hongdae)"),
    # ── 방이(동) — 'Banghwa' 는 PROTECT 격리. Bangi-dong longest-first ──
    ("Bangi-dong", "방이동(Bangi-dong)"),
    ("Bangi", "방이(Bangi)"),
    # ── 성내 ──
    ("Seongnae", "성내(Seongnae)"),
]

# en 카드 aria-label 역순(Latin(한글)) → 원문우선(한글(Latin)) 정정.
#   카드 .pname 은 이미 원문우선('봉피양 방이점(Bongpiyang Bangi)')이라 aria-label 만 역순.
#   고정 enumerable set → 직접 치환(엔진 외). longest-first 불요(상호 superstring 아님).
EN_ARIA_REVERSE: list[tuple[str, str]] = [
    ('aria-label="Bongpiyang Bangi (봉피양)"', 'aria-label="봉피양(Bongpiyang Bangi)"'),
    (
        'aria-label="Somunnan Seongsu Gamjatang (소문난성수감자탕)"',
        'aria-label="소문난성수감자탕(Somunnan Seongsu Gamjatang)"',
    ),
    ('aria-label="Onion Seongsu (어니언)"', 'aria-label="어니언(Onion Seongsu)"'),
    (
        'aria-label="Myeongdong Kyoja (명동교자)"',
        'aria-label="명동교자(Myeongdong Kyoja)"',
    ),
    ('aria-label="Hadongkwan (하동관)"', 'aria-label="하동관(Hadongkwan)"'),
    (
        'aria-label="London Bagel Museum Jamsil (런던베이글뮤지엄)"',
        'aria-label="런던베이글뮤지엄(London Bagel Museum Jamsil)"',
    ),
]

# ──────────────────────────────────────────────────────────────────────────
# ja 캡션 layer 변종 → 본문 SSOT. (현 캡션 토큰, 본문 SSOT final). longest-first 자동.
#   해시태그(#…グルメ)는 グルメ 접미 유지하되 음 표기를 본문 SSOT 로 교정(화면당 1읽기).
# ──────────────────────────────────────────────────────────────────────────
JA_CAPTION_VARIANTS: list[tuple[str, str]] = [
    # ⚠ 해시태그(#…) vs 일반 캡션 분기. 해시태그는 음 표기만 본문 reading 으로 교정(괄호/공백
    #   금지 — Instagram 검색 토큰 유효성 유지). 일반 캡션은 본문 full dual-notation 적용.
    #   longest-first: '#…グルメ' 가 'セクチョン湖グルメ'(label) 보다 먼저 매칭되도록 코드 자동 정렬.
    # ── 석촌호수: 해시태그 #セクチョン湖グルメ → #ソクチョノスグルメ(reading만), 일반 → full ──
    ("#セクチョン湖グルメ", "#ソクチョノスグルメ"),
    ("セクチョン湖グルメ", "석촌호수(石村湖 / ソクチョノス)グルメ"),
    ("セクチョン湖ビュー", "석촌호수(石村湖 / ソクチョノス)ビュー"),
    ("セクチョン湖", "석촌호수(石村湖 / ソクチョノス)"),
    # ── 송리단길: 해시태그 #ソングリダンギルグルメ → #ソンリダンギルグルメ(reading만), 일반 → full ──
    ("#ソングリダンギルグルメ", "#ソンリダンギルグルメ"),
    ("ソングリダンギルグルメ", "송리단길(ソンリダンギル)グルメ"),
    ("ソングリダンギル", "송리단길(ソンリダンギル)"),
    # ── 잠실 access 캡션: チャムシル(駅/地区) → 본문 SSOT 蚕室+한글 원문 병기 (해시태그 無) ──
    ("チャムシル駅", "잠실역(蚕室駅 / ジャムシル)"),
    ("チャムシル地区", "잠실(蚕室 / ジャムシル)地区"),
    ("チャムシル", "잠실(蚕室 / ジャムシル)"),
]


def _two_phase_replace(
    html: str, variants: list[tuple[str, str]], protect: list[str]
) -> tuple[str, dict]:
    """R75 검증 엔진: 멱등 final 잠금 + 보호 토큰 잠금 + longest-first 토큰 치환.

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
    # 2) 보호 토큰 잠금 (합성어/별개역명/숙소명)
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


def _protect_intact(before: str, after: str, protect: list[str]) -> list[str]:
    """보호 토큰 출현수 보존 검증."""
    broken = []
    for p in protect:
        if before.count(p) != after.count(p):
            broken.append(f"{p}: {before.count(p)}→{after.count(p)}")
    return broken


def apply_en(html: str) -> tuple[str, dict, dict]:
    # 카드/속성 콘텐츠 동적 보호 — R74/R75 가 카드 .pname/aria-label 에 박은 원문병기
    #   (예 '고도식 잠실점(Godosik Jamsil)' 내부 'Jamsil')를 산문 bare 토큰 치환서 격리.
    card_protect = list(PROTECT_TOKENS["en"])
    for cls in ("pname", "sname", "ptag", "crs-tag"):
        for m in re.finditer(rf'class="{cls}">(.*?)</', html, flags=re.DOTALL):
            inner = m.group(1)
            if inner and inner not in card_protect:
                card_protect.append(inner)
    # aria-label 속성 값 전체를 보호(산문 bare 토큰 침범 차단). 역순 정정은 별도 단계.
    for m in re.finditer(r'aria-label="([^"]*)"', html):
        inner = m.group(1)
        if inner and inner not in card_protect:
            card_protect.append(inner)

    html, c_prose = _two_phase_replace(html, EN_BODY_VARIANTS, card_protect)

    # aria-label 역순 정정 (보호로 잠겼던 원본 → 원문우선 형태로 직접 치환)
    c_aria: dict[str, int] = {}
    for old, new in EN_ARIA_REVERSE:
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            c_aria[old] = n
    return html, c_prose, c_aria


def apply_ja(html: str) -> tuple[str, dict]:
    card_protect = list(PROTECT_TOKENS["ja"])
    for cls in ("pname", "sname", "ptag", "crs-tag"):
        for m in re.finditer(rf'class="{cls}">(.*?)</', html, flags=re.DOTALL):
            inner = m.group(1)
            if inner and inner not in card_protect:
                card_protect.append(inner)
    html, c_cap = _two_phase_replace(html, JA_CAPTION_VARIANTS, card_protect)
    return html, c_cap


def run(lang: str, write: bool) -> bool:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")
    pnames_before = re.findall(r'class="pname">(.*?)</div>', orig, flags=re.DOTALL)

    if lang == "en":
        html, c_prose, c_aria = apply_en(orig)
    else:
        html, c_cap = apply_ja(orig)
        c_prose, c_aria = c_cap, {}

    # 게이트: 보호 토큰 무손상
    broken = _protect_intact(orig, html, PROTECT_TOKENS[lang])
    if broken:
        print(f"ABORT [{lang}]: 보호 토큰 손상 — {broken}")
        return False
    # 게이트: 카드 .pname 무손상
    pnames_after = re.findall(r'class="pname">(.*?)</div>', html, flags=re.DOTALL)
    if pnames_before != pnames_after:
        diff = [
            (pnames_before[i], pnames_after[i])
            for i in range(min(len(pnames_before), len(pnames_after)))
            if pnames_before[i] != pnames_after[i]
        ]
        print(f"ABORT [{lang}]: 카드 .pname 손상 {len(diff)}건 — {diff[:3]}")
        return False

    changed = html != orig
    if changed and write:
        path.write_text(html, encoding="utf-8")

    label = "산문 병기" if lang == "en" else "캡션 SSOT"
    print(
        f"=== [{lang}] {path.name} ({'WROTE' if (changed and write) else 'DRY' if not write else '변경없음'}) ==="
    )
    print(f"  {label}: {sum(c_prose.values())}건 ({len(c_prose)} 토큰종)")
    for tok, n in sorted(c_prose.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    if lang == "en":
        print(f"  aria-label 역순 정정: {sum(c_aria.values())}건")
        for tok, n in c_aria.items():
            print(f"      {tok[:40]}… ×{n}")
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
    print(f"\nOK: R76 en 산문 P0 + ja 캡션 P1 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
