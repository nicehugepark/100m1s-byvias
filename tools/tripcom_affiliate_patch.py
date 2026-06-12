#!/usr/bin/env python3
"""Trip.com 어필리에이트 삽입 — TWICE Seoul 리치 페이지(ko·en).

대표 직접 가입 계정 (호텔 기본 7%·쿠키 30일). Allianceid=8661388 / SID=319326505 (실측 확보).
- 숙소: 각 stay 카드 ota-row 에 Trip.com 버튼 추가 — Seoul(city=274) 호텔 *목록* 딥링크.
  미검증 권역(zone) ID 날조 금지(FLR-20260408-TEC-001 동형) → 목록 진입 + 라벨 "검색" 정직 표기.
  기존 Agoda·Booking 특정 호텔 직링크는 불변(대체 금지).
- 항공: steps5(ICN 도착 안내) + lock-now 에 Trip.com Flights 일반형 — Skyscanner 병렬(대체 금지).
- 추적 태그 trip_sub1 = twice_seoul_{lang}_{surface}{pos} (소문자·언더스코어 일관 체계).
- URL 2종 모두 curl -L 200 + 파라미터 보존 실측 검증(2026-06-12).
멱등: 표면별 data-aff-vendor="Trip.com" 가드 — 2회 실행 diff 0.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ("ko", ROOT / "dist" / "twice-thisisfor-seoul.html"),
    ("en", ROOT / "dist" / "en" / "twice-thisisfor-seoul.html"),
]

ALLIANCE_ID = "8661388"
SID = "319326505"
EVENT = "twice-thisisfor-seoul"

PLANE_SVG = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="1.7" aria-hidden="true">'
    '<path d="M10.5 13.5 21 3M21 3l-6 18-3.5-7.5L4 10z"/></svg>'
)

OTA_LABEL = {"ko": "Trip.com 검색", "en": "Trip.com search"}
S5_LABEL = {"ko": "Trip.com 항공권 ↗", "en": "Trip.com flights ↗"}
PREP_NAME = {"ko": "항공", "en": "Flights"}
PREP_SUB = {
    "ko": "같은 노선도 채널 따라 가격이 달라요 — 트립닷컴에서 한 번 더 비교",
    "en": "The same route can price differently by channel — cross-check on Trip.com",
}
PREP_WHEN = {"ko": "빠를수록", "en": "Sooner the better"}


def _aff_qs(sub1: str) -> str:
    return f"Allianceid={ALLIANCE_ID}&amp;SID={SID}&amp;trip_sub1={sub1}"


def hotels_url(sub1: str) -> str:
    # lead 실측 검증 포맷 그대로 (Seoul city=274 목록) + trip_sub1
    return (
        "https://www.trip.com/hotels/list?city=274&amp;display=Seoul&amp;optionId=274"
        f"&amp;optionType=City&amp;optionName=Seoul&amp;{_aff_qs(sub1)}"
    )


def flights_url(sub1: str) -> str:
    return f"https://www.trip.com/flights/?{_aff_qs(sub1)}"


def patch_steps5(s: str, lang: str):
    """① 항공권 단계 — Skyscanner 비교 링크 옆 병렬 텍스트 링크."""
    if re.search(r'data-aff-surface="steps5" data-aff-vendor="Trip\.com"', s):
        return s, "skip"
    m = re.search(
        r'<a [^>]*data-aff-surface="steps5" data-aff-vendor="Skyscanner"[^>]*>[^<]*</a>',
        s,
    )
    if not m:
        return s, "MISS"
    lg = lang or "ko"
    link = (
        f' · <a href="{flights_url(f"twice_seoul_{lg}_steps5_flight")}"'
        ' rel="sponsored nofollow" target="_blank" data-aff="1"'
        ' data-aff-surface="steps5" data-aff-vendor="Trip.com"'
        f' data-aff-event="{EVENT}" data-aff-pos="1">{S5_LABEL[lg]}</a>'
    )
    return s[: m.end()] + link + s[m.end() :], "ok"


def patch_locknow(s: str, lang: str):
    """잠금 섹션 — Skyscanner prep-row 직후 Trip.com Flights prep-row 병렬.
    pos=6: lock-now pos 는 DOM 순서가 아닌 고정 슬롯 ID(기존 0~5 점유, Klook=3 이 KKday=4·5
    뒤 DOM 선례) — 기존 슬롯 재번호 금지(분석 연속성)."""
    if re.search(r'data-aff-surface="lock-now" data-aff-vendor="Trip\.com"', s):
        return s, "skip"
    m = re.search(
        r'<a class="prep-row"[^>]*data-aff-surface="lock-now" data-aff-vendor="Skyscanner"[^>]*>',
        s,
    )
    if not m:
        return s, "MISS"
    end = s.find("</a>", m.end())
    if end < 0:
        return s, "MISS"
    end += len("</a>")
    lg = lang or "ko"
    row = (
        f'\n  <a class="prep-row" href="{flights_url(f"twice_seoul_{lg}_lock_flight")}"'
        ' rel="sponsored nofollow" target="_blank" data-aff="1"'
        ' data-aff-surface="lock-now" data-aff-vendor="Trip.com"'
        f' data-aff-event="{EVENT}" data-aff-pos="6">\n'
        f'    <span class="prep-ico">{PLANE_SVG}</span>\n'
        f'    <span class="prep-main"><span class="prep-name">{PREP_NAME[lg]}'
        f' <small>· Trip.com</small></span><span class="prep-sub">{PREP_SUB[lg]}</span></span>\n'
        f'    <span class="prep-when prep-when--soon">{PREP_WHEN[lg]}</span>\n'
        "  </a>"
    )
    return s[:end] + row + s[end:], "ok"


def patch_stays(s: str, lang: str):
    """숙소 카드 ota-row 4행 — Trip.com 목록 버튼 추가 (기존 .ota-btn 토큰 재사용,
    다크/라이트 자동). pos = 카드 인덱스(해당 행 기존 버튼과 동일)."""
    lg = lang or "ko"
    added = 0

    def repl(m):
        nonlocal added
        row = m.group(0)
        if 'data-aff-vendor="Trip.com"' in row:
            return row
        pm = re.search(r'data-aff-pos="(\d+)"', row)
        if not pm:
            return row
        pos = pm.group(1)
        btn = (
            f'<a class="ota-btn" href="{hotels_url(f"twice_seoul_{lg}_stay{pos}")}"'
            ' rel="sponsored nofollow" target="_blank" data-aff="1"'
            ' data-aff-surface="stay-ota" data-aff-vendor="Trip.com"'
            f' data-aff-event="{EVENT}" data-aff-pos="{pos}">{OTA_LABEL[lg]}</a>'
        )
        added += 1
        return row[: -len("</div>")] + btn + "</div>"

    s2 = re.sub(r'<div class="ota-row">.*?</div>', repl, s)
    return s2, added


def main() -> int:
    fail = False
    for lang, path in FILES:
        s0 = path.read_text(encoding="utf-8")
        s1, r5 = patch_steps5(s0, lang)
        s2, rl = patch_locknow(s1, lang)
        s3, n = patch_stays(s2, lang)
        already = r5 == "skip" and rl == "skip" and n == 0
        if "MISS" in (r5, rl) or (not already and n not in (0, 4)):
            print(
                f"[FAIL] {path.name} lang={lang or 'ko'} steps5={r5} lock={rl} stays={n}"
            )
            fail = True
            continue
        if s3 != s0:
            path.write_text(s3, encoding="utf-8")
        state = "idempotent-skip" if already else "patched"
        print(f"[{state}] {path} steps5={r5} lock={rl} stays+={n}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
