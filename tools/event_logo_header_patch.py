#!/usr/bin/env python3
"""이벤트 페이지 헤더 로고 삽입 패치.

문제: dist/ja, dist/en, dist/zh-cn, dist/zh-tw 이벤트 페이지 + dist/*.html (ko)에
     헤더 로고가 없음. share-row div에 back 링크·공유 버튼만 있고
     <picture><source><img> 로고 요소 자체 누락.

수정:
  - share-row div를 top div로 교체 (로고 + back 링크 + 공유 버튼)
  - 언어별 로고 경로: 서브디렉토리(ja/en/zh-cn/zh-tw) → ../logo.svg, 루트(ko) → logo.svg
  - CSS: .top{display:flex;align-items:center;gap:8px;margin:0 0 6px}
         .top .logo{height:38px;width:auto;display:block}
  - 멱등: LOGO-HEADER-v1 마커로 이미 적용된 파일 스킵

멱등 마커: <!-- LOGO-HEADER-v1 -->
FLR 참조: 대표 반복 지적 — 이벤트 페이지 로고 안 뜸 (2026-06-15)
"""

from __future__ import annotations

import re
from pathlib import Path

DIST = Path("/Users/seongjinpark/company/100m1s-byvias/dist")
MARKER = "<!-- LOGO-HEADER-v1 -->"
CSS_PATCH = ".top{display:flex;align-items:center;gap:8px;margin:0 0 6px}.top .logo{height:38px;width:auto;display:block}"


def get_logo_path(html_path: Path) -> tuple[str, str]:
    """파일 위치에 따라 로고 경로 반환 (light, dark)."""
    parent = html_path.parent
    if parent == DIST:
        # 루트 dist/*.html (ko 원본)
        return "logo.svg", "logo-dark.svg"
    else:
        # 서브디렉토리 (ja/en/zh-cn/zh-tw)
        return "../logo.svg", "../logo-dark.svg"


def get_share_row_pattern(content: str) -> re.Match | None:
    """share-row div 전체 블록 탐색."""
    # share-row 시작 위치
    pattern = re.compile(r'<div class="share-row">(.*?)</div>', re.DOTALL)
    return pattern.search(content)


def build_top_div(logo_src: str, logo_dark_src: str, inner_html: str) -> str:
    """로고가 포함된 top div 생성."""
    logo_html = (
        f"<picture>"
        f'<source srcset="{logo_dark_src}" media="(prefers-color-scheme: dark)">'
        f'<img class="logo" src="{logo_src}" alt="ByVias" width="87" height="38">'
        f"</picture>"
    )
    return f'{MARKER}<div class="top">{logo_html}{inner_html}</div>'


def patch_css(content: str) -> str:
    """CSS에 .top 스타일 추가 (이미 있으면 스킵)."""
    if CSS_PATCH in content:
        return content
    # </style> 첫 번째 위치 앞에 삽입
    return content.replace("</style>", f"{CSS_PATCH}</style>", 1)


def patch_file(html_path: Path) -> bool:
    """단일 파일 패치. 변경 있으면 True."""
    content = html_path.read_text(encoding="utf-8")

    if MARKER in content:
        return False  # 이미 적용됨

    match = get_share_row_pattern(content)
    if not match:
        return False  # share-row 없는 파일 (index.html 등) 스킵

    logo_src, logo_dark_src = get_logo_path(html_path)
    inner_html = match.group(1)  # share-row 내부 HTML

    new_top = build_top_div(logo_src, logo_dark_src, inner_html)
    new_content = content[: match.start()] + new_top + content[match.end() :]
    new_content = patch_css(new_content)

    html_path.write_text(new_content, encoding="utf-8")
    return True


def main() -> None:
    # 대상 디렉토리: 루트(ko) + 4개 언어 서브디렉토리
    targets: list[Path] = []

    # 루트 dist/*.html (index.html 제외)
    for f in sorted(DIST.glob("*.html")):
        if f.name != "index.html":
            targets.append(f)

    # 서브디렉토리
    for lang in ("ja", "en", "zh-cn", "zh-tw"):
        lang_dir = DIST / lang
        if lang_dir.is_dir():
            for f in sorted(lang_dir.glob("*.html")):
                if f.name != "index.html":
                    targets.append(f)

    print(f"[LOGO-HEADER] 이벤트 페이지 로고 삽입 패치 시작 — {len(targets)}개")
    changed = 0
    skipped = 0

    for html_path in targets:
        if patch_file(html_path):
            changed += 1
            rel = html_path.relative_to(DIST)
            print(f"  [ok] {rel}")
        else:
            skipped += 1

    print(f"\n[완료] 변경 {changed}개 / 스킵 {skipped}개 (마커 있음 or share-row 없음)")


if __name__ == "__main__":
    main()
