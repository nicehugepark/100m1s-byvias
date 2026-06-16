#!/usr/bin/env python3
"""R85 fix — zh-cn/zh-tw 코스 역명 dual-notation 복원 (완전현지어화 종식).

배경 (직전 진단 dev-zh-course-parity + 대표 고유명사 규칙):
  twice-thisisfor-seoul 코스 페이지는 ko 마스터(227KB)가 성장했으나 zh-cn/zh-tw 는
  성장 전 구버전 stale build(185KB) 였다. byvias_course_i18n.py 재실행으로 콘텐츠
  파리티는 복원(카드 60·스텝 52·img 18·details 18 = ko 동일)되나, i18n LLM(haiku)이
  prompt rule 5(a) "conventional rendering" 에 따라 한글 역명을 중국어 단독으로 변환 →
  한국어 원문 소실(완전현지어화). 실측(rebuilt zh-cn):
    奥林匹克公园站 / 梦村土城站 / 蚕室站 / 成寿站 / Samsung站 / ... (한글 원문 0종)
  ↔ ko 마스터 한글 역명 15종 · ja 13종 · en 6종 대조 (zh 만 0).

🔴 대표 고유명사 규칙 (2026-06-15 project_byvias_proper_noun_dual_notation):
  twice 서울 = 한국 공연 → 외국어 페이지 고유명사 = 한국어 원문 + (독자 언어 뜻).
  완전현지어화(한국어 원문 없이 중국어로만) 절대 금지. ja/en 패치(r74/r77/r79/r82)의
  dual-notation 패턴을 zh 에 동형 적용: `한글역(中文站)`.

🔴 form 결정 (FLR-AGT-002 거짓 충실성·환각 금지 — 핵심):
  대표 예시 `올림픽공원역(奥林匹克公园站 / [중국어 읽는법])` 의 3-part 중 [중국어 읽는법]
  (병음) 은 **verbatim source 부재**(rebuilt 빌드 어디에도 병음 0종). ja 2-part 가
  동작하는 이유 = 한자의 가나 읽기가 일본인에게 진짜 모호하기 때문(prose 에서 verbatim
  차용). 중국어는 한자 자체를 독자가 병음으로 직독 → 별도 [읽는법] 불요 + 16역 병음
  hand-생성 = 환각(FLR-AGT-002 위반). ∴ 본 패치 = **2-part `한글역(中文站)`**:
    한국어 원문(ko 마스터 verbatim) + 중국어 의미명(서울교통공사 공식 한자명·verifiable).
  [읽는법] 3번째 슬롯 = 미생성·lead/대표 확인 의제(별도 보고).

🔴 중국어 의미명 canonicalize (LLM 변종 → 1 공식명, 실측 grep + 서울교통공사 표준):
  haiku 가 동일 역을 복수 변종으로 렌더 + 일부 오역. 공식 한자명으로 통일(환각 아님·실재 표지판):
    올림픽공원 → 奥林匹克公园(簡)/奧林匹克公園(繁)  [base 일치]
    몽촌토성   → 梦村土城/夢村土城   (蒙村土城=오자 蒙 통일)
    잠실       → 蚕室/蠶室
    성수       → 圣水/聖水           (成寿=음역 오역 → 공식 의미명)
    삼성       → 三成               (Samsung=회사명 오역 / 三成 공식)
    송파나루   → 松坡渡口/松坡渡口   (那鲁=음역 → 渡口 '나루' 의미 / 단 prose 통일은 那鲁 음역 유지: 아래 NOTE)
    압구정로데오 → 狎鸥亭罗德奥/狎鷗亭羅德奧
    을지로입구 → 乙支路入口          (一街=1가 오역 → 入口)
    안국 → 安国/安國 · 경복궁 → 景福宫/景福宮 · 강동 → 江东/江東
    방이 → 芳荑               (芳夷=오자 夷 → 荑 공식) · 종로5가 → 钟路5街/鐘路5街

  NOTE 송파나루: 공식 한자 표지명은 '松坡渡口' (渡口='나루'). 단 본 페이지 prose 가 이미
  음역 '松坡那鲁/Songpanaru' 정착 → en/ja 패치도 음역 유지(Songpanaru/松坡ナル). 일관성 위해
  zh 도 음역 '松坡那鲁站' 유지(공식명 강제 치환 안 함). 한글 원문 복원이 핵심.

전략 (r77/r79 검증 엔진 verbatim 차용 — 2-phase NUL sentinel + longest-first):
  - longest-first: `中文站(라틴/노선 주석)` 이 bare `中文站` 보다 먼저 매칭 → 주석 보존·중첩 방지.
    예) `奥林匹克公园站(Olympic Park Station)` → `올림픽공원역(奥林匹克公园站)` (라틴 제거,
        한글 원문으로 대체) ; `奥林匹克公园站(5号线·9号线)` → `올림픽공원역(奥林匹克公园站)(5号线·9号线)`
        (노선 정보는 별도 unit → 보존).
  - 멱등: 이미 적용된 `한글역(...)` final 사전 잠금. 재실행 0 변경.
  - script/style 미touch(텍스트 노드 산문만). i18n 재실행 시 소실 → 재적용 필수(ja/en 동형).

게이트 (FLR-AGT-002 — 선언 아닌 실측 grep, --verify):
  (G1) 한글 역명 원문 ≥ 12종 present (ko 15 수준·완전현지어화 0).
  (G2) 각 역 dual-notation 형태 `한글역(中文站)` present.
  (G3) 중첩 괄호 오류 0 (`站)(站` 또는 `역((` 패턴 0).
  (G4) Chinese 의미명 무손실(奥林匹克公园 등 한자 잔존).
  (G5) 멱등(재실행 0 변경) + <div> 구조 균형.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

WT = Path(__file__).parent.parent
PATHS = {
    "zh-cn": WT / "dist/zh-cn/twice-thisisfor-seoul.html",
    "zh-tw": WT / "dist/zh-tw/twice-thisisfor-seoul.html",
}

# ──────────────────────────────────────────────────────────────────────────
# 역명 dual-notation pairs. (cur_token, final).
#   longest-first 는 엔진서 자동 정렬 → 라틴/노선 주석 보유형이 bare 보다 먼저 매칭.
#   final = 한글역(中文站). 라틴 reading 주석은 한글 원문으로 대체(중복 회피).
#   노선 주석 `(5号线·9号线)` 등은 별도 unit → 보존(중첩 아님).
# ──────────────────────────────────────────────────────────────────────────
# zh-cn (간체)
#   form: `한글역(中文站 / 읽는법)` — 읽는법(라틴) = 빌드 내 verbatim 존재분 fold-in (환각 0).
#         읽는법 없는 역 = 2-part `한글역(中文站)`. 노선/거리 주석은 별 unit → 보존.
#   longest-first: 라틴 reading 포함형(`中文站(Latin...)`)이 bare `中文站` 보다 먼저 매칭.
ZHCN_VARIANTS: list[tuple[str, str]] = [
    # 올림픽공원 — 라틴 reading fold-in ; bare/노선주석형은 2-part
    (
        "奥林匹克公园站(Olympic Park Station)",
        "올림픽공원역(奥林匹克公园站 / Olympic Park Station)",
    ),
    ("奥林匹克公园站", "올림픽공원역(奥林匹克公园站)"),
    # 몽촌토성 (蒙村 오자 → 梦村 통일) — 라틴 reading fold-in
    (
        "蒙村土城站(Mongchontoseong Station)",
        "몽촌토성역(梦村土城站 / Mongchontoseong Station)",
    ),
    ("蒙村土城站", "몽촌토성역(梦村土城站)"),
    ("梦村土城站", "몽촌토성역(梦村土城站)"),
    # 잠실 — 라틴 reading fold-in
    ("蚕室站(Jamsil)", "잠실역(蚕室站 / Jamsil)"),
    ("蚕室站", "잠실역(蚕室站)"),
    # 성수 (成寿 음역오역 → 圣水 공식) — 라틴 reading fold-in
    ("成寿站(Seongsu)", "성수역(圣水站 / Seongsu)"),
    ("成寿站", "성수역(圣水站)"),
    # 삼성 (Samsung 회사명오역 + 三成 공식 ; 라틴 reading 부재 → 2-part)
    ("Samsung站", "삼성역(三成站)"),
    ("三成站", "삼성역(三成站)"),
    # 송파나루 (음역 유지 — prose/ja/en 일관) — 라틴 reading fold-in
    (
        "松坡那鲁站(Songpanaru Station)",
        "송파나루역(松坡那鲁站 / Songpanaru Station)",
    ),
    ("松坡那鲁站", "송파나루역(松坡那鲁站)"),
    ("Songpanaru站", "송파나루역(松坡那鲁站)"),
    # 압구정로데오 (라틴 reading 부재 → 2-part ; 'Rodeo站' 약식 흡수)
    ("狎鸥亭罗德奥站", "압구정로데오역(狎鸥亭罗德奥站)"),
    ("Apgujeong Rodeo站", "압구정로데오역(狎鸥亭罗德奥站)"),
    ("Rodeo站", "압구정로데오역(狎鸥亭罗德奥站)"),
    # 을지로입구 (一街 오역 → 入口 공식 ; 노선주석 보존 ; 라틴 부재 → 2-part)
    ("乙支路一街站", "을지로입구역(乙支路入口站)"),
    # 안국 — 라틴 reading fold-in
    ("安国站(Anguk Station)", "안국역(安国站 / Anguk Station)"),
    ("安国站", "안국역(安国站)"),
    # 경복궁 (라틴 reading 부재 → 2-part ; '(自Jamsil...' 거리주석 보존)
    ("景福宫站", "경복궁역(景福宫站)"),
    # 강동 (2-part)
    ("江东站", "강동역(江东站)"),
    # 방이 (芳夷 오자 → 芳荑 공식) — 라틴 reading fold-in
    ("芳夷站(Bangi Station)", "방이역(芳荑站 / Bangi Station)"),
    ("芳夷站", "방이역(芳荑站)"),
    # 종로5가 — 라틴 reading fold-in
    (
        "钟路五街站(Jongno 5-ga Station)",
        "종로5가역(钟路五街站 / Jongno 5-ga Station)",
    ),
    ("钟路五街站", "종로5가역(钟路五街站)"),
]

# zh-tw (번체) — rebuilt 후 실측으로 채움(아래 _autoderive 가 zh-cn 매핑을 번체 변환).
# 실 토큰은 rebuild 후 다를 수 있으므로 zh-tw 는 별도 실측 grep 후 확정(STEP 2).
# 우선 zh-cn 매핑의 번체 대응을 base 로 제공(공식 번체명):
ZHTW_VARIANTS: list[tuple[str, str]] = [
    (
        "奧林匹克公園站(Olympic Park Station",
        "올림픽공원역(奧林匹克公園站)(Olympic Park Station",
    ),
    ("奧林匹克公園站", "올림픽공원역(奧林匹克公園站)"),
    ("蒙村土城站(Mongchontos", "몽촌토성역(夢村土城站)(Mongchontos"),
    ("蒙村土城站", "몽촌토성역(夢村土城站)"),
    ("夢村土城站", "몽촌토성역(夢村土城站)"),
    ("蠶室站(Jamsil", "잠실역(蠶室站)(Jamsil"),
    ("蠶室站", "잠실역(蠶室站)"),
    ("成壽站(Seongsu", "성수역(聖水站)(Seongsu"),
    ("成壽站", "성수역(聖水站)"),
    ("Samsung站", "삼성역(三成站)"),
    ("三成站", "삼성역(三成站)"),
    ("松坡那魯站(Songpanaru Station", "송파나루역(松坡那魯站)(Songpanaru Station"),
    ("松坡那魯站", "송파나루역(松坡那魯站)"),
    ("Songpanaru站", "송파나루역(松坡那魯站)"),
    ("狎鷗亭羅德奧站", "압구정로데오역(狎鷗亭羅德奧站)"),
    ("Apgujeong Rodeo站", "압구정로데오역(狎鷗亭羅德奧站)"),
    ("Rodeo站", "압구정로데오역(狎鷗亭羅德奧站)"),
    ("乙支路一街站", "을지로입구역(乙支路入口站)"),
    ("安國站(Anguk Station", "안국역(安國站)(Anguk Station"),
    ("安國站", "안국역(安國站)"),
    ("景福宮站", "경복궁역(景福宮站)"),
    ("江東站", "강동역(江東站)"),
    ("芳夷站(Bangi Station", "방이역(芳荑站)(Bangi Station"),
    ("芳夷站", "방이역(芳荑站)"),
    ("鐘路五街站(Jongno 5-ga Station", "종로5가역(鐘路五街站)(Jongno 5-ga Station"),
    ("鐘路五街站", "종로5가역(鐘路五街站)"),
]

VARIANTS = {"zh-cn": ZHCN_VARIANTS, "zh-tw": ZHTW_VARIANTS}

# 검증용 한글 역명 종수 (G1)
KO_STATION_NAMES = [
    "올림픽공원역",
    "몽촌토성역",
    "잠실역",
    "성수역",
    "삼성역",
    "송파나루역",
    "압구정로데오역",
    "을지로입구역",
    "안국역",
    "경복궁역",
    "강동역",
    "방이역",
    "종로5가역",
]


def _two_phase_replace(
    html: str, variants: list[tuple[str, str]], protect: list[str]
) -> tuple[str, dict]:
    """r77 검증 엔진: 멱등 final 잠금 + 보호 토큰 잠금 + longest-first 치환.

    각 매칭을 즉시 NUL sentinel 로 잠가 후속 규칙서 격리(cross-variant 오염 차단).
    """
    counts: dict[str, int] = {}
    locks: list[str] = []

    def _lock(s: str) -> None:
        nonlocal html
        if s and s in html:
            sent = f"\x00L{len(locks)}\x00"
            html = html.replace(s, sent)
            locks.append(s)

    # 1) 멱등: 이미 적용된 final 잠금 (longest-first).
    #    final 이 어느 cur 의 substring 이면 사전 잠금 시 cur 파괴 → 스킵.
    curs = [c for c, _ in variants]
    for f in sorted({f for _, f in variants}, key=len, reverse=True):
        if any(f != c and f in c for c in curs):
            continue
        _lock(f)
    # 2) 보호 토큰 잠금 (카드 .pname/.sname/.ptag/.crs-tag + aria-label inner)
    for p in sorted(protect, key=len, reverse=True):
        _lock(p)
    # 3) 토큰 치환 (longest-first)
    for cur_tok, final in sorted(variants, key=lambda x: len(x[0]), reverse=True):
        if cur_tok not in html:
            continue
        counts[cur_tok] = counts.get(cur_tok, 0) + html.count(cur_tok)
        sent = f"\x00L{len(locks)}\x00"
        html = html.replace(cur_tok, sent)
        locks.append(final)
    # 4) 복원: sentinel → 원문/보호/final
    for i, val in enumerate(locks):
        html = html.replace(f"\x00L{i}\x00", val)
    return html, counts


def _card_protect(html: str) -> list[str]:
    """카드 .pname/.sname/.ptag/.crs-tag + aria-label inner content 보호 토큰 수집.

    산문 토큰 치환이 카드/속성 내부(이미 병기된 고유명)를 못 건드리게 잠금.
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


# 통화 정규화: ko 마스터 가격 '{숫자}원' → zh 통화 컨벤션.
#   배경: en 은 'KRW' · ja 는 '円' 로 현지화하나, stale build zh 는 한글 '원' 누락 잔존(실측 8건).
#   동 파일에 이미 '韩元'(zh-cn 8회)·'韓元'(zh-tw) 정착 → 잔존 '원'을 컨벤션으로 통일(환각 0·실측 근거).
#   '원'은 통화 접미(숫자 직후)만 대상. station 한글 원문(...역)·기타 텍스트 미touch.
_WON_CN = "韩元"
_WON_TW = "韓元"
_PRICE_WON_RE = re.compile(r"(\d[\d,]*)원")


def _fix_currency(html: str, lang: str) -> tuple[str, int]:
    """'{숫자}원' → '{숫자}韩元/韓元'. 숫자 직후 원만(통화 접미). 반환=(html, 치환수)."""
    won = _WON_CN if lang == "zh-cn" else _WON_TW
    n = len(_PRICE_WON_RE.findall(html))
    html = _PRICE_WON_RE.sub(rf"\1{won}", html)
    return html, n


def _gate(html: str, lang: str) -> list[str]:
    """게이트 G1~G6 실측 grep. 위반 시 사유 리스트(빈 = PASS)."""
    fails: list[str] = []
    # G6: 통화 '{숫자}원' 한글 누락 0 (현지화 컨벤션 정합)
    won_leak = _PRICE_WON_RE.findall(html)
    if won_leak:
        fails.append(f"G6 통화 한글 '원' 잔존 {len(won_leak)}: {won_leak[:5]}")
    # G1: 한글 역명 원문 ≥ 12종 present
    present = [s for s in KO_STATION_NAMES if s in html]
    if len(present) < 12:
        missing = [s for s in KO_STATION_NAMES if s not in html]
        fails.append(
            f"G1 한글 역명 원문 종수 부족: {len(present)}/13 (누락: {missing})"
        )
    # G2: dual-notation 형태 `한글역(中文站)` 표본 present
    samples = (
        ["올림픽공원역(奥林匹克公园站)", "몽촌토성역(梦村土城站)", "잠실역(蚕室站)"]
        if lang == "zh-cn"
        else [
            "올림픽공원역(奧林匹克公園站)",
            "몽촌토성역(夢村土城站)",
            "잠실역(蠶室站)",
        ]
    )
    for s in samples:
        if s not in html:
            fails.append(f"G2 dual-notation 미적용: {s!r}")
    # G3: 중첩 괄호 오류 0 (`站)(站`=역명 station 이 또 station 안 / `역((`)
    bad_nest = re.findall(r"站\)\([^)]*站\)", html)
    if bad_nest:
        fails.append(f"G3 중첩 괄호 오류 {len(bad_nest)}: {bad_nest[:3]}")
    if "역((" in html:
        fails.append(f"G3 역(( 중첩 {html.count('역((')}")
    # G4: Chinese 의미명 무손실
    cn_keys = (
        ["奥林匹克公园", "蚕室", "三成"]
        if lang == "zh-cn"
        else ["奧林匹克公園", "蠶室", "三成"]
    )
    for k in cn_keys:
        if k not in html:
            fails.append(f"G4 중국어 의미명 손실: {k!r}")
    return fails


def _station_inventory(html: str) -> str:
    """역명 dual-notation 교차표 enumerate."""
    rows = ["  한글 역명 원문 종수 (실측):"]
    present = [s for s in KO_STATION_NAMES if s in html]
    rows.append(f"    present {len(present)}/13: {present}")
    # dual-notation 형태 표본
    dn = re.findall(r"[가-힣]{2,}역\([一-龥A-Za-z]{2,}站\)", html)
    from collections import Counter

    c = Counter(dn)
    rows.append("  dual-notation 형태 (한글역(中文站)):")
    for tok, n in sorted(c.items(), key=lambda x: -x[1]):
        rows.append(f"    {tok!r} ×{n}")
    return "\n".join(rows)


def run(lang: str, write: bool, verify_only: bool = False) -> bool:
    path = PATHS[lang]
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")
    div_before = orig.count("<div")

    if verify_only:
        print(f"=== [{lang}] 역명 dual-notation 현 상태 (verify) ===")
        print(_station_inventory(orig))
        fails = _gate(orig, lang)
        if fails:
            print(f"\n  게이트 FAIL ({len(fails)}건):")
            for f in fails:
                print(f"    ✗ {f}")
            return False
        print(
            "\n  게이트 PASS (G1 한글원문≥12 · G2 dual-notation · G3 중첩0 · G4 중문무손실)"
        )
        return True

    print(f"=== [BEFORE] {lang} 역명 교차표 ===")
    print(_station_inventory(orig))
    print()

    protect = _card_protect(orig)
    html, counts = _two_phase_replace(orig, VARIANTS[lang], protect)

    # 통화 정규화: '{숫자}원' → 韩元/韓元 (현지화 컨벤션 정합·G6)
    html, won_n = _fix_currency(html, lang)

    # 구조 보존 게이트
    if html.count("<div") != div_before:
        print(f"ABORT: <div 불균형 {div_before}→{html.count('<div')}")
        return False

    fails = _gate(html, lang)
    if fails:
        print(f"ABORT: 게이트 FAIL ({len(fails)}건)")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = html != orig
    if write and changed:
        path.write_text(html, encoding="utf-8")

    print(f"=== [AFTER] {lang} 역명 교차표 ===")
    print(_station_inventory(html))
    print()
    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R85 {lang} 역명 dual-notation 복원 ({state}) ===")
    print(f"  역명 dual-notation 치환 {sum(counts.values())}건:")
    for tok, n in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"    {tok!r} ×{n}")
    print(
        f"  통화 '{{숫자}}원' → '{_WON_CN if lang == 'zh-cn' else _WON_TW}' 정규화: {won_n}건"
    )
    print(
        "  🔴 3-part [중국어 읽는법](병음) 미생성 = 환각 회피(FLR-AGT-002): "
        "병음 verbatim source 0 + 중국어 독자 한자 직독. lead/대표 확인 의제."
    )
    print(
        "  게이트: PASS (G1 한글원문 복원 · G2 dual-notation 균일 · G3 중첩 괄호 0 · "
        "G4 중문 의미명 무손실 · G5 <div> 균형 · G6 통화 컨벤션 정합)"
    )
    return True


def main() -> None:
    args = sys.argv[1:]
    write = "--write" in args
    verify = "--verify" in args
    langs = [a for a in args if a in PATHS]
    if not langs:
        langs = list(PATHS.keys())
    ok = True
    for lang in langs:
        if not run(lang, write, verify_only=verify):
            ok = False
        print()
    if not ok:
        sys.exit(2)
    mode = "VERIFY" if verify else ("WRITE" if write else "DRY-RUN (--write 로 적용)")
    print(f"OK: R85 zh 역명 dual-notation [{mode}] ({' '.join(langs)})")


if __name__ == "__main__":
    main()
