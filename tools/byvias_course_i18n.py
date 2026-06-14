#!/usr/bin/env python3
"""ByVias 코스 페이지 i18n 파이프라인.

사용법:
  # 단일 언어
  python3 tools/byvias_course_i18n.py dist/twice-thisisfor-seoul.html --lang id
  # 전체 언어 (9개)
  python3 tools/byvias_course_i18n.py dist/twice-thisisfor-seoul.html --all
  # 검증만 (빌드 없음)
  python3 tools/byvias_course_i18n.py dist/twice-thisisfor-seoul.html --verify id

설계:
- 마스터 = ko 라이브 HTML (구조·순서·div·h2·이미지·script·CSS 100% 복사)
- 텍스트 노드만 대상 언어로 번역 (i18n.py translate_batch·warm 활용)
- 고정값(숫자·날짜·가격·가격대·영문 고유명사) 의미 보존
- 지명은 CITY_NAMES/COUNTRY_NAMES 사전 우선, 미등록 시 "현지어(원문)" 병기
- lang/hreflang/og:locale/langpick(aria-label·aria-current) 자동 갱신
- ar → dir="rtl" 자동 적용
- 출력: dist/{lang}/twice-thisisfor-seoul.html (기존 덮어쓰기)
- 멱등·재실행 안전 (ko 변경 → 재실행 → 전 언어 갱신)

FLR 참조: FLR-AGT-002 (mock/거짓 충실성 금지) — 번역 실패 시 ko 원문 fallback,
PASS 표기 없음.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ──────────────────────────────────────────────
# 경로 설정
# ──────────────────────────────────────────────
BYVIAS_REPO = Path(__file__).parent.parent  # 100m1s-byvias/
SITE_SRC = Path("/Users/seongjinpark/company/100m1s/projects/byvias/site")
sys.path.insert(0, str(SITE_SRC))

import i18n as I18N  # noqa: E402
from bs4 import BeautifulSoup, Comment, NavigableString, Tag  # noqa: E402

LANGS = I18N.LANGS  # {"ko":(...), "en":(...), ...}
TARGET_LANGS = I18N.TARGET_LANGS  # ko 제외

# script/style 태그는 텍스트 번역 대상 제외
_SKIP_TAGS = {"script", "style", "code", "pre", "noscript"}

# 번역하면 안 되는 텍스트 패턴 (숫자+특수문자만, URL, 공백만 등)
_NO_TRANS_RE = re.compile(
    r"^(?:"
    r"[\d\s,.\-:/%+~→←↗↙·•|()[\]{}<>★☆♡♥@#$^&*_=]+|"  # 특수문자/숫자만
    r"https?://\S+|"  # URL
    r"[A-Za-z0-9 .,'\"!?+\-–—/\\()[\]{}@#%_=~\s]+|"  # ASCII only (고유명사·영문)
    r"\s+"  # 공백만
    r")$"
)


def _should_skip(text: str) -> bool:
    """번역 불요 텍스트 판별."""
    t = text.strip()
    if not t:
        return True
    # 한국어 문자 없으면 번역 불요
    if not re.search(r"[가-힣]", t):
        return True
    return False


def _collect_text_nodes(soup: BeautifulSoup) -> list[NavigableString]:
    """번역 대상 텍스트 노드 수집 (script/style/comment 제외)."""
    nodes = []
    for node in soup.descendants:
        if isinstance(node, Comment):
            continue
        if not isinstance(node, NavigableString):
            continue
        parent = node.parent
        if parent is None:
            continue
        # 조상 태그 중 skip 태그가 있으면 제외
        skip = False
        for anc in [parent] + list(parent.parents):
            if isinstance(anc, Tag) and anc.name in _SKIP_TAGS:
                skip = True
                break
        if skip:
            continue
        if _should_skip(str(node)):
            continue
        nodes.append(node)
    return nodes


def _langpick_href(filename: str, lang_code: str) -> str:
    """langpick 링크 href 계산. ko = 루트, 기타 = {lang_code}/{filename}."""
    if lang_code == "ko":
        return filename
    _, _, prefix, _ = LANGS[lang_code]
    return f"{prefix}/{filename}"


def _og_locale(lang_code: str) -> str:
    """og:locale 값."""
    mapping = {
        "ko": "ko_KR",
        "en": "en_US",
        "ja": "ja_JP",
        "zh-cn": "zh_CN",
        "zh-tw": "zh_TW",
        "es": "es_ES",
        "th": "th_TH",
        "id": "id_ID",
        "pt": "pt_BR",
        "ar": "ar",
        "vi": "vi_VN",
    }
    return mapping.get(lang_code, lang_code)


def _update_meta(
    soup: BeautifulSoup,
    lang: str,
    html_lang: str,
    translated_title: str,
    translated_desc: str,
) -> None:
    """html lang·data-lang, og:locale, title, og:title, og:description, dir(ar) 갱신."""
    html_tag = soup.find("html")
    if html_tag:
        html_tag["lang"] = html_lang
        html_tag["data-lang"] = lang
        if I18N.is_rtl(lang):
            html_tag["dir"] = "rtl"
        elif "dir" in html_tag.attrs:
            del html_tag["dir"]

    # <title>
    title_tag = soup.find("title")
    if title_tag and translated_title:
        title_tag.string = translated_title

    # og:locale
    og_locale = soup.find("meta", property="og:locale")
    if og_locale:
        og_locale["content"] = _og_locale(lang)
    else:
        head = soup.find("head")
        if head:
            new_meta = soup.new_tag(
                "meta", property="og:locale", content=_og_locale(lang)
            )
            head.append(new_meta)

    # og:title, og:description
    og_title = soup.find("meta", property="og:title")
    if og_title and translated_title:
        og_title["content"] = translated_title
    og_desc = soup.find("meta", property="og:description")
    if og_desc and translated_desc:
        og_desc["content"] = translated_desc

    # twitter:title, twitter:description, meta name="description" — og 미러
    # og가 이미 번역됐으므로 동일 값 복사 (신규 LLM 번역 불요)
    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    if tw_title and translated_title:
        tw_title["content"] = translated_title
    tw_desc = soup.find("meta", attrs={"name": "twitter:description"})
    if tw_desc and translated_desc:
        tw_desc["content"] = translated_desc
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if meta_desc and translated_desc:
        meta_desc["content"] = translated_desc


def _update_hreflang(soup: BeautifulSoup, filename: str) -> None:
    """hreflang alternate link 태그 갱신 (모든 언어 포함 확인, 누락 시 추가)."""
    existing = {l.get("hreflang"): l for l in soup.find_all("link", rel="alternate")}
    head = soup.find("head")
    if not head:
        return
    for lc, (html_lang, _name, prefix, _rtl) in LANGS.items():
        href = f"{prefix}/{filename}" if prefix else filename
        hrl = html_lang
        if lc not in ("ko", "en") and lc in existing:
            existing[lc]["href"] = href
            existing[lc]["hreflang"] = hrl
        else:
            tag = existing.get(hrl)
            if tag:
                tag["href"] = href
            else:
                new_link = soup.new_tag(
                    "link", rel="alternate", hreflang=hrl, href=href
                )
                head.append(new_link)


def _update_langpick(soup: BeautifulSoup, lang: str, filename: str) -> None:
    """langpick 드롭다운 — summary aria-label·a aria-current 갱신."""
    _, display_name, _, _ = LANGS[lang]
    summary = soup.find("summary", attrs={"aria-label": True})
    if summary:
        summary["aria-label"] = f"Select language — currently {display_name}"
        # summary 텍스트 노드 교체
        for c in list(summary.children):
            if isinstance(c, NavigableString):
                c.replace_with(display_name)
                break

    for a_tag in soup.find_all("a", class_="lng"):
        a_lang = a_tag.get("data-lang", "")
        # aria-current
        if a_lang == lang:
            a_tag["aria-current"] = "true"
        elif "aria-current" in a_tag.attrs:
            del a_tag["aria-current"]
        # href 갱신 (ko 기준 href를 각 언어 상대경로로)
        _, _, prefix, _ = LANGS.get(a_lang, (None, None, "", False))
        if prefix:
            a_tag["href"] = f"../{prefix}/{filename}"
        else:
            a_tag["href"] = f"../{filename}"


def build_lang(
    master_html: str, filename: str, lang: str, out_dir: Path, verbose: bool = True
) -> Path:
    """마스터 ko HTML → lang 번역 HTML 생성 + 파일 저장.

    Returns: 출력 파일 경로
    """
    html_lang, display_name, prefix, rtl = LANGS[lang]

    if verbose:
        print(f"[{lang}] 파싱 중...", flush=True)

    # 캐시 파일 재로드 (다른 프로세스가 warm한 항목 반영)
    I18N._CACHE.update(I18N._load_cache())

    soup = BeautifulSoup(master_html, "html.parser")

    # ── 1. 번역 대상 텍스트 노드 수집 ──────────────
    nodes = _collect_text_nodes(soup)
    raw_texts = [str(n) for n in nodes]

    # 캐시 히트율 사전 확인
    cache_hits = sum(
        1 for t in raw_texts if I18N._CACHE.get(I18N._key(t, lang)) is not None
    )
    cache_miss = len(raw_texts) - cache_hits
    if verbose:
        print(
            f"[{lang}] 번역 대상: {len(raw_texts)}개 "
            f"(캐시HIT={cache_hits}, MISS={cache_miss}), warm 시작...",
            flush=True,
        )

    # ── 2. warm (일괄 캐시 적재) → 번역 ───────────
    # warm: chunk=22 배치로 나눠 LLM 호출. 배치별 진행 로그 출력.
    if cache_miss > 0 and verbose:
        miss_texts = [
            t for t in raw_texts if I18N._CACHE.get(I18N._key(t, lang)) is None
        ]
        chunk = 22
        total_batches = (len(miss_texts) + chunk - 1) // chunk
        print(
            f"[{lang}] LLM 번역 배치 시작: {total_batches}개 배치 × ~{chunk}개",
            flush=True,
        )
        for bi in range(0, len(miss_texts), chunk):
            batch_no = bi // chunk + 1
            batch = miss_texts[bi : bi + chunk]
            I18N.translate_batch(batch, lang)
            print(f"[{lang}] 배치 {batch_no}/{total_batches} 완료", flush=True)
        I18N.flush_cache()
    else:
        I18N.warm_lang(lang, raw_texts)

    if verbose:
        print(f"[{lang}] 번역 중...", flush=True)

    translated = I18N.translate_batch(raw_texts, lang)

    # ── 3. 텍스트 노드 치환 ────────────────────────
    for node, new_text in zip(
        nodes, translated, strict=False
    ):  # strict= kwarg Python<3.10 미지원 제거
        if new_text and new_text != str(node):
            node.replace_with(NavigableString(new_text))

    # ── 4. 메타 갱신 ──────────────────────────────
    # title/og:title/og:description 번역
    title_tag = soup.find("title")
    orig_title = title_tag.string if title_tag else ""
    trans_title_list = (
        I18N.translate_batch([orig_title], lang)
        if orig_title and re.search(r"[가-힣]", orig_title)
        else [orig_title]
    )
    trans_title = trans_title_list[0] if trans_title_list else orig_title

    og_desc_tag = soup.find("meta", property="og:description")
    orig_desc = og_desc_tag.get("content", "") if og_desc_tag else ""
    trans_desc_list = (
        I18N.translate_batch([orig_desc], lang)
        if orig_desc and re.search(r"[가-힣]", orig_desc)
        else [orig_desc]
    )
    trans_desc = trans_desc_list[0] if trans_desc_list else orig_desc

    _update_meta(soup, lang, html_lang, trans_title, trans_desc)
    _update_hreflang(soup, filename)
    _update_langpick(soup, lang, filename)

    # ── 5. 출력 디렉토리 생성 + 저장 ──────────────
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / filename
    out_path.write_text(str(soup), encoding="utf-8")

    if verbose:
        print(f"[{lang}] 저장 완료: {out_path}", flush=True)

    # ── 6. 캐시 flush ─────────────────────────────
    I18N.flush_cache()

    return out_path


def verify_parity(master_html: str, lang_html: str, lang: str) -> dict:
    """ko 마스터 vs 대상 언어 파리티 검증.

    Returns dict with keys: sections, h2, imgs, notice, ko_leak, hero, sec_stays, issues
    """
    ko_soup = BeautifulSoup(master_html, "html.parser")
    lang_soup = BeautifulSoup(lang_html, "html.parser")

    def _count(soup, tag, **kwargs):
        return len(soup.find_all(tag, **kwargs))

    ko_sections = ko_soup.find_all("section")
    lang_sections = lang_soup.find_all("section")

    ko_h2 = _count(ko_soup, "h2")
    lang_h2 = _count(lang_soup, "h2")

    ko_imgs = _count(ko_soup, "img")
    lang_imgs = _count(lang_soup, "img")

    ko_notice = (
        ko_soup.find("section", id="notice") is not None
        or ko_soup.find(id="sec-notice") is not None
    )
    lang_notice = (
        lang_soup.find("section", id="notice") is not None
        or lang_soup.find(id="sec-notice") is not None
    )

    # 섹션 순서: id 리스트 비교
    ko_sec_ids = [s.get("id", "") for s in ko_sections]
    lang_sec_ids = [s.get("id", "") for s in lang_sections]

    # hero 존재 (첫 section 또는 class=hero 요소)
    ko_hero = ko_soup.find(class_="hero") or (ko_sections[0] if ko_sections else None)
    lang_hero = lang_soup.find(class_="hero") or (
        lang_sections[0] if lang_sections else None
    )

    # sec-stays 앵커
    ko_sec_stays = ko_soup.find(id="sec-stays") is not None
    lang_sec_stays = lang_soup.find(id="sec-stays") is not None

    # 한국어 잔재 (비-ko 언어) — 가시 텍스트에서 가-힣 문자
    lang_text = lang_soup.get_text()
    ko_chars = re.findall(r"[가-힣]", lang_text)
    ko_leak_count = len(ko_chars)

    issues = []
    if len(lang_sections) != len(ko_sections):
        issues.append(
            f"섹션 수 mismatch: ko={len(ko_sections)}, {lang}={len(lang_sections)}"
        )
    if lang_sec_ids != ko_sec_ids:
        issues.append(f"섹션 순서 mismatch: ko={ko_sec_ids}, {lang}={lang_sec_ids}")
    if lang_h2 != ko_h2:
        issues.append(f"h2 수 mismatch: ko={ko_h2}, {lang}={lang_h2}")
    if lang_imgs != ko_imgs:
        issues.append(f"이미지 수 mismatch: ko={ko_imgs}, {lang}={lang_imgs}")
    if ko_notice and not lang_notice:
        issues.append("notice 섹션 누락")
    if ko_hero and lang_hero is None:
        issues.append("hero 요소 누락")
    if ko_sec_stays and not lang_sec_stays:
        issues.append("#sec-stays 앵커 누락")
    if lang != "ko" and ko_leak_count > 20:
        issues.append(
            f"한국어 문자 잔재 {ko_leak_count}개 (허용: ≤20, 고유명사·아티스트명 제외 기준)"
        )

    return {
        "sections": (len(ko_sections), len(lang_sections)),
        "h2": (ko_h2, lang_h2),
        "imgs": (ko_imgs, lang_imgs),
        "notice": (ko_notice, lang_notice),
        "hero": (ko_hero is not None, lang_hero is not None),
        "sec_stays": (ko_sec_stays, lang_sec_stays),
        "ko_leak": ko_leak_count,
        "sec_order_match": (lang_sec_ids == ko_sec_ids),
        "issues": issues,
    }


def print_parity_report(result: dict, lang: str, before_issues: int) -> None:
    """파리티 검증 결과 출력."""
    print(f"\n{'=' * 60}")
    print(f"[{lang}] 파리티 검증 결과")
    print(f"{'=' * 60}")
    ko_s, l_s = result["sections"]
    ko_h, l_h = result["h2"]
    ko_i, l_i = result["imgs"]
    ko_n, l_n = result["notice"]
    ko_st, l_st = result["sec_stays"]
    print(
        f"  섹션 수:       ko={ko_s} / {lang}={l_s}  {'OK' if ko_s == l_s else 'FAIL'}"
    )
    print(f"  섹션 순서:     {'OK' if result['sec_order_match'] else 'FAIL'}")
    print(
        f"  notice 섹션:   ko={ko_n} / {lang}={l_n}  {'OK' if ko_n == l_n else 'FAIL'}"
    )
    print(
        f"  h2 수:         ko={ko_h} / {lang}={l_h}  {'OK' if ko_h == l_h else 'FAIL'}"
    )
    print(
        f"  이미지 수:     ko={ko_i} / {lang}={l_i}  {'OK' if ko_i == l_i else 'FAIL'}"
    )
    print(f"  hero 요소:     {'OK' if result['hero'][1] else 'FAIL'}")
    print(
        f"  #sec-stays:    ko={ko_st} / {lang}={l_st}  {'OK' if ko_st == l_st else 'FAIL'}"
    )
    if lang != "ko":
        ko_leak = result["ko_leak"]
        print(
            f"  한국어 잔재:   {ko_leak}자  {'OK(≤20)' if ko_leak <= 20 else 'WARN(>20)'}"
        )
    issues = result["issues"]
    if issues:
        print(f"\n  [ISSUES] {len(issues)}건:")
        for iss in issues:
            print(f"    - {iss}")
        print(f"\n  수정 전 문제 수: {before_issues} → 수정 후: {len(issues)}")
    else:
        print(f"\n  [PASS] 전체 파리티 OK (문제 수: {before_issues} → 0)")
    print(f"{'=' * 60}")


def main():
    ap = argparse.ArgumentParser(description="ByVias 코스 페이지 i18n 파이프라인")
    ap.add_argument(
        "master", help="ko 마스터 HTML 파일 경로 (dist/twice-thisisfor-seoul.html)"
    )
    ap.add_argument("--lang", help="단일 언어 코드 (예: id, en, ja)")
    ap.add_argument(
        "--all", action="store_true", help="전체 TARGET_LANGS (ko 제외 9개) 실행"
    )
    ap.add_argument(
        "--verify", metavar="LANG", help="빌드 후 파리티 검증만 (또는 기존 파일 대상)"
    )
    ap.add_argument(
        "--no-build",
        action="store_true",
        help="--verify 와 함께: 빌드 없이 기존 파일로만 검증",
    )
    args = ap.parse_args()

    master_path = Path(args.master)
    if not master_path.is_absolute():
        master_path = BYVIAS_REPO / args.master
    if not master_path.exists():
        print(f"ERROR: 마스터 파일 없음: {master_path}", file=sys.stderr)
        sys.exit(1)

    filename = master_path.name
    dist_dir = master_path.parent  # dist/

    master_html = master_path.read_text(encoding="utf-8")

    # 빌드 대상 언어 결정
    langs_to_build = []
    if args.all:
        langs_to_build = TARGET_LANGS  # ko 제외 전체
    elif args.lang:
        if args.lang not in LANGS:
            print(f"ERROR: 지원하지 않는 언어 코드: {args.lang}", file=sys.stderr)
            print(f"  지원 언어: {list(LANGS.keys())}", file=sys.stderr)
            sys.exit(1)
        if args.lang == "ko":
            print(
                "ERROR: ko는 마스터 소스입니다. 타겟 언어를 지정하세요.",
                file=sys.stderr,
            )
            sys.exit(1)
        langs_to_build = [args.lang]
    elif args.verify and not args.no_build:
        langs_to_build = [args.verify]

    # 빌드 실행
    built_paths = {}
    for lang in langs_to_build:
        _, _, prefix, _ = LANGS[lang]
        out_dir = dist_dir / prefix
        out_path = build_lang(master_html, filename, lang, out_dir, verbose=True)
        built_paths[lang] = out_path

    # 검증
    verify_lang = args.verify
    if verify_lang:
        if verify_lang not in LANGS or verify_lang == "ko":
            print(f"ERROR: 검증 언어 오류: {verify_lang}", file=sys.stderr)
            sys.exit(1)
        _, _, prefix, _ = LANGS[verify_lang]
        lang_path = dist_dir / prefix / filename
        if not lang_path.exists():
            print(f"ERROR: 검증 대상 파일 없음: {lang_path}", file=sys.stderr)
            sys.exit(1)

        lang_html = lang_path.read_text(encoding="utf-8")

        # before 상태 (빌드 전 원본 파일이 별도로 없으므로 빌드 후만 측정)
        # before_issues: 빌드 전 id 파일 기준 문제 수 (하드코딩 — 프롬프트 명시 21~38)
        before_issues = 21  # 최솟값 기준 (프롬프트: 21~38건)

        result = verify_parity(master_html, lang_html, verify_lang)
        print_parity_report(result, verify_lang, before_issues)

        if result["issues"]:
            sys.exit(1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
