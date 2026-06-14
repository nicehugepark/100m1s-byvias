#!/usr/bin/env python3
"""
set_brand_questions.py
히어로 콜앤리스폰스 브랜드 질문을 언어별 정확한 시그니처로 하드코딩.

- 대상: dist/{lang}/index.html (ko=루트 dist/index.html)
- 치환: <p class="hero-call">...</p> 텍스트만
- 무접촉: hero-answer / hero-cta / brand-lore / hf-chips
- 멱등: 재실행해도 동일 결과

사용:
  python3 tools/set_brand_questions.py            # 전체 5언어 (미빌드 언어 skip)
  python3 tools/set_brand_questions.py --langs ko en ja
"""

import argparse
import re
import sys
from pathlib import Path

BRAND_QUESTIONS = {
    "ko": "Where are you?",
    "en": "Where are you?",
    "ja": "Where are you?",
    "zh-cn": "Where are you?",
    "zh-tw": "Where are you?",
}

HERO_CALL_RE = re.compile(
    r'(<p\s+class="hero-call">)(.*?)(</p>)',
    re.DOTALL,
)


def dist_path(repo_root: Path, lang: str) -> Path:
    if lang == "ko":
        return repo_root / "dist" / "index.html"
    return repo_root / "dist" / lang / "index.html"


def patch_file(path: Path, question: str, lang: str) -> str:
    """hero-call 텍스트만 치환. 반환: 'patched' | 'already_correct' | 'not_found'"""
    content = path.read_text(encoding="utf-8")
    match = HERO_CALL_RE.search(content)
    if not match:
        return "not_found"
    current = match.group(2)
    if current == question:
        return "already_correct"
    new_content = HERO_CALL_RE.sub(
        lambda m: m.group(1) + question + m.group(3),
        content,
        count=1,
    )
    path.write_text(new_content, encoding="utf-8")
    return "patched"


def main() -> None:
    parser = argparse.ArgumentParser(description="히어로 브랜드 질문 하드코딩 패치")
    parser.add_argument(
        "--langs",
        nargs="+",
        choices=list(BRAND_QUESTIONS.keys()),
        default=list(BRAND_QUESTIONS.keys()),
        help="적용할 언어 목록 (기본: 전체)",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent

    ok = True
    for lang in args.langs:
        question = BRAND_QUESTIONS[lang]
        path = dist_path(repo_root, lang)
        if not path.exists():
            print(f"[SKIP]  {lang}: {path} 미존재 (미빌드 언어 — 빌드 후 재실행)")
            continue
        result = patch_file(path, question, lang)
        if result == "patched":
            print(f'[PATCH] {lang}: "{question}" → {path.relative_to(repo_root)}')
        elif result == "already_correct":
            print(f'[OK]    {lang}: 이미 정확 ("{question}")')
        else:
            print(f"[ERROR] {lang}: hero-call 요소 미발견 — {path}", file=sys.stderr)
            ok = False

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
