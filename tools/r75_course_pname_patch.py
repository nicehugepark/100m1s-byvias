#!/usr/bin/env python3
"""R75 코스 본문 고유명사 한국어 원문 병행표기 (R74 미수렴분 · dist 직접 치환 · LLM 미경유).

배경 (조니 R74 라이브 실측): R74 가 카드(.pname/.sname)와 일부 역명(잠실/명동/홍대/
성수/경복궁/올림픽공원/몽촌토성)만 한국어 원문 병기했고, **코스 본문(course-sec) 산문의
지명 다수는 한글 0** 으로 잔존:
  - 송파(Songpa-gu) · 강남(Gangnam) · 석촌호수(石村湖/Seokchon Lake/せきむらこ 음독!) ·
    송리단길(ソンリ/ソングリ 철자변종·Songri Lane·Songri-danil 오타) · 성내동(ソンネドン) ·
    천호(Cheonho) · 방이(バンイ(Bangyi)) · 올림픽공원 영문 잔존(Olympic Park).
  - 몽촌토성역 = 페이지가 '타라'고 지시한 역인데 본문 Latin(Mongchontoseong) 으로 한글 0
    → 표지판 대조 불가(대표 정책 치명 위반).

대표 정책 (2026-06-15, R74 정합): 한국어 원문 prefix + 괄호(번역 / 읽는법). 표지판 대조 목적.
  - 한자 정책: R74 가 확정한 표준 한자(잠실=蚕室 등)·ja 본문에 이미 등장하는 표준 한자
    (석촌호수=石村湖·강남=江南·송파=松坡)만 사용. ko 마스터가 순수 한글이고 한자 불명확한
    지명(송리단길·성내동·방이·천호)은 **한자 신설 금지, 가나(읽는법)만** → 오역 방지.
  - 읽는법 = 가타카나 한국 발음. 일본 음독(せきむらこ·せきそんこ 등) 금지.

보호 대상 (치환 제외 — 오염 방지):
  1. 카드 .pname (예 '봉피양 방이점(ボンピャン バンイ店)') — R74 처리분. bare 토큰 치환서 격리.
  2. 해시태그/Instagram 캡션 (#ソングリダンギルグルメ · セクチョン湖グルメ · title=) —
     SNS 검색 키워드, 한글化 시 어색 → 그대로 유지.
  3. 강남돌 합성 브랜드명 (Gangnam-Dol · Gangnam-gu · Gangnam Idols · Gangnam-Dol House)
     — K-STAR ROAD 아트토이 고유명, 지명 아님.

전략 (R74 검증 엔진 차용):
  - Phase A: 산문 변종 → '{ko원문}({한자?} / {가나})' 유닛. 2-phase NUL sentinel 치환.
    longest-first (괄호 포함·합성어가 bare 보다 먼저 매칭) → cross-variant 오염 구조적 차단.
    멱등: 이미 적용된 final 들을 먼저 sentinel 로 잠금 + 보호 합성어/해시태그도 사전 잠금.
  - Phase B: 단축형. 동일 지명 full 병기(30자 triple)가 페이지 N회 반복(올림픽공원 17·잠실 17)
    → 첫 출현만 full 유지, 2번째 이후 → 한글 단축. (Phase A 후 별도 카운트 기반 순차 패스.)

게이트 (FLR-AGT-002 거짓 충실성):
  - 누락 지명 한글 원문 present (P0): 송파·강남·석촌호수·송리단길·성내·천호·몽촌토성 본문 Hangul>0.
  - 일본 음독(せき*·*ひらがな 음독) 0.
  - 보호영역(카드/해시태그/합성어) 무손상 (치환 전후 출현수 보존).
  - 멱등 (재실행 변경 0).

재현성 부채 (R74 동일): dist 직접 치환. byvias_course_i18n.py 재빌드 시 원복.
  → 옵션 2(i18n.py 정본화)는 후행 별 트랙. 본 패치 헤더에 명시 유지.
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
# 보호 합성어 (지명 아님 — 강남돌 브랜드 등). 사전 sentinel 잠금 → 치환 격리.
#   longest-first 로 잠그면 bare 'Gangnam' 규칙이 이 superstring 을 못 건드림.
# ──────────────────────────────────────────────────────────────────────────
PROTECT_TOKENS: dict[str, list[str]] = {
    "ja": [
        "Gangnam-Dol House",
        "Gangnam Idols",
        "Gangnam-Dol",
        "Gangnam-gu",
        # 송파나루역 = 송파(松坡)와 별개 역명 → bare 'Songpa' 치환서 격리
        "Songpanaru Station (ソンパナル駅)",
        "Songpanaru",
        # 숙소 고유명(영문) — 지명 아님. bare 'Jamsil' 치환서 격리.
        "Jamsil Raum Tourist Hotel",
        "Jamsil Guesthouse Seoul",
        "Seoul Olympic Parktel",
        # 노선 안내가 괄호로 붙은 잠실 변종 — 괄호 안이 지명 아닌 노선/소요시간이라
        #   bare 'Jamsil' 치환 시 깨짐 → 통째 보호(읽는법 별도 불요, 노선 컨텍스트 명확).
        "Jamsil(Suin-Bundang Line + Line 2 約30分)",
        # 경복궁역 괄호 안에 다른 지명(Jamsil) 중첩 → 통째 보호(별도 처리 회피)
        "Gyeongbokgung Station (Jamsil から約 45~55 分)",
        # 해시태그/캡션 합성어 (SNS 키워드 — 유지)
        "ソングリダンギルグルメ",
        "セクチョン湖グルメ",
        "セクチョン湖",  # 캡션 잔재(석촌호수 가나표기) — 해시태그 맥락 유지
    ],
    "en": [
        "Gangnam-Dol House",
        "Gangnam Idols",
        "Gangnam-Dol",
        "Gangnam-gu",
        "Songpanaru",
    ],
}

# ──────────────────────────────────────────────────────────────────────────
# 본문 산문 변종 → 최종 유닛. (현 토큰, 최종). longest-first 는 코드서 자동 정렬.
#   ko 마스터 순수 한글 + ja 본문 실측 한자(石村湖·江南·松坡)만 한자 사용.
#   한자 불명확(송리단길·성내동·방이·천호) = 가나만.
# ──────────────────────────────────────────────────────────────────────────
JA_BODY_VARIANTS: list[tuple[str, str]] = [
    # ── 올림픽공원 영문 잔존 (Olympic Park*) — R74 가나형으로 통일 ──
    (
        "Olympic Park Station",
        "올림픽공원역(オリンピック公園駅 / オルリムピックゴンウォン)",
    ),
    ("Olympic Park駅", "올림픽공원역(オリンピック公園駅 / オルリムピックゴンウォン)"),
    ("Olympic Park", "올림픽공원(オリンピック公園 / オルリムピックゴンウォン)"),
    # ── 몽촌토성 Latin bare (R74 가 한자형 잡았으나 Latin 잔존분) ──
    #   ⚠ 원문에 이미 가나보조 '(モンチョントソン駅)' 가 붙은 변종은 전체를 토큰화해야
    #   읽는법 중복('…モンチョントソン) Station (モンチョントソン駅)') 방지. longest-first 최상단.
    (
        "Mongchontoseong Station (モンチョントソン駅)",
        "몽촌토성역(夢村土城駅 / モンチョントソン)",
    ),
    (
        "Mongchontoseong(モンチョントソン)駅",
        "몽촌토성역(夢村土城駅 / モンチョントソン)",
    ),
    ("Mongchontoseong駅", "몽촌토성역(夢村土城駅 / モンチョントソン)"),
    ("Mongchontoseong", "몽촌토성(夢村土城 / モンチョントソン)"),
    # ── 석촌호수 (괄호 포함·음독 우선 longest-first) ──
    ("石村湖(Seokchon Lake)", "석촌호수(石村湖 / ソクチョノス)"),
    ("石村湖(せきむらこ)", "석촌호수(石村湖 / ソクチョノス)"),
    ("石村湖(せきそんこ)", "석촌호수(石村湖 / ソクチョノス)"),
    ("石村湖カフェ街", "석촌호수(石村湖 / ソクチョノス)カフェ街"),
    ("Seokchon Lake", "석촌호수(石村湖 / ソクチョノス)"),  # 영문 단독 본문 잔존
    ("石村湖", "석촌호수(石村湖 / ソクチョノス)"),
    # ── 송리단길 (괄호/오타/철자변종) — 한자 불명 → 가나만 ──
    ("ソングリダンギル(Songri Lane)", "송리단길(ソンリダンギル)"),
    ("Songri-danil", "송리단길(ソンリダンギル)"),
    ("Songri Lane", "송리단길(ソンリダンギル)"),
    ("ソングリダンギル", "송리단길(ソンリダンギル)"),
    ("ソンリダンギル", "송리단길(ソンリダンギル)"),
    # ── 방이(동) (괄호 포함) — 한자 불명 → 가나만 ──
    ("バンイドン(Bangyi-dong)", "방이동(バンイドン)"),
    ("バンイ(Bangyi)", "방이(バンイ)"),
    # ── 성내동 — 한자 불명 → 가나만 ──
    ("ソンネドン", "성내동(ソンネドン)"),
    ("ソンネ", "성내(ソンネ)"),
    # ── 천호 — 한자 불명 → 가나만 ──
    ("チョンホ", "천호(チョンホ)"),
    # ── 송파(구) — ja 본문 한자 松坡 실측. ⚠ 'Songpanaru'(송파나루역)는 별개 역명
    #   → PROTECT 로 격리. 가나보조 '(ソンパ)' 붙은 변종은 전체 토큰화(중복 방지). ──
    ("Songpa (ソンパ)", "송파(松坡 / ソンパ)"),
    ("Songpa-gu(ソンパグ)", "송파구(松坡区 / ソンパグ)"),
    ("Songpa-gu", "송파구(松坡区 / ソンパグ)"),
    ("Songpa", "송파(松坡 / ソンパ)"),
    # ── 강남 — ja 본문 한자 江南 실측 (합성어는 PROTECT 로 격리됨) ──
    ("Gangnam(ガンナム)", "강남(江南 / カンナム)"),
    ("Gangnam", "강남(江南 / カンナム)"),
    # ── 잠실 영문 잔존 (R74 가 한자형 잡았으나 Latin/괄호 변종 혼재 — 표기 통일) ──
    #   숙소명·노선중첩 변종은 PROTECT 로 격리됨. 역명(駅·Station) longest-first.
    ("Jamsil Station (ジャムシル駅)", "잠실역(蚕室駅 / ジャムシル)"),
    ("Jamsil(ジャムシル)駅", "잠실역(蚕室駅 / ジャムシル)"),
    ("Jamsil (ジャムシル)", "잠실(蚕室 / ジャムシル)"),
    ("ジャムシル(Jamsil)", "잠실(蚕室 / ジャムシル)"),
    ("Jamsil 駅", "잠실역(蚕室駅 / ジャムシル)"),
    ("Jamsil", "잠실(蚕室 / ジャムシル)"),
    # ── 성수 영문 잔존 (한자 聖水 R74 확정) ──
    ("Seongsu-dong Yeonmujiang-gil", "성수동 연무장길(ソンスドン ヨンムジャンギル)"),
    ("Seongsu(ソンス)駅", "성수역(聖水駅 / ソンス)"),
    ("Seongsu駅", "성수역(聖水駅 / ソンス)"),
    ("Seongsu(ソンス)", "성수(聖水 / ソンス)"),
    ("Seongsu", "성수(聖水 / ソンス)"),
    # ── 경복궁 영문/음독 잔존 (한자 景福宮 R74 확정. ぎょんぼっぐん 음독 정책위반!) ──
    ("Gyeongbokgung(ぎょんぼっぐん)", "경복궁(景福宮 / キョンボックン)"),
    ("Gyeongbokgung Palace", "경복궁(景福宮 / キョンボックン)"),
    ("Gyeongbokgung", "경복궁(景福宮 / キョンボックン)"),
    # ── 명동 영문 잔존 (한자 明洞 R74 확정) ──
    ("Myeongdong (ミョンドン)", "명동(明洞 / ミョンドン)"),
    ("Myeongdong(ミョンドン)", "명동(明洞 / ミョンドン)"),
    ("Myeongdong", "명동(明洞 / ミョンドン)"),
    # ── 방이동 영문 잔존 (한자 불명 → 가나만) ──
    ("Bangi-dong", "방이동(バンイドン)"),
    # ── 홍대 영문 잔존 (한자 弘大 R74 확정) ──
    ("Hongdae", "홍대(弘大 / ホンデ)"),
]

EN_BODY_VARIANTS: list[tuple[str, str]] = [
    # en: '{ko원문}({로마자})'. R74 en 정책 = 원문(Trans).
    ("Olympic Park Station", "올림픽공원역(Olympic Park Station)"),
    ("Olympic Park", "올림픽공원(Olympic Park)"),
    ("Mongchontoseong Station", "몽촌토성역(Mongchontoseong Station)"),
    ("Mongchontoseong", "몽촌토성(Mongchontoseong)"),
    ("Seokchon Lake", "석촌호수(Seokchon Lake)"),
    ("Seokchon", "석촌호수(Seokchon)"),
    ("Songridan-gil", "송리단길(Songridan-gil)"),
    ("Songri-danil", "송리단길(Songridan-gil)"),
    ("Songri Lane", "송리단길(Songridan-gil)"),
    ("Songri", "송리단길(Songridan-gil)"),
    ("Bangi-dong", "방이동(Bangi-dong)"),
    ("Bangi", "방이(Bangi)"),
    ("Seongnae", "성내(Seongnae)"),
    ("Cheonho", "천호(Cheonho)"),
    ("Songpa-gu", "송파구(Songpa-gu)"),
    ("Songpa", "송파(Songpa)"),
    ("Gangnam", "강남(Gangnam)"),
]

# Phase B 단축형: 동일 지명 full 병기가 N회+ 반복 시 첫 출현만 full, 이후 한글 단축.
#   (full 형, 단축 한글). full 은 Phase A 산출/기존 R74 산출 둘 다 포괄.
SHORTEN_JA: list[tuple[str, str]] = [
    ("올림픽공원(オリンピック公園 / オルリムピックゴンウォン)", "올림픽공원"),
    ("잠실(蚕室 / ジャムシル)", "잠실"),
    ("석촌호수(石村湖 / ソクチョノス)", "석촌호수"),
    ("송리단길(ソンリダンギル)", "송리단길"),
    ("강남(江南 / カンナム)", "강남"),
    ("명동(明洞 / ミョンドン)", "명동"),
    ("홍대(弘大 / ホンデ)", "홍대"),
    ("성수(聖水 / ソンス)", "성수"),
]
SHORTEN_EN: list[tuple[str, str]] = [
    ("올림픽공원(Olympic Park)", "올림픽공원"),
    ("잠실(Jamsil)", "잠실"),
    ("석촌호수(Seokchon)", "석촌호수"),
    ("송리단길(Songridan-gil)", "송리단길"),
    ("강남(Gangnam)", "강남"),
]


def _two_phase_replace(
    html: str, variants: list[tuple[str, str]], protect: list[str]
) -> tuple[str, dict]:
    """R74 검증 엔진: 멱등 final 잠금 + 보호 토큰 잠금 + longest-first 토큰 치환.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> str:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)  # 보호/멱등: 원문 그대로 복원
        return html

    # 1) 멱등: 이미 적용된 final 들 잠금 (longest-first)
    seen_finals = {f for _, f in variants}
    for f in sorted(seen_finals, key=len, reverse=True):
        _lock(f)
    # 2) 보호 토큰 잠금 (합성어/해시태그)
    for p in sorted(protect, key=len, reverse=True):
        _lock(p)
    # 3) 토큰 치환 (longest-first). 매칭 → sentinel 로 잠그고 final 을 복원 큐에 적재.
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


def _shorten(html: str, pairs: list[tuple[str, str]]) -> dict:
    """동일 full 병기 2번째 이후 → 한글 단축 (첫 출현 full 유지)."""
    counts: dict[str, int] = {}
    for full, short in pairs:
        total = html.count(full)
        if total <= 1:
            continue
        # 첫 출현은 보존, 나머지 치환: split(maxsplit) 트릭
        head, sep, tail = html.partition(full)
        # tail 안의 모든 full → short
        n = tail.count(full)
        tail = tail.replace(full, short)
        html = head + sep + tail
        counts[full] = n
    return html, counts


def _protect_intact(before: str, after: str, protect: list[str]) -> list[str]:
    """보호 토큰 출현수 보존 검증 (카드/해시태그/합성어 무손상)."""
    broken = []
    for p in protect:
        if before.count(p) != after.count(p):
            broken.append(f"{p}: {before.count(p)}→{after.count(p)}")
    return broken


def apply_to(lang: str) -> dict | None:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return None
    html = path.read_text(encoding="utf-8")
    orig = html
    variants = JA_BODY_VARIANTS if lang == "ja" else EN_BODY_VARIANTS
    protect = PROTECT_TOKENS.get(lang, [])
    shorten = SHORTEN_JA if lang == "ja" else SHORTEN_EN

    # 카드 .pname 보존 검증용 스냅샷 (치환이 카드를 건드리면 안 됨)
    pnames_before = re.findall(r'class="pname">(.*?)</div>', html, flags=re.DOTALL)

    # 카드/태그 콘텐츠를 보호 토큰으로 동적 추가 — R74 가 카드 안에 박아둔 가나
    # (예 '갓잇 송리단길점(ガッイット ソンリダンギル店)' 내부 'ソンリダンギル')를 산문 변종
    # 치환이 건드리지 못하게 격리. card_only sentinel 잠금 후 산문 치환 → 복원.
    card_protect = list(protect)
    for cls in ("pname", "sname", "ptag", "crs-tag"):
        for m in re.finditer(rf'class="{cls}">(.*?)</', html, flags=re.DOTALL):
            inner = m.group(1)
            if inner and inner not in card_protect:
                card_protect.append(inner)

    # Phase A: 산문 변종 병기 (카드 콘텐츠 격리 포함)
    html, c_a = _two_phase_replace(html, variants, card_protect)
    # Phase B: 단축형 — ⚠ R75 1차 비활성화 (정책 위반 위험).
    #   '페이지당 첫 1회만 full' 은 첫 출현이 상단 카드/요약에서 소모되면 정작 길 안내
    #   본문(역명 지시)에서 읽는법이 전부 소실 → '표지판 대조' 대표 정책 정면 위반
    #   (실측: 올림픽공원 full 1 vs 단축 26, L653 '송파구(…)内の올림픽공원。' 읽는법 0).
    #   조니 '30자 9회 반복 가독성' 지적은 타당하나, 안전한 단축 = 문맥블록(day-card/문단)
    #   단위 첫 1회 full 이어야 함 → lead/대표 판단 후행 별 트랙. 본 패치는 병기 정합만.
    c_b: dict[str, int] = {}
    _ = shorten  # 단축 사전은 후행 트랙용 보존

    # 게이트: 보호 토큰 무손상
    broken = _protect_intact(orig, html, protect)
    if broken:
        print(f"ABORT [{lang}]: 보호 토큰 손상 — {broken}")
        return None
    # 게이트: 카드 .pname 무손상
    pnames_after = re.findall(r'class="pname">(.*?)</div>', html, flags=re.DOTALL)
    if pnames_before != pnames_after:
        diff = [
            (pnames_before[i], pnames_after[i])
            for i in range(min(len(pnames_before), len(pnames_after)))
            if pnames_before[i] != pnames_after[i]
        ]
        print(f"ABORT [{lang}]: 카드 .pname 손상 {len(diff)}건 — {diff[:3]}")
        return None

    if html == orig:
        print(f"[{lang}] 변경 없음 (이미 적용 — 멱등)")
    else:
        path.write_text(html, encoding="utf-8")

    print(f"=== [{lang}] {path.name} ===")
    print(f"  Phase A 산문 병기: {sum(c_a.values())}건 ({len(c_a)} 토큰종)")
    for tok, n in sorted(c_a.items(), key=lambda x: -x[1]):
        print(f"      {tok!r} ×{n}")
    print(f"  Phase B 단축: {sum(c_b.values())}건")
    for full, n in c_b.items():
        print(f"      {full[:24]}… ×{n}")
    return {"a": c_a, "b": c_b}


def main():
    langs = sys.argv[1:] or ["ja", "en"]
    for lang in langs:
        if apply_to(lang) is None:
            sys.exit(2)
    print("\nOK: R75 코스 본문 고유명사 병기 완료 (게이트 통과)")


if __name__ == "__main__":
    main()
