#!/usr/bin/env python3
"""WAVE7 — R44 2심 조니 확정 fix (idempotent dist patch).

#6  c4(4박5일) 동등화 — sl-2 규격: 일자별 타임라인(lirow)·스팟 카드(kakao+google 페어,
    en은 en sl-2 규격 정합 google 단독)·경고 박스(wait-note)·showday ckstep 체크리스트.
    재료 = 이시카와 실측 draft(메인 repo projects/byvias/site/twice-seoul-course-c4c7.draft.json,
    전 항목 WebSearch ≥2소스 교차 검증 2026-06-12). draft에 없는 정보 날조 0 — gaps는
    비우거나 '직전 확인' 일반 안내. c7은 R45 범위(본 패치 미접촉).
#7  맛집 카드 정직화 — ①청와옥 중복 카드 제거(showday 야식 step의 동일 카드 — 같은
    뷰 내 2회 노출) ②why = 실제 추천 사유 1줄 비정형(draft 6곳: 미쉐린·노포·원조 등
    사유 실재 항목만 pwhy 사용) ③빈 필드 추가 0 ④균질 4필드 금지 — 기존 카드의
    'ptag · 주소' 가짜 why는 pinfo(주소 정보줄)로 정직 전환, en의 'ptag 동어반복' why는
    제거(있는 정보만). 카드 자체는 보존(실측 place id·맵 링크 — 데이터 연속성,
    rules/data-continuity.md. 전수 제거는 사실상 sl-2 구조 해체 → lead 별도 결정 사안).
#8  radius 토큰 수렴 — 홈 비정합 8종(9px·10px·5px·6px·7px·16px 등) → 이벤트 페이지
    체계(--r-s:8 / --r-m:12 / --r-pill:999, 50%·0 자연값 유지). 소스 generate.py 동시 정합
    (메인 repo 단독 pathspec commit — 양층 정합).
#9  터치 — ckstep 히트박스 44×44 실측화(레이아웃 박스 자체 44, 시각 22 박스는 ::before
    렌더 — wave8 ::before 히트 핵은 실측 22 잔존이 R44 재적발 본질) + psrc min-width 44.
#11 wait-note 표기 1종 통일(ko) — '1~2h'→'1~2시간', '1h+'→'1시간+' (h/시간 혼용 해소).
#12 워드마크 패스화 선행 준비 — 로고 3중 치수 불일치(natural 206×90 / attr 119×38 /
    css 87×38) 해소: attr = 실비율(87×38, 206:90 = 87:38.0…). 패스화 자체는 대표 시안
    선택 후 별건.

멱등: 전 치환 old→new 소진형 + panel 교체는 내용 고정. 2회 실행 diff 0.
검증: tools/locale_parity_gate.py (W7 체크 5종 추가) + tools/cr_audit.py + 4모드 캡처.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

LOCALES = ["", "en", "ja", "zh-cn", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]
RICH = ["", "en"]  # 코스 리치 페이지 보유 locale (9 locale은 경량 — 코스 섹션 부재)
COURSE = "twice-thisisfor-seoul.html"
HOME = "index.html"

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
def spot_card(sp: dict, lang: str) -> str:
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


def showday(day: dict, lang: str) -> str:
    rows = "".join(
        lirow(s, lang, ck=f"showday-s4-{i}") for i, s in enumerate(day["steps"])
    )
    return (
        f'<div class="day-card day-card--show" id="showday-s4">'
        f'<div class="dhead">{day["h"]} <span style="font-weight:400;color:var(--muted)">· {day["cap"]}</span></div>'
        f'<div class="day-note">{WARN_SVG}<span>{day["warn"]}</span></div>{rows}</div>'
    )


# ------------------------------------------------------------ c4 데이터 ----
# 출처: twice-seoul-course-c4c7.draft.json (이시카와, 2026-06-12 ≥2소스 교차).
# 날조 0 — 모든 시각·가격·운영시간·경고는 draft 본문 그대로(추정·변동 표기 보존).
KAKAO = {
    "bong": "https://map.kakao.com/?q=%EB%B4%89%ED%94%BC%EC%96%91%20%EB%B0%A9%EC%9D%B4%EC%A0%90",
    "gamja": "https://map.kakao.com/?q=%EC%86%8C%EB%AC%B8%EB%82%9C%EC%84%B1%EC%88%98%EA%B0%90%EC%9E%90%ED%83%95",
    "onion": "https://map.kakao.com/?q=%EC%96%B4%EB%8B%88%EC%96%B8%20%EC%84%B1%EC%88%98",
    "kyoja": "https://map.kakao.com/?q=%EB%AA%85%EB%8F%99%EA%B5%90%EC%9E%90%20%EB%B3%B8%EC%A0%90",
    "hadong": "https://map.kakao.com/?q=%ED%95%98%EB%8F%99%EA%B4%80%20%EB%AA%85%EB%8F%99",
    "bagel": "https://map.kakao.com/?q=%EB%9F%B0%EB%8D%98%EB%B2%A0%EC%9D%B4%EA%B8%80%EB%AE%A4%EC%A7%80%EC%97%84%20%EC%9E%A0%EC%8B%A4",
}
GOOGLE = {
    "bong": "https://www.google.com/maps/search/?api=1&amp;query=%EB%B4%89%ED%94%BC%EC%96%91%20%EB%B0%A9%EC%9D%B4%EC%A0%90",
    "gamja": "https://www.google.com/maps/search/?api=1&amp;query=%EC%86%8C%EB%AC%B8%EB%82%9C%EC%84%B1%EC%88%98%EA%B0%90%EC%9E%90%ED%83%95",
    "onion": "https://www.google.com/maps/search/?api=1&amp;query=onion%20%EC%84%B1%EC%88%98",
    "kyoja": "https://www.google.com/maps/search/?api=1&amp;query=%EB%AA%85%EB%8F%99%EA%B5%90%EC%9E%90%20%EB%B3%B8%EC%A0%90",
    "hadong": "https://www.google.com/maps/search/?api=1&amp;query=%ED%95%98%EB%8F%99%EA%B4%80%20%EB%AA%85%EB%8F%99",
    "bagel": "https://www.google.com/maps/search/?api=1&amp;query=%EB%9F%B0%EB%8D%98%EB%B2%A0%EC%9D%B4%EA%B8%80%EB%AE%A4%EC%A7%80%EC%97%84%20%EC%9E%A0%EC%8B%A4",
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
    "bagel": {
        "name": "런던베이글뮤지엄 잠실점",
        "chip": "베이글",
        "init": "런",
        "cat": "cafe",
        "var": "2",
        "why": "전국구 베이글 웨이팅 성지 — 롯데월드몰 1층",
        "info": "10:30~22:00(LO 21:30) · 주말 2시간+ 웨이팅(현장 등록만)",
        "kakao": KAKAO["bagel"],
        "google": GOOGLE["bagel"],
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
    "bagel": {
        "name": "London Bagel Museum Jamsil (런던베이글뮤지엄)",
        "chip": "Bagels",
        "init": "L",
        "cat": "cafe",
        "var": "2",
        "why": "Korea's most-queued bagel shop — Lotte World Mall 1F",
        "info": "10:30–22:00 (LO 21:30) · weekend waits 2 hrs+ (on-site list only)",
        "google": GOOGLE["bagel"],
    },
}


def c4_days(lang: str) -> list:
    S = SPOTS_KO if lang == "ko" else SPOTS_EN
    if lang == "ko":
        return [
            {
                "h": "Day 1",
                "cap": "도착 · 잠실 정착",
                "line": "잠실·방이 숙소 체크인 → 석촌호수·송리단길 → 방이동 먹자골목 저녁",
                "steps": [
                    {
                        "t": "14:00",
                        "d": "약 1시간",
                        "p": "잠실·방이 숙소 체크인",
                        "b": "숙소",
                        "s": "인천공항 → 공항철도+2·8호선 또는 리무진버스(공항철도 약 4,950원~ · 리무진 약 17,000원 안팎, 노선별 상이). 공연 3일 중 어느 회차든 도보권 베이스가 최강",
                    },
                    {
                        "t": "15:30",
                        "d": "약 2시간",
                        "p": "석촌호수·송리단길 산책",
                        "b": "카페",
                        "s": "도보 또는 8호선 1정거장 · 호수 한 바퀴 + 카페. 롯데월드타워 뷰 포토",
                        "w": "주말 인기 카페 오후 웨이팅, 평일 14~16시 한산",
                    },
                    {
                        "t": "18:30",
                        "d": "약 1.5시간",
                        "p": "방이동 먹자골목 저녁",
                        "b": "식당",
                        "s": "도보(방이역·올림픽공원역 권역) · 공연장 최근접 식당가에서 첫 저녁",
                        "w": "공연 주간(7/10~12)은 원정 팬 몰림 — 피크(18~20시) 웨이팅 여유 두기",
                        "spots": [S["bong"]],
                    },
                    {
                        "t": "21:00",
                        "d": "약 1시간",
                        "p": "석촌호수 야경 · 롯데월드타워 뷰",
                        "b": "관광",
                        "s": "도보 · 다음날 성지순례 동선 점검하며 마무리",
                    },
                ],
            },
            {
                "h": "Day 2",
                "cap": "성지순례 DAY — JYP 사옥 · 코엑스 · K-스타로드",
                "line": "JYP 사옥 외관 → 올림픽공원 답사 → Ktown4u 코엑스 → K-STAR ROAD",
                "note": "잠실 베이스의 숨은 장점 — JYP 신사옥(성내동)이 올림픽공원 동편 바로 옆. 오전 사옥, 오후 코엑스 굿즈, 저녁 압구정 K-스타로드.",
                "steps": [
                    {
                        "t": "10:00",
                        "d": "약 1.5시간",
                        "p": "JYP엔터테인먼트 사옥 (JYP Center)",
                        "b": "관광",
                        "s": "숙소에서 도보~버스 — 강동구 강동대로 205(올림픽수영장 입구 맞은편) · 무료(외부 관람) · 2018년부터 TWICE·Stray Kids·ITZY가 쓰는 본사. 외관·입구 포토 성지",
                        "w": "사옥 1층 카페 ‘쏘울컵(Soul Cup)’은 외부인 입장 불가(직원 전용 전환) — 외부 포토만. 건물 내부 진입 시도 금지",
                    },
                    {
                        "t": "11:30",
                        "d": "약 1.5시간",
                        "p": "올림픽공원 산책 + 공연장 사전 답사",
                        "b": "관광",
                        "s": "도보 · 무료 · KSPO돔 위치·게이트 확인, 평화의문·들꽃마루 포토 — 내일 동선 시뮬레이션",
                    },
                    {
                        "t": "13:00",
                        "d": "약 1시간",
                        "p": "방이동 점심",
                        "b": "식당",
                        "s": "도보 · 오후 원정 전 든든하게",
                    },
                    {
                        "t": "14:30",
                        "d": "약 2.5시간",
                        "p": "Ktown4u 코엑스 (케이타운포유)",
                        "b": "쇼핑",
                        "s": "8호선 몽촌토성 → 잠실 2호선 환승 → 삼성역 5·6번 출구(약 20~25분) · 코엑스 아티움 2~4F K-pop 복합공간 — 앨범·굿즈·팝업(강남구 영동대로 513)",
                        "w": "운영시간 상세 미공개 — 방문 전 ktown4u.com/stores 확인. 공연 주간 TWICE 코너 품절 빠를 수 있음",
                    },
                    {
                        "t": "17:30",
                        "d": "약 1.5시간",
                        "p": "K-STAR ROAD (압구정 한류스타거리)",
                        "b": "관광",
                        "s": "삼성역 → 압구정로데오역(수인분당선 환승, 약 20분) · 무료 · 압구정로데오역~청담사거리 약 1km, 스타 18팀 협업 ‘강남돌’ 아트토이 거리 — 갤러리아 앞 강남돌하우스가 출발점",
                        "w": "강남돌 라인업·위치는 변동 이력 있음 — TWICE 강남돌 위치는 현장 확인",
                    },
                    {
                        "t": "19:30",
                        "d": "약 1.5시간",
                        "p": "압구정·청담 저녁 후 복귀",
                        "b": "식당",
                        "s": "압구정로데오 → 잠실(수인분당선+2호선 약 30분) · 내일 공연 — 일찍 복귀해 컨디션 관리",
                    },
                ],
            },
            {
                "h": "Day 3",
                "cap": "공연 DAY (대기로 하루 대부분 소진)",
                "warn": "공연 시각 회차별 상이 — 7/10(금) 19:00 · 7/11(토) 18:00 · 7/12(일) 17:00. 굿즈 오픈런 + 입장 줄 + 종료 후 1만4천여 명 동시 퇴장 혼잡으로 하루 소진. 관광 배제.",
                "steps": [
                    {
                        "t": "09:30",
                        "d": "약 3.5시간",
                        "p": "KSPO돔 — 공식 MD 부스 오픈런",
                        "b": "공연장",
                        "s": "도보(잠실 베이스 최대 강점) · 인기 굿즈·포토카드는 오전 줄. 공식 운영시간은 공연 직전 공지 확인",
                        "w": "피날레 3연속 공연 — 원정 수요 집중, 인기 회차는 새벽~오전 줄. 품절 빠름",
                    },
                    {
                        "t": "13:00",
                        "d": "약 1시간",
                        "p": "올림픽공원역 인근 간단 점심",
                        "b": "식당",
                        "s": "도보 · 분식·김밥류 빠른 한 끼 — 대열 이탈 최소화",
                    },
                    {
                        "t": "14:30",
                        "d": "약 1.5시간",
                        "p": "숙소 복귀 — 응원봉·슬로건 준비",
                        "b": "숙소",
                        "s": "도보 · 도보권 숙소라 잠깐 복귀 가능. CANDYBONG 충전 확인",
                    },
                    {
                        "t": "16:00",
                        "d": "약 1.5시간",
                        "p": "KSPO돔 입장 줄 (회차별 시각 −2시간 기준)",
                        "b": "공연장",
                        "s": "도보 · 보안검색·티켓 확인. 좌석석도 1~2시간 전 도착 권장",
                        "w": "금요일 19시 회차는 퇴근시간 겹침 — 주변 도로·역 혼잡 가중",
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
                        "p": "종료 후 시간차 퇴장 · 방이동 야식",
                        "b": "식당",
                        "s": "도보 · 동시 퇴장 혼잡 — 근처에서 치맥으로 여운",
                        "w": "종료 직후 역·도로 1시간+ 혼잡. 도보권 야식으로 분산 후 복귀가 정답",
                    },
                ],
            },
            {
                "h": "Day 4",
                "cap": "굿즈·팝업 DAY — 성수 · 명동",
                "line": "성수 연무장길 팝업 → 명동 굿즈샵(위드뮤·뮤직코리아) → 명동 저녁",
                "warn": "공연 주간 팝업은 변동 — 출발 전 팝가(popga.co.kr)·팝플리(popply.co.kr)에서 ‘성수 팝업’ 당주 일정 확인. K-pop 팝업은 성수·더현대 서울에 집중되는 패턴.",
                "steps": [
                    {
                        "t": "10:30",
                        "d": "약 3시간",
                        "p": "성수동 연무장길 — 팝업 투어",
                        "b": "쇼핑",
                        "s": "8호선 잠실 → 2호선 성수역(약 25분) · 연무장길 일대가 팝업 밀집 코어 — K-pop·뷰티·패션 팝업이 주 단위 교체",
                        "w": "인기 팝업은 오픈 전 줄 + 입장 예약제 빈번 — 당일 아침 예약 오픈 확인",
                    },
                    {
                        "t": "13:30",
                        "d": "약 1.5시간",
                        "p": "성수 점심 — 감자탕 또는 베이커리",
                        "b": "식당",
                        "s": "도보 · 팝업 동선 한복판에서 해결",
                        "spots": [S["gamja"], S["onion"]],
                    },
                    {
                        "t": "15:30",
                        "d": "약 2.5시간",
                        "p": "명동 — K-pop 굿즈샵 투어",
                        "b": "쇼핑",
                        "s": "2호선 성수 → 을지로입구역(약 20분) 도보 명동 · 위드뮤 명동점 + 뮤직코리아 명동 2호점 — 앨범·공식 굿즈·포토카드 전문",
                        "w": "매장 운영시간은 시즌 변동 — withmuu.com·musickorea.com 직전 확인 권장",
                    },
                    {
                        "t": "18:30",
                        "d": "약 1.5시간",
                        "p": "명동 저녁",
                        "b": "식당",
                        "s": "도보 · 굿즈샵 동선 도보권에서 마무리",
                        "spots": [S["kyoja"], S["hadong"]],
                    },
                    {
                        "t": "20:30",
                        "d": "약 1시간",
                        "p": "남산 야경 또는 복귀",
                        "b": "관광",
                        "s": "명동 → 잠실 2·8호선 약 40분 · 체력 여유 시 N서울타워 야경, 아니면 복귀 휴식",
                    },
                ],
            },
            {
                "h": "Day 5",
                "cap": "롯데월드몰 마무리 · 출국",
                "line": "롯데월드몰 브런치·막판 쇼핑 → 체크아웃 · 공항 이동",
                "steps": [
                    {
                        "t": "09:30",
                        "d": "약 2시간",
                        "p": "롯데월드몰 — 브런치·막판 쇼핑",
                        "b": "쇼핑",
                        "s": "8호선·도보(송파구 올림픽로 300) · 출국 전 마지막 쇼핑·기념품",
                        "w": "런던베이글뮤지엄 잠실점(월드몰 1층)은 주말 2시간+ 웨이팅·현장 캐치테이블 등록만 가능 — 비행기 시간 빠듯하면 포기가 안전",
                        "spots": [S["bagel"]],
                    },
                    {
                        "t": "12:00",
                        "d": "약 1시간",
                        "p": "체크아웃 · 공항 이동",
                        "b": "숙소",
                        "s": "공항철도/리무진 · 잠실 → 인천공항 약 1시간 20분~1시간 40분 여유 잡기",
                    },
                ],
            },
        ]
    # ---- EN (draft 사실 동일 — 번역만, 신규 주장 0) ----
    return [
        {
            "h": "Day 1",
            "cap": "Arrival · settle in Jamsil",
            "line": "Check in around Jamsil/Bangi → Seokchon Lake & Songnidan-gil → Bangi-dong dinner",
            "steps": [
                {
                    "t": "2:00 PM",
                    "d": "~1 hr",
                    "p": "Check in around Jamsil/Bangi",
                    "b": "Stay",
                    "s": "Incheon Airport → AREX + Line 2/8, or limousine bus (AREX from approx. 4,950 KRW · limousine approx. 17,000 KRW, varies by route). A walkable base wins for any of the 3 shows",
                },
                {
                    "t": "3:30 PM",
                    "d": "~2 hrs",
                    "p": "Seokchon Lake & Songnidan-gil stroll",
                    "b": "Café",
                    "s": "On foot or 1 stop on Line 8 · a lap of the lake + a café. Lotte World Tower view photo spot",
                    "w": "Popular cafés have afternoon waits on weekends; quiet on weekdays 2–4 PM",
                },
                {
                    "t": "6:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Dinner in the Bangi-dong food alley",
                    "b": "Food",
                    "s": "On foot (Bangi Stn / Olympic Park Stn area) · first dinner in the dining strip closest to the venue",
                    "w": "Show week (Jul 10–12) draws traveling fans — allow extra wait time at the 6–8 PM peak",
                    "spots": [S["bong"]],
                },
                {
                    "t": "9:00 PM",
                    "d": "~1 hr",
                    "p": "Seokchon Lake at night · Lotte World Tower view",
                    "b": "Sights",
                    "s": "On foot · wind down while checking tomorrow's pilgrimage route",
                },
            ],
        },
        {
            "h": "Day 2",
            "cap": "Pilgrimage DAY — JYP HQ · COEX · K-Star Road",
            "line": "JYP Center exterior → Olympic Park recon → Ktown4u COEX → K-STAR ROAD",
            "note": "A hidden perk of the Jamsil base — the new JYP HQ (Seongnae-dong) sits just east of Olympic Park. HQ in the morning, COEX goods in the afternoon, Apgujeong K-Star Road in the evening.",
            "steps": [
                {
                    "t": "10:00 AM",
                    "d": "~1.5 hrs",
                    "p": "JYP Entertainment HQ (JYP Center)",
                    "b": "Sights",
                    "s": "Walk or short bus ride — 205 Gangdong-daero, Gangdong-gu (opposite the Olympic Pool entrance) · free (exterior only) · home base of TWICE, Stray Kids & ITZY since 2018. Exterior & entrance photo spot",
                    "w": "The 1F café 'Soul Cup' no longer admits outside visitors (staff only) — exterior photos only. Do not attempt to enter the building",
                },
                {
                    "t": "11:30 AM",
                    "d": "~1.5 hrs",
                    "p": "Olympic Park walk + venue recon",
                    "b": "Sights",
                    "s": "On foot · free · confirm KSPO Dome location & gates, World Peace Gate & wildflower hill photos — simulate tomorrow's route",
                },
                {
                    "t": "1:00 PM",
                    "d": "~1 hr",
                    "p": "Lunch in Bangi-dong",
                    "b": "Food",
                    "s": "On foot · fuel up before the afternoon run",
                },
                {
                    "t": "2:30 PM",
                    "d": "~2.5 hrs",
                    "p": "Ktown4u COEX",
                    "b": "Shopping",
                    "s": "Line 8 Mongchontoseong → Jamsil, transfer to Line 2 → Samseong Stn Exit 5/6 (approx. 20–25 min) · K-pop complex on COEX Artium 2–4F — albums, goods, pop-ups (513 Yeongdong-daero, Gangnam-gu)",
                    "w": "Detailed opening hours unpublished — check ktown4u.com/stores before visiting. TWICE sections can sell out fast in show week",
                },
                {
                    "t": "5:30 PM",
                    "d": "~1.5 hrs",
                    "p": "K-STAR ROAD (Apgujeong)",
                    "b": "Sights",
                    "s": "Samseong Stn → Apgujeong Rodeo Stn (Suin-Bundang transfer, approx. 20 min) · free · approx. 1 km from Apgujeong Rodeo to Cheongdam crossing, 'GangnamDol' art-toy street with 18 K-pop acts — start at GangnamDol Haus by Galleria",
                    "w": "GangnamDol lineup & positions have changed over time — confirm the TWICE figure's spot on site",
                },
                {
                    "t": "7:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Dinner in Apgujeong/Cheongdam, then back",
                    "b": "Food",
                    "s": "Apgujeong Rodeo → Jamsil (Suin-Bundang + Line 2, approx. 30 min) · show tomorrow — head back early and rest up",
                },
            ],
        },
        {
            "h": "Day 3",
            "cap": "Show DAY (queues eat most of the day)",
            "warn": "Start time differs by date — Fri Jul 10 7 PM · Sat Jul 11 6 PM · Sun Jul 12 5 PM. Goods open-run + entry queue + ~14,000 people exiting at once eat the whole day. No sightseeing.",
            "steps": [
                {
                    "t": "9:30 AM",
                    "d": "~3.5 hrs",
                    "p": "KSPO Dome — official MD booth open-run",
                    "b": "Venue",
                    "s": "On foot (the Jamsil base's biggest edge) · popular goods & photocards queue from the morning. Official booth hours are announced just before the show",
                    "w": "3-night tour finale — traveling demand peaks; popular dates queue from dawn. Sellouts are fast",
                },
                {
                    "t": "1:00 PM",
                    "d": "~1 hr",
                    "p": "Quick lunch near Olympic Park Stn",
                    "b": "Food",
                    "s": "On foot · fast snack-bar / gimbap bite — minimize time away from the queue",
                },
                {
                    "t": "2:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Back to lodging — light stick & slogan prep",
                    "b": "Stay",
                    "s": "On foot · a walkable base lets you pop back. Check your CANDYBONG charge",
                },
                {
                    "t": "4:00 PM",
                    "d": "~1.5 hrs",
                    "p": "KSPO Dome entry queue (2 hrs before your date's start)",
                    "b": "Venue",
                    "s": "On foot · security & ticket checks. Even seated tickets: arrive 1–2 hrs early",
                    "w": "The Friday 7 PM date overlaps rush hour — roads & stations around the park get worse",
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
                    "w": "Stations & roads stay jammed 1 hr+ right after. Walkable late-night food, then back — that's the play",
                },
            ],
        },
        {
            "h": "Day 4",
            "cap": "Goods & pop-up DAY — Seongsu · Myeongdong",
            "line": "Seongsu Yeonmujang-gil pop-ups → Myeongdong goods shops (Withmuu · Music Korea) → Myeongdong dinner",
            "warn": "Show-week pop-ups change weekly — before heading out, check that week's 'Seongsu pop-ups' on Popga (popga.co.kr) / Popply (popply.co.kr). K-pop pop-ups cluster in Seongsu & The Hyundai Seoul.",
            "steps": [
                {
                    "t": "10:30 AM",
                    "d": "~3 hrs",
                    "p": "Seongsu Yeonmujang-gil — pop-up tour",
                    "b": "Shopping",
                    "s": "Line 8 Jamsil → Line 2 Seongsu Stn (approx. 25 min) · Yeonmujang-gil is the pop-up core — K-pop, beauty & fashion pop-ups rotate weekly",
                    "w": "Popular pop-ups queue before opening + often use entry reservations — check the booking drop that morning",
                },
                {
                    "t": "1:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Seongsu lunch — gamjatang or a bakery",
                    "b": "Food",
                    "s": "On foot · eat right on the pop-up route",
                    "spots": [S["gamja"], S["onion"]],
                },
                {
                    "t": "3:30 PM",
                    "d": "~2.5 hrs",
                    "p": "Myeongdong — K-pop goods shop tour",
                    "b": "Shopping",
                    "s": "Line 2 Seongsu → Euljiro 1-ga Stn (approx. 20 min), walk into Myeongdong · Withmuu Myeongdong + Music Korea Myeongdong 2nd — albums, official goods & photocards",
                    "w": "Store hours vary by season — check withmuu.com / musickorea.com right before you go",
                },
                {
                    "t": "6:30 PM",
                    "d": "~1.5 hrs",
                    "p": "Myeongdong dinner",
                    "b": "Food",
                    "s": "On foot · wrap up within walking distance of the goods shops",
                    "spots": [S["kyoja"], S["hadong"]],
                },
                {
                    "t": "8:30 PM",
                    "d": "~1 hr",
                    "p": "Namsan night view, or head back",
                    "b": "Sights",
                    "s": "Myeongdong → Jamsil, Lines 2/8, approx. 40 min · N Seoul Tower night view if you have energy left — otherwise rest up",
                },
            ],
        },
        {
            "h": "Day 5",
            "cap": "Lotte World Mall finish · departure",
            "line": "Lotte World Mall brunch & last shopping → check-out · airport",
            "steps": [
                {
                    "t": "9:30 AM",
                    "d": "~2 hrs",
                    "p": "Lotte World Mall — brunch & last shopping",
                    "b": "Shopping",
                    "s": "Line 8 / on foot (300 Olympic-ro, Songpa-gu) · final shopping & souvenirs before the flight",
                    "w": "London Bagel Museum Jamsil (mall 1F) has 2 hr+ weekend waits, on-site CatchTable list only — skip it if your flight is tight",
                    "spots": [S["bagel"]],
                },
                {
                    "t": "12:00 PM",
                    "d": "~1 hr",
                    "p": "Check out · to the airport",
                    "b": "Stay",
                    "s": "AREX / limousine · Jamsil → Incheon Airport approx. 1 hr 20 min–1 hr 40 min — leave a buffer",
                },
            ],
        },
    ]


def build_c4_panel(lang: str) -> str:
    days = c4_days(lang)
    if lang == "ko":
        head = (
            '<div class="box"><h2 id="sec-c4" style="font-weight:600;font-size:14px;margin:0 0 0">4박5일 표준 코스</h2>'
            '<p class="scap" style="margin:4px 0 0">공연장 도보권 잠실·방이 베이스 — Day1 정착, Day2 JYP 성지순례·코엑스·K-스타로드, '
            "Day3 공연, Day4 성수 팝업·명동 굿즈, Day5 롯데월드몰·출국. 실제 장소이며 가격은 대략 시세입니다. 실시간 예약가는 예약처에서 확인하세요.</p>"
            '<p class="scap w5-basenote" style="margin:2px 0 0;font-weight:600">잠실 베이스 기준</p>'
            '<p class="crs-sum">잠실 베이스 4박. 동선: Day1 도착·정착 → Day2 성지순례·굿즈 원정 → <b>Day3 공연</b> → Day4 팝업·굿즈 → Day5 출국. '
            '<span style="color:var(--muted)">대략 예산: 숙박 4박 약 $228~488(아래 ‘함께 묵는 숙소’ 시세 기준) · 항공·티켓·식비 별도.</span></p>'
            f'<a class="showday-jump" data-w6-course-jump="1" href="#showday-s4">{JUMP_SVG}공연 당일 한눈에 보기 →</a>\n'
        )
    else:
        head = (
            '<div class="box"><h2 id="sec-c4" style="font-weight:600;font-size:14px;margin:0 0 0">4N5D Standard Course</h2>'
            '<p class="scap" style="margin:4px 0 0">A Jamsil/Bangi base within walking distance of the venue — Day 1 settle in, '
            "Day 2 JYP pilgrimage · COEX · K-Star Road, Day 3 the show, Day 4 Seongsu pop-ups & Myeongdong goods, Day 5 Lotte World Mall & departure. "
            "Real places; prices are rough estimates — confirm live rates with the booking site.</p>"
            '<p class="scap w5-basenote" style="margin:2px 0 0;font-weight:600">Jamsil base reference</p>'
            '<p class="crs-sum">Jamsil base, 4 nights. Flow: Day 1 arrive & settle → Day 2 pilgrimage & goods run → <b>Day 3 show</b> → '
            'Day 4 pop-ups & goods → Day 5 departure. <span style="color:var(--muted)">Rough budget: 4 nights\' lodging approx. $228–488 '
            "(based on the 'Where to stay' rates below) · flights, tickets & meals not included.</span></p>"
            f'<a class="showday-jump" data-w6-course-jump="1" href="#showday-s4">{JUMP_SVG}Show day at a glance →</a>\n'
        )
    body = "\n".join(
        [
            day_acc(days[0], lang, open_=True),
            day_acc(days[1], lang),
            showday(days[2], lang),
            day_acc(days[3], lang),
            day_acc(days[4], lang),
        ]
    )
    return (
        '<div class="sl-panel sl-4" data-w7-c4="1"><!--W5RULE: day 카드 임계 룰 — 총 3일 이하 코스 flat / 4일+ 코스 day-acc 아코디언. '
        "공연 당일 상세(day-card--show)는 길이 무관 항상 flat 노출-->\n"
        + head
        + body
        + "\n</div>\n  </div>\n  "
    )


# ---------------------------------------------------------------- 패치 ----
def sub_required(
    s: str, old: str, new: str, label: str, count: int | None = None
) -> str:
    n = s.count(old)
    if n == 0:
        if new in s:
            return s  # 이미 적용 (멱등)
        raise SystemExit(
            f"FAIL {label}: 패턴 부재 — divergence 의심 (FLR-20260611-TEC-001)"
        )
    if count is not None and n != count:
        raise SystemExit(f"FAIL {label}: 기대 {count}건, 실제 {n}건")
    return s.replace(old, new)


def patch_course(path: Path, lang: str) -> None:
    s = path.read_text(encoding="utf-8")

    # ---- #6 sl-4 패널 교체 (positional — 멱등) ----
    a = s.find('<div class="sl-panel sl-4"')
    b = s.find('<div class="sl-panel sl-7"')
    if a < 0 or b < 0 or b <= a:
        raise SystemExit(f"FAIL c4-panel {lang}: sl-4/sl-7 마커 부재")
    s = s[:a] + build_c4_panel(lang) + s[b:]

    # ---- #7-① 청와옥 중복 카드 제거 (showday 야식 step rail — 같은 뷰 2회 노출) ----
    anchor = "퇴장·야식" if lang == "ko" else "Exit · late-night food"
    dupname = "청와옥" if lang == "ko" else "Cheongwaok"
    i = s.find(anchor)
    if i < 0:
        raise SystemExit(f"FAIL dup-card {lang}: anchor 부재")
    j = s.find('<div class="spot-rail">', i)
    if 0 < j < i + 3000:
        k = s.find("</div></div></div>", j)  # 단일 카드 rail 종단 (card>pbody>rail)
        rail = s[j : k + len("</div></div></div>")]
        if dupname in rail and rail.count('<div class="spot-card">') == 1:
            s = s[:j] + s[k + len("</div></div></div>") :]
        elif dupname in rail:
            raise SystemExit(
                f"FAIL dup-card {lang}: rail 카드 수 예상 밖 — 수동 확인 필요"
            )
    # 멱등: rail 이미 제거됐으면 no-op

    # ---- #7-②④ 기존 카드 why 정직화 — 'ptag · 주소' / 'ptag 동어반복' → 정보줄·제거 ----
    s = re.sub(
        r'<div class="ptag">([^<]+)</div><div class="pwhy">\1 · ([^<]+)</div>',
        r'<div class="ptag">\1</div><div class="pinfo">\2</div>',
        s,
    )
    s = re.sub(
        r'<div class="ptag">([^<]+)</div><div class="pwhy">\1</div>',
        r'<div class="ptag">\1</div>',
        s,
    )

    # ---- #9 ckstep 44×44 실측화 (시각 22 ::before 박스) + psrc min-width 44 ----
    s = sub_required(
        s,
        ".ckstep{appearance:none;-webkit-appearance:none;width:22px;height:22px;margin:1px 0 0;"
        "border:1.8px solid #D9B3C2;border-radius:var(--r-s);background:var(--card);cursor:pointer;"
        "flex:0 0 auto;position:relative;transition:background .15s,border-color .15s}",
        ".ckstep{appearance:none;-webkit-appearance:none;width:44px;height:44px;margin:-10px -7px -11px;"
        "border:0;background:transparent;cursor:pointer;flex:0 0 auto;position:relative}",
        f"ckstep-base {lang}",
    )
    s = sub_required(
        s,
        '.ckstep::before{content:"";position:absolute;left:50%;top:50%;width:44px;height:44px;'
        "transform:translate(-50%,-50%)}",
        '.ckstep::before{content:"";position:absolute;left:50%;top:50%;width:22px;height:22px;'
        "transform:translate(-50%,-50%);box-sizing:border-box;border:1.8px solid #D9B3C2;"
        "border-radius:var(--r-s);background:var(--card);transition:background .15s,border-color .15s}",
        f"ckstep-box {lang}",
    )
    s = sub_required(
        s,
        ".ckstep:checked{background:var(--rose);border-color:#E84A7F}",
        ".ckstep:checked::before{background:var(--rose);border-color:#E84A7F}",
        f"ckstep-checked {lang}",
    )
    s = sub_required(
        s,
        ".ckstep{border-color:#5A3A47;background:var(--card)}",
        ".ckstep::before{border-color:#5A3A47;background:var(--card)}",
        f"ckstep-dark {lang}",
    )
    s = sub_required(
        s,
        '.ckstep:checked::after{content:"";position:absolute;left:7px;top:3px;width:5px;height:10px;'
        "border:solid #fff;border-width:0 2px 2px 0;transform:rotate(45deg)}",
        '.ckstep:checked::after{content:"";position:absolute;left:18px;top:14px;width:5px;height:10px;'
        "border:solid #fff;border-width:0 2px 2px 0;transform:rotate(45deg)}",
        f"ckstep-mark {lang}",
    )
    s = sub_required(
        s,
        ".ckstep:focus-visible{outline:2px solid #E84A7F;outline-offset:2px}",
        ".ckstep:focus-visible{outline:none}.ckstep:focus-visible::before{outline:2px solid #E84A7F;outline-offset:2px}",
        f"ckstep-focus {lang}",
    )
    s = sub_required(
        s,
        ".psrc{align-self:flex-end;margin-top:auto;font-size:12px;font-weight:600;color:var(--accent);"
        "text-decoration:none;min-height:44px;display:inline-flex;align-items:center}",
        ".psrc{align-self:flex-end;margin-top:auto;font-size:12px;font-weight:600;color:var(--accent);"
        "text-decoration:none;min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center}",
        f"psrc {lang}",
    )
    s = sub_required(
        s,
        ".psrc-row .psrc-g{font-size:12px;font-weight:600;color:var(--muted);text-decoration:none;"
        "min-height:44px;display:inline-flex;align-items:center}",
        ".psrc-row .psrc-g{font-size:12px;font-weight:600;color:var(--muted);text-decoration:none;"
        "min-height:44px;min-width:44px;display:inline-flex;align-items:center;justify-content:center}",
        f"psrc-g {lang}",
    )

    # ---- #7 pinfo CSS (1회 주입) ----
    if "/*W7R44C*/" not in s:
        s = s.replace(
            "</style>",
            "/*W7R44C*/.pinfo{font-size:12px;color:var(--muted);line-height:1.35}</style>",
            1,
        )

    # ---- #11 wait-note 표기 1종 통일 (ko: h/시간 혼용 → 시간) ----
    if lang == "ko":

        def _fix_note(m: re.Match) -> str:
            t = m.group(0)
            t = (
                t.replace("1~2h", "1~2시간")
                .replace("1h+", "1시간+")
                .replace("2h+", "2시간+")
            )
            return t

        s = re.sub(r'<div class="wait-note">.*?</div>', _fix_note, s, flags=re.S)

    path.write_text(s, encoding="utf-8")
    print(f"  course {lang or 'ko'}: OK")


HOME_RADIUS_MAP = [
    (".abadge", "9px", "var(--r-m)"),
    (".oshow", "9px", "var(--r-m)"),
    (".tabs>label", "9px", "var(--r-m)"),
    (".crs-tabs label", "9px", "var(--r-m)"),
    (".stay22-btn", "9px", "var(--r-m)"),
    (".step-img", "9px", "var(--r-m)"),
    (".hf-chip", "9px", "var(--r-s)"),
    (".btn", "10px", "var(--r-m)"),
    (".news", "10px", "var(--r-m)"),
    (".news-soon", "10px", "var(--r-m)"),
    (".ytfacade", "10px", "var(--r-m)"),
    (".ytframe", "10px", "var(--r-m)"),
    (".langpick .langmenu", "10px", "var(--r-m)"),
    (".spot-card", "10px", "var(--r-m)"),
    (".hf-search input", "10px", "var(--r-s)"),
    (".langpick .langmenu .lng", "6px", "var(--r-s)"),
    (".dday", "5px", "var(--r-s)"),
    (".srclink", "7px", "var(--r-s)"),
    (".wait-note", "7px", "var(--r-s)"),
]


def patch_home(path: Path, lang: str) -> None:
    s = path.read_text(encoding="utf-8")

    # ---- #8 radius 토큰 정의 (이벤트 페이지 체계 동일값) + homeviz 구토큰 수렴 ----
    s = sub_required(
        s,
        "--r-sm:6px;--r-md:10px;--r-lg:16px",
        "--r-sm:8px;--r-md:12px;--r-lg:12px;--r-s:8px;--r-m:12px;--r-pill:999px",
        f"home-tokens {lang}",
    )
    # ---- #8 비정합 radius → 토큰 (선택자 스코프 치환) ----
    for sel, old, new in HOME_RADIUS_MAP:
        pat = re.compile(re.escape(sel) + r"\{[^}]*?\}")
        decl_old = f"border-radius:{old}"
        decl_new = f"border-radius:{new}"
        rules = list(pat.finditer(s))
        if not rules:
            # locale 홈에 해당 모듈 자체 부재 (ko 전용 패치 레이어 등) — 정직 스킵 로그
            print(f"    skip {lang}: {sel} 모듈 부재")
            continue
        if any(decl_old in r.group(0) for r in rules):
            s = pat.sub(
                lambda m: (
                    m.group(0).replace(decl_old, decl_new)
                    if decl_old in m.group(0)
                    else m.group(0)
                ),
                s,
            )
        elif any(decl_new in r.group(0) for r in rules):
            pass  # 이미 적용 (멱등)
        else:
            # 선택자는 있으나 radius decl 자체가 없는 변형 (다크 오버라이드 등만 존재)
            print(f"    skip {lang}: {sel} radius decl 부재")

    # ---- #12 로고 attr = 실비율 (206:90 → 87×38, css 87×38 · natural 비율 일치) ----
    s = re.sub(r'(class="logo"[^>]*?)width="119"', r'\1width="87"', s)
    if 'class="logo"' in s and 'width="87"' not in s:
        raise SystemExit(f"FAIL logo-attr {lang}")

    path.write_text(s, encoding="utf-8")
    print(f"  home {lang or 'ko'}: OK")


def main() -> None:
    for lang in RICH:
        p = DIST / lang / COURSE if lang else DIST / COURSE
        patch_course(p, lang or "ko")
    for lang in LOCALES:
        p = DIST / lang / HOME if lang else DIST / HOME
        patch_home(p, lang or "ko")
    print("WAVE7 R44 patch done.")


if __name__ == "__main__":
    sys.exit(main())
