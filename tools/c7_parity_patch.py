#!/usr/bin/env python3
"""R45 — c7(7박8일) 패널 동등화 (idempotent dist patch). wave7 c4(0059d204) 패턴 동형.

c7 sl-7 패널을 c4(sl-4) 규격으로 교체: 일자별 타임라인(lirow)·스팟 카드(ko 카카오+구글
페어, en은 en sl-2 규격 google 단독)·경고 박스(wait-note)·showday-s7 flat ckstep 체크리스트.
재료 = 이시카와 실측 draft(메인 repo projects/byvias/site/twice-seoul-course-c4c7.draft.json,
전 항목 WebSearch ≥2소스 교차 검증 2026-06-12). 날조 0 —
  · draft gaps('직전 확인'·'미공지'·'미검증')는 그대로 정직 노출.
  · draft가 "c4 Day spots 참조"로 지시한 step만 c4 검증 스팟 카드 재사용(봉피양·소문난성수
    감자탕·어니언·명동교자·하동관 — wave7 SPOTS 동일 데이터).
  · Day5 광장시장 "c2 검증 스팟 동일 권역" 지시는 draft가 거명한 순희네·박가네가 c2에
    실재하지 않아(검증 불가) 실존 c2 검증 카드(진주육회·통큰누이네빈대떡, kakao place id
    보존)를 sl-2에서 런타임 verbatim 추출 재사용. 미검증 상호명 신규 기재 0건.
  · 구 sl-7의 draft 밖 주장(WOWPASS·올림픽파크텔·KWANGYA·엠카 Live Pass 유료 예약 등)은
    draft 미검증 → 교체 제거 (c4 동등화와 동일 — wave7 선례).
표기: wave7 #11 정합 — wait-note 'h' 표기는 '시간'으로 통일 기재.
멱등: 패널 교체 positional + 내용 고정, c2 카드 추출은 sl-2 영역 한정. 2회 실행 diff 0.
검증: tools/locale_parity_gate.py (r45 체크 4종 추가) + tools/cr_audit.py + 4모드 캡처.
FLR-20260611-TEC-001 (dist/root divergence) 정합 — 서빙 자산 dist 직접 패치(소스 빌드 부재 페이지).
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

RICH = ["", "en"]  # 코스 리치 페이지 보유 locale (9 locale은 경량 — 코스 섹션 부재)
COURSE = "twice-thisisfor-seoul.html"

WARN_SVG = (
    '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="1.9" aria-hidden="true"><path d="M12 4l9 16H3z"/>'
    '<path d="M12 10v4M12 17.5v.2"/></svg>'
)
JUMP_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="1.8" aria-hidden="true"><path d="M3 7l9-4 9 4v6c0 5-9 8-9 8s-9-3-9-8V7z"/>'
    '<path d="M9 12l2 2 4-4"/></svg>'
)
ICON_RESTAURANT = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="1.6" aria-hidden="true"><path d="M5 3v8M8 3v8M5 11h3M6.5 11v10"/>'
    '<path d="M16 3c-1.5 1-2.5 3-2.5 6 0 1.5 1 2.5 2.5 2.5V21"/></svg>'
)
ICON_CAFE = (
    '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"'
    ' stroke-width="1.6" aria-hidden="true"><path d="M4 8h13v5a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8z"/>'
    '<path d="M17 9h2.5a2.5 2.5 0 0 1 0 5H17"/><path d="M7 3v2M11 3v2"/></svg>'
)
ICON_SHOW = (
    '<svg class="step-ph-ico" width="18" height="18" viewBox="0 0 24 24" fill="none"'
    ' stroke="currentColor" stroke-width="1.6" aria-hidden="true">'
    '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>'
)


# ---------------------------------------------------------------- 렌더러 ----
# wave7_r44_patch.py 동형 (lirow/spot_card/day_acc) + showday id 파라미터화.
def spot_card(sp: dict, lang: str) -> str:
    if sp.get("raw"):  # c2 verbatim 재사용 카드 (광장시장 — place id 보존)
        return sp["raw"]
    icon = ICON_CAFE if sp["cat"] == "cafe" else ICON_RESTAURANT
    links = []
    if lang == "ko" and sp.get("kakao"):
        links.append(
            f'<a class="psrc" href="{sp["kakao"]}" target="_blank" rel="noopener nofollow">카카오맵 ↗</a>'
        )
        links.append('<span class="psrc-sep">·</span>')
    glabel = "구글맵 ↗" if lang == "ko" else "Google Maps ↗"
    links.append(
        f'<a class="psrc psrc-g" href="{sp["google"]}" target="_blank" rel="noopener nofollow">{glabel}</a>'
    )
    pinfo = f'<div class="pinfo">{sp["info"]}</div>' if sp.get("info") else ""
    return (
        f'<div class="spot-card"><div class="place-ph" data-ph-var="{sp["var"]}" data-cat="{sp["cat"]}"'
        f' role="img" aria-label="{sp["name"]}"><span class="ph-chip">{sp["chip"]}</span>'
        f'<span class="ph-pic">{icon}</span>'
        f'<span class="ph-init" aria-hidden="true">{sp["init"]}</span></div>'
        f'<div class="pbody"><div class="pname">{sp["name"]}</div><div class="ptag">{sp["chip"]}</div>'
        f'<div class="pwhy">{sp["why"]}</div>{pinfo}'
        f'<span class="psrc-row">{"".join(links)}</span></div></div>'
    )


def lirow(step: dict, lang: str, ck: str | None = None) -> str:
    ckhtml = (
        f'<input type="checkbox" class="ckstep" data-ck="{ck}" aria-label="'
        + ("완료 체크" if lang == "ko" else "Mark done")
        + '">'
        if ck
        else ""
    )
    out = (
        f'<div class="lirow">{ckhtml}<div class="lk">{step["t"]}'
        f'<span class="dur">{step["d"]}</span></div>'
        f'<div class="lv">{step["p"]} <span class="badge badge--cat">{step["b"]}</span>'
        f'<div class="dsum">{step["s"]}</div></div></div>'
    )
    if step.get("w"):
        out += f'<div class="wait-note">{WARN_SVG}<span>{step["w"]}</span></div>'
    if step.get("ph"):
        out += (
            f'<div class="step-ph" data-cat="show">{ICON_SHOW}'
            f'<span class="step-ph-lbl">{step["ph"]}</span></div>'
        )
    if step.get("spots"):
        cards = "".join(spot_card(sp, lang) for sp in step["spots"])
        out += f'<div class="spot-rail">{cards}</div>'
    return out


def day_acc(day: dict, lang: str, open_: bool = False) -> str:
    note = (
        f'<p class="scap" style="margin:0 0 6px">{day["note"]}</p>'
        if day.get("note")
        else ""
    )
    warn = (
        f'<div class="day-note">{WARN_SVG}<span>{day["warn"]}</span></div>'
        if day.get("warn")
        else ""
    )
    rows = "".join(lirow(s, lang) for s in day["steps"])
    return (
        f'<details class="day-card day-acc"{" open" if open_ else ""}>'
        f'<summary>{day["h"]} <span style="font-weight:400;color:var(--muted)">· {day["cap"]}</span>'
        f'<span class="dsumline">{day["line"]}</span></summary>'
        f'<div class="day-acc-body">{note}{warn}{rows}</div></details>'
    )


def showday(day: dict, lang: str, sid: str) -> str:
    rows = "".join(lirow(s, lang, ck=f"{sid}-{i}") for i, s in enumerate(day["steps"]))
    return (
        f'<div class="day-card day-card--show" id="{sid}">'
        f'<div class="dhead">{day["h"]} <span style="font-weight:400;color:var(--muted)">· {day["cap"]}</span></div>'
        f'<div class="day-note">{WARN_SVG}<span>{day["warn"]}</span></div>{rows}</div>'
    )


# ------------------------------------------------------------ c7 데이터 ----
# 출처: twice-seoul-course-c4c7.draft.json courses[c7] (이시카와, ≥2소스 교차).
# 날조 0 — 시각·가격·운영시간·경고는 draft 본문 그대로(추정·변동·미검증 표기 보존).
# "c4 spots 참조" 지시 step의 스팟 데이터 = wave7_r44_patch.py SPOTS 동일 (c4 검증분 재사용).
KAKAO = {
    "bong": "https://map.kakao.com/?q=%EB%B4%89%ED%94%BC%EC%96%91%20%EB%B0%A9%EC%9D%B4%EC%A0%90",
    "gamja": "https://map.kakao.com/?q=%EC%86%8C%EB%AC%B8%EB%82%9C%EC%84%B1%EC%88%98%EA%B0%90%EC%9E%90%ED%83%95",
    "onion": "https://map.kakao.com/?q=%EC%96%B4%EB%8B%88%EC%96%B8%20%EC%84%B1%EC%88%98",
    "kyoja": "https://map.kakao.com/?q=%EB%AA%85%EB%8F%99%EA%B5%90%EC%9E%90%20%EB%B3%B8%EC%A0%90",
    "hadong": "https://map.kakao.com/?q=%ED%95%98%EB%8F%99%EA%B4%80%20%EB%AA%85%EB%8F%99",
}
GOOGLE = {
    "bong": "https://www.google.com/maps/search/?api=1&amp;query=%EB%B4%89%ED%94%BC%EC%96%91%20%EB%B0%A9%EC%9D%B4%EC%A0%90",
    "gamja": "https://www.google.com/maps/search/?api=1&amp;query=%EC%86%8C%EB%AC%B8%EB%82%9C%EC%84%B1%EC%88%98%EA%B0%90%EC%9E%90%ED%83%95",
    "onion": "https://www.google.com/maps/search/?api=1&amp;query=onion%20%EC%84%B1%EC%88%98",
    "kyoja": "https://www.google.com/maps/search/?api=1&amp;query=%EB%AA%85%EB%8F%99%EA%B5%90%EC%9E%90%20%EB%B3%B8%EC%A0%90",
    "hadong": "https://www.google.com/maps/search/?api=1&amp;query=%ED%95%98%EB%8F%99%EA%B4%80%20%EB%AA%85%EB%8F%99",
}

SPOTS_KO = {
    "bong": {
        "name": "봉피양 방이점",
        "chip": "평양냉면",
        "init": "봉",
        "cat": "restaurant",
        "var": "1",
        "why": "벽제갈비 계열 평양냉면 명가 — 미쉐린 가이드 등재",
        "info": "평양냉면 16,000원 · 11:00~22:00(LO 21:00) · 올림픽공원 권역",
        "kakao": KAKAO["bong"],
        "google": GOOGLE["bong"],
    },
    "gamja": {
        "name": "소문난성수감자탕",
        "chip": "감자탕",
        "init": "소",
        "cat": "restaurant",
        "var": "2",
        "why": "백종원 3대천왕에 소개된 40년 노포",
        "info": "감자국 12,000원 · 24시간 · 성수역 4번 출구 5분",
        "kakao": KAKAO["gamja"],
        "google": GOOGLE["gamja"],
    },
    "onion": {
        "name": "어니언 성수 (onion)",
        "chip": "카페",
        "init": "어",
        "cat": "cafe",
        "var": "1",
        "why": "공장 개조 인더스트리얼 카페의 원조",
        "info": "평일 08:00~22:00 · 주말 10:00~22:00(LO 21:30)",
        "kakao": KAKAO["onion"],
        "google": GOOGLE["onion"],
    },
    "kyoja": {
        "name": "명동교자 본점",
        "chip": "칼국수",
        "init": "명",
        "cat": "restaurant",
        "var": "2",
        "why": "미쉐린 가이드 등재 칼국수·만두 — 회전이 빨라 대기 짧은 편",
        "info": "칼국수 11,000원 · 10:30~21:00 연중무휴",
        "kakao": KAKAO["kyoja"],
        "google": GOOGLE["kyoja"],
    },
    "hadong": {
        "name": "하동관 본점",
        "chip": "곰탕",
        "init": "하",
        "cat": "restaurant",
        "var": "1",
        "why": "1939년 창업 한우곰탕 — 미쉐린 가이드 등재",
        "info": "곰탕 18,000원 · 07:00~16:00(재료 소진 시 조기 마감) · 일요일 휴무",
        "kakao": KAKAO["hadong"],
        "google": GOOGLE["hadong"],
    },
}

SPOTS_EN = {
    "bong": {
        "name": "Bongpiyang Bangi (봉피양)",
        "chip": "Naengmyeon",
        "init": "B",
        "cat": "restaurant",
        "var": "1",
        "why": "Pyongyang-naengmyeon house of the Byeokje Galbi family — Michelin Guide listed",
        "info": "Naengmyeon 16,000 KRW · 11:00–22:00 (LO 21:00) · Olympic Park area",
        "google": GOOGLE["bong"],
    },
    "gamja": {
        "name": "Somunnan Seongsu Gamjatang (소문난성수감자탕)",
        "chip": "Gamjatang",
        "init": "S",
        "cat": "restaurant",
        "var": "2",
        "why": "40-year stalwart featured on Baek Jong-won's Top 3 Chef King",
        "info": "Gamja-guk 12,000 KRW · open 24 hours · 5 min from Seongsu Stn Exit 4",
        "google": GOOGLE["gamja"],
    },
    "onion": {
        "name": "Onion Seongsu (어니언)",
        "chip": "Café",
        "init": "O",
        "cat": "cafe",
        "var": "1",
        "why": "The original factory-conversion industrial café",
        "info": "Weekdays 08:00–22:00 · weekends 10:00–22:00 (LO 21:30)",
        "google": GOOGLE["onion"],
    },
    "kyoja": {
        "name": "Myeongdong Kyoja (명동교자)",
        "chip": "Kalguksu",
        "init": "M",
        "cat": "restaurant",
        "var": "2",
        "why": "Michelin Guide-listed kalguksu & mandu — the line moves fast",
        "info": "Kalguksu 11,000 KRW · 10:30–21:00, open daily",
        "google": GOOGLE["kyoja"],
    },
    "hadong": {
        "name": "Hadongkwan (하동관)",
        "chip": "Gomtang",
        "init": "H",
        "cat": "restaurant",
        "var": "1",
        "why": "Hanwoo beef gomtang since 1939 — Michelin Guide listed",
        "info": "Gomtang 18,000 KRW · 07:00–16:00 (closes early when sold out) · closed Sundays",
        "google": GOOGLE["hadong"],
    },
}

# 광장시장 c2 검증 카드 (런타임 verbatim 추출 대상 — aria-label 키)
GWANGJANG_CARDS = ["진주육회", "광장시장통큰누이네육회빈대떡"]


def extract_c2_card(s: str, aria: str) -> str:
    """sl-2 영역 내 spot-card를 verbatim 추출 (place id 보존, 멱등 — sl-2 한정)."""
    a2 = s.find('<div class="sl-panel sl-2"')
    a4 = s.find('<div class="sl-panel sl-4"')
    if a2 < 0 or a4 < 0 or a4 <= a2:
        raise SystemExit("FAIL c2-extract: sl-2/sl-4 마커 부재")
    region = s[a2:a4]
    j = region.find(f'aria-label="{aria}"')
    if j < 0:
        raise SystemExit(f"FAIL c2-extract: {aria} 카드 부재 — divergence 의심")
    st = region.rfind('<div class="spot-card">', 0, j)
    # 카드 종단: pbody 닫힘 + 카드 닫힘 (sl-2 카드 구조 고정: ...</span></div></div>)
    en_ = region.find("</span></div></div>", j)
    if st < 0 or en_ < 0:
        raise SystemExit(f"FAIL c2-extract: {aria} 카드 경계 실패")
    return region[st : en_ + len("</span></div></div>")]


def c7_days(lang: str, gw_cards: list) -> list:
    S = SPOTS_KO if lang == "ko" else SPOTS_EN
    if lang == "ko":
        return [
            {
                "h": "Day 1",
                "cap": "도착 · 잠실 정착",
                "line": "잠실·방이 체크인 → 석촌호수·송리단길 → 방이동 저녁",
                "steps": [
                    {
                        "t": "14:00",
                        "d": "약 1시간",
                        "p": "잠실·방이 숙소 체크인",
                        "b": "숙소",
                        "s": "공항철도+환승 또는 리무진 · 장기 체류 — 짐 정리·유심/교통카드 세팅. T-money 등 교통카드 발급 후 충전 권장(지하철 기본 약 1,550원)",
                    },
                    {
                        "t": "16:00",
                        "d": "약 2.5시간",
                        "p": "석촌호수·송리단길",
                        "b": "카페",
                        "s": "도보 · 시차 적응 겸 가벼운 산책·카페",
                        "w": "주말 인기 카페 오후 웨이팅",
                    },
                    {
                        "t": "19:00",
                        "d": "약 1.5시간",
                        "p": "방이동 먹자골목 저녁",
                        "b": "식당",
                        "s": "도보 · 공연장 최근접 식당가에서 첫 저녁",
                        "spots": [S["bong"]],
                    },
                ],
            },
            {
                "h": "Day 2",
                "cap": "성지순례 DAY — JYP 사옥 · 코엑스 · K-스타로드",
                "line": "JYP 사옥 외관 → 올림픽공원 → Ktown4u 코엑스 → K-STAR ROAD",
                "note": "JYP Center(강동대로 205) 외관 포토 → 올림픽공원 → Ktown4u 코엑스 → K-STAR ROAD 동선.",
                "steps": [
                    {
                        "t": "10:00",
                        "d": "약 1.5시간",
                        "p": "JYP Center 외관 성지순례",
                        "b": "관광",
                        "s": "도보~버스 — 올림픽수영장 입구 맞은편(강동대로 205) · 무료",
                        "w": "사옥 1층 카페 ‘쏘울컵(Soul Cup)’은 외부인 입장 불가(직원 전용 전환) — 외부 포토만",
                    },
                    {
                        "t": "12:00",
                        "d": "약 2시간",
                        "p": "올림픽공원 산책 + 점심",
                        "b": "관광",
                        "s": "도보 · KSPO돔 게이트 사전 답사",
                    },
                    {
                        "t": "14:30",
                        "d": "약 2.5시간",
                        "p": "Ktown4u 코엑스",
                        "b": "쇼핑",
                        "s": "8호선→2호선 삼성역(약 20~25분) · 앨범·굿즈 1차 쇼핑 — 공연 전 응원 준비물 확보",
                    },
                    {
                        "t": "17:30",
                        "d": "약 2시간",
                        "p": "K-STAR ROAD + 압구정 저녁",
                        "b": "관광",
                        "s": "수인분당선 압구정로데오역 · 스타 18팀 협업 ‘강남돌’ 아트토이 거리",
                    },
                ],
            },
            {
                "h": "Day 3",
                "cap": "공연 DAY (대기로 하루 소진)",
                "warn": "공연 시각 회차별 상이 — 7/10(금) 19:00 · 7/11(토) 18:00 · 7/12(일) 17:00. MD 오픈런 → 간단 점심 → 입장 줄 → 본 공연 → 시간차 퇴장 야식.",
                "steps": [
                    {
                        "t": "09:30",
                        "d": "약 3.5시간",
                        "p": "KSPO돔 MD 부스 오픈런",
                        "b": "공연장",
                        "s": "도보(잠실 베이스 최대 강점) · 인기 굿즈·포토카드는 오전 줄",
                        "w": "피날레 3연속 — 인기 굿즈 오전 품절 리스크",
                    },
                    {
                        "t": "16:00",
                        "d": "약 1.5시간",
                        "p": "KSPO돔 입장 줄 (회차 시각 −2시간)",
                        "b": "공연장",
                        "s": "도보 · 보안검색·티켓 확인",
                        "w": "좌석석도 1~2시간 전 도착 권장",
                    },
                    {
                        "t": "18:00",
                        "d": "약 2.5시간",
                        "p": "TWICE 〈THIS IS FOR〉 FINALE in SEOUL — 본 공연",
                        "b": "공연장",
                        "s": "월드투어 81회 대장정 피날레",
                        "ph": "TWICE THIS IS FOR · 공연 (KSPO돔)",
                    },
                    {
                        "t": "21:00",
                        "d": "약 1.5시간",
                        "p": "시간차 퇴장 · 방이동 야식",
                        "b": "식당",
                        "s": "도보 · 동시 퇴장 혼잡 — 근처에서 치맥으로 여운",
                        "w": "종료 후 1시간+ 혼잡 — 도보권 야식 분산",
                    },
                ],
            },
            {
                "h": "Day 4",
                "cap": "굿즈·팝업 DAY — 성수 · 명동",
                "line": "성수 연무장길 팝업 → 명동 굿즈샵 → 명동 저녁",
                "warn": "팝업 주 단위 변동 — 출발 전 팝가(popga.co.kr)·팝플리(popply.co.kr)에서 당주 일정 확인.",
                "steps": [
                    {
                        "t": "10:30",
                        "d": "약 3시간",
                        "p": "성수 연무장길 팝업 투어",
                        "b": "쇼핑",
                        "s": "2호선 성수역 · 연무장길 일대가 팝업 밀집 코어 — 점심·카페는 동선 한복판에서",
                        "spots": [S["gamja"], S["onion"]],
                    },
                    {
                        "t": "15:30",
                        "d": "약 2.5시간",
                        "p": "명동 굿즈샵 — 위드뮤·뮤직코리아",
                        "b": "쇼핑",
                        "s": "2호선 을지로입구 · 앨범·공식 굿즈·포토카드 전문",
                    },
                    {
                        "t": "18:30",
                        "d": "약 1.5시간",
                        "p": "명동 저녁 — 명동교자 본점 등",
                        "b": "식당",
                        "s": "도보 · 굿즈샵 동선 도보권에서 마무리",
                        "spots": [S["kyoja"], S["hadong"]],
                    },
                ],
            },
            {
                "h": "Day 5",
                "cap": "궁 · 전통 DAY — 경복궁 · 북촌 · 광장시장",
                "line": "경복궁 → 북촌 → 인사동 → 광장시장 → 청계천",
                "warn": "경복궁 화요일 휴궁 — 7/14(화)와 겹치면 창덕궁·덕수궁 등으로 대체(각 궁 휴무일 상이, royal.khs.go.kr 확인).",
                "steps": [
                    {
                        "t": "09:30",
                        "d": "약 2.5시간",
                        "p": "경복궁",
                        "b": "관광",
                        "s": "8호선→3호선 경복궁역(잠실에서 약 45~55분) · 성인 3,000원(한복 착용 시 무료) · 6~8월 09:00~18:30(입장마감 17:30). 수문장 교대식 등은 현장 일정 확인",
                        "w": "매주 화요일 휴궁. 7월 야간개장 일정 미공지 — 상반기 야간개장은 6/14 종료",
                    },
                    {
                        "t": "12:30",
                        "d": "약 1.5시간",
                        "p": "북촌한옥마을",
                        "b": "관광",
                        "s": "도보(경복궁 동편) · 무료 · 한옥 골목 포토. 한복 대여 시 경복궁 무료입장과 연계 효율",
                        "w": "레드존(북촌로11길 일대)은 방문 10:00~17:00만 허용(2025-03 시행) — 위반 시 과태료. 17시 전 퇴장, 거주지역 정숙",
                    },
                    {
                        "t": "14:30",
                        "d": "약 1.5시간",
                        "p": "인사동 거리",
                        "b": "관광",
                        "s": "도보~3호선 안국역 1정거장 · 전통 기념품·전통차 골목",
                    },
                    {
                        "t": "16:30",
                        "d": "약 2시간",
                        "p": "광장시장 — 먹거리 투어 (이른 저녁)",
                        "b": "시장",
                        "s": "1호선 종로5가역 · 빈대떡·마약김밥·육회",
                        "w": "인기집 상시 웨이팅 — 피크 전 16~17시대 공략",
                        "spots": gw_cards,
                    },
                    {
                        "t": "19:00",
                        "d": "약 1시간",
                        "p": "청계천 산책 후 복귀",
                        "b": "관광",
                        "s": "2호선 을지로 → 잠실",
                    },
                ],
            },
            {
                "h": "Day 6",
                "cap": "음악방송 방청 도전 DAY (+실패 시 대안 동선)",
                "line": "음방 방청 도전 → [대안] 더현대 서울 · 한강공원",
                "warn": "음방 방청은 ‘도전’ — 사전 신청·추첨제, 출연 라인업은 매주 변동. TWICE 출연 여부는 컴백·활동 일정에 따라 다름. 신청 실패 시 대안 동선으로 자연 전환.",
                "steps": [
                    {
                        "t": "08:00",
                        "d": "약 4시간",
                        "p": "음악방송 방청 (사전 당첨 시)",
                        "b": "방송",
                        "s": "KBS 여의도(뮤직뱅크 금요일) / CJ ENM 상암(엠카운트다운 목요일) · 방청 무료 · 뮤직뱅크: KBS 홈페이지 시청자참여 > 방청신청 — 방송 전주 목요일 09:00~24:00 접수, 1인 2매, 15세 이상, 당첨 시 신분증 지참. 엠카운트다운: 출연 아티스트 공식 플랫폼(Mnet Plus 등)별 사전 신청",
                        "w": "음악중심(MBC)·인기가요(SBS)는 방청 정책 미검증 — 방송사·팬클럽 공지 직접 확인. 사전녹화는 팬클럽 우선 관행",
                    },
                    {
                        "t": "13:00",
                        "d": "약 2시간",
                        "p": "[대안] 여의도 더현대 서울 — 팝업 체크",
                        "b": "쇼핑",
                        "s": "여의도 도보권(뮤직뱅크 동선 연결) / 상암에서 약 30분 · K-pop 팝업 단골 베뉴 — 당주 팝업은 공식 인스타·팝가 확인",
                        "w": "공연 주간 특정 팝업 미공지(2026-06 기준) — 방문 직전 확인",
                    },
                    {
                        "t": "16:00",
                        "d": "약 2시간",
                        "p": "[대안] 한강공원 (여의도)",
                        "b": "관광",
                        "s": "도보 · 무료(치맥 별도 약 2~3만원/2인) · 한강 돗자리+배달 치맥 — K-드라마 클리셰 체험",
                    },
                    {
                        "t": "19:00",
                        "d": "약 1.5시간",
                        "p": "여의도 → 잠실 복귀 저녁",
                        "b": "식당",
                        "s": "9호선 급행 약 30~40분",
                    },
                ],
            },
            {
                "h": "Day 7",
                "cap": "자유일 — 옵션 3종",
                "line": "옵션 A 롯데월드 / B 홍대·남산 / C 성수·DDP 중 택1",
                "note": "취향대로 1개 선택. 모두 잠실 베이스 기준 동선.",
                "steps": [
                    {
                        "t": "10:00",
                        "d": "약 8시간",
                        "p": "[옵션 A] 롯데월드 어드벤처 + 석촌호수",
                        "b": "관광",
                        "s": "도보~8호선 · 종합이용권 정가 약 6만원대(온라인 할인 변동 — 공식 확인) · 공연 여운 + 테마파크 마무리. 런던베이글(월드몰 1층)은 평일 오전 공략 찬스",
                        "w": "주말 어트랙션 대기 김 — 매직패스 고려",
                    },
                    {
                        "t": "10:00",
                        "d": "약 8시간",
                        "p": "[옵션 B] 홍대·연남 + 남산 N서울타워 야경",
                        "b": "관광",
                        "s": "2호선 · 버스킹·쇼핑·포토부스 → 저녁 남산 야경 코스",
                        "w": "N서울타워 전망대는 야경 시간대 매표 줄",
                    },
                    {
                        "t": "10:00",
                        "d": "약 8시간",
                        "p": "[옵션 C] 성수 재방문(팝업 2차) + 동대문 DDP·야시장",
                        "b": "쇼핑",
                        "s": "2호선 · Day4에 못 간 팝업 재도전 + DDP 야경",
                    },
                ],
            },
            {
                "h": "Day 8",
                "cap": "출국",
                "line": "석촌호수 산책 → 체크아웃 · 공항",
                "steps": [
                    {
                        "t": "09:30",
                        "d": "약 1.5시간",
                        "p": "석촌호수 마지막 산책 · 기념품 정리",
                        "b": "관광",
                        "s": "도보",
                    },
                    {
                        "t": "11:30",
                        "d": "약 1시간",
                        "p": "체크아웃 · 공항 이동",
                        "b": "숙소",
                        "s": "공항철도/리무진 — 잠실발 약 1시간 20분~1시간 40분 · 앨범·굿즈 수하물 무게 체크(다량 구매 시 초과 주의)",
                    },
                ],
            },
        ]
    # ---- EN (draft 사실 동일 — 번역만, 신규 주장 0. c4-en 규격: 12h 표기·google 단독) ----
    return [
        {
            "h": "Day 1",
            "cap": "Arrival · settle in Jamsil",
            "line": "Check in Jamsil/Bangi → Seokchon Lake & Songnidan-gil → Bangi-dong dinner",
            "steps": [
                {
                    "t": "2:00 PM",
                    "d": "~1 hr",
                    "p": "Check in around Jamsil/Bangi",
                    "b": "Stay",
                    "s": "AREX + transfer, or limousine bus · long stay — unpack, set up SIM & transit card. Get a T-money card and top up (subway base fare approx. 1,550 KRW)",
                },
                {
                    "t": "4:00 PM",
                    "d": "~2.5 hrs",
                    "p": "Seokchon Lake & Songnidan-gil",
                    "b": "Café",
                    "s": "On foot · an easy stroll and a café while the jet lag wears off",
                    "w": "Popular cafés have afternoon waits on weekends",
                },
                {
                    "t": "7:00 PM",
                    "d": "~1.5 hrs",
                    "p": "Dinner in the Bangi-dong food alley",
                    "b": "Food",
                    "s": "On foot · first dinner in the dining strip closest to the venue",
                    "spots": [S["bong"]],
                },
            ],
        },
        {
            "h": "Day 2",
            "cap": "Pilgrimage DAY — JYP HQ · COEX · K-Star Road",
            "line": "JYP Center exterior → Olympic Park → Ktown4u COEX → K-STAR ROAD",
            "note": "JYP Center (205 Gangdong-daero) exterior photos → Olympic Park → Ktown4u COEX → K-STAR ROAD.",
            "steps": [
                {
                    "t": "10:00 AM",
                    "d": "~1.5 hrs",
                    "p": "JYP Center exterior pilgrimage",
                    "b": "Sights",
                    "s": "Walk or short bus ride — opposite the Olympic Pool entrance (205 Gangdong-daero) · free",
                    "w": "The 1F café 'Soul Cup' no longer admits outside visitors (staff only) — exterior photos only",
                },
                {
                    "t": "12:00 PM",
                    "d": "~2 hrs",
                    "p": "Olympic Park walk + lunch",
                    "b": "Sights",
                    "s": "On foot · KSPO Dome gate recon for show day",
                },
                {
                    "t": "2:30 PM",
                    "d": "~2.5 hrs",
                    "p": "Ktown4u COEX",
                    "b": "Shopping",
                    "s": "Line 8 → Line 2, Samseong Stn (approx. 20–25 min) · first album & goods run — stock up on show essentials",
                },
                {
                    "t": "5:30 PM",
                    "d": "~2 hrs",
                    "p": "K-STAR ROAD + Apgujeong dinner",
                    "b": "Sights",
                    "s": "Suin-Bundang Line, Apgujeong Rodeo Stn · 'GangnamDol' art-toy street with 18 K-pop acts",
                },
            ],
        },
        {
            "h": "Day 3",
            "cap": "Show DAY (queues eat the day)",
            "warn": "Start time differs by date — Fri Jul 10 7 PM · Sat Jul 11 6 PM · Sun Jul 12 5 PM. MD open-run → quick lunch → entry queue → the show → staggered exit & late-night food.",
            "steps": [
                {
                    "t": "9:30 AM",
                    "d": "~3.5 hrs",
                    "p": "KSPO Dome MD booth open-run",
                    "b": "Venue",
                    "s": "On foot (the Jamsil base's biggest edge) · popular goods & photocards queue from the morning",
                    "w": "3-night finale — popular goods risk selling out in the morning",
                },
                {
                    "t": "4:00 PM",
                    "d": "~1.5 hrs",
                    "p": "KSPO Dome entry queue (2 hrs before your date's start)",
                    "b": "Venue",
                    "s": "On foot · security & ticket checks",
                    "w": "Even seated tickets: arrive 1–2 hrs early",
                },
                {
                    "t": "6:00 PM",
                    "d": "~2.5 hrs",
                    "p": "TWICE 〈THIS IS FOR〉 FINALE in SEOUL — the show",
                    "b": "Venue",
                    "s": "The finale of an 81-show world tour",
                    "ph": "TWICE THIS IS FOR · the show (KSPO Dome)",
                },
                {
                    "t": "9:00 PM",
                    "d": "~1.5 hrs",
                    "p": "Staggered exit · late-night food in Bangi-dong",
                    "b": "Food",
                    "s": "On foot · everyone leaves at once — chicken & beer nearby while it clears",
                    "w": "Stations & roads stay jammed 1 hr+ after the show — spread out to walkable late-night spots",
                },
            ],
        },
        {
            "h": "Day 4",
            "cap": "Goods & pop-up DAY — Seongsu · Myeongdong",
            "line": "Seongsu pop-ups → Myeongdong goods shops → Myeongdong dinner",
            "warn": "Pop-ups rotate weekly — before heading out, check that week's lineup on Popga (popga.co.kr) / Popply (popply.co.kr).",
            "steps": [
                {
                    "t": "10:30 AM",
                    "d": "~3 hrs",
                    "p": "Seongsu Yeonmujang-gil pop-up tour",
                    "b": "Shopping",
                    "s": "Line 2 Seongsu Stn · Yeonmujang-gil is the pop-up core — lunch & coffee right on the route",
                    "spots": [S["gamja"], S["onion"]],
                },
                {
                    "t": "3:30 PM",
                    "d": "~2.5 hrs",
                    "p": "Myeongdong goods shops — Withmuu · Music Korea",
                    "b": "Shopping",
                    "s": "Line 2 to Euljiro 1-ga Stn · albums, official goods & photocards",
                },
                {
                    "t": "6:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Myeongdong dinner — Myeongdong Kyoja & more",
                    "b": "Food",
                    "s": "On foot · wrap up within walking distance of the goods shops",
                    "spots": [S["kyoja"], S["hadong"]],
                },
            ],
        },
        {
            "h": "Day 5",
            "cap": "Palace & tradition DAY — Gyeongbokgung · Bukchon · Gwangjang",
            "line": "Gyeongbokgung → Bukchon → Insadong → Gwangjang Market → Cheonggyecheon",
            "warn": "Gyeongbokgung closes on Tuesdays — if your Day 5 lands on one (e.g. Tue Jul 14), swap in Changdeokgung or Deoksugung (closure days differ by palace — check royal.khs.go.kr).",
            "steps": [
                {
                    "t": "9:30 AM",
                    "d": "~2.5 hrs",
                    "p": "Gyeongbokgung Palace",
                    "b": "Sights",
                    "s": "Line 8 → Line 3, Gyeongbokgung Stn (approx. 45–55 min from Jamsil) · adults 3,000 KRW (free in hanbok) · Jun–Aug 09:00–18:30 (last entry 17:30). Royal-guard ceremony times — check on site",
                    "w": "Closed every Tuesday. July night openings unannounced — the first-half season ended Jun 14",
                },
                {
                    "t": "12:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Bukchon Hanok Village",
                    "b": "Sights",
                    "s": "On foot (east of the palace) · free · hanok-alley photos. Renting hanbok pairs well with free palace entry",
                    "w": "The red zone (Bukchon-ro 11-gil area) only allows visitors 10:00–17:00 (since Mar 2025) — fines apply. Leave by 5 PM and keep quiet in residential lanes",
                },
                {
                    "t": "2:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Insadong street",
                    "b": "Sights",
                    "s": "On foot, or 1 stop to Anguk Stn (Line 3) · traditional souvenirs & tea alleys",
                },
                {
                    "t": "4:30 PM",
                    "d": "~2 hrs",
                    "p": "Gwangjang Market — street-food tour (early dinner)",
                    "b": "Market",
                    "s": "Line 1, Jongno 5-ga Stn · bindaetteok, mayak gimbap & yukhoe",
                    "w": "Popular stalls queue all day — go before the peak, around 4–5 PM",
                    "spots": gw_cards,
                },
                {
                    "t": "7:00 PM",
                    "d": "~1 hr",
                    "p": "Cheonggyecheon stroll, then back",
                    "b": "Sights",
                    "s": "Line 2, Euljiro → Jamsil",
                },
            ],
        },
        {
            "h": "Day 6",
            "cap": "Music-show audience try DAY (+ Plan B route)",
            "line": "Music-show audience try → [Plan B] The Hyundai · Han River Park",
            "warn": "A music-show audience seat is a 'try' — advance application & lottery, and lineups change weekly. Whether TWICE appears depends on their comeback schedule. If you miss out, the Plan B route takes over naturally.",
            "steps": [
                {
                    "t": "8:00 AM",
                    "d": "~4 hrs",
                    "p": "Music-show audience (if you won a seat)",
                    "b": "TV show",
                    "s": "KBS Yeouido (Music Bank, Fridays) / CJ ENM Sangam (M Countdown, Thursdays) · audience entry is free · Music Bank: KBS website → Viewer Participation > Audience Application — opens 09:00–24:00 on the Thursday of the week before, 2 per person, 15+, bring ID if selected. M Countdown: advance application via each artist's official platform (Mnet Plus etc.)",
                    "w": "Show! Music Core (MBC) & Inkigayo (SBS) audience policies unverified — check broadcaster & fan-club notices directly. Pre-recordings usually prioritize fan clubs",
                },
                {
                    "t": "1:00 PM",
                    "d": "~2 hrs",
                    "p": "[Plan B] The Hyundai Seoul, Yeouido — pop-up check",
                    "b": "Shopping",
                    "s": "Walkable in Yeouido (links with the Music Bank route) / approx. 30 min from Sangam · a K-pop pop-up regular — check that week's lineup on official Instagram or Popga",
                    "w": "No show-week pop-up announced yet (as of Jun 2026) — confirm right before you go",
                },
                {
                    "t": "4:00 PM",
                    "d": "~2 hrs",
                    "p": "[Plan B] Han River Park (Yeouido)",
                    "b": "Sights",
                    "s": "On foot · free (chimaek approx. 20,000–30,000 KRW for two) · picnic mat + delivery chicken & beer — the K-drama cliché, done right",
                },
                {
                    "t": "7:00 PM",
                    "d": "~1.5 hrs",
                    "p": "Back to Jamsil for dinner",
                    "b": "Food",
                    "s": "Line 9 express, approx. 30–40 min",
                },
            ],
        },
        {
            "h": "Day 7",
            "cap": "Free day — 3 options",
            "line": "Pick one: A Lotte World / B Hongdae & Namsan / C Seongsu & DDP",
            "note": "Pick whichever suits you. All three start from the Jamsil base.",
            "steps": [
                {
                    "t": "10:00 AM",
                    "d": "~8 hrs",
                    "p": "[Option A] Lotte World Adventure + Seokchon Lake",
                    "b": "Sights",
                    "s": "On foot / Line 8 · day pass list price in the 60,000-KRW range (online discounts vary — check official) · ride the post-show high into a theme-park finish. Weekday morning is your London Bagel Museum (mall 1F) window",
                    "w": "Weekend ride waits run long — consider Magic Pass",
                },
                {
                    "t": "10:00 AM",
                    "d": "~8 hrs",
                    "p": "[Option B] Hongdae & Yeonnam + N Seoul Tower night view",
                    "b": "Sights",
                    "s": "Line 2 · busking, shopping & photo booths → Namsan night view in the evening",
                    "w": "Observatory ticket lines build at night-view hours",
                },
                {
                    "t": "10:00 AM",
                    "d": "~8 hrs",
                    "p": "[Option C] Seongsu revisit (pop-up round 2) + Dongdaemun DDP & night views",
                    "b": "Shopping",
                    "s": "Line 2 · retry the pop-ups you missed on Day 4 + DDP at night",
                },
            ],
        },
        {
            "h": "Day 8",
            "cap": "Departure",
            "line": "Last lake stroll → check-out · airport",
            "steps": [
                {
                    "t": "9:30 AM",
                    "d": "~1.5 hrs",
                    "p": "Last Seokchon Lake stroll · pack the souvenirs",
                    "b": "Sights",
                    "s": "On foot",
                },
                {
                    "t": "11:30 AM",
                    "d": "~1 hr",
                    "p": "Check out · to the airport",
                    "b": "Stay",
                    "s": "AREX / limousine — approx. 1 hr 20 min–1 hr 40 min from Jamsil · weigh your album & goods haul (excess-baggage risk if you bought big)",
                },
            ],
        },
    ]


def build_c7_panel(lang: str, gw_cards: list) -> str:
    days = c7_days(lang, gw_cards)
    if lang == "ko":
        head = (
            '<div class="box"><h2 id="sec-c7" style="font-weight:600;font-size:14px;margin:0 0 0">7박8일 풀 원정 코스</h2>'
            '<p class="scap" style="margin:4px 0 0">원정 팬 평균 체류(8.7일) 정합. 공연 + 성지순례 + 굿즈·팝업에 궁·전통(경복궁·북촌), '
            "음악방송 방청 도전, 자유일까지. 실제 장소이며 가격은 대략 시세입니다. 실시간 예약가는 예약처에서 확인하세요.</p>"
            '<p class="scap w5-basenote" style="margin:2px 0 0;font-weight:600">잠실 베이스 기준</p>'
            '<p class="crs-sum">잠실 베이스 7박. 동선: Day1 도착·정착 → Day2 성지순례 → <b>Day3 공연</b> → Day4 굿즈·팝업 → '
            "Day5 궁·전통 → Day6 음악방송 도전 → Day7 자유일 → Day8 출국. "
            '<span style="color:var(--muted)">대략 예산: 숙박 7박 약 $399~854(아래 ‘함께 묵는 숙소’ 시세 기준) · 항공·티켓·식비 별도.</span></p>'
            f'<a class="showday-jump" data-w6-course-jump="1" href="#showday-s7">{JUMP_SVG}공연 당일 한눈에 보기 →</a>\n'
        )
    else:
        head = (
            '<div class="box"><h2 id="sec-c7" style="font-weight:600;font-size:14px;margin:0 0 0">7N8D Full Pilgrimage Course</h2>'
            '<p class="scap" style="margin:4px 0 0">Matched to the average fan stay (8.7 days). The show + pilgrimage + goods & pop-ups, '
            "plus palace & tradition (Gyeongbokgung · Bukchon), a music-show audience try and a free day. "
            "Real places; prices are rough estimates — confirm live rates with the booking site.</p>"
            '<p class="scap w5-basenote" style="margin:2px 0 0;font-weight:600">Jamsil base reference</p>'
            '<p class="crs-sum">Jamsil base, 7 nights. Flow: Day 1 arrive & settle → Day 2 pilgrimage → <b>Day 3 show</b> → '
            "Day 4 goods & pop-ups → Day 5 palace & tradition → Day 6 music-show try → Day 7 free day → Day 8 departure. "
            '<span style="color:var(--muted)">Rough budget: 7 nights\' lodging approx. $399–854 '
            "(based on the 'Where to stay' rates below) · flights, tickets & meals not included.</span></p>"
            f'<a class="showday-jump" data-w6-course-jump="1" href="#showday-s7">{JUMP_SVG}Show day at a glance →</a>\n'
        )
    body = "\n".join(
        [
            day_acc(days[0], lang, open_=True),
            day_acc(days[1], lang),
            showday(days[2], lang, "showday-s7"),
            day_acc(days[3], lang),
            day_acc(days[4], lang),
            day_acc(days[5], lang),
            day_acc(days[6], lang),
            day_acc(days[7], lang),
        ]
    )
    return (
        '<div class="sl-panel sl-7" data-w7-c7="1"><!--W5RULE: day 카드 임계 룰 — 총 3일 이하 코스 flat / 4일+ 코스 day-acc 아코디언. '
        "공연 당일 상세(day-card--show)는 길이 무관 항상 flat 노출-->\n"
        + head
        + body
        + "\n</div>\n  </div>\n"
    )


# ---------------------------------------------------------------- 패치 ----
def patch_course(path: Path, lang: str) -> None:
    s = path.read_text(encoding="utf-8")

    # c2 검증 광장시장 카드 verbatim 추출 (sl-2 영역 한정 — 멱등·place id 보존)
    gw_cards = [{"raw": extract_c2_card(s, aria)} for aria in GWANGJANG_CARDS]

    # sl-7 패널 교체 (positional — 멱등). 경계: sl-7 시작 ~ stay-len 래퍼 닫힘 직전.
    a = s.find('<div class="sl-panel sl-7"')
    b = s.find("</div><!-- /stay-len -->")
    if a < 0 or b < 0 or b <= a:
        raise SystemExit(
            f"FAIL c7-panel {lang}: sl-7/stay-len 마커 부재 — divergence 의심 (FLR-20260611-TEC-001)"
        )
    s = s[:a] + build_c7_panel(lang, gw_cards) + s[b:]

    path.write_text(s, encoding="utf-8")
    print(f"  course {lang or 'ko'}: OK")


def main() -> None:
    for lang in RICH:
        p = DIST / lang / COURSE if lang else DIST / COURSE
        patch_course(p, lang or "ko")
    print("R45 c7 parity patch done.")


if __name__ == "__main__":
    sys.exit(main())
