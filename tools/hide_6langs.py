#!/usr/bin/env python3
"""
hide_6langs.py — ByVias 언어 11→5 축소 스크립트
결정: ko·en·ja·zh-cn·zh-tw 유지, es·th·id·pt·ar·vi 가리기

작업 목록:
1. 스위처 a.lng 제거 (data-lang=es/th/id/pt/ar/vi)
2. head hreflang 제거 (es/th/id/pt-BR/ar/vi)
3. 6개 dir 삭제 (dist/es,th,id,pt,ar,vi)
4. sitemap.xml 해당 언어 url 블록 + alternate 제거
5. JS 리다이렉트 로직 확인 (없으면 무수정)

실행: python3 tools/hide_6langs.py
"""

import glob
import re
import shutil
from pathlib import Path

DIST = Path(__file__).parent.parent / "dist"
KEEP_LANGS = {"ko", "en", "ja", "zh-cn", "zh-tw"}
REMOVE_LANGS = {"es", "th", "id", "pt", "ar", "vi"}
# hreflang 값 기준 (pt-BR 포함)
REMOVE_HREFLANG = {"es", "th", "id", "pt-BR", "ar", "vi"}
# data-lang 값 기준
REMOVE_DATA_LANG = {"es", "th", "id", "pt", "ar", "vi"}


# ── HTML 파일 대상 수집 ──────────────────────────────────────────────────
def collect_html_files():
    files = []
    # 루트 이벤트 HTML + index
    files += glob.glob(str(DIST / "*.html"))
    # 유지 언어 하위 디렉토리
    for lang in KEEP_LANGS:
        lang_dir = DIST / lang
        if lang_dir.exists():
            files += glob.glob(str(lang_dir / "*.html"))
    return sorted(set(files))


# ── 1. 스위처 a.lng 제거 ─────────────────────────────────────────────────
def remove_lng_anchors(content: str) -> tuple[str, int]:
    """data-lang이 REMOVE_DATA_LANG인 <a class="lng" ...>...</a> 제거"""
    count = 0
    for lang in REMOVE_DATA_LANG:
        # <a class="lng" ... data-lang="es" ...>텍스트</a>
        # 속성 순서가 다를 수 있으므로 lookahead 방식
        pattern = r'<a\b[^>]*\bdata-lang="' + re.escape(lang) + r'"[^>]*>.*?</a>'
        new_content, n = re.subn(pattern, "", content, flags=re.DOTALL)
        count += n
        content = new_content
    return content, count


# ── 2. head hreflang 제거 ────────────────────────────────────────────────
def remove_hreflang_links(content: str) -> tuple[str, int]:
    """hreflang 값이 REMOVE_HREFLANG인 <link rel="alternate"> 제거"""
    count = 0
    for lang in REMOVE_HREFLANG:
        pattern = r'<link\b[^>]*\bhreflang="' + re.escape(lang) + r'"[^>]*>\n?'
        new_content, n = re.subn(pattern, "", content)
        count += n
        content = new_content
    return content, count


# ── 3. HTML 파일 처리 ────────────────────────────────────────────────────
def process_html_files(files: list) -> dict:
    stats = {"files_modified": 0, "lng_removed": 0, "hreflang_removed": 0}
    for fpath in files:
        with open(fpath, encoding="utf-8") as f:
            original = f.read()

        content, n_lng = remove_lng_anchors(original)
        content, n_hreflang = remove_hreflang_links(content)

        if content != original:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(content)
            stats["files_modified"] += 1
            stats["lng_removed"] += n_lng
            stats["hreflang_removed"] += n_hreflang

    return stats


# ── 4. 6개 dir 삭제 ──────────────────────────────────────────────────────
def delete_lang_dirs() -> list:
    deleted = []
    for lang in REMOVE_LANGS:
        lang_dir = DIST / lang
        if lang_dir.exists():
            shutil.rmtree(lang_dir)
            deleted.append(lang)
        else:
            print(f"  [WARN] {lang_dir} 이미 없음 — 스킵")
    return deleted


# ── 5. sitemap.xml 처리 ──────────────────────────────────────────────────
def process_sitemap() -> dict:
    sitemap = DIST / "sitemap.xml"
    if not sitemap.exists():
        return {"status": "NOT_FOUND"}

    with open(sitemap, encoding="utf-8") as f:
        content = f.read()

    original = content

    # (a) 6개 언어 경로를 포함한 <url>...</url> 블록 전체 제거
    # /es/, /th/, /id/, /pt/, /ar/, /vi/ 경로가 loc 안에 있는 url 블록 제거
    lang_path_pattern = r"/(?:" + "|".join(REMOVE_LANGS) + r")/"

    def remove_url_blocks(text: str) -> tuple[str, int]:
        url_block_pattern = (
            r"<url>\s*<loc>[^<]*(?:"
            + lang_path_pattern[1:-1]
            + r")[^<]*</loc>.*?</url>\s*"
        )
        new_text, n = re.subn(url_block_pattern, "", text, flags=re.DOTALL)
        return new_text, n

    content, n_url_blocks = remove_url_blocks(content)

    # (b) 남은 entry 안의 <xhtml:link hreflang="es/th/id/pt-BR/ar/vi" ...> alternate 제거
    xhtml_count = 0
    for lang in REMOVE_HREFLANG:
        pattern = (
            r'\s*<xhtml:link\b[^>]*\bhreflang="' + re.escape(lang) + r'"[^/]*/>\s*'
        )
        new_content, n = re.subn(pattern, "\n", content)
        xhtml_count += n
        content = new_content

    # 연속 공백 줄 정리
    content = re.sub(r"\n{3,}", "\n\n", content)

    if content != original:
        with open(sitemap, "w", encoding="utf-8") as f:
            f.write(content)

    return {
        "status": "MODIFIED" if content != original else "UNCHANGED",
        "url_blocks_removed": n_url_blocks,
        "xhtml_alternates_removed": xhtml_count,
    }


# ── 6. JS 리다이렉트 확인 ────────────────────────────────────────────────
def check_js_redirects() -> str:
    js_files = glob.glob(str(DIST / "assets" / "*.js"))
    found = []
    for jf in js_files:
        with open(jf, encoding="utf-8") as f:
            text = f.read()
        if re.search(
            r"navigator\.language|window\.location.*(?:"
            + "|".join(REMOVE_LANGS)
            + r")",
            text,
        ):
            found.append(jf)
    return found


# ── verify 출력 ──────────────────────────────────────────────────────────
def run_verify():
    print("\n[VERIFY]")

    # 샘플 3개 스위처 카운트
    samples = [
        DIST / "twice-thisisfor-seoul.html",
        DIST / "en" / "twice-thisisfor-seoul.html",
        DIST / "zh-cn" / "twice-thisisfor-seoul.html",
    ]
    for s in samples:
        if s.exists():
            with open(s, encoding="utf-8") as f:
                content = f.read()
            lng_count = len(re.findall(r'class="lng"', content))
            hreflang_count = len(re.findall(r'<link[^>]+rel="alternate"', content))
            print(
                f"  {s.relative_to(DIST)}: a.lng={lng_count}개, hreflang(alternate)={hreflang_count}개"
            )
        else:
            print(f"  [NOT FOUND] {s}")

    # 6개 dir 부재
    missing_dirs = [lang for lang in REMOVE_LANGS if not (DIST / lang).exists()]
    print(f"\n  삭제된 dir ({len(missing_dirs)}/6): {missing_dirs}")

    # data-lang 잔재
    residual = []
    for html in collect_html_files():
        with open(html, encoding="utf-8") as f:
            text = f.read()
        for lang in REMOVE_DATA_LANG:
            if f'data-lang="{lang}"' in text:
                residual.append(html)
                break
    print(f"\n  data-lang 잔재 파일 수: {len(residual)} (0이어야 PASS)")

    # sitemap 잔재
    sitemap = DIST / "sitemap.xml"
    if sitemap.exists():
        with open(sitemap, encoding="utf-8") as f:
            sm = f.read()
        sm_count = sum(sm.count(f"/{lang}/") for lang in REMOVE_LANGS)
        print(f"  sitemap 6언어 경로 잔재: {sm_count} (0이어야 PASS)")
    else:
        print("  sitemap.xml 없음")


# ── main ─────────────────────────────────────────────────────────────────
def main():
    print("=== hide_6langs.py 시작 ===")
    print(f"DIST: {DIST}")

    # 6개 dir 사전 존재 확인
    print("\n[STEP 0] 삭제 대상 dir 확인")
    for lang in sorted(REMOVE_LANGS):
        exists = (DIST / lang).exists()
        print(f"  dist/{lang}: {'존재' if exists else '없음(WARN)'}")

    # HTML 파일 수집
    html_files = collect_html_files()
    print(f"\n[STEP 1+2] HTML 처리 대상: {len(html_files)}개")

    # HTML 처리 (스위처 + hreflang)
    stats = process_html_files(html_files)
    print(f"  수정된 파일: {stats['files_modified']}개")
    print(f"  a.lng 제거: {stats['lng_removed']}건")
    print(f"  hreflang 제거: {stats['hreflang_removed']}건")

    # 6개 dir 삭제
    print("\n[STEP 3] 6개 언어 dir 삭제 (lead 사전 승인됨)")
    deleted = delete_lang_dirs()
    print(f"  삭제 완료: {deleted}")

    # sitemap 처리
    print("\n[STEP 4] sitemap.xml 처리")
    sm_stats = process_sitemap()
    print(f"  상태: {sm_stats}")

    # JS 리다이렉트 확인
    print("\n[STEP 5] JS 리다이렉트 확인")
    js_found = check_js_redirects()
    if js_found:
        print(f"  [주의] 리다이렉트 로직 발견: {js_found}")
    else:
        print("  리다이렉트 로직 없음 — JS 무수정")

    # verify
    run_verify()
    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()
