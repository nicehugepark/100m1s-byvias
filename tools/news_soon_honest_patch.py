#!/usr/bin/env python3
"""news-soon 빈 약속 라벨 → 정직 정보형 교체 (twice 상세 한정).

원칙: "준비 중 남발" 금지. 약속형("coming soon"/"준비 중") 라벨 제거 →
없는 기능임을 명시하고 공식 예매처(대안)를 안내.

- seoul: 본문에 NOL Ticket 딥링크 존재 → 해당 링크로 직접 안내.
- kaohsiung: 대만 공연 (NOL 미사용) → 공식 예매처 일반 안내 (잘못된 링크 박제 금지).

zh-cn/zh-tw 는 동시 세션(zh-localization) 영역이라 제외.
index 계열은 동시 세션(byvias-home-impl) 영역이라 제외.
twice 외 845개 파일의 동일 라벨은 별도 사이클에서 일괄 처리 (lead 결정 대기).
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

NOL = "https://world.nol.com/en/ticket/places/26000627/products/26007949"

# (old news-soon innerHTML, seoul 대체, kaohsiung 대체) — 언어별
# 약속형 문구 제거 + 정직 정보 + (seoul) NOL 링크 / (kaohsiung) 공식 예매처 일반 안내.
LANGS = {
    "": (  # ko
        "🔔 가격·매진 알림 기능 준비 중입니다",
        f"🔔 별도 가격·매진 알림 기능은 없습니다 — 잔여석·재오픈은 "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">공식 예매처(NOL Ticket) ↗</a>에서 직접 확인하세요',
        "🔔 별도 가격·매진 알림 기능은 없습니다 — 잔여석·재오픈은 공식 예매처에서 직접 확인하세요",
    ),
    "en/": (
        "🔔 Price &amp; sold-out alerts — coming soon",
        f"🔔 No built-in price/sold-out alerts — check seat returns &amp; re-opens directly on the "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">official seller (NOL Ticket) ↗</a>',
        "🔔 No built-in price/sold-out alerts — check seat returns &amp; re-opens directly on the official ticketing site",
    ),
    "ja/": (
        "🔔 価格・売切通知機能は準備中です",
        f"🔔 価格・売切通知機能はありません — 残席・再販は"
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">公式販売サイト（NOL Ticket）↗</a>で直接ご確認ください',
        "🔔 価格・売切通知機能はありません — 残席・再販は公式販売サイトで直接ご確認ください",
    ),
    "es/": (
        "🔔 Alertas de precio y agotamiento — próximamente",
        f"🔔 No hay alertas de precio/agotamiento — consulta devoluciones y reaperturas directamente en el "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">vendedor oficial (NOL Ticket) ↗</a>',
        "🔔 No hay alertas de precio/agotamiento — consulta devoluciones y reaperturas directamente en la web oficial de venta",
    ),
    "pt/": (
        "🔔 Alertas de preço e esgotamento — em breve",
        f"🔔 Sem alertas de preço/esgotamento — verifique devoluções e reaberturas diretamente no "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">vendedor oficial (NOL Ticket) ↗</a>',
        "🔔 Sem alertas de preço/esgotamento — verifique devoluções e reaberturas diretamente no site oficial de venda",
    ),
    "id/": (
        "🔔 Notifikasi harga &amp; tiket habis — segera hadir",
        f"🔔 Tidak ada notifikasi harga/tiket habis — cek kursi yang dikembalikan &amp; dibuka ulang langsung di "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">penjual resmi (NOL Ticket) ↗</a>',
        "🔔 Tidak ada notifikasi harga/tiket habis — cek kursi yang dikembalikan &amp; dibuka ulang langsung di situs penjualan resmi",
    ),
    "th/": (
        "🔔 ฟีเจอร์แจ้งเตือนราคา/ตั๋วหมด เร็วๆ นี้",
        f"🔔 ไม่มีฟีเจอร์แจ้งเตือนราคา/ตั๋วหมด — ตรวจสอบที่นั่งคืน/เปิดรอบใหม่ได้โดยตรงที่"
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">ผู้จำหน่ายอย่างเป็นทางการ (NOL Ticket) ↗</a>',
        "🔔 ไม่มีฟีเจอร์แจ้งเตือนราคา/ตั๋วหมด — ตรวจสอบที่นั่งคืน/เปิดรอบใหม่ได้โดยตรงที่เว็บไซต์จำหน่ายอย่างเป็นทางการ",
    ),
    "vi/": (
        "🔔 Tính năng thông báo giá &amp; hết vé — sắp ra mắt",
        f"🔔 Không có thông báo giá/hết vé — kiểm tra vé trả lại &amp; mở bán lại trực tiếp trên "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">trang bán vé chính thức (NOL Ticket) ↗</a>',
        "🔔 Không có thông báo giá/hết vé — kiểm tra vé trả lại &amp; mở bán lại trực tiếp trên trang bán vé chính thức",
    ),
    "ar/": (
        "🔔 ميزة إشعارات الأسعار ونفاد التذاكر — قريبًا",
        f"🔔 لا توجد إشعارات للأسعار أو نفاد التذاكر — تحقّق من المقاعد المُعادة وإعادة الطرح مباشرةً عبر "
        f'<a href="{NOL}" target="_blank" rel="noopener nofollow">البائع الرسمي (NOL Ticket) ↗</a>',
        "🔔 لا توجد إشعارات للأسعار أو نفاد التذاكر — تحقّق من المقاعد المُعادة وإعادة الطرح مباشرةً عبر موقع البيع الرسمي",
    ),
}

EVENTS = {
    "twice-thisisfor-seoul.html": "seoul",
    "twice-thisisfor-kaohsiung.html": "kaohsiung",
}


def main() -> int:
    changed = []
    missing = []
    for prefix, (old, seoul_new, kao_new) in LANGS.items():
        for fname, kind in EVENTS.items():
            path = DIST / prefix / fname
            if not path.exists():
                missing.append(str(path))
                continue
            html = path.read_text(encoding="utf-8")
            old_div = f'<div class="news-soon">{old}</div>'
            new_inner = seoul_new if kind == "seoul" else kao_new
            new_div = f'<div class="news-soon">{new_inner}</div>'
            if old_div not in html:
                missing.append(f"{path} (old label not found)")
                continue
            if html.count(old_div) != 1:
                missing.append(
                    f"{path} (expected 1 occurrence, got {html.count(old_div)})"
                )
                continue
            path.write_text(html.replace(old_div, new_div), encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))

    print(f"changed: {len(changed)}")
    for c in changed:
        print(f"  {c}")
    if missing:
        print(f"MISSING/SKIPPED: {len(missing)}", file=sys.stderr)
        for m in missing:
            print(f"  {m}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
