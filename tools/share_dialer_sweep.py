#!/usr/bin/env python3
"""공유 동선 전수 주입 — twice-seoul 검증 패턴을 전 이벤트(루트 ko + 10 로케일)로 확장.

배경: 공유 버튼(Web Share API 우선 / 미지원·데스크탑은 클립보드 복사 + 토스트)이
twice-thisisfor-seoul 1개 페이지에만 존재. 나머지 76 이벤트 × 11언어(루트 ko +
10 로케일) 전수에 동일 동선 주입. + 홈(index.html 11언어)에도 공유 버튼.

설계 원칙(트랩 회피):
  - 자산·CSS 경로 절대경로 무관(인라인 CSS/JS만 주입, 외부 자산 0) → 로케일
    상대경로 404 함정(FLR-20260611-TEC-001 인접) 구조적 비해당.
  - 멱등(SHARE-DIALER marker 가드): 재실행·이미 보유 페이지(twice-seoul) 중복 0.
  - dist/ = 배포 SSOT (repo-root 에 *.html 없음 — 분기 비해당).
  - 11언어 라벨: ko/en 우선 자연 문구, 9언어 보수 직역(어휘 단순·오역 0 지향).
  - RTL(ar): .share-row 는 logical property(margin-inline-end) + flex-end →
    dir=rtl 자동 반전. 별도 분기 불요.

대상 마크업(이벤트 페이지, 비-twice 공통):
  - 단독 라인 `<a class="back" href="index.html">← {label}</a>` → .share-row 래핑
    + 공유 버튼(localized aria/label) 추가.
  - 공유 CSS(.share-row/.share-btn/.share-toast) </style> 직전 주입.
  - 공유 JS(navigator.share → clipboard → 주소 fallback) </body> 직전 주입.

홈(index.html): .back 링크 없음 → 히어로 직하 첫 액션 슬롯에 공유 버튼 단독 주입은
범위 외(별 슬롯 결정 필요). 본 sweep 은 이벤트 상세 전수 + 홈은 langbar 우측에
공유 버튼만 인라인 추가(home 변형 함수 분리).
"""

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

MARKER = "SHARE-DIALER"

# 로케일별 라벨 — (button_label, aria_label, toast_copied, addr_prefix)
# ko/en 우선 자연 문구. 9언어 보수 직역.
L10N = {
    "ko": ("공유하기", "이 가이드 공유하기", "링크가 복사됐어요", "주소: "),
    "en": ("Share", "Share this guide", "Link copied", "URL: "),
    "ja": ("共有", "このガイドを共有", "リンクをコピーしました", "URL: "),
    "zh-cn": ("分享", "分享此指南", "链接已复制", "网址: "),
    "zh-tw": ("分享", "分享此指南", "連結已複製", "網址: "),
    "es": ("Compartir", "Compartir esta guía", "Enlace copiado", "URL: "),
    "th": ("แชร์", "แชร์ไกด์นี้", "คัดลอกลิงก์แล้ว", "URL: "),
    "id": ("Bagikan", "Bagikan panduan ini", "Tautan disalin", "URL: "),
    "pt": ("Compartilhar", "Compartilhar este guia", "Link copiado", "URL: "),
    "ar": ("مشاركة", "مشاركة هذا الدليل", "تم نسخ الرابط", "الرابط: "),
    "vi": ("Chia sẻ", "Chia sẻ hướng dẫn này", "Đã sao chép liên kết", "URL: "),
}

# 공유 CSS — twice-seoul 검증본 verbatim. </style> 직전 주입.
CSS_BLOCK = (
    "/* SHARE-DIALER */"
    ".share-row{display:flex;justify-content:flex-end;margin:0 0 6px}"
    ".share-btn{display:inline-flex;align-items:center;gap:6px;min-height:44px;"
    "padding:6px 13px;font-size:13px;font-weight:600;color:var(--accent);"
    "background:var(--card);border:1px solid var(--line);border-radius:12px;cursor:pointer}"
    ".share-btn:hover{border-color:var(--accent)}"
    ".share-btn svg{flex:0 0 auto}"
    ".share-toast{position:fixed;left:50%;bottom:24px;"
    "transform:translateX(-50%) translateY(8px);opacity:0;pointer-events:none;"
    "background:var(--ink);color:var(--bg);font-size:13px;font-weight:600;"
    "padding:10px 16px;border-radius:12px;z-index:50;transition:opacity .2s,transform .2s}"
    ".share-toast.show{opacity:1;transform:translateX(-50%) translateY(0)}"
)

# 공유 아이콘 SVG(twice-seoul verbatim) — 업로드/공유 글리프.
SHARE_SVG = (
    '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.8" aria-hidden="true"><path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/>'
    '<path d="M12 3v13M8 7l4-4 4 4"/></svg>'
)


def js_block(toast_copied: str, addr_prefix: str) -> str:
    # JS 문자열은 ' 로 감싸므로 라벨 내 ' 이스케이프. 토스트 메시지·주소 prefix 만 가변.
    tc = toast_copied.replace("\\", "\\\\").replace("'", "\\'")
    ap = addr_prefix.replace("\\", "\\\\").replace("'", "\\'")
    return (
        "<script>"
        "(function(){try{"
        "var btn=document.getElementById('shareBtn');if(!btn)return;"
        "var title=document.title;var url=location.href;"
        "function toast(msg){var t=document.createElement('div');t.className='share-toast';"
        "t.setAttribute('role','status');t.setAttribute('aria-live','polite');"
        "t.textContent=msg;document.body.appendChild(t);"
        "requestAnimationFrame(function(){t.classList.add('show');});"
        "setTimeout(function(){t.classList.remove('show');"
        "setTimeout(function(){t.remove();},250);},1800);}"
        "btn.addEventListener('click',function(){"
        "if(navigator.share){navigator.share({title:title,url:url}).catch(function(){});return;}"
        "if(navigator.clipboard&&navigator.clipboard.writeText){"
        "navigator.clipboard.writeText(url).then(function(){toast('" + tc + "');})"
        ".catch(function(){toast('" + ap + "'+url);});return;}"
        "toast('" + ap + "'+url);"
        "});"
        "}catch(e){}})();"
        "</script>"
    )


def lang_key(rel: str) -> str:
    parts = rel.split("/")
    if len(parts) == 1:  # 루트 = ko
        return "ko"
    return parts[0]


def patch_event(path: pathlib.Path) -> str:
    rel = str(path.relative_to(DIST))
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return f"{rel}: SKIP (already)"
    if 'id="shareBtn"' in html:
        return f"{rel}: SKIP (share already, e.g. twice-seoul)"

    lk = lang_key(rel)
    if lk not in L10N:
        return f"{rel}: SKIP (unknown locale {lk})"
    label, aria, toast_copied, addr_prefix = L10N[lk]

    # (1) back 링크 단독 라인 탐색 — `<a class="back" href="index.html">...</a>`
    m = re.search(r'(<a class="back" href="index\.html">.*?</a>)', html)
    if not m:
        return f"{rel}: FAIL (back link 미발견)"
    back = m.group(1)

    # (2) .share-row 로 래핑 + 공유 버튼. back 은 margin-inline-end:auto 로 좌측 고정.
    back_inrow = back.replace(
        '<a class="back"',
        '<a class="back" style="margin-inline-end:auto;align-self:center"',
        1,
    )
    btn = (
        f'<button type="button" class="share-btn" id="shareBtn" '
        f'aria-label="{aria}">{SHARE_SVG}{label}</button>'
    )
    share_row = f'<div class="share-row">{back_inrow}\n  {btn}</div>'
    html = html.replace(back, share_row, 1)

    # (3) CSS 주입 (</style> 직전 첫 번째만).
    if "</style>" not in html:
        return f"{rel}: FAIL (</style> 없음)"
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

    # (4) JS 주입 (</body> 직전).
    if "</body>" not in html:
        return f"{rel}: FAIL (</body> 없음)"
    html = html.replace("</body>", js_block(toast_copied, addr_prefix) + "</body>", 1)

    path.write_text(html, encoding="utf-8")
    return f"{rel}: OK ({lk})"


def is_event(path: pathlib.Path) -> bool:
    # index.html 은 홈(별도 처리). 그 외 dist 직속/로케일 직속 *.html 이 이벤트.
    return path.name != "index.html"


def patch_home(path: pathlib.Path) -> str:
    """홈(index.html 11언어) — .top 바(로고+도메인) 우측에 공유 버튼 인라인 추가."""
    rel = str(path.relative_to(DIST))
    html = path.read_text(encoding="utf-8")
    if MARKER in html:
        return f"{rel}: SKIP (already)"
    if 'id="shareBtn"' in html:
        return f"{rel}: SKIP (share already)"

    lk = lang_key(rel)
    if lk not in L10N:
        return f"{rel}: SKIP (unknown locale {lk})"
    label, aria, toast_copied, addr_prefix = L10N[lk]

    # (1) .top 바를 flex 로 펴고 공유 버튼을 우측에 — 도메인 span 다음, </div> 직전.
    # .top 마크업: <div class="top"><img ...><span>...domain...</span></div>
    m = re.search(r'(<div class="top">.*?)(</div>)', html)
    if not m:
        return f"{rel}: FAIL (.top 바 미발견)"
    top_inner, close = m.group(1), m.group(2)
    btn = (
        f'<button type="button" class="share-btn" id="shareBtn" '
        f'aria-label="{aria}" style="margin-inline-start:auto">{SHARE_SVG}{label}</button>'
    )
    # .top 에 flex 정렬 보강(기존 클래스 유지, 인라인 보강) + 버튼 삽입.
    new_top = top_inner.replace(
        '<div class="top">',
        '<div class="top" style="display:flex;align-items:center;gap:8px">',
        1,
    )
    html = html.replace(top_inner + close, new_top + btn + close, 1)

    # (2) CSS 주입.
    if "</style>" not in html:
        return f"{rel}: FAIL (</style> 없음)"
    html = html.replace("</style>", CSS_BLOCK + "</style>", 1)

    # (3) JS 주입.
    if "</body>" not in html:
        return f"{rel}: FAIL (</body> 없음)"
    html = html.replace("</body>", js_block(toast_copied, addr_prefix) + "</body>", 1)

    path.write_text(html, encoding="utf-8")
    return f"{rel}: OK home ({lk})"


def main() -> int:
    results = []
    for path in sorted(DIST.rglob("*.html")):
        if is_event(path):
            results.append(patch_event(path))
        else:
            results.append(patch_home(path))

    ok = [r for r in results if ": OK" in r]
    skip = [r for r in results if ": SKIP" in r]
    fail = [r for r in results if ": FAIL" in r]
    for r in fail:
        print("  " + r, file=sys.stderr)
    print(f"event pages — OK={len(ok)} SKIP={len(skip)} FAIL={len(fail)}")

    # 검증: marker 누락(OK 인데 shareBtn 없음) 0 확인.
    bad = 0
    for path in sorted(DIST.rglob("*.html")):
        h = path.read_text(encoding="utf-8")
        if MARKER in h and 'id="shareBtn"' not in h:
            bad += 1
            print(f"  INCONSISTENT {path.relative_to(DIST)}", file=sys.stderr)
    print(f"inconsistent(marker w/o btn): {bad}")
    return 1 if (fail or bad) else 0


if __name__ == "__main__":
    raise SystemExit(main())
