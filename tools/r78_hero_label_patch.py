#!/usr/bin/env python3
"""R78 — hero 라벨 수식어 한정 'K-pop' (조니 (A) 채택·전 로케일 i18n).

배경 (R77 미수렴 — 조니 2심 P1-3·fable 적발):
  R77 hero-spot `!wc` filter 가 모집단을 K-pop 으로 좁힌 것은 옳으나(브랜드 정합 회복)
  라벨 wording '가장 임박한 일정'(무수식 superlative)은 미수정 → 同 fold rail/jbar 에
  더 임박한 D-3 축구(South Korea National Team·2026-06-18)가 있어 'D-3 < D-5 (G)I-DLE'
  = '가장 임박' 라벨이 自 화면 위에서 거짓.

조니 위계 판정 (fable A/B/C 중):
  **(A) 라벨 수식어 한정 단독 채택** — superlative 의 모집단을 라벨이 솔직히 한정하면
  (가장 임박한 *K-pop* 일정) D-3 축구가 rail 에 있어도 모순이 소멸(최소 변경·근본 해법).
  hero 가 K-pop 필터된 것(R77)과 라벨 정합. (B)배지·(C)통일 비채택.

구현 (dist/{ko,en,ja,zh-cn,zh-tw}/index.html — R77HERO 동형 dist 패치):
  hero 라벨 = locale 당 2 instance (a) <a> aria-label  (b) 인라인 JS '<span hs-eye>'.
  hero population 은 R77 에서 이미 K-pop(`!wc`) — 본 패치는 라벨 텍스트만 수식어 한정.
  R77 5 locale 전수 적용과 동일 scope(hero filter 가 5 locale 이므로 라벨도 5 locale).

멱등: 이미 'K-pop' 한정 라벨 present 시 skip. 게이트: locale 당 정확히 2건 치환.
"""

from __future__ import annotations

import sys
from pathlib import Path

WT = Path(__file__).parent.parent

# locale → (현재 무수식 라벨, K-pop 한정 라벨). 각 라벨 2 instance(aria-label + hs-eye).
HERO_LABELS: dict[str, tuple[str, str]] = {
    "dist/index.html": ("가장 임박한 일정", "가장 임박한 K-pop 일정"),
    "dist/en/index.html": ("Most imminent schedule", "Most imminent K-pop schedule"),
    "dist/ja/index.html": ("もっとも近いスケジュール", "もっとも近いK-popスケジュール"),
    "dist/zh-cn/index.html": ("最临近的行程", "最临近的K-pop行程"),
    "dist/zh-tw/index.html": ("最臨近的行程", "最臨近的K-pop行程"),
}


def run(rel: str, old: str, new: str, write: bool) -> bool:
    path = WT / rel
    if not path.exists():
        print(f"ERROR: {path} 없음")
        return False
    orig = path.read_text(encoding="utf-8")

    if new in orig and old not in orig:
        print(f"=== [{rel}] 이미 적용 (멱등 skip) ===")
        return True

    n_old = orig.count(old)
    if n_old != 2:
        # aria-label(1) + hs-eye(1) = 2 가 기대값. 다르면 구조 변동 — ABORT(거짓 충실성 회피).
        print(f"ABORT [{rel}]: 라벨 {old!r} 기대 2건 vs 실측 {n_old}건")
        return False

    html = orig.replace(old, new)
    if html.count(new) != 2:
        print(f"ABORT [{rel}]: 치환 후 {new!r} 카운트 이상 ({html.count(new)})")
        return False

    changed = html != orig
    if changed and write:
        path.write_text(html, encoding="utf-8")
    state = "WROTE" if (changed and write) else "DRY"
    print(f"=== [{rel}] ({state}) — hero 라벨 K-pop 한정 2건 치환 ===")
    print(f"      {old!r} → {new!r}")
    return True


def main() -> None:
    write = "--write" in sys.argv[1:]
    ok = all(run(rel, old, new, write) for rel, (old, new) in HERO_LABELS.items())
    if not ok:
        sys.exit(2)
    mode = "WRITE" if write else "DRY-RUN (--write 로 적용)"
    print(f"\nOK: R78 hero 라벨 K-pop 한정 [{mode}] (5 locale · 조니 (A))")


if __name__ == "__main__":
    main()
