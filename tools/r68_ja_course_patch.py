#!/usr/bin/env python3
"""R68 ja 코스/이벤트 페이지 미번역 전수 fix.

수정 항목:
  P0-1. jbar locale: l:"ko" → l:"ja"
  P0-2. 인라인 JS 한글: 일 남음→日後, 오늘→今日, 선예매 D-→先行 D-,
         선예매 오늘→先行 今日, 오늘 오픈→本日オープン, 종료→終了 (뱃지),
         링크가 복사됐어요→リンクをコピーしました, 주소: →住所:
  P0-3. CSS 제휴 뱃지: content:"제휴" → ja lang 오버라이드 提携 삽입
  P0-4. dh-site: bybias.100m1s.com → ByVias
  P0-5. aria-label 한글 → ja (기능설명·가시텍스트, 식당/지명 고유명사 유지)
  P0-6. alt 한글 → ja (고유명사 유지)
  P1-1. trip_sub1 _ko_ → _ja_
  P1-2. KKday /en/ → /ja/

적용: dist/ja/*.html (index.html 제외)
FLR: FLR-005 (LLM 대량번역 금지) — 하드코딩 번역 사전 사용
"""

from __future__ import annotations

import re
from pathlib import Path

BYVIAS_DIST = Path("/Users/seongjinpark/company/100m1s-byvias/dist/ja")

# ── 인라인 JS 한글 치환 (정확한 패턴만) ──────────────────────
JS_REPLACEMENTS = [
    # 카운트다운 D-day
    ("unit.textContent='일 남음';", "unit.textContent='日後';"),
    ("unit.textContent='일 남음'}", "unit.textContent='日後'}"),
    # 오늘 (카운트다운 label)
    ("label.textContent='오늘';", "label.textContent='今日';"),
    # 선예매 D-N
    ("ps.textContent='선예매 D-'+pd;", "ps.textContent='先行 D-'+pd;"),
    # 선예매 오늘
    ("ps.textContent='선예매 오늘';", "ps.textContent='先行 今日';"),
    # 티켓뱃지 오늘 오픈
    ("b.textContent='오늘 오픈';", "b.textContent='本日オープン';"),
    # 티켓뱃지 종료 (정확한 context)
    (
        "b.textContent=b.getAttribute('data-tkpast')||'종료';",
        "b.textContent=b.getAttribute('data-tkpast')||'終了';",
    ),
    # 공유 toast
    ("toast('링크가 복사됐어요');", "toast('リンクをコピーしました');"),
    ("toast('주소: '+url);", "toast('住所: '+url);"),
    # 단순 패턴 (context 없이 일 남음이 남은 경우)
    ("'일 남음'", "'日後'"),
]

# ── aria-label 번역 사전 (기능설명 → ja, 고유명사 skip) ───────
# 식당명·지명 aria-label은 제외 (고유명사)
ARIA_LABEL_MAP: dict[str, str] = {
    "이 가이드 공유하기": "このガイドをシェアする",
    "첫 공연일 카운트다운": "初日カウントダウン",
    "30초 핵심 요약": "30秒サマリー",
    "이 페이지에서 얻는 것": "このページで得られること",
    "처음이어도 이 순서대로": "初めてでもこの順番で",
    "도착 첫 1시간": "到着後の最初の1時間",
    "3일 공연 날짜 카드": "3日間の公演日程カード",
    "바로가기": "ジャンプ",
    "완료 체크": "完了チェック",
    "완료됨": "完了",
    "미완료": "未完了",
    # jbar/langpick — 이미 처리된 경우 skip
    # (Select language — currently ... : 건드리지 않음)
}

# ── alt 번역 사전 (가시 텍스트 한글 alt → ja) ────────────────
ALT_MAP: dict[str, str] = {
    "공연장을 가득 채운 핑크빛 응원봉 물결": "会場を埋め尽くすピンクのペンライトの波",
    "인천공항 도착장 — 리무진 버스 정류장으로 향하는 길": "仁川空港到着ロビー — リムジンバス乗り場への道",
    "인천공항에서 잠실까지 동선: 6705A 리무진(환승 없음) · 공항철도+9호선 · 택시": "仁川空港から蚕室までのルート: 6705Aリムジン(乗換なし) · 空港鉄道+9号線 · タクシー",
    "공연 당일 아레나 객석을 가득 메운 응원봉 불빛 물결": "公演当日のアリーナを埋め尽くすペンライトの光の波",
    "7월 10일 금요일 · 시작 19:00 · 종료 약 21:40 · D-day Night 1": "7月10日(金) · 開演19:00 · 終演約21:40 · D-day Night 1",
    "7월 11일 토요일 · 시작 18:00 · 종료 약 20:40 · Night 2": "7月11日(土) · 開演18:00 · 終演約20:40 · Night 2",
    "7월 12일 일요일 · 시작 17:00 · 종료 약 19:40 · FINALE": "7月12日(日) · 開演17:00 · 終演約19:40 · FINALE",
    "공연 종료부터 막차까지 노선별 타임라인 — 9호선 개화행 토·일 22:55가 가장 빠름, 나머지 23:55~00:54": "終演から終電までの路線別タイムライン — 9号線開花行き土日22:55が最速、その他23:55~00:54",
    "막차 단 하나의 함정 — 9호선 김포공항행은 토·일 22:55에 끊긴다. 다른 노선은 23:55~00:54.": "終電の落とし穴 — 9号線金浦空港行きは土日22:55が終電。他路線は23:55~00:54。",
    "공연 끝나고 설레는 귀갓길 — 캐리어와 응원봉을 든 원정 팬들(9호선)": "公演後の帰り道 — キャリーとペンライトを持つ遠征ファンたち(9号線)",
    "여름밤 호숫가 조명 무드 이미지": "夏の夜の湖畔照明ムードイメージ",
    "홍대 거리·연남동": "弘大通り・延南洞",
    "가로수길 짧은 아침 쇼핑": "カロスキルでの短い朝ショッピング",
    "숲길 옛 성곽 산책 무드 이미지": "森道・旧城郭散策ムードイメージ",
}

# ── title 번역 사전 ───────────────────────────────────────────
TITLE_MAP: dict[str, str] = {
    "신양로스터스 공식 인스타그램 게시물": "シンヤンロースターズ公式インスタグラム投稿",
    "잠실 송리단길 카페 인스타 사진": "蚕室ソンリダンギルカフェInstagram写真",
    "잠실 송리단길 감성 카페 인스타 사진": "蚕室ソンリダンギルセンス系カフェInstagram写真",
    "잠실 송리단길 루프탑 카페 인스타 사진": "蚕室ソンリダンギルルーフトップカフェInstagram写真",
    "송리단길·석촌호수 맛집 인스타 사진": "ソンリダンギル・石村湖グルメInstagram写真",
    # 예매 타임라인 alt — 날짜 포함 복잡 → 최대한 직역
    "예매 타임라인 — 선예매 6/9(화) 20:00, 일반예매 6/11(목) 20:00, 취소표는 예매 다음날 새벽 0~2시, 취소 마감은 관람 전일 17:00": "チケット購入タイムライン — 先行販売6/9(火)20:00、一般販売6/11(木)20:00、キャンセル票は翌日0~2時、キャンセル締切は観覧前日17:00",
    "WOWPASS 3단계 — 1.공항 키오스크에서 여권으로 발급(약 5분, 등록비 6,000원), 2.앱에서 해외카드로 충전(앱 4%·키오스크 무료), 3.티켓·교통·편의점 결제까지 한 장으로": "WOWPASS 3ステップ — 1.空港キオスクでパスポートで発行(約5分、登録費6,000ウォン)、2.アプリで海外カード入金(アプリ4%·キオスク無料)、3.チケット·交通·コンビニ決済まで1枚で",
}

# ── CSS 제휴 뱃지 — ja 오버라이드 삽입 ──────────────────────
# 기존 CSS: a[data-aff="1"]::after,.aff-eg::after{content:"제휴"}
# ja 파일에 [lang="ja"] 오버라이드 추가
AFF_CSS_PATTERN = re.compile(
    r'(a\[data-aff="1"\]::after,\.aff-eg::after\{content:"제휴"\})'
)
AFF_CSS_REPLACE = (
    r'a[data-aff="1"]::after,.aff-eg::after{content:"提携"}'
    # ja 파일이므로 직접 提携로 교체 (lang 오버라이드 불필요)
)


def patch_file(path: Path) -> dict:
    """ja 코스 페이지 1개 패치. 변경 항목 수 반환."""
    html = path.read_text(encoding="utf-8")
    original = html
    counts: dict[str, int] = {}

    # ── P0-1. jbar locale ───────────────────────────────────
    new_html, n = re.subn(
        r'(window\.__JB=\{t:"[^"]*",l:)"ko"',
        r'\1"ja"',
        html,
    )
    if n:
        counts["jbar_locale"] = n
    html = new_html

    # ── P0-2. 인라인 JS 한글 ────────────────────────────────
    for old, new in JS_REPLACEMENTS:
        if old in html:
            html = html.replace(old, new)
            counts[f"js_{old[:15].strip()}"] = 1

    # ── P0-3. CSS 제휴 → 提携 ───────────────────────────────
    new_html, n = re.subn(
        r'content:"제휴"',
        'content:"提携"',
        html,
    )
    if n:
        counts["css_aff_badge"] = n
    html = new_html

    # ── P0-4. dh-site ────────────────────────────────────────
    old_dh = 'class="dh-site">bybias.100m1s.com<'
    new_dh = 'class="dh-site">ByVias<'
    if old_dh in html:
        html = html.replace(old_dh, new_dh)
        counts["dh_site"] = 1

    # ── P0-5. aria-label 번역 ────────────────────────────────
    aria_count = 0
    for ko, ja in ARIA_LABEL_MAP.items():
        pattern = f'aria-label="{ko}"'
        replacement = f'aria-label="{ja}"'
        c = html.count(pattern)
        if c:
            html = html.replace(pattern, replacement)
            aria_count += c
    if aria_count:
        counts["aria_label"] = aria_count

    # ── P0-6. alt 한글 번역 ──────────────────────────────────
    alt_count = 0
    for ko, ja in ALT_MAP.items():
        pattern = f'alt="{ko}"'
        replacement = f'alt="{ja}"'
        c = html.count(pattern)
        if c:
            html = html.replace(pattern, replacement)
            alt_count += c
    if alt_count:
        counts["alt"] = alt_count

    # title 속성
    title_count = 0
    for ko, ja in TITLE_MAP.items():
        pattern = f'title="{ko}"'
        replacement = f'title="{ja}"'
        c = html.count(pattern)
        if c:
            html = html.replace(pattern, replacement)
            title_count += c
    if title_count:
        counts["title_attr"] = title_count

    # ── P1-1. trip_sub1 _ko_ → _ja_ ─────────────────────────
    new_html, n = re.subn(
        r"(trip_sub1=[a-zA-Z0-9_]*)_ko_",
        r"\1_ja_",
        html,
    )
    if n:
        counts["trip_sub1"] = n
    html = new_html

    # ── P1-2. KKday /en/ → /ja/ ──────────────────────────────
    new_html, n = re.subn(
        r"(kkday\.com)/en/",
        r"\1/ja/",
        html,
    )
    if n:
        counts["kkday_lang"] = n
    html = new_html

    # 변경 없으면 write skip
    if html == original:
        return {"changed": False, "counts": counts}

    path.write_text(html, encoding="utf-8")
    return {"changed": True, "counts": counts}


def main() -> None:
    files = sorted(f for f in BYVIAS_DIST.glob("*.html") if f.name != "index.html")
    total_files = len(files)
    changed_files = 0
    total_changes: dict[str, int] = {}

    print(f"[R68] ja 코스/이벤트 페이지 패치 시작 — {total_files}개", flush=True)

    for f in files:
        result = patch_file(f)
        if result["changed"]:
            changed_files += 1
            for k, v in result["counts"].items():
                total_changes[k] = total_changes.get(k, 0) + v
            print(f"  [OK] {f.name}: {result['counts']}", flush=True)
        else:
            print(f"  [skip] {f.name} — 변경 없음", flush=True)

    print(f"\n[R68] 완료 — {changed_files}/{total_files}개 수정")
    print(f"  항목별 합계: {total_changes}")


if __name__ == "__main__":
    main()
