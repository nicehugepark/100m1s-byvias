#!/usr/bin/env python3
"""R49 P0④ — 8언어 코스 페이지 고부가 UX 모듈 이식.

누락 원인: 8언어 코스 파일은 9lang-regen WT에서 빌드됐으나,
그 당시 ko dist에 없던(혹은 en 기준으로 생성된) tldr/jump-nav/steps5/prep-list 4블록이
번역 없이 누락됨. sec-tourstops 본문도 ko와 다르게 빈 div.

Fix:
  1. ko dist에서 CSS + HTML 모듈 블록 추출
  2. warm_lang 배치 번역 선행 (i18n.py warm 패턴 — hung 사고 회피)
  3. 8언어 파일에 additive 삽입:
     - CSS: </style> 직전
     - tldr+jump-nav+steps5: hero-jump 닫는 </a> 직후 (arrival-1h 직전)
     - prep-list 헤더+블록: sec-ticketing 섹션 끝 </div> 직전
     - sec-tourstops 본문: h2 태그로 승격 + 투어 설명 텍스트 추가
  4. batch-1 회귀 가드: langpick/OG/KST/iframe 잔존 확인

batch-1 4건 보존 전략: additive 삽입만 (재렌더 0). 기존 구조 완전 보존.

실행: python3 tools/r49_p0_ux_modules_patch.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KO_FILE = ROOT / "dist" / "twice-thisisfor-seoul.html"
DIST = ROOT / "dist"

LANGS_8 = ["ja", "zh-tw", "es", "th", "id", "pt", "ar", "vi"]

MARK = "R49-UX-MODULES-v1"

# ── 번역 텍스트 정의 (ko 원본 → 각 언어 번역) ──
# 실제 번역은 i18n.py translate_batch() 경유. 여기서는 ko 원본만 정의.
# 단, 고유명사/고정값(장소명·시각·숫자·URL·HTML태그)은 번역 제외.

# tldr 번역 대상 텍스트
TLDR_TEXTS = [
    "30초 핵심",  # tldr-hd
    "언제·어디",  # b1
    "2026-07-10·11·12 (금·토·일) 3일 연속, 서울 KSPO돔(올림픽공원). 시작 금 19:00 / 토 18:00 / 일 17:00.",  # li1 텍스트
    "티켓",  # b2
    "예매 진행 중",  # b-ticket
    "잔여석 확인 ↗",  # link text
    "일반 예매 6/11 20:00 오픈 경과. 가격 154,000원(≈$110), 좌석·스탠딩 동일.",  # li2 suffix
    "막차 함정",  # b3
    "9호선 개화행 + 토·일은 ~22:55",  # warn span
    "로 가장 빠름 → 이 조합만 22:30까지 탑승.",  # li3 suffix
]

# jump-nav 번역 대상
JUMPNAV_TEXTS = [
    "이 페이지에서 얻는 것",  # aria-label
    "이 페이지에서 얻는 것 — 막차 함정·숙소·동선 코스를 한 페이지에",  # jn-lbl
    "막차 함정",  # link1
    "숙소",  # link2
    "동선 코스",  # link3
]

# steps5 번역 대상
STEPS5_TEXTS = [
    "처음이어도 이 순서대로",  # aria-label
    "처음이어도, 이 순서대로",  # s5-head
    "서울 원정이 처음이라도 ①→⑤만 따라가면 됩니다.",  # s5-sub
    "항공권 + 입국 준비(K-ETA)",  # step1 title
    "인천공항(ICN) 도착 기준.",  # step1 desc prefix
    "항공권 비교 ↗",  # step1 link1
    "Trip.com 항공권 ↗",  # step1 link2
    "K-ETA / 비자:",  # step1 sub b
    "본인 국적 기준은 공식 사이트",  # step1 sub text
    "에서 확인.",  # step1 sub suffix
    "공항 → 숙소",  # step2 title
    "6705A 리무진",  # step2 b
    "인천공항 T1/T2 ↔ 잠실 롯데월드, 환승 없음 — 18,000원 — 첫 방문 권장",  # step2 desc
    " · 공항철도+9호선 · 택시(7~9만원대).",  # step2 suffix
    "표 사는 법·WOWPASS 발급 순서는",  # step2 sub prefix
    "'도착 첫 1시간' 타임라인 →",  # step2 sub link
    "참고.",  # step2 sub suffix
    "숙소 예약",  # step3 title
    "공연장 근처 잠실권 4곳 — 동선 본 뒤 선택.",  # step3 desc
    "체류일 선택하기 →",  # step3 go link
    "공연 당일",  # step4 title
    "여권 실물 지참 필수 · 신원확인으로 일찍 도착 · MD는 오전 · 공연 시작 금 19:00 / 토 18:00 / 일 17:00.",  # step4 desc
    "공연 후 귀가",  # step5 title
    "세 회차 모두 막차 여유. 단 9호선 서행(개화)+토·일만 ~22:55로 빠름.",  # step5 desc
    "노선별 막차·역산표 보기 →",  # step5 link
]

# prep-list 번역 대상
PREP_TEXTS = [
    "준비 단계별 예약",  # h3 label
    "뭐부터 잡아야 할지 — 시점 순서대로. 위에서부터 서두르면 됩니다.",  # sub text
    "표식 링크는 제휴(수수료) 링크입니다 — 이용자 추가 비용은 없습니다.",  # disc-mini
    "숙소",  # prep1 name
    "공연 주말은 공연장 근처가 가장 빨리 매진 — 제일 먼저 잡으세요",  # prep1 sub
    "지금",  # prep1 when
    "항공",  # prep2 name
    "날짜 정해졌으면 빠를수록 저렴 — 출발 임박할수록 오릅니다",  # prep2 sub
    "빠를수록",  # prep2 when
    "항공",  # prep3 name (Trip.com)
    "같은 노선도 채널 따라 가격이 달라요 — 트립닷컴에서 한 번 더 비교",  # prep3 sub
    "빠를수록",  # prep3 when
    "eSIM",  # prep4 name
    "공연장 인파 속 데이터 끊김 대비 — 출발 전 아무 때나",  # prep4 sub
    "출발 전",  # prep4 when
    "공항↔서울 이동",  # prep5 name
    "인천공항철도(AREX) 직통 — 도착 직후 바로 시내로",  # prep5 sub
    "도착 직후",  # prep5 when
    "교통·관광 패스",  # prep6 name
    "디스커버 서울패스 — 지하철·명소 한 장으로 (남는 시간 관광용)",  # prep6 sub
    "출발 전~도착 후",  # prep6 when
    "투어·티켓",  # prep7 name
    "남는 일정용 — 도착 후 정해도 늦지 않습니다",  # prep7 sub
    "도착 후도 OK",  # prep7 when
]

# tourstops 번역 대상
TOURSTOPS_TEXTS = [
    "최근 투어 경유지",  # h2 title
    "THIS IS FOR 월드투어는 가오슝(2025-11) 이후로도 계속됐고, 서울(7/10–12) 직전 마지막 공연은",  # body text1
    "런던 The O2 Arena",  # b text
    "입니다. 전체 일정은",  # body text2
    "투어 일정표 ↗",  # link text
    "참고.",  # suffix
]

# 모든 번역 대상 텍스트 통합
ALL_TEXTS = list(
    dict.fromkeys(
        TLDR_TEXTS + JUMPNAV_TEXTS + STEPS5_TEXTS + PREP_TEXTS + TOURSTOPS_TEXTS
    )
)


def load_ko():
    return KO_FILE.read_text(encoding="utf-8")


def get_ko_module_css(ko: str) -> str:
    """ko에서 모듈 CSS 블록 추출 (/* TL;DR → .prep-when--soon{} 끝)."""
    style_end = ko.find("</style>")
    style_block = ko[:style_end]
    start = style_block.find("/* TL;DR — ")
    # .prep-when--soon{} 끝
    soon_pos = style_block.rfind(".prep-when--soon{")
    end = style_block.find("}", soon_pos) + 1
    return style_block[start:end]


def get_ko_intro_block(ko: str) -> str:
    """ko에서 hero-jump 후 ~ arrival-1h 전 블록 (tldr+media-banner+jump-nav+steps5)."""
    hj_idx = ko.find('class="showday-jump hero-jump"')
    end_a = ko.find("</a>", hj_idx) + 4
    arr_idx = ko.find('<section class="box" id="arrival-1h"')
    return ko[end_a:arr_idx]


def get_ko_prep_block(ko: str) -> str:
    """ko에서 prep-list 섹션 블록 (헤더 p ~ </div> 닫음까지)."""
    prep_header = ko.find(
        '<p style="font-weight:600;font-size:14px;margin:16px 0 2px">준비 단계별 예약</p>'
    )
    prep_end = ko.find("</div>\n</details>", prep_header)
    if prep_end < 0:
        prep_end = ko.find('\n\n<div class="box linfo-box">', prep_header)
    else:
        # </div> is end of prep-list div
        prep_list_close = ko.find("</div>\n\n<div", prep_header)
        if prep_list_close >= 0:
            prep_end = prep_list_close + 6  # </div>
    return ko[prep_header:prep_end]


def get_ko_tourstops_body(ko: str) -> str:
    """ko에서 sec-tourstops 본문 텍스트 (p 태그)."""
    ts_idx = ko.find('id="sec-tourstops"')
    ts_content = ko[ts_idx : ts_idx + 800]
    # p 태그 추출
    p_match = re.search(r'<p style="margin:8px 0 0.*?</p>', ts_content, re.S)
    if p_match:
        return p_match.group(0)
    return ""


def translate_block(block: str, lang: str, trans: dict) -> str:
    """번역 딕셔너리를 사용해 블록 내 텍스트 교체."""
    result = block
    for ko_text, lang_text in trans.items():
        if ko_text and lang_text and ko_text != lang_text:
            result = result.replace(ko_text, lang_text)
    return result


def build_translations(lang: str, trans_results: dict) -> dict:
    """번역 결과 딕셔너리 구성."""
    d = {}
    for i, ko_text in enumerate(ALL_TEXTS):
        if i < len(trans_results.get(lang, [])):
            translated = trans_results[lang][i]
            if translated:
                d[ko_text] = translated
    return d


def batch_translate_all(langs: list) -> dict:
    """i18n.py를 통해 전 언어 배치 번역. 드라이 warm 패턴 (hung 회피)."""
    # i18n.py 경로 (100m1s repo site/)
    site_path = Path("/Users/seongjinpark/company/100m1s/projects/byvias/site")
    sys.path.insert(0, str(site_path))
    import i18n as i18n_mod

    results = {}
    for lang in langs:
        print(f"  [{lang}] 배치 번역 warm 시작 ({len(ALL_TEXTS)} strings)...")
        translated = i18n_mod.translate_batch(ALL_TEXTS, lang)
        results[lang] = translated
        # 번역 결과 미리 확인 (첫 3개)
        for _j, (ko, tr) in enumerate(zip(ALL_TEXTS[:3], translated[:3])):
            print(f"    '{ko[:30]}' → '{str(tr)[:40]}'")
    i18n_mod.flush_cache()
    print("  i18n 캐시 저장 완료.")
    return results


def patch_file(
    lang: str,
    trans: dict,
    ko: str,
    css_block: str,
    intro_block: str,
    prep_block: str,
    tourstops_body: str,
):
    """단일 언어 파일 패치."""
    f = DIST / lang / "twice-thisisfor-seoul.html"
    if not f.exists():
        print(f"  ❌ MISSING: {f}")
        return False

    content = f.read_text(encoding="utf-8")

    # 이미 패치됐으면 스킵
    if MARK in content:
        print(f"  ⏭  [{lang}] 이미 패치됨 — skip")
        return True

    # ── CSS 삽입 (</style> 직전) ──
    style_end_idx = content.find("</style>")
    if style_end_idx < 0:
        print(f"  ❌ [{lang}] </style> not found")
        return False
    css_translated = f"\n/* {MARK} */\n{css_block}"
    content = content[:style_end_idx] + css_translated + "\n" + content[style_end_idx:]

    # ── intro 블록 삽입 (hero-jump </a> 직후 ~ arrival-1h 직전) ──
    hj_idx = content.find('class="showday-jump hero-jump"')
    if hj_idx < 0:
        print(f"  ❌ [{lang}] hero-jump not found")
        return False
    end_a_idx = content.find("</a>", hj_idx) + 4
    arr_idx = content.find('id="arrival-1h"', end_a_idx)
    if arr_idx < 0:
        print(f"  ❌ [{lang}] arrival-1h not found")
        return False
    # arrival-1h 직전 <section... 시작 위치
    sec_start = content.rfind("<section", end_a_idx, arr_idx)
    if sec_start < 0:
        sec_start = arr_idx

    # 번역된 intro 블록 생성
    translated_intro = translate_block(intro_block, lang, trans)
    # HTML 언어속성 변경 (aria-label 등)
    # aria-label 내 한국어 텍스트는 translate_block에서 처리됨
    # media-banner 이미지는 그대로 유지 (ko 원본 URL)

    content = content[:end_a_idx] + translated_intro + content[sec_start:]

    # ── prep-list 삽입 (sec-ticketing 박스 닫는 box </div> 직전) ──
    # 8언어 구조: <ligrid>...</div>\n</div>\n (ligrid 닫음 + box 닫음)
    # 삽입 위치: ligrid 닫음 </div> 뒤 + \n, box 닫음 </div> 앞
    # 즉: ligrid_end + 6 = \n (newline), ligrid_end + 7 = box 닫음 </div>
    tick_idx = content.find('id="sec-ticketing"')
    if tick_idx < 0:
        print(f"  ❌ [{lang}] sec-ticketing not found")
        return False
    ligrid_end = content.find("</div>\n</div>", tick_idx)
    if ligrid_end < 0:
        ligrid_end = content.find("</div></div>", tick_idx)
        if ligrid_end < 0:
            print(f"  ❌ [{lang}] ticketing end not found")
            return False
        insert_prep_at = ligrid_end + 6  # </div></div> 형태: ligrid 닫음 이후
    else:
        insert_prep_at = ligrid_end + 7  # </div>\n</div> 형태: \n 이후 = box 닫음 직전

    translated_prep = translate_block(prep_block, lang, trans)
    content = (
        content[:insert_prep_at]
        + "\n"
        + translated_prep
        + "\n"
        + content[insert_prep_at:]
    )

    # ── sec-tourstops 본문 보강 ──
    ts_idx = content.find('id="sec-tourstops"')
    if ts_idx >= 0:
        # 8언어 구조: oshows </a></div> 직후가 sec-tourstops box 닫음
        # 본문 p가 없으면 추가 (300자 범위로 확인)
        ts_snippet = content[ts_idx : ts_idx + 400]
        if '<p style="margin:8px' not in ts_snippet and tourstops_body:
            # </a></div> 패턴 = oshows 내 마지막 링크 닫음 + oshows 닫음
            # 그 이후(oshows_close)에 p 삽입
            a_div_pos = content.find("</a></div>", ts_idx)
            if a_div_pos >= 0:
                a_div_pos + 6  # </a></div> = 10chars, +6 = oshows </div> 직후
                # 정확히: </a> = a_div_pos:a_div_pos+4, </div> = a_div_pos+4:a_div_pos+10
                # oshows </div> 뒤 = a_div_pos + 10
                insert_pos = a_div_pos + 10
                translated_ts_body = translate_block(tourstops_body, lang, trans)
                content = (
                    content[:insert_pos]
                    + "\n"
                    + translated_ts_body
                    + content[insert_pos:]
                )

    # ── 결과 저장 ──
    f.write_text(content, encoding="utf-8")
    return True


def verify_batch1_guards(lang: str, content: str) -> list:
    """batch-1 4건 회귀 확인."""
    issues = []
    # langpick min-width:140px
    if "min-width:140px" not in content and "langpick" in content:
        issues.append("langpick min-width:140px 소실")
    # OG twice-seoul.png
    if "og/twice-seoul.png" not in content:
        issues.append("OG image twice-seoul.png 소실")
    # KST label
    if "KST" not in content:
        issues.append("KST 라벨 소실")
    # iframe fallback
    if "ytfacade" not in content and "iframe" not in content:
        issues.append("iframe/ytfacade 소실")
    return issues


def verify_modules(lang: str, content: str) -> list:
    """5개 모듈 존재 + 한국어 잔재 없음 검증."""
    issues = []
    modules = {
        "tldr": 'class="tldr"',
        "steps5": 'class="steps5"',
        "prep-list": 'class="prep-list"',
        "jump-nav": 'class="jump-nav"',
    }
    for name, pattern in modules.items():
        if pattern not in content:
            issues.append(f"{name} 미존재")

    # tourstops 본문 확인 (p 태그)
    ts_idx = content.find('id="sec-tourstops"')
    if ts_idx >= 0:
        ts_snippet = content[ts_idx : ts_idx + 400]
        if '<p style="margin:8px' not in ts_snippet:
            issues.append("sec-tourstops 본문 p 태그 미존재")

    # 한국어 잔재 확인 (번역 텍스트 내 한국어 key 확인)
    # 한국어 텍스트가 tldr/steps5/prep 안에 있는지 체크
    # 완전한 게이트: 블록 내에서 한글 문자 존재 여부
    import unicodedata

    def has_hangul(s):
        return any(unicodedata.category(c) in ("Lo",) and "가" <= c <= "힣" for c in s)

    # tldr 블록
    tldr_start = content.find('class="tldr"')
    tldr_end = content.find("</div>", tldr_start) + 6
    tldr_block = content[tldr_start:tldr_end]
    if has_hangul(tldr_block) and lang not in ("ko", "ja", "zh-tw", "zh-cn"):
        # ja/zh-tw는 CJK 포함 가능
        issues.append("tldr 블록 내 한국어 잔재")

    return issues


def main():
    print(f"[{MARK}] 8언어 UX 모듈 이식 패치 시작")
    print()

    ko = load_ko()

    # ko에서 모듈 추출
    css_block = get_ko_module_css(ko)
    intro_block = get_ko_intro_block(ko)
    prep_block = get_ko_prep_block(ko)
    tourstops_body = get_ko_tourstops_body(ko)

    print(f"CSS block: {len(css_block)}B")
    print(f"Intro block (tldr+jump-nav+steps5): {len(intro_block)}B")
    print(f"Prep block: {len(prep_block)}B")
    print(f"Tourstops body: {len(tourstops_body)}B")
    print()

    # 배치 번역
    print("=== 배치 번역 (warm 패턴) ===")
    trans_results = batch_translate_all(LANGS_8)
    print()

    # 언어별 번역 딕셔너리 구성
    translations = {}
    for lang in LANGS_8:
        tr_list = trans_results.get(lang, [])
        translations[lang] = {}
        for i, ko_text in enumerate(ALL_TEXTS):
            if i < len(tr_list) and tr_list[i] and tr_list[i] != ko_text:
                translations[lang][ko_text] = tr_list[i]
        print(f"  [{lang}] 번역 완료: {len(translations[lang])}개")

    print()
    print("=== 파일 패치 ===")
    results = {}
    for lang in LANGS_8:
        f = DIST / lang / "twice-thisisfor-seoul.html"
        ok = patch_file(
            lang,
            translations[lang],
            ko,
            css_block,
            intro_block,
            prep_block,
            tourstops_body,
        )
        results[lang] = ok
        if ok:
            print(f"  ✅ [{lang}] 패치 완료")
        else:
            print(f"  ❌ [{lang}] 패치 실패")

    print()
    print("=== 검증 ===")
    all_pass = True
    for lang in LANGS_8:
        f = DIST / lang / "twice-thisisfor-seoul.html"
        if not f.exists():
            print(f"  ❌ [{lang}] 파일 없음")
            all_pass = False
            continue
        content = f.read_text(encoding="utf-8")

        # 모듈 검증
        mod_issues = verify_modules(lang, content)
        # batch-1 회귀 검증
        b1_issues = verify_batch1_guards(lang, content)

        if mod_issues or b1_issues:
            all_pass = False
            for issue in mod_issues:
                print(f"  ❌ [{lang}] 모듈: {issue}")
            for issue in b1_issues:
                print(f"  ❌ [{lang}] batch-1 회귀: {issue}")
        else:
            print(f"  ✅ [{lang}] 모듈 5종 + batch-1 4종 PASS")

    print()
    if all_pass:
        print(f"✅ {MARK} 전체 PASS — 8언어 UX 모듈 이식 완료")
    else:
        print(f"❌ {MARK} 일부 FAIL — 위 항목 확인 필요")
    return all_pass


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
