#!/usr/bin/env python3
"""R84 fix — ja 막차 타임라인 SVG 평일 9호선 막차 라벨 `東行き 00:50` ↔ Line9 dot 좌측 충돌 근본 해소.

배경 (R83 조니 2심 DOC-20260616-JDG-066 P1 확정 — 안전 critical 정직성 결함):
  R83 fix(우클립 해소 — text-anchor=end + x=874 + font 13→12)가 R82 우클립을 *좌측 dot 충돌로 이동*
  시킴 (가용 공간 부족 root 미해결). R83 게이트가 getComputedTextLength advance-width 추정으로 좌
  gap 을 +3px PASS 보고했으나, 실 렌더(Hiragino) native ink 는 충돌 → FLR-AGT-002 거짓 충실성 동형.

  rsvg 4x native painted-ink 실측 (R83 적용 상태, tools/_r84_probe.py):
    `東行き 00:50` (anchor=end x=874 font12) 좌 ink 경계 svg = 793.50
    vs Line9 dot(cx786 r9) 우 ink 경계 = 795 → GAP = -1.50px (겹침).
    dot disc 내 텍스트-골드 over-paint = 390px @4x ≈ 24.38 svg px² (원형 실루엣 파손).
  형제 역 막차 라벨(00:38·00:54)·mid-gloss 전부 dot↔텍스트 +7px clear 규약인데 R83 막차만 위반.

근본 진단 (가용 공간 deficit — 추정 아닌 실측 기반):
  dot 우경계 795 ↔ viewBox 880 사이 = 85px. 형제 +7 clear(좌 ≥802) + 우 패딩 7(우 ≤873) →
  단일행 가용 window = 873-802 = 71px. ja 라벨 `東行き 00:50`(CJK×3 + ASCII×5) 은 font12 ~78px /
  font11 ~76px 로 window 초과. 후보 직접 ink 측정 (tools/_r84_candidates.py, rsvg 4x):
    C1 1행 font11 x873 → 좌 gap +2.00 (FAIL) ··· CJK advance 가 ASCII 추정 초과, R83 동형 함정.
    C2 1행 font11 x872 → 좌 gap +1.00 (FAIL).
    C3 2행 분리(東行き / 00:50) anchor=end x873 font12 → 좌 gap +35.25 · 우 872.5(≤880) · over-paint 0.
  ∴ 단일행 폰트 축소로는 dot 무이동·viewBox 무변 조건 하 +7 도달 불가 (공간 deficit 본질).
     dot cx 이동은 시간축 의미 손상(00:50→00:47 오표기, axis 200px/h), viewBox 확장은 전 element
     rescale 로 en/ko 대비 로케일 종횡비 비대칭 (R83 기각 사유 동일). → 2행 분리만 근본 해소.

🔴 fix 선택 (조니 R84 의제 옵션 (a)dot이동 / (b)viewBox / (c)1행분리 중 dev 실측 선택):
  ▸ 선택: 옵션 (c) 2행 분리 — `東行き`(상) / `00:50`(하), anchor=end x=873 font12 (ja만):
      수평 footprint 를 max(東行き~37px, 00:50~31px) 로 압축 → window 71px 대비 대폭 여유.
      · dot circle(cx786) 무이동 → 00:50 시간축 위치(620+50/60·200=786.7) data semantic 보존.
      · viewBox 880 무변 → 전 element scale 불변, en/ko 통제군 무touch (locale 종횡비 정합).
      · 2행 baseline y=291 / y=306 (행간 15) — ink y[280.75..306.5], divider(340) 33.5px clear,
        개화 mid-gloss(중앙 x548..666)와 우측 컬럼(x820+) 수평 분리로 무충돌 (tools/_r84_vcheck.py).
      · 안전정보 00:50(분단위)은 독립 행으로 오히려 가독 향상. 형제 라벨(00:38·00:54 font13 1행)
        무touch (CJK 접두 보유한 본 라벨만 구조적 2행 필요).

🔴 게이트 (rsvg 4x native painted-ink 실측·advance-width 추정 금지·FLR-AGT-002 봉쇄):
  (G1) `東行き`+`00:50` 2행 우경계 ≤ 880 (클립 0·末尾 0 완전 노출·마지막 컬럼 ink 0).
  (G2) ja timeline 全 9개 시각 라벨(+2행 추가행) 동형 클립 0 (전수 ink-edge 측정).
  (G3) 막차 라벨 좌 ink 경계 - dot 우경계(795) ≥ +7px (형제 규약).
  (G3b) dot disc 내 텍스트-골드 over-paint = 0px (원형 실루엣 무파손).
  (G4) en/ko 통제군 동일 라벨(east/동행 00:50) 무회귀 (좌표·폭 무변·한자 미오염).
  (G5) R82 역명 글로스 무회귀: 馬川(マチョン)·傍花(バンファ)·開化(ケファ) + 開花(벚꽃 오자)=0.
  (G6) 멱등(재실행 0 변경)·<text> 노드 균형(+1: 1노드→2노드)·라벨 문자열 `東行き`·`00:50` 보존.
"""

from __future__ import annotations

import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

WT = Path(__file__).parent.parent
SVG_LT_JA = WT / "dist/assets/gen/lasttrain-timeline-ja.svg"
SVG_LT_EN = WT / "dist/assets/gen/lasttrain-timeline-en.svg"
SVG_LT_KO = WT / "dist/assets/gen/lasttrain-timeline.svg"  # ko base

VIEWBOX_W = 880

# ── 단일 노드(1행) → 2행 분리 치환 (라벨 텍스트 verbatim 보존, geometry 만 2행화) ──
_OLD = (
    '<circle cx="786" cy="293" r="9" fill="#C9A227"/>'
    '<text x="874" y="298" text-anchor="end" font-size="12" font-weight="800" '
    'fill="#9A7B1E">東行き 00:50</text>'
)
_NEW = (
    '<circle cx="786" cy="293" r="9" fill="#C9A227"/>'
    '<text x="873" y="291" text-anchor="end" font-size="12" font-weight="800" '
    'fill="#9A7B1E">東行き</text>'
    '<text x="873" y="306" text-anchor="end" font-size="12" font-weight="800" '
    'fill="#9A7B1E">00:50</text>'
)
FIX: list[tuple[str, str]] = [(_OLD, _NEW)]

# 평일/주말 全 시각 라벨 baseline y (svg) — 전수 클립 측정 (G2). 막차는 2행(291·306)으로 분리.
_LABEL_ROWS: list[tuple[int, str]] = [
    (218, "00:38 평일 L5"),
    (258, "00:54 평일 L8"),
    (291, "東行き 평일 L9 막차 1행 (FIX)"),
    (306, "00:50 평일 L9 막차 2행 (FIX)"),
    (316, "開化(ケファ) 23:56 평일 L9 mid"),
    (422, "傍花(バンファ) 23:54 주말 L5"),
    (440, "馬川(マチョン) 23:49 주말 L5 mid"),
    (462, "23:56 주말 L8"),
    (502, "東行き 23:55 주말 L9"),
    (520, "開化(ケファ) 22:55 TRAP"),
]


def _two_phase_replace(text: str, pairs: list[tuple[str, str]]) -> tuple[str, dict]:
    """멱등 final 잠금 + longest-first 치환 + NUL sentinel 격리 (R78~R83 검증 엔진)."""
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


# ── rsvg 4x 렌더 + 순수 PNG 디코더 (PIL 부재·native ink 실측) ──
def _render_png(
    svg_text: str, scale: int = 4
) -> tuple[int, int, int, list[bytes], int]:
    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_text[:400])
    vw, vh = (int(m.group(1)), int(m.group(2))) if m else (880, 620)
    with tempfile.NamedTemporaryFile(
        suffix=".svg", delete=False, mode="w", encoding="utf-8"
    ) as tf:
        tf.write(svg_text)
        sp = tf.name
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        out = tf.name
    subprocess.run(
        ["rsvg-convert", "-w", str(vw * scale), "-h", str(vh * scale), sp, "-o", out],
        check=True,
        capture_output=True,
    )
    w, h, ch, rows = _decode_png(out)
    return w, h, ch, rows, vw


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


def _gold(r: int, g: int, b: int) -> bool:
    # 골드 텍스트 #9A7B1E ~ (154,123,30) 검출 (bg ~750, dot #C9A227 ~(201,162,39) 와 구분).
    return r < 200 and g < 170 and b < 120 and (r + g + b) < 470


def _measure(svg_text: str, scale: int = 4) -> dict:
    """全 시각 라벨 우경계/클립 + 막차 라벨 좌경계(dot gap) + dot over-paint native ink 실측."""
    w, h, ch, rows, vw = _render_png(svg_text, scale)
    dot_cx, dot_cy, dot_r = 786, 293, 9

    res: dict = {
        "rows": [],
        "any_clip": False,
        "fix_left": None,
        "fix_right": None,
        "overpaint": 0,
    }
    for ysvg, desc in _LABEL_ROWS:
        yc = ysvg * scale
        lo, hi = yc - int(11 * scale), yc + int(4 * scale)
        rightmost = -1
        edge = 0
        for y in range(lo, hi):
            if y < 0 or y >= h:
                continue
            row = rows[y]
            for x in range(w - 1, -1, -1):
                if _gold(row[x * ch], row[x * ch + 1], row[x * ch + 2]):
                    rightmost = max(rightmost, x)
                    break
            xl = w - 1
            if _gold(row[xl * ch], row[xl * ch + 1], row[xl * ch + 2]):
                edge += 1
        right_svg = rightmost / scale if rightmost > 0 else 0
        clip = edge > 0 or right_svg > VIEWBOX_W - 0.5
        if clip:
            res["any_clip"] = True
        res["rows"].append((desc, right_svg, edge, clip))

    # 막차 라벨(2행) 좌 ink 경계 + dot disc over-paint — band y 280..308
    band_lo, band_hi = int(280 * scale), int(308 * scale)
    left = 10**9
    fix_right = -1
    overpaint = 0
    for y in range(band_lo, band_hi):
        if y < 0 or y >= h:
            continue
        row = rows[y]
        ysvg = y / scale
        for x in range(int(760 * scale), w):
            xsvg = x / scale
            r = row[x * ch]
            g = row[x * ch + 1]
            b = row[x * ch + 2]
            inside = (xsvg - dot_cx) ** 2 + (ysvg - dot_cy) ** 2 <= dot_r**2
            if inside:
                # disc 안에서 텍스트 골드(dot 보다 어두운)면 over-paint
                if r < 175 and g < 140 and b < 110 and (r + g + b) < 420:
                    overpaint += 1
                continue
            if _gold(r, g, b):
                left = min(left, x)
                fix_right = max(fix_right, x)
    res["fix_left"] = left / scale if left < 10**9 else None
    res["fix_right"] = fix_right / scale if fix_right > 0 else None
    res["overpaint"] = overpaint
    return res


def _gate(lt_text: str) -> list[str]:
    fails: list[str] = []

    # G4: en/ko 통제군 무회귀
    if SVG_LT_EN.exists():
        en = SVG_LT_EN.read_text(encoding="utf-8")
        if (
            '<text x="802" y="298" font-size="13" font-weight="800" fill="#9A7B1E">east 00:50</text>'
            not in en
        ):
            fails.append("G4 en 통제군 'east 00:50' 좌표/속성 회귀")
        if any(c in en for c in ("東行", "西行", "開化", "開花")):
            fails.append("G4 en 통제군 ja 한자 오염")
    else:
        fails.append(f"G4 en 통제군 부재: {SVG_LT_EN.name}")
    if SVG_LT_KO.exists():
        ko = SVG_LT_KO.read_text(encoding="utf-8")
        if "동행 00:50" not in ko:
            fails.append("G4 ko 통제군 '동행 00:50' 회귀")
        if any(c in ko for c in ("東行", "開化", "開花")):
            fails.append("G4 ko 통제군 ja 한자 오염")
    else:
        fails.append(f"G4 ko 통제군 부재: {SVG_LT_KO.name}")

    # G5: R82 글로스 무회귀 + 開花(오자)=0
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

    # G6: 라벨 문자열 보존 (東行き ≥2 [평일막차+주말막차+TRAP 본문], 00:50 1건) + 2행 노드 적용
    if "東行き" not in lt_text:
        fails.append("G6 '東行き' 문자열 소실")
    if lt_text.count("00:50") != 1:
        fails.append(f"G6 '00:50' 카운트 변동 ({lt_text.count('00:50')}/1)")
    if (
        '<text x="873" y="291" text-anchor="end" font-size="12" font-weight="800" '
        'fill="#9A7B1E">東行き</text>'
        '<text x="873" y="306" text-anchor="end" font-size="12" font-weight="800" '
        'fill="#9A7B1E">00:50</text>'
    ) not in lt_text:
        fails.append(
            "G6 FIX 2행 노드 미적용 (東行き y291 / 00:50 y306 anchor=end font12 기대)"
        )
    return fails


def run(write: bool) -> bool:
    if not SVG_LT_JA.exists():
        print(f"ERROR: {SVG_LT_JA} 없음")
        return False

    lt0 = SVG_LT_JA.read_text(encoding="utf-8")
    text_before = lt0.count("<text")

    print("=== [BEFORE] ja 막차 라벨 native ink 실측 (rsvg 4x) ===")
    m0 = _measure(lt0)
    if m0["fix_left"] is not None:
        print(
            f"  막차 좌 ink {m0['fix_left']:.2f} vs dot 우경계 795 → gap {m0['fix_left'] - 795:+.2f}px"
            f"  | over-paint {m0['overpaint']}px @4x"
        )
    print(f"  ANY CLIP: {m0['any_clip']}\n")

    lt, counts = _two_phase_replace(lt0, FIX)

    # <text> 노드 +1 기대 (1행 → 2행)
    if lt.count("<text") != text_before + 1:
        print(f"ABORT: <text 노드 불균형 {text_before}→{lt.count('<text')} (+1 기대)")
        return False

    fails = _gate(lt)

    print("=== [AFTER] ja 막차 라벨 native ink 실측 (rsvg 4x) ===")
    m1 = _measure(lt)
    for desc, right, edge, clip in m1["rows"]:
        flag = "*** CLIP ***" if clip else "ok"
        print(f"  {desc:<34} 우경계 {right:6.1f}  lastcol_ink {edge:>2}  {flag}")
    if m1["fix_left"] is not None:
        print(
            f"\n  막차 좌 ink {m1['fix_left']:.2f} vs dot 우경계 795 → "
            f"GAP {m1['fix_left'] - 795:+.2f}px (≥+7 규약)"
        )
    print(f"  막차 우 ink {m1['fix_right']}  (viewBox {VIEWBOX_W})")
    print(f"  dot disc over-paint {m1['overpaint']}px @4x  ANY CLIP {m1['any_clip']}\n")

    # 동적 게이트 G1/G2/G3/G3b
    if m1["any_clip"]:
        fails.append("G1/G2 클립 잔존 (any_clip=True)")
    if m1["fix_right"] is not None and m1["fix_right"] > VIEWBOX_W - 0.5:
        fails.append(f"G1 막차 우 ink {m1['fix_right']} > {VIEWBOX_W}")
    if m1["fix_left"] is None:
        fails.append("G3 막차 좌 ink 미검출")
    elif (m1["fix_left"] - 795) < 7:
        fails.append(f"G3 막차 좌 gap {m1['fix_left'] - 795:+.2f} < +7 (dot 충돌/근접)")
    if m1["overpaint"] > 0:
        fails.append(f"G3b dot disc over-paint {m1['overpaint']}px (실루엣 파손)")

    if fails:
        print("ABORT: 게이트 FAIL")
        for f in fails:
            print(f"    ✗ {f}")
        return False

    changed = lt != lt0
    if write and changed:
        SVG_LT_JA.write_text(lt, encoding="utf-8")

    state = "WROTE" if (changed and write) else ("DRY" if not write else "변경없음")
    print(f"=== R84 ja 막차 라벨 dot 충돌 근본 해소 ({state}) ===")
    print(
        f"  치환: {sum(counts.values())}건 (1행 anchor=end x874 → 2행 東行き/00:50 x873 font12)"
    )
    print(
        "  게이트 PASS: G1 우클립0 · G2 全라벨 클립0 · G3 dot gap≥+7 · G3b over-paint0 · "
        "G4 en/ko 무회귀 · G5 R82 글로스+開化 무회귀·開花=0 · G6 라벨 문자열 보존·2행 노드"
    )
    return True


def main() -> None:
    write = "--write" in sys.argv[1:]
    if not run(write):
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R84 ja 막차 라벨 dot 충돌 근본 해소 [{mode}] (게이트 통과)")


if __name__ == "__main__":
    main()
