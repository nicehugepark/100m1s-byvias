#!/usr/bin/env python3
"""news-soon 빈 약속 라벨 → 정직 정보형 전수 치환 (twice 외 전 이벤트 + index).

원칙: "준비 중 남발" 금지. 약속형("coming soon"/"준비 중"/"即將推出" 등) 라벨 제거 →
알림 기능 부재 명시 + 공식 예매처 일반 안내. 전 이벤트 페이지(811+)는 예매처가
제각각(NOL/tixcraft/Klook/Pia 등)이라 이벤트별 딥링크 하드코딩 불가 → 잘못된 링크
박제 금지(FLR-AGT-002) 위해 "공식 예매처" 일반 안내로 통일. (twice-seoul 의 NOL
딥링크는 별건 commit dc7ae5c 에서 검증 적용 완료, 본 sweep 대상 아님.)

대상: 남은 11개 언어 promise 라벨 전수. zh-cn/zh-tw 포함(zh-localization 세션 종료).
zh 문구는 기존 라벨 어휘 기반 보수 치환 — 간/번 혼입 0 (zh-cn=简体, zh-tw=繁體 분리).
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# old promise innerHTML -> new honest innerHTML (언어별, 1:1)
PAIRS = {
    # ko
    "🔔 가격·매진 알림 기능 준비 중입니다": "🔔 별도 가격·매진 알림 기능은 없습니다 — 잔여석·재오픈은 공식 예매처에서 직접 확인하세요",
    # en
    "🔔 Price &amp; sold-out alerts — coming soon": "🔔 No built-in price/sold-out alerts — check seat returns &amp; re-opens directly on the official ticketing site",
    # ja
    "🔔 価格・売切通知機能は準備中です": "🔔 価格・売切通知機能はありません — 残席・再販は公式販売サイトで直接ご確認ください",
    # es
    "🔔 Alertas de precio y agotamiento — próximamente": "🔔 No hay alertas de precio/agotamiento — consulta devoluciones y reaperturas directamente en la web oficial de venta",
    # pt
    "🔔 Alertas de preço e esgotamento — em breve": "🔔 Sem alertas de preço/esgotamento — verifique devoluções e reaberturas diretamente no site oficial de venda",
    # id
    "🔔 Notifikasi harga &amp; tiket habis — segera hadir": "🔔 Tidak ada notifikasi harga/tiket habis — cek kursi yang dikembalikan &amp; dibuka ulang langsung di situs penjualan resmi",
    # th
    "🔔 ฟีเจอร์แจ้งเตือนราคา/ตั๋วหมด เร็วๆ นี้": "🔔 ไม่มีฟีเจอร์แจ้งเตือนราคา/ตั๋วหมด — ตรวจสอบที่นั่งคืน/เปิดรอบใหม่ได้โดยตรงที่เว็บไซต์จำหน่ายอย่างเป็นทางการ",
    # vi
    "🔔 Tính năng thông báo giá &amp; hết vé — sắp ra mắt": "🔔 Không có thông báo giá/hết vé — kiểm tra vé trả lại &amp; mở bán lại trực tiếp trên trang bán vé chính thức",
    # ar
    "🔔 ميزة إشعارات الأسعار ونفاد التذاكر — قريبًا": "🔔 لا توجد إشعارات للأسعار أو نفاد التذاكر — تحقّق من المقاعد المُعادة وإعادة الطرح مباشرةً عبر موقع البيع الرسمي",
    # zh-cn (简体) — 약속 "即將推出" 제거 → 부재 명시 + 공식 예매처
    "🔔 价格·售罄提醒功能即将推出": "🔔 暂无价格·售罄提醒功能 — 余票·补票请直接在官方购票网站查询",
    # zh-tw (繁體)
    "🔔 票價·完售提醒功能即將推出": "🔔 暫無票價·完售提醒功能 — 餘票·補票請直接於官方售票網站查詢",
}


def main() -> int:
    changed = 0
    files_touched = []
    for path in DIST.rglob("*.html"):
        html = path.read_text(encoding="utf-8")
        orig = html
        for old, new in PAIRS.items():
            old_div = f'<div class="news-soon">{old}</div>'
            if old_div in html:
                new_div = f'<div class="news-soon">{new}</div>'
                # 페이지당 라벨 1개 가정 — 다중 시 모두 치환 (동일 언어 페이지 내 1개)
                html = html.replace(old_div, new_div)
        if html != orig:
            path.write_text(html, encoding="utf-8")
            changed += 1
            files_touched.append(str(path.relative_to(ROOT)))

    print(f"files changed: {changed}")

    # 잔존 검증: 어떤 promise 라벨도 남으면 안 됨
    remaining = 0
    for path in DIST.rglob("*.html"):
        h = path.read_text(encoding="utf-8")
        for old in PAIRS:
            if f'<div class="news-soon">{old}</div>' in h:
                remaining += 1
                print(
                    f"  REMAINING promise in {path.relative_to(ROOT)}: {old[:30]}",
                    file=sys.stderr,
                )
    print(f"remaining promise labels: {remaining}")
    return 0 if remaining == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
