#!/usr/bin/env python3
"""채택된 raw PNG → 웹용 1200px jpg 변환.

usage: python3 _webify.py <slug1> <slug2> ...
  각 slug 의 채택안 raw 파일(예: hero_a.png)을 받아
  - 원본 png 를 photo/<slug>.png 로 복사(보존)
  - 1200px wide jpg 를 photo/<slug>.jpg 로 저장
"""

import shutil
import sys

from PIL import Image

BASE = "/Users/seongjinpark/company/100m1s-byvias/assets/gen/photo"
RAW = f"{BASE}/raw"
TARGET_W = 1200


def webify(src_png, slug):
    # 원본 보존
    shutil.copy(src_png, f"{BASE}/{slug}.png")
    img = Image.open(src_png).convert("RGB")
    w, h = img.size
    if w > TARGET_W:
        nh = int(h * TARGET_W / w)
        img = img.resize((TARGET_W, nh), Image.LANCZOS)
    out = f"{BASE}/{slug}.jpg"
    img.save(out, "JPEG", quality=85, optimize=True)
    import os

    print(
        f"{slug}: {out} ({os.path.getsize(out) // 1024}KB, {img.size[0]}x{img.size[1]})"
    )


def main():
    # args: slug=rawfile pairs, e.g. hero=hero_a
    for arg in sys.argv[1:]:
        if "=" in arg:
            slug, rawname = arg.split("=", 1)
        else:
            slug, rawname = arg, f"{arg}_a"
        webify(f"{RAW}/{rawname}.png", slug)


if __name__ == "__main__":
    main()
