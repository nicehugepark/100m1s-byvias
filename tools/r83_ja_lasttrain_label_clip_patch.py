#!/usr/bin/env python3
"""R83 fix — ja 막차 타임라인 SVG 평일 9호선 막차 라벨 `東行き 00:50` 우경계 클립 해소.

배경 (R82 조니 2심 DOC-20260616-JDG-065 P1 확정 — 안전 critical 정직성 결함):
  lasttrain-timeline-ja.svg L47 평일 Line9 막차 라벨이 SVG 우경계서 클립 →
  `東行き 00:50` 末尾 `0` 절단 = 막차 분단위 거짓 노출 (00:5? 로 보임).
  rsvg 실측 (2x 렌더, ink 픽셀 측정):
    text x="802" text-anchor=start(좌고정) + ja `東行き`(전각 CJK ×3, 36.5u) + ` 00:50` →
    true 라벨 폭 88.5u → true 우경계 x = 802 + 88.5 = 890.5 > viewBox width 880 (+10.5 over).
    렌더 시 viewBox 가 890.5 를 880 에서 클립 → 末尾 `0` 의 15개 row 가 마지막 컬럼(svg 880) 접촉.
  en(`east 00:50` 협폭 ASCII) · ko(`동행 00:50` 협폭 Hangul) 은 同좌표 x=802 무클립 → ja 전용 결함.
  pre-existing (R80↔R81 byte-identical, R82 글로스 fix 무관) 이나 라이브 출하 중.

근본 진단 (R79~R82 verbatim 상속 — generator 부재 = SVG 파일 자체가 source):
  grep 재확인 (R83): `lasttrain-timeline|東行き|x="802"` 전수 grep → tools/rNN 외 generator(.py/.js) 0건.
  base ko `lasttrain-timeline.svg` 동일 라벨은 `동행 00:50`(협폭) → 무클립 = 재생성 전파 경로 무해.
  ∴ ja SVG 직접 치환 = source 단일화 (R82 와 동일 구조 확정).

🔴 fix 선택 (조니 R83 의제 옵션 중 dev 선택 — ja만·ko/en 회귀 0·레이아웃 충돌 0):
  옵션 평가 (실측 기반):
    (c) viewBox +12  → 전 element scale 변경, ja 차트만 en/ko 와 다른 종횡비/스케일 → 로케일 시각
                       비대칭. ja-isolated 아님 (전 좌표 영향). 기각.
    (d) 라벨 단축    → 콘텐츠/의미 변경. 기각.
    (b) font 13→12  단독 → 폭 88.5→82u, x=802 시 우경계 884 여전 클립(+4). 불충분.
    (a) anchor=end 단독 (x=868) → 우경계 868 OK 이나 left edge 779.5 가 dot(cx=786 r=9 우경계 795)
                       과 충돌(-15.5u). 단독 불가.
  ▸ 선택: (a)+(b) 결합 — text-anchor=end + x=874 + font-size 12 (단일 <text> 노드, ja만):
      anchor=end 로 우경계를 x=874 에 고정 (우 패딩 6px) + font 12 로 폭 75u 축소 →
      좌경계 798 (dot 우경계 795 와 3px gap clear) · 우경계 873 (viewBox 880, 7px 패딩, 클립 0).
      circle(cx=786) 무이동 (data semantic = 00:50 시간축 위치 보존). sibling 라벨(00:38·00:54
      font13) 무touch (size 비대칭은 본 라벨이 유일하게 CJK 접두 보유 → 폭 초과 본질적).

🔴 게이트 (rsvg 2x 렌더 ink 픽셀 실측·선언 금지):
  (G1) `東行き 00:50` 우경계 ≤ 880 (클립 0·마지막 컬럼 ink 0 = 末尾 `0` 완전 노출).
  (G2) ja timeline 全 9개 시각 라벨 동형 클립 0 (전수 ink-edge 측정).
  (G3) `東行き 00:50` 좌경계 > circle 우경계(795) = dot 충돌 0.
  (G4) en/ko 통제군 동일 라벨(east/동행 00:50) 무회귀 (좌표·폭 무변·한자 미오염).
  (G5) R82 역명 글로스 무회귀: 馬川(マチョン)·傍花(バンファ)·開化(ケファ) 유지 + 開花(벚꽃 오자)=0.
  (G6) 멱등(재실행 0 변경)·<text> 노드 균형·라벨 텍스트 `東行き 00:50` 문자열 무변(폭만 조정).
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

WT = Path(__file__).parent.parent
SVG_LT_JA = WT / "dist/assets/gen/lasttrain-timeline-ja.svg"

# 통제군 (무회귀 cross-check 전용·비편집)
SVG_LT_EN = WT / "dist/assets/gen/lasttrain-timeline-en.svg"
SVG_LT_KO = WT / "dist/assets/gen/lasttrain-timeline.svg"

VIEWBOX_W = 880  # ja timeline viewBox width (역명 글로스 layer 무관·R80~R82 불변)

# ── 단일 노드 치환 (old, new) — 라벨 텍스트는 verbatim 동일, geometry 속성만 조정 ──
#   anchor=start x=802 (좌고정·클립) → anchor=end x=874 font12 (우정렬·우패딩6·클립0)
_OLD = (
    '<circle cx="786" cy="293" r="9" fill="#C9A227"/>'
    '<text x="802" y="298" font-size="13" font-weight="800" fill="#9A7B1E">東行き 00:50</text>'
)
_NEW = (
    '<circle cx="786" cy="293" r="9" fill="#C9A227"/>'
    '<text x="874" y="298" text-anchor="end" font-size="12" font-weight="800" '
    'fill="#9A7B1E">東行き 00:50</text>'
)
FIX: list[tuple[str, str]] = [(_OLD, _NEW)]

# 평일/주말 全 시각 라벨 baseline y (svg) — 전수 클립 측정 대상 (G2)
_LABEL_ROWS: list[tuple[int, str]] = [
    (218, "00:38 평일 L5"),
    (258, "00:54 평일 L8"),
    (298, "東行き 00:50 평일 L9 (FIX 대상)"),
    (316, "開化(ケファ) 23:56 평일 L9 mid"),
    (422, "傍花(バンファ) 23:54 주말 L5"),
    (440, "馬川(マチョン) 23:49 주말 L5 mid"),
    (462, "23:56 주말 L8"),
    (502, "東行き 23:55 주말 L9"),
    (520, "開化(ケファ) 22:55 TRAP"),
]


def _two_phase_replace(text: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """R78~R82 검증 엔진: 멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리."""
    counts: dict[str, int] = {}
    locks: list[str] = []
    olds = [o for o, _ in pairs]
    for f in sorted({f for _, f in pairs}, key=len, reverse=True):
        if any(f != o and f in o for o in olds):
            continue
        if f and f in text:
            sent = f"\x00L{len(locks)}\x00"
            text = text.replace(f, sent)
            locks.append(f)
    for old, new in sorted(pairs, key=lambda x: len(x[0]), reverse=True):
        if old not in text:
            continue
        counts[old] = counts.get(old, 0) + text.count(old)
        sent = f"\x00L{len(locks)}\x00"
        text = text.replace(old, sent)
        locks.append(new)
    for i, val in enumerate(locks):
        text = text.replace(f"\x00L{i}\x00", val)
    return text, counts


# ── rsvg 2x 렌더 + 순수 PNG 디코더 (PIL 부재 환경·ink 픽셀 실측) ──
def _render_png(svg_path: Path, scale: int = 2) -> tuple[int, int, int, list[bytes]]:
    import subprocess
    import tempfile

    # viewBox 폭/높이 읽어 정확 배율 렌더
    head = svg_path.read_text(encoding="utf-8")[:400]
    import re

    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', head)
    vw, vh = (int(m.group(1)), int(m.group(2))) if m else (880, 620)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        out = tf.name
    subprocess.run(
        [
            "rsvg-convert",
            "-w",
            str(vw * scale),
            "-h",
            str(vh * scale),
            str(svg_path),
            "-o",
            out,
        ],
        check=True,
        capture_output=True,
    )
    return _decode_png(out)


def _decode_png(p: str) -> tuple[int, int, int, list[bytes]]:
    data = Path(p).read_bytes()
    i = 8
    idat = b""
    w = h = ct = 0
    while i < len(data):
        ln = struct.unpack(">I", data[i : i + 4])[0]
        typ = data[i + 4 : i + 8]
        chunk = data[i + 8 : i + 8 + ln]
        i += 12 + ln
        if typ == b"IHDR":
            w, h, _bd, ct = struct.unpack(">IIBB", chunk[:10])
        elif typ == b"IDAT":
            idat += chunk
        elif typ == b"IEND":
            break
    raw = zlib.decompress(idat)
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    stride = w * ch
    out: list[bytes] = []
    prev = bytes(stride)
    pos = 0

    def paeth(a: int, b: int, c: int) -> int:
        pp = a + b - c
        pa, pb, pc = abs(pp - a), abs(pp - b), abs(pp - c)
        return a if pa <= pb and pa <= pc else (b if pb <= pc else c)

    for _y in range(h):
        f = raw[pos]
        pos += 1
        line = bytearray(raw[pos : pos + stride])
        pos += stride
        if f == 1:
            for x in range(ch, stride):
                line[x] = (line[x] + line[x - ch]) & 255
        elif f == 2:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 255
        elif f == 3:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 255
        elif f == 4:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                c = prev[x - ch] if x >= ch else 0
                line[x] = (line[x] + paeth(a, prev[x], c)) & 255
        out.append(bytes(line))
        prev = bytes(line)
    return w, h, ch, out


def _measure_ja(svg_text: str) -> dict:
    """ja timeline 全 시각 라벨 우경계/클립 + FIX 라벨 좌경계 실측 (rsvg 2x)."""
    import tempfile

    with tempfile.NamedTemporaryFile(
        suffix=".svg", delete=False, mode="w", encoding="utf-8"
    ) as tf:
        tf.write(svg_text)
        path = Path(tf.name)
    w, h, ch, rows = _render_png(path, scale=2)

    def is_ink(r: int, g: int, b: int) -> bool:
        return (r + g + b) < 480  # bg ~750, gold text ~307

    res: dict = {"rows": [], "any_clip": False, "fix_left": None}
    for ysvg, desc in _LABEL_ROWS:
        yc = ysvg * 2
        lo, hi = yc - 26, yc + 6
        rightmost = -1
        edge = 0
        for y in range(lo, hi):
            if y < 0 or y >= h:
                continue
            row = rows[y]
            for x in range(w - 1, -1, -1):
                if is_ink(row[x * ch], row[x * ch + 1], row[x * ch + 2]):
                    rightmost = max(rightmost, x)
                    break
            xl = w - 1
            if is_ink(row[xl * ch], row[xl * ch + 1], row[xl * ch + 2]):
                edge += 1
        right_svg = rightmost / 2
        clip = edge > 0 or right_svg > VIEWBOX_W - 0.5
        if clip:
            res["any_clip"] = True
        res["rows"].append((desc, right_svg, edge, clip))
        # FIX 라벨 좌경계 (text x>=798, circle 제외)
        if "FIX" in desc:
            xmin = int(798 * 2)
            left = 10**9
            for y in range(lo, hi):
                if y < 0 or y >= h:
                    continue
                row = rows[y]
                for x in range(xmin, w):
                    if is_ink(row[x * ch], row[x * ch + 1], row[x * ch + 2]):
                        left = min(left, x)
                        break
            res["fix_left"] = left / 2 if left < 10**9 else None
    return res


def _gate(lt_text: str) -> list[str]:
    fails: list[str] = []

    # G4: en/ko 통제군 무회귀 (동일 라벨 좌표·폭 무변·한자 미오염)
    if SVG_LT_EN.exists():
        en = SVG_LT_EN.read_text(encoding="utf-8")
        if (
            '<text x="802" y="298" font-size="13" font-weight="800" fill="#9A7B1E">east 00:50</text>'
            not in en
        ):
            fails.append(
                "G4 en 통제군 'east 00:50' 좌표/속성 회귀 (x=802 anchor=start font13 무변 기대)"
            )
        if "東行" in en or "西行" in en or "開化" in en or "開花" in en:
            fails.append("G4 en 통제군 ja 한자 오염")
    else:
        fails.append(f"G4 en 통제군 부재: {SVG_LT_EN.name}")
    if SVG_LT_KO.exists():
        ko = SVG_LT_KO.read_text(encoding="utf-8")
        if (
            '<text x="802" y="298" font-size="13" font-weight="800" fill="#9A7B1E">동행 00:50</text>'
            not in ko
        ):
            fails.append(
                "G4 ko 통제군 '동행 00:50' 좌표/속성 회귀 (x=802 anchor=start font13 무변 기대)"
            )
    else:
        fails.append(f"G4 ko 통제군 부재: {SVG_LT_KO.name}")

    # G5: R82 역명 글로스 무회귀 + 開花(오자)=0
    for need, label in (
        ("馬川(マチョン)", "R82 馬川 글로스"),
        ("傍花(バンファ)", "R82 傍花 글로스"),
        ("開化(ケファ)", "開化 글로스"),
    ):
        if need not in lt_text:
            fails.append(f"G5 {label} 회귀: {need!r} 누락")
    if lt_text.count("開化(ケファ)") < 3:
        fails.append(f"G5 開化(ケファ) 회귀 ({lt_text.count('開化(ケファ)')}/3)")
    if "開花" in lt_text:
        fails.append(f"G5 開花(벚꽃 오자) 잔존 {lt_text.count('開花')}")

    # G6: 라벨 텍스트 문자열 무변 (폭만 조정·콘텐츠 동일) + anchor=end 적용 확인
    #   '東行き 00:50'(평일 L9, FIX 대상) ×1 — 주말 L9 는 '東行き 23:55'(별 라벨) 이므로 1건이 정상.
    if lt_text.count("東行き 00:50") != 1:
        fails.append(
            f"G6 '東行き 00:50' 문자열 카운트 변동 ({lt_text.count('東行き 00:50')}/1 기대)"
        )
    if 'x="874" y="298" text-anchor="end" font-size="12"' not in lt_text:
        fails.append("G6 FIX 노드 geometry 미적용 (x=874 anchor=end font12 기대)")

    return fails


def run(write: bool) -> bool:
    if not SVG_LT_JA.exists():
        print(f"ERROR: {SVG_LT_JA} 없음")
        return False

    lt0 = SVG_LT_JA.read_text(encoding="utf-8")
    text_before = lt0.count("<text")

    # BEFORE 측정 (클립 입증)
    print("=== [BEFORE] ja timeline 全 시각 라벨 우경계/클립 실측 (rsvg 2x) ===")
    m0 = _measure_ja(lt0)
    for desc, right, edge, clip in m0["rows"]:
        flag = "*** CLIP ***" if clip else "ok"
        print(f"  {desc:<32} 우경계 svg {right:6.1f}  lastcol_ink {edge:>2}  {flag}")
    print(f"  [BEFORE] ANY CLIP: {m0['any_clip']}\n")

    lt, counts = _two_phase_replace(lt0, FIX)

    if lt.count("<text") != text_before:
        print(f"ABORT: <text 노드 불균형 {text_before}→{lt.count('<text')}")
        return False

    # 정적 게이트
    fails = _gate(lt)

    # AFTER 측정 (클립 해소 입증)
    print("=== [AFTER] ja timeline 全 시각 라벨 우경계/클립 실측 (rsvg 2x) ===")
    m1 = _measure_ja(lt)
    for desc, right, edge, clip in m1["rows"]:
        flag = "*** CLIP ***" if clip else "ok"
        print(f"  {desc:<32} 우경계 svg {right:6.1f}  lastcol_ink {edge:>2}  {flag}")
    print(f"  [AFTER] ANY CLIP: {m1['any_clip']}")
    print(
        f"  FIX 라벨 좌경계 svg {m1['fix_left']}  (circle 우경계 795 → gap {(m1['fix_left'] or 0) - 795:.1f}px)\n"
    )

    # G1/G2/G3 동적 게이트
    if m1["any_clip"]:
        fails.append("G1/G2 클립 잔존 (AFTER any_clip=True)")
    fix_row = next((r for r in m1["rows"] if "FIX" in r[0]), None)
    if fix_row and fix_row[1] > VIEWBOX_W:
        fails.append(f"G1 FIX 라벨 우경계 {fix_row[1]} > {VIEWBOX_W}")
    if m1["fix_left"] is not None and m1["fix_left"] <= 795:
        fails.append(
            f"G3 FIX 라벨 좌경계 {m1['fix_left']} <= circle 우경계 795 (dot 충돌)"
        )

    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = lt != lt0
    if write and changed:
        SVG_LT_JA.write_text(lt, encoding="utf-8")

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R83 ja 막차 라벨 클립 해소 ({state}) ===")
    print(
        f"  치환: {sum(counts.values())}건 (anchor=start x=802 font13 → anchor=end x=874 font12)"
    )
    print(
        "  게이트: PASS "
        "(G1 FIX 우경계 ≤880 클립0·G2 全9라벨 클립0·G3 dot 충돌0·"
        "G4 en/ko 통제군 무회귀·G5 R82 글로스+開化 무회귀·開花=0·G6 라벨 문자열 무변)"
    )
    return True


def main() -> None:
    write = "--write" in sys.argv[1:]
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R83 ja 막차 라벨 클립 해소 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
