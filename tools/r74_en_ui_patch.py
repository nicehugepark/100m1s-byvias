#!/usr/bin/env python3
"""R74 en index/코스 UI 산문 한글 → 영어화 (고유명사 아님 · LLM 미경유 사전 치환).

대표 catch(2026-06-15 13:28): "영어 페이지도 한글이 그대로 노출중."
en index의 동적 JS 텍스트·HTML 속성(placeholder/aria-label/alt)·empty state·단위 등이
한글 잔존(ja는 R64~R67서 일본어화 완료·en 누락 = zh 누락과 동형). 목표 = en 가시 한글 0
(단 고유명사 한국어 원문은 정책상 유지 — 음악쇼명 '뮤직뱅크(Music Bank)' 등은 보존).

번역 SSOT = ja index 동일 위치(R64~R67 검증). 동일 키를 en으로.
대상: dist/en/index.html (+ 코스 UI 잔여 있으면 dist/en/twice-thisisfor-seoul.html).

추가 교정(correctness): en COUNTRIES 배열이 한글 키('대한민국'…)인데 en 카드 .c는 영문
('South Korea'…) → indexOf 매칭 0 = 나라칩 필터 무용(latent bug). 영문 키로 교정.

게이트: en index 가시 UI 한글 0 (음악쇼/이벤트 고유명사 '원문(번역)'·언어스위처 endonym
'한국어' 제외). 멱등(이미 영문이면 skip). 치환 실패 시 보고만(거짓 PASS 0).

FLR 참조: FLR-AGT-002.
"""

from __future__ import annotations

from pathlib import Path

WT = Path(__file__).parent.parent
EN_IDX = WT / "dist/en/index.html"

# ──────────────────────────────────────────────────────────────────────────
# UI 문자열 치환 (정확 문자열 → 영어). ja 동일 위치 번역과 정합.
#   verbatim 단위로 치환(부분 토큰 금지) → 오염 방지.
# ──────────────────────────────────────────────────────────────────────────
UI: dict[str, str] = {
    # ── HTML 속성 (placeholder/aria-label/alt) ──
    'placeholder="아티스트 · 나라 · 도시 검색"': 'placeholder="Search artist · country · city"',
    'aria-label="아티스트·나라·도시로 일정 검색"': 'aria-label="Search schedules by artist, country, city"',
    'aria-label="검색어 지우기"': 'aria-label="Clear search"',
    'aria-label="나라별 거르기"': 'aria-label="Filter by country"',
    'aria-label="가장 임박한 일정"': 'aria-label="Most imminent schedule"',
    'aria-label="다가오는 14일"': 'aria-label="Next 14 days"',
    'aria-label="이 가이드 공유하기"': 'aria-label="Share this guide"',
    'aria-label="ByVias 소개"': 'aria-label="About ByVias"',
    'alt="공연장 무드"': 'alt="Concert venue mood"',
    # ── 정적 hero eyebrow (가시 기본 라벨) ──
    '<span class="hs-eye">가장 임박한 일정</span>': '<span class="hs-eye">Most imminent schedule</span>',
    # ── 동적 JS 문자열 ──
    "'+'다가오는 14일'+'": "'+'Next 14 days'+'",
    '<span class="live-cta">오늘 공연 · 상세 보기 ›</span>': (
        '<span class="live-cta">Live today · See details ›</span>'
    ),
    # empty state (검색 결과 없음)
    "검색·필터에 맞는 일정이 없어요.<br><b>다른 나라</b>를 골라보거나 검색어를 지워보세요.": (
        "No schedules match your search.<br>Try <b>another country</b> or clear your search."
    ),
    # 단위·라벨
    "var unit='건'": "var unit='results'",
    "+'</b>개'": "+'</b>'",  # '<b>N</b>개' → '<b>N</b>' (en은 단위 생략·자연)
    "var label=activeCountry||'검색'": "var label=activeCountry||'Search'",
    # 칩 '전체'
    "makeChip('전체','',null)": "makeChip('All','',null)",
    # toast (공유)
    "toast('링크가 복사됐어요')": "toast('Link copied')",
    "toast('주소: '+url)": "toast('URL: '+url)",
    # ── TKO 티켓팅 상태 (티켓 바·hero eyebrow 동적) ──
    '"e0": "오늘 티켓팅 오픈"': '"e0": "Ticket sale today"',
    '"e1": "티켓팅 오픈 임박"': '"e1": "Ticket sale soon"',
    '"e2": "티켓팅 오픈 중"': '"e2": "On sale now"',
    "🇰🇷 대한민국 서울 · ": "🇰🇷 Seoul, South Korea · ",
    # ── 이벤트/쇼명 title (고유명사) — 영문 병기 없는 4개에 읽는법 괄호 추가(원문 보존).
    #    정책: 원문(번역). 음악쇼명(뮤직뱅크 (Music Bank))은 이미 병기 → 유지.
    'title="대한민국 대표팀"': 'title="대한민국 대표팀(Team Korea)"',
    'title="서울 라이브아이돌 페스티벌"': 'title="서울 라이브아이돌 페스티벌(Seoul Live Idol Festival)"',
    'title="라이브아이돌 합동공연 (2026-06-10)"': (
        'title="라이브아이돌 합동공연(Live Idol Joint Concert) (2026-06-10)"'
    ),
    'title="주간 아이돌 점프 vol.19"': 'title="주간 아이돌 점프(Weekly Idol Jump) vol.19"',
}

# ──────────────────────────────────────────────────────────────────────────
# COUNTRIES 필터 교정: 한글 키 배열 → 영문(en 카드 .c 와 매칭). COUNTRY_LABELS 불요
#   (라벨=키=영문). ja는 한글키+COUNTRY_LABELS였으나 en은 카드가 영문이므로 영문키 직결.
# ──────────────────────────────────────────────────────────────────────────
COUNTRIES_KO = (
    "var COUNTRIES=['대한민국','일본','대만','미국','싱가포르','홍콩','태국','영국',"
    "'멕시코','마카오','필리핀','인도네시아','독일','중국','베트남','캐나다','호주','말레이시아']"
)
COUNTRIES_EN = (
    "var COUNTRIES=['South Korea','Japan','Taiwan','United States','Singapore',"
    "'Hong Kong','Thailand','United Kingdom','Mexico','Macau','Philippines',"
    "'Indonesia','Germany','China','Vietnam','Canada','Australia','Malaysia']"
)


def apply_ui(path: Path):
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return None
    html = path.read_text(encoding="utf-8")
    orig = html
    applied, missing = [], []

    for ko, en in UI.items():
        if ko in html:
            html = html.replace(ko, en)
            applied.append(ko[:40])
        elif en not in html:
            missing.append(ko[:40])

    # COUNTRIES 교정
    cc = "skip"
    if COUNTRIES_KO in html:
        html = html.replace(COUNTRIES_KO, COUNTRIES_EN)
        cc = "fixed"
    elif COUNTRIES_EN in html:
        cc = "already"

    if html != orig:
        path.write_text(html, encoding="utf-8")
    print(f"=== [en UI] {path.name} ===")
    print(f"  UI 치환: {len(applied)}건 / 미발견(이미 영문 추정): {len(missing)}건")
    print(f"  COUNTRIES 필터: {cc}")
    if missing:
        for m in missing:
            print(f"    · 미발견: {m}")
    return {"applied": len(applied), "missing": missing, "countries": cc}


def main():
    apply_ui(EN_IDX)


if __name__ == "__main__":
    main()
