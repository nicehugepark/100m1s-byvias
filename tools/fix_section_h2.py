#!/usr/bin/env python3
"""
CP0-1: 단순 코스 페이지 섹션 헤더 div → h2 변환 (WCAG 1.3.1)

변환 대상: <div style="font-weight:600;font-size:14px[margin-top:... 또는 margin 없음]...">
변환 제외: margin-bottom 포함 div (다음 공연·아티스트·현지 정보·안전 등 박스 헤더)

멱등: 이미 h2인 경우 스킵.
"""

import re
from pathlib import Path

DIST_DIR = Path(__file__).parent.parent / "dist"

# 섹션 헤더 패턴 — font-weight:600;font-size:14px 로 시작하며 margin-bottom이 없는 div
# style 시작: "font-weight:600;font-size:14px" 이후 margin-top 또는 없음만 허용
SECTION_DIV_RE = re.compile(
    r'<div\s+style="font-weight:600;font-size:14px(?:;margin-top:[^;"]*)?">',
)

# ID 부여용 — 텍스트→슬러그 매핑 (알려진 섹션만 명시, 나머지는 id 생략)
SECTION_ID_MAP = {
    "공연장": "sec-venue",
    "근처 숙소 팁": "sec-staytips",
    "공연 후 귀가 동선": "sec-return",
    "일정 출처": "sec-schedule-src",
    "Venue": "sec-venue",
    "Nearby accommodation tips": "sec-staytips",
    "Getting back after the concert": "sec-return",
    "회차별 귀가 여유 (역산)": "sec-return",
    # 일본어/스페인어 등 다국어 텍스트는 id 없이 변환
}


def extract_text(html_chunk: str) -> str:
    """닫는 태그 이전까지 텍스트 추출."""
    end = html_chunk.find("</div>")
    if end == -1:
        return ""
    inner = html_chunk[:end]
    return re.sub(r"<[^>]+>", "", inner).strip()


def convert_file(path: Path) -> int:
    """파일 내 섹션 헤더 div → h2 변환. 변환 수 반환."""
    content = path.read_text(encoding="utf-8")
    count = 0

    def replacer(m: re.Match) -> str:
        nonlocal count
        full_div_open = m.group(0)
        style_content = re.search(r'style="([^"]*)"', full_div_open).group(1)

        # 닫는 div 까지 텍스트 추출하여 id 결정
        m.start()
        # 매칭 직후부터 </div> 찾아 텍스트 파싱
        after_open = content[m.end() :]
        text = extract_text(after_open)

        sec_id = SECTION_ID_MAP.get(text, "")
        id_attr = f' id="{sec_id}"' if sec_id else ""
        count += 1
        return f'<h2{id_attr} style="{style_content}">'

    # </div> → </h2> 변환은 replacer에서 처리 후 별도로
    # 전략: 매칭 구간을 찾아 <div...> → <h2...>, 해당 </div> → </h2> 치환
    new_content = []
    pos = 0
    for m in SECTION_DIV_RE.finditer(content):
        new_content.append(content[pos : m.start()])
        full_div_open = m.group(0)
        style_content = re.search(r'style="([^"]*)"', full_div_open).group(1)

        # 대응 </div> 위치 찾기 (단순 코스는 중첩 없음 — 안전 확인)
        after_open = content[m.end() :]
        close_idx = after_open.find("</div>")

        if close_idx == -1:
            # 닫는 div 없으면 변환하지 않음
            new_content.append(full_div_open)
            pos = m.end()
            continue

        inner_html = after_open[:close_idx]

        # 내부에 <div> 가 있으면 중첩 div — 섹션 헤더가 아닐 수 있음 (안전 제외)
        if "<div" in inner_html:
            new_content.append(full_div_open)
            pos = m.end()
            continue

        text = re.sub(r"<[^>]+>", "", inner_html).strip()
        sec_id = SECTION_ID_MAP.get(text, "")
        id_attr = f' id="{sec_id}"' if sec_id else ""
        count += 1
        new_content.append(f'<h2{id_attr} style="{style_content}">')
        new_content.append(inner_html)
        new_content.append("</h2>")
        pos = m.end() + close_idx + len("</div>")

    new_content.append(content[pos:])
    new_text = "".join(new_content)

    if new_text != content:
        path.write_text(new_text, encoding="utf-8")

    return count


def main() -> None:
    html_files = sorted(DIST_DIR.glob("*.html"))
    total_files = 0
    total_converts = 0

    for f in html_files:
        n = convert_file(f)
        if n > 0:
            total_files += 1
            total_converts += n
            print(f"  {f.name}: {n}건 변환")

    print(f"\n완료: {total_files}개 파일, 총 {total_converts}건 h2 변환")


if __name__ == "__main__":
    main()
