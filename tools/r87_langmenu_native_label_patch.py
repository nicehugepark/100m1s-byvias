#!/usr/bin/env python3
"""R87 — langmenu(.lng) 라벨을 언어별 고정 native self-name으로 강제 정정.

근본 원인(2026-06-16 확인):
  byvias_course_i18n.py 의 `.lng` 루프(line 212~)는 href/aria-current만 갱신하고
  앵커 텍스트는 복원하지 않음. `_collect_text_nodes` 가 모든 텍스트 노드를 수집하고
  `_should_skip` 은 "한글 미포함"만 skip → native name 중 유일하게 한글인 '한국어'가
  translate_batch 로 흘러가 zh-cn='简体中文' / en='Korean' 로 오역되어 dist에 baked.
  zh-tw 는 zh-cn OpenCC 변환본이라 '簡體中文' 상속. (日本語→日本语, 繁體中文→繁体中文 은
  zh-cn 페이지 OpenCC/cross-conversion 부산물.)

본 패치 = dist 라벨 직접 정정(번역 파이프라인 회피). 멱등.
각 <a class="lng" ... data-lang="X" ...>LABEL</a> 의 LABEL 을 NATIVE[X] 로 강제.
속성(href/hreflang/aria-current)·순서·그 외 모든 바이트 무손상.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# 언어별 고정 native self-name (i18n.LANGS[code][1] SSOT 와 동일). 현재 페이지 언어 무관.
NATIVE = {
    "ko": "한국어",
    "en": "English",
    "ja": "日本語",
    "zh-cn": "简体中文",
    "zh-tw": "繁體中文",
    "es": "Español",
    "th": "ไทย",
    "id": "Bahasa Indonesia",
    "pt": "Português",
    "ar": "العربية",
    "vi": "Tiếng Việt",
}

# <a ... class="lng" ... data-lang="CODE" ...>LABEL</a>
# class/data-lang 속성 순서 무관(dist 에 두 가지 순서 공존). LABEL = 텍스트만(중첩 태그 없음 전제).
_ANCHOR_RE = re.compile(
    r'(<a\b(?=[^>]*\bclass="lng")(?=[^>]*\bdata-lang="(?P<code>[a-z-]+)")[^>]*>)'
    r"(?P<label>[^<]*)"
    r"(</a>)"
)


def patch_html(html: str) -> tuple[str, int]:
    """반환: (patched_html, 정정된 라벨 수)."""
    fixed = 0

    def _sub(m: re.Match) -> str:
        nonlocal fixed
        code = m.group("code")
        want = NATIVE.get(code)
        if want is None:  # 미등록 언어 = 손대지 않음
            return m.group(0)
        if m.group("label") != want:
            fixed += 1
        return f"{m.group(1)}{want}{m.group(4)}"

    return _ANCHOR_RE.sub(_sub, html), fixed


def main() -> int:
    root = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else Path(__file__).resolve().parent.parent / "dist"
    )
    if not root.is_dir():
        print(f"ERROR: dist not found: {root}", file=sys.stderr)
        return 2

    files = sorted(root.rglob("*.html"))
    files_with_menu = 0
    files_changed = 0
    total_fixed = 0
    changed_files: list[tuple[str, int]] = []

    for f in files:
        try:
            html = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            print(f"SKIP (read err) {f}: {e}", file=sys.stderr)
            continue
        if 'class="lng"' not in html:
            continue
        files_with_menu += 1
        new_html, fixed = patch_html(html)
        if fixed:
            f.write_text(new_html, encoding="utf-8")
            files_changed += 1
            total_fixed += fixed
            changed_files.append((str(f.relative_to(root)), fixed))

    print(f"dist root           : {root}")
    print(f"html files scanned  : {len(files)}")
    print(f"files w/ langmenu   : {files_with_menu}")
    print(f"files changed       : {files_changed}")
    print(f"labels corrected    : {total_fixed}")
    if changed_files:
        print("--- changed files (relpath : labels fixed) ---")
        for rel, n in changed_files:
            print(f"  {rel} : {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
