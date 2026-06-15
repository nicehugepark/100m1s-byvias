#!/usr/bin/env python3
"""R74 고유명사 한국어 원문 병행표기 패치 (옵션 1 · dist 직접 치환 · LLM 미경유).

대표 정책 (2026-06-15): 고유명사(역명·지명·식당명·숙소명) = 한국어 원문 우선(prefix) +
괄호 (번역 / 읽는법) 병행. 관광객이 한글 간판·표지판과 눈으로 대조하기 위함.
  - ja: 청와옥(チョンワオク 本店) · 잠실(蚕室 / ジャムシル)
  - en: 청와옥(Cheongwaok) · 잠실(Jamsil)
읽는법 = ja 가타카나(한국 발음, ジャムシル) · en 로마자. 일본 음독(さんしつ) 금지.

대상: dist/ja/twice-thisisfor-seoul.html · dist/en/twice-thisisfor-seoul.html
SSOT  = dist/twice-thisisfor-seoul.html (ko 마스터, 한국어 원문 보존).

전략 = 인덱스 정렬 치환:
  ko·ja·en 세 로케일의 .pname(28)·.sname(4)이 문서 순서 100% 동일(실측 확인).
  → 위치(i)를 키로, ko원문[i] 를 SSOT로 가져와 '{ko원문}({정규화 번역})' 로 카드 교체.
  ja 카드 텍스트가 변종 혼재(ゴディート·Seongsuで有名な·成水 등)여도 위치로 정확 교체 +
  번역측을 사전값으로 정규화(조니 '3변종 혼재' 동시 해소). en은 'Trans (원문)'→'원문(Trans)' 재배열.

body 산문(역명·지명): 번역 토큰(蚕室/明洞 등)을 '{ko원문}({한자} / {가나})' 유닛으로 복원.

게이트:
  - 한국어 원문 누락 0 (P0): 모든 카드·역명에 한글 원문 present.
  - 괄호 병기 + 일본 음독(さんしつ·ひらがな 등) 0.
  - 멱등 (재실행 안전): 이미 '원문(' 형태면 재치환 skip.

재현성 부채: 본 패치는 dist 직접 치환. byvias_course_i18n.py 재빌드 시 원복됨.
  → 옵션 2(i18n.py PROMPT 한국어-원문-보존 규칙 정본화)는 후행 별 트랙 필요.

FLR 참조: FLR-AGT-002 (거짓 충실성 — 카드 수 불일치/원문 누락 시 비-0 exit, PASS 표기 0).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
KO = WT / "dist/twice-thisisfor-seoul.html"
PATHS = {
    "ja": WT / "dist/ja/twice-thisisfor-seoul.html",
    "en": WT / "dist/en/twice-thisisfor-seoul.html",
}

# ──────────────────────────────────────────────────────────────────────────
# 정규화 번역 사전: ko원문 → {ja, en}. (읽는법 가나 = 한국 발음, 일본 음독 금지)
# 카드(.pname/.sname)용. 렌더 = '{ko원문}({번역})'. ko원문은 ko 마스터서 위치로 취득.
# ──────────────────────────────────────────────────────────────────────────
TRANS: dict[str, dict[str, str]] = {
    # ── .pname (식당/장소) ──
    "코히루": {"ja": "コヒル", "en": "Cohiru"},
    "신양로스터스": {"ja": "シンヤンロースターズ", "en": "Sinyang Roasters"},
    "고도식 잠실점": {"ja": "ゴドシク ジャムシル店", "en": "Godosik Jamsil"},
    "갓잇 송리단길점": {
        "ja": "ガッイット ソンリダンギル店",
        "en": "Got-it Songridan-gil",
    },
    "청와옥 본점": {"ja": "チョンワオク 本店", "en": "Cheongwaok"},
    "토속촌삼계탕": {"ja": "トソクチョン サムゲタン", "en": "Tosokchon Samgyetang"},
    "칸다소바 경복궁점": {
        "ja": "カンダソバ キョンボックン店",
        "en": "Kanda Soba Gyeongbokgung",
    },
    "츠케루": {"ja": "ツケル", "en": "Tsukeru"},
    "비스트로주라 홍대점": {
        "ja": "ビストロジュラ ホンデ店",
        "en": "Bistro Jura Hongdae",
    },
    "교도리 홍대본점": {"ja": "キョドリ ホンデ本店", "en": "Gyodori Hongdae"},
    "농민백암순대 본점": {
        "ja": "ノンミン ペガム スンデ 本店",
        "en": "Nongmin Baegam Sundae",
    },
    "아베베베이커리 서울": {
        "ja": "アベベベーカリー ソウル",
        "en": "Ababe Bakery Seoul",
    },
    "진주육회": {"ja": "チンジュ ユッケ", "en": "Jinju Yukhoe"},
    "광장시장통큰누이네육회빈대떡": {
        "ja": "クァンジャン市場 トンクンヌイネ ユッケ・ビンデトク",
        "en": "Gwangjang Tongkeun Nui Yukhoe Bindaetteok",
    },
    "봉피양 방이점": {"ja": "ボンピャン バンイ店", "en": "Bongpiyang Bangi"},
    "소문난성수감자탕": {
        "ja": "ソムンナン ソンス カムジャタン",
        "en": "Somunnan Seongsu Gamjatang",
    },
    "어니언 성수 (onion)": {"ja": "オニオン ソンス(Onion)", "en": "Onion Seongsu"},
    "명동교자 본점": {"ja": "ミョンドン餃子 本店", "en": "Myeongdong Kyoja"},
    "하동관 본점": {"ja": "ハドンクァン 本店", "en": "Hadongkwan"},
    "런던베이글뮤지엄 잠실점": {
        "ja": "ロンドンベーグルミュージアム ジャムシル店",
        "en": "London Bagel Museum Jamsil",
    },
    # ── .sname (숙소) ──
    "서울올림픽파크텔": {
        "ja": "ソウルオリンピックパークテル",
        "en": "Seoul Olympic Parktel",
    },
    "잠실 라움 관광호텔": {
        "ja": "ジャムシル ラウム 観光ホテル",
        "en": "Jamsil Raum Tourist Hotel",
    },
    "24게스트하우스 잠실점": {
        "ja": "24ゲストハウス ジャムシル店",
        "en": "24 Guesthouse Jamsil",
    },
    "잠실 게스트하우스 서울": {
        "ja": "ジャムシル ゲストハウス ソウル",
        "en": "Jamsil Guesthouse Seoul",
    },
}

# ──────────────────────────────────────────────────────────────────────────
# 역명·지명 (body 산문) — ja 현 등장 토큰 → 최종 '{ko원문}({한자} / {가나})' 유닛.
#   정책 예시: 역명은 '잠실역(蚕室駅 / ジャムシル)'. 일반 지명은 '잠실(蚕室 / ジャムシル)'.
#   읽는법 = 가타카나 한국 발음. 일본 음독(さんしつ)·히라가나(じゃむしる) 금지.
#   list = (현 ja 토큰, 최종 유닛). longest-first 정렬(역명+駅·괄호형이 bare보다 먼저).
# ──────────────────────────────────────────────────────────────────────────
JA_BODY_VARIANTS: list[tuple[str, str]] = [
    # 잠실 — 역명(駅) 우선, 그 다음 일반
    ("蚕室駅(チャムシル駅)", "잠실역(蚕室駅 / ジャムシル)"),
    ("蚕室駅", "잠실역(蚕室駅 / ジャムシル)"),
    ("蚕室(チャムシル)", "잠실(蚕室 / ジャムシル)"),
    ("蚕室", "잠실(蚕室 / ジャムシル)"),
    # 명동 — 히라가나/로마자 변종 정규화
    ("明洞(Myeongdong)", "명동(明洞 / ミョンドン)"),
    ("明洞(みょんどん)", "명동(明洞 / ミョンドン)"),
    ("明洞(ミョンドン)", "명동(明洞 / ミョンドン)"),
    ("明洞", "명동(明洞 / ミョンドン)"),
    # 홍대
    ("弘大(ホンデ)", "홍대(弘大 / ホンデ)"),
    ("弘大", "홍대(弘大 / ホンデ)"),
    # 성수
    ("聖水(ソンス)", "성수(聖水 / ソンス)"),
    ("聖水", "성수(聖水 / ソンス)"),
    # 경복궁
    ("景福宮(キョンボックン)", "경복궁(景福宮 / キョンボックン)"),
    ("景福宮", "경복궁(景福宮 / キョンボックン)"),
    # 올림픽공원 — 역명(駅) 우선. 가나 = 의미역(공원=公園) 유지, 원문 한글 prefix.
    (
        "オリンピック公園駅(5号線·9号線)",
        "올림픽공원역(オリンピック公園駅 / オルリムピックゴンウォン)(5号線·9号線)",
    ),
    (
        "オリンピック公園駅",
        "올림픽공원역(オリンピック公園駅 / オルリムピックゴンウォン)",
    ),
    ("オリンピック公園", "올림픽공원(オリンピック公園 / オルリムピックゴンウォン)"),
    # 몽촌토성 — 한자 변종(蒙村土城/夢村土城) 모두 정규화
    ("蒙村土城駅", "몽촌토성역(夢村土城駅 / モンチョントソン)"),
    ("夢村土城駅", "몽촌토성역(夢村土城駅 / モンチョントソン)"),
    ("蒙村土城", "몽촌토성(夢村土城 / モンチョントソン)"),
    ("夢村土城", "몽촌토성(夢村土城 / モンチョントソン)"),
]

CARD_RE_TMPL = r'(class="{cls}">)(.*?)(</div>|<span\b|<br\b)'


def _ko_cards(html: str, cls: str) -> list[str]:
    return [
        m.group(2)
        for m in re.finditer(CARD_RE_TMPL.format(cls=cls), html, flags=re.DOTALL)
    ]


def _patch_cards(html: str, ko_vals: list[str], lang: str, cls: str):
    """위치 정렬: i번째 카드를 ko_vals[i] 원문 + 정규화 번역으로 교체.

    부제 span/br 이하(중복 영문 부제 등)는 버린다(조니 제거 후보 #3 — 1차명 원문化 후
    동일 영문 반복 = 노이즈). 멱등: 이미 '원문(' 형태면 그대로 둔다.
    """
    counts = {"patched": 0, "already": 0, "miss": 0, "n_cards": 0}
    idx = [0]
    pat = re.compile(CARD_RE_TMPL.format(cls=cls), flags=re.DOTALL)

    def _rep(mo):
        i = idx[0]
        idx[0] += 1
        counts["n_cards"] += 1
        if i >= len(ko_vals):
            counts["miss"] += 1
            return mo.group(0)
        ko = ko_vals[i].strip()
        tr = TRANS.get(ko)
        if not tr or lang not in tr:
            counts["miss"] += 1
            return mo.group(0)
        # ko 원문에 라틴 보조명이 괄호로 박혀 있으면(예: '어니언 성수 (onion)') prefix에서
        # 제거 — 번역측이 이미 라틴 별칭을 품으므로 이중 괄호 방지. 원문 한글은 보존.
        ko_disp = re.sub(r"\s*\([A-Za-z][^)]*\)\s*$", "", ko).strip()
        final = f"{ko_disp}({tr[lang]})"
        cur = mo.group(2)
        if cur.strip() == final:
            counts["already"] += 1
            return mo.group(0)
        counts["patched"] += 1
        return mo.group(1) + final + "</div>"

    return pat.sub(_rep, html), counts


def _patch_body_ja(html: str):
    """body 산문: 현 ja 토큰 → 최종 유닛. longest-first.

    2-phase 치환: 각 토큰을 NUL sentinel(\\x00{i}\\x00)로 먼저 잠그고(원본 토큰이
    이후 토큰의 부분문자열이어도 재매칭 안 됨), 전수 잠근 뒤 sentinel→final 복원.
    이로써 '蚕室駅'→final 후 그 안의 '蚕室'을 다음 규칙이 다시 건드리는 cross-variant
    오염을 구조적으로 차단. 멱등: 이미 final 형태면 그 안의 ja 토큰이 sentinel로 잠겨
    재치환 안 됨(단 final 자체가 토큰 superstring이므로 longest-first 전제로 안전).
    """
    counts = {"patched": 0}
    # 멱등 보호: 이미 적용된 final 들을 먼저 잠가 둔다(재실행 시 내부 한자 재매칭 방지).
    locks: list[str] = []
    seen_finals = {f for _, f in JA_BODY_VARIANTS}
    for f in sorted(seen_finals, key=len, reverse=True):
        if f in html:
            s = f"\x00F{len(locks)}\x00"
            html = html.replace(f, s)
            locks.append(f)
    # 토큰 치환(longest-first). 각 매칭을 즉시 sentinel로 잠가 후속 규칙서 격리.
    for cur_tok, final in JA_BODY_VARIANTS:
        if cur_tok not in html:
            continue
        n = html.count(cur_tok)
        s = f"\x00F{len(locks)}\x00"
        html = html.replace(cur_tok, s)
        locks.append(final)
        counts["patched"] += n
    # 복원: sentinel → 원래/최종 문자열 (역순 무관·sentinel 유일)
    for i, val in enumerate(locks):
        html = html.replace(f"\x00F{i}\x00", val)
    return html, counts


def apply_to(lang: str, ko_pname: list[str], ko_sname: list[str]):
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return None
    html = path.read_text(encoding="utf-8")
    orig = html

    # 카드 수 정합 사전 점검 (거짓 충실성 방지: 위치 정렬 전제 검증)
    cur_pn = _ko_cards(html, "pname")
    cur_sn = _ko_cards(html, "sname")
    if len(cur_pn) != len(ko_pname) or len(cur_sn) != len(ko_sname):
        print(
            f"ABORT [{lang}]: 카드 수 불일치 — pname {len(cur_pn)} vs ko {len(ko_pname)}, "
            f"sname {len(cur_sn)} vs ko {len(ko_sname)} (위치 정렬 전제 깨짐)"
        )
        return None

    html, c_p = _patch_cards(html, ko_pname, lang, "pname")
    html, c_s = _patch_cards(html, ko_sname, lang, "sname")
    c_b = {"patched": 0}
    if lang == "ja":
        html, c_b = _patch_body_ja(html)

    if html == orig:
        print(f"[{lang}] 변경 없음 (이미 적용)")
    else:
        path.write_text(html, encoding="utf-8")
    print(f"=== [{lang}] {path.name} ===")
    print(
        f"  .pname: patched={c_p['patched']} already={c_p['already']} "
        f"miss={c_p['miss']} (n={c_p['n_cards']})"
    )
    print(
        f"  .sname: patched={c_s['patched']} already={c_s['already']} "
        f"miss={c_s['miss']} (n={c_s['n_cards']})"
    )
    print(f"  body  : patched={c_b['patched']}")
    miss = c_p["miss"] + c_s["miss"]
    return {"pname": c_p, "sname": c_s, "body": c_b, "miss": miss}


def main():
    ko_html = KO.read_text(encoding="utf-8")
    ko_pname = _ko_cards(ko_html, "pname")
    ko_sname = _ko_cards(ko_html, "sname")
    print(f"[ko SSOT] pname={len(ko_pname)} sname={len(ko_sname)}")

    langs = sys.argv[1:] or ["ja", "en"]
    total_miss = 0
    for lang in langs:
        r = apply_to(lang, ko_pname, ko_sname)
        if r is None:
            sys.exit(2)
        total_miss += r["miss"]
    if total_miss:
        print(
            f"\nWARN: 카드 miss {total_miss}건 (사전 미등록 또는 원문 누락) — 게이트 검토 필요"
        )
        sys.exit(1)
    print("\nOK: 카드 miss 0 — 한국어 원문 present 게이트 통과(카드 레이어)")


if __name__ == "__main__":
    main()
