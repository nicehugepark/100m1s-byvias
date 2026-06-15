#!/usr/bin/env python3
"""
R69 ja 이벤트 페이지 P0/P1 fix 패치
대상: dist/ja/twice-thisisfor-seoul.html (1개 파일)

P0-1: langmenu ko 라벨 '日本語' → '한국어' (langpick 구조)
P0-2: og:url /ja/ prefix 누락 수정
P1-3: aria-label 한글 고유명사 → ja 독음/표기 (26건)
P1-4: pinfo 내 가격 '원' → 'ウォン' (LLM 번역 0, 하드코딩 사전)

ref: R69 풀패널 신규 P0/P1 결함 fix
"""

import re
from pathlib import Path

TARGET = Path(__file__).parent.parent / "dist/ja/twice-thisisfor-seoul.html"

# ── P1-3: aria-label 한글 → ja 사전 (고유명사 독음/표기·지도링크 일본어) ──
ARIA_MAP = {
    "24게스트하우스 잠실점": "24ゲストハウス ジャムシル店",
    "갓잇 송리단길점": "ガッイット ソンリダンギル店",
    "고도식 잠실점": "ゴドシク ジャムシル店",
    "광장시장통큰누이네육회빈대떡": "クァンジャン市場 通クンヌイネ 牛肉ユッケ・チヂミ",
    "교도리 홍대본점": "キョドリ ホンデ本店",
    "농민백암순대 본점": "ノンミン・ペガム・スンデ 本店",
    "런던베이글뮤지엄 잠실점": "ロンドンベーグルミュージアム ジャムシル店",
    "롯데월드몰 📍 지도에서 보기": "ロッテワールドモール 📍 地図で見る",
    "명동교자 본점": "明洞餃子(ミョンドンキョジャ) 本店",
    "봉피양 방이점": "ボンピャン バンギ店",
    "비스트로주라 홍대점": "ビストロジュラ ホンデ店",
    "서울올림픽파크텔": "ソウルオリンピックパークテル",
    "소문난성수감자탕": "聖水で有名なカムジャタン(ソムンナン・ソンス・カムジャタン)",
    "신양로스터스": "シンヤンロースターズ",
    "아베베베이커리 서울": "アベベベーカリー ソウル",
    "어니언 성수 (onion)": "オニオン(Onion) 聖水店",
    "올림픽공원 평화의 문 📍 지도에서 보기": "オリンピック公園 平和の門 📍 地図で見る",
    "잠실 게스트하우스 서울": "ジャムシル ゲストハウス ソウル",
    "잠실 라움 관광호텔": "ジャムシル ラウム 観光ホテル",
    "진주육회": "チンジュ ユッケ",
    "청와옥 본점": "チョンワオク 本店",
    "츠케루": "ツケル",
    "칸다소바 경복궁점": "カンダ蕎麦(そば) 景福宮(キョンボックン)店",
    "코히루": "コヒル",
    "토속촌삼계탕": "トソクチョン サムゲタン",
    "하동관 본점": "ハドンクァン 本店",
}

# ── P1-4: pinfo 내 가격 '원' → 'ウォン' 사전 ──
PRICE_MAP = {
    "12,000원": "₩12,000",
    "6,000원": "₩6,000",
}


def apply_fixes(html: str) -> tuple[str, dict]:
    counts = {
        "p0_langmenu_ko": 0,
        "p0_og_url": 0,
        "p1_aria": 0,
        "p1_price": 0,
    }

    # P0-1: langmenu ko 라벨 버그 수정 (langpick 구조)
    # Before: data-lang="ko" href="...">日本語</a>
    # After:  data-lang="ko" href="...">한국어</a>
    old_ko = (
        'data-lang="ko" href="../twice-thisisfor-seoul.html" hreflang="ko">日本語</a>'
    )
    new_ko = (
        'data-lang="ko" href="../twice-thisisfor-seoul.html" hreflang="ko">한국어</a>'
    )
    if old_ko in html:
        html = html.replace(old_ko, new_ko, 1)
        counts["p0_langmenu_ko"] += 1

    # P0-2: og:url /ja/ prefix 수정
    # Before: <meta content="https://bybias.100m1s.com/twice-thisisfor-seoul.html" property="og:url"/>
    # After:  <meta property="og:url" content="https://bybias.100m1s.com/ja/twice-thisisfor-seoul.html">
    old_ogurl = '<meta content="https://bybias.100m1s.com/twice-thisisfor-seoul.html" property="og:url"/>'
    new_ogurl = '<meta property="og:url" content="https://bybias.100m1s.com/ja/twice-thisisfor-seoul.html">'
    if old_ogurl in html:
        html = html.replace(old_ogurl, new_ogurl, 1)
        counts["p0_og_url"] += 1

    # P1-3: aria-label 한글 → ja
    for ko_label, ja_label in ARIA_MAP.items():
        old = f'aria-label="{ko_label}"'
        new = f'aria-label="{ja_label}"'
        n = html.count(old)
        if n:
            html = html.replace(old, new)
            counts["p1_aria"] += n

    # P1-4: pinfo 내 가격 '원' → '₩' (pinfo 태그 안에서만)
    # 정규식으로 .pinfo 태그 내부만 대상
    def replace_price_in_pinfo(m):
        inner = m.group(1)
        for src, tgt in PRICE_MAP.items():
            if src in inner:
                inner = inner.replace(src, tgt)
                counts["p1_price"] += 1
        return f'<div class="pinfo">{inner}</div>'

    html = re.sub(
        r'<div class="pinfo">(.*?)</div>',
        replace_price_in_pinfo,
        html,
        flags=re.DOTALL,
    )

    return html, counts


def main():
    if not TARGET.exists():
        print(f"ERROR: {TARGET} 없음")
        return

    original = TARGET.read_text(encoding="utf-8")
    patched, counts = apply_fixes(original)

    if patched == original:
        print("변경 없음 — 이미 적용됐거나 패턴 불일치")
        return

    TARGET.write_text(patched, encoding="utf-8")

    print("=== R69 fix 결과 ===")
    print(f"P0-1 langmenu ko 라벨: {counts['p0_langmenu_ko']}건 수정")
    print(f"P0-2 og:url /ja/ prefix: {counts['p0_og_url']}건 수정")
    print(f"P1-3 aria-label ja 변환: {counts['p1_aria']}건 수정")
    print(f"P1-4 가격 원→₩: {counts['p1_price']}건 수정")
    print(f"출력: {TARGET}")


if __name__ == "__main__":
    main()
