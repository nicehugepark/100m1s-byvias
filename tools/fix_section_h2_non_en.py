#!/usr/bin/env python3
"""
CP0-1 확장: 비-en 10개 언어 dist 섹션 헤더 div → h2 변환 (WCAG 1.3.1)

변환 대상: <div style="font-weight:600;font-size:14px[;margin-top:...]">
변환 제외: margin-bottom 포함 div (다음 공연·아티스트·현지정보·안전 박스 헤더)

멱등: 이미 h2인 경우 스킵. 번역 0 · LLM 0 · 태그 구조만.
대상 언어: en 제외 10개 (ja·zh-tw·zh-cn·es·th·id·pt·ar·vi + ko 재확인)
"""

import re
from pathlib import Path

DIST_DIR = Path(__file__).parent.parent / "dist"

NON_EN_LANGS = ["ja", "zh-tw", "zh-cn", "es", "th", "id", "pt", "ar", "vi", "ko"]

# 섹션 헤더 패턴 — font-weight:600;font-size:14px 로 시작하며 margin-bottom이 없는 div
SECTION_DIV_RE = re.compile(
    r'<div\s+style="font-weight:600;font-size:14px(?:;margin-top:[^;"]*)?">',
)


def convert_file(path: Path) -> int:
    """파일 내 섹션 헤더 div → h2 변환. 변환 수 반환."""
    content = path.read_text(encoding="utf-8")
    count = 0

    new_content = []
    pos = 0
    for m in SECTION_DIV_RE.finditer(content):
        new_content.append(content[pos : m.start()])
        full_div_open = m.group(0)
        style_content = re.search(r'style="([^"]*)"', full_div_open).group(1)

        # 대응 </div> 위치 찾기
        after_open = content[m.end() :]
        close_idx = after_open.find("</div>")

        if close_idx == -1:
            new_content.append(full_div_open)
            pos = m.end()
            continue

        inner_html = after_open[:close_idx]

        # 내부에 <div> 가 있으면 중첩 div — 안전 제외
        if "<div" in inner_html:
            new_content.append(full_div_open)
            pos = m.end()
            continue

        count += 1
        new_content.append(f'<h2 style="{style_content}">')
        new_content.append(inner_html)
        new_content.append("</h2>")
        pos = m.end() + close_idx + len("</div>")

    new_content.append(content[pos:])
    new_text = "".join(new_content)

    if new_text != content:
        path.write_text(new_text, encoding="utf-8")

    return count


def main() -> None:
    lang_summary = {}

    for lang in NON_EN_LANGS:
        lang_dir = DIST_DIR / lang
        if not lang_dir.exists():
            print(f"  [{lang}] 디렉토리 없음 — 스킵")
            continue

        html_files = sorted(lang_dir.glob("*.html"))
        lang_files = 0
        lang_converts = 0

        for f in html_files:
            n = convert_file(f)
            if n > 0:
                lang_files += 1
                lang_converts += n

        lang_summary[lang] = (lang_files, lang_converts)
        print(f"  [{lang}] {lang_files}개 파일, {lang_converts}건 변환")

    total_files = sum(v[0] for v in lang_summary.values())
    total_converts = sum(v[1] for v in lang_summary.values())
    print(f"\n완료: {total_files}개 파일, 총 {total_converts}건 h2 변환")
    print(
        f"언어 분포: {', '.join(f'{k}={v[0]}f/{v[1]}h' for k, v in lang_summary.items())}"
    )


if __name__ == "__main__":
    main()
