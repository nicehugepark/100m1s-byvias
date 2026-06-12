#!/usr/bin/env python3
"""WAVE8 #6+#7 멱등 패치 (R45 2심 조니 확정).

#6 sl-7(7박8일 코스) 인트로 재작성 — twice ko/en 2파일 한정:
    내부 용어 '정합' 제거 + 8.7일 수치 출처 명기.
    출처 2소스 교차 검증: 문화체육관광부·한국관광공사·한국문화관광연구원 조사
    (BTS 2026-03-21 광화문(서울) 공연 방한 외국인 관람객 평균 체류 8.7일).
    zdnet.co.kr/view/?no=20260429173051 + biz.heraldcorp.com/article/10728182.

#7 Travelpayouts(tpembars) 조건부 로드 — dist 전 페이지(847):
    미승인 상태에서 entrypoint_config 가 403 + CORS 헤더 부재 →
    브라우저 CORS 로그 + "config is not valid" console.error = 콘솔 에러 3건/페이지.
    원격 config 직접 프로브(사전 fetch)는 실패 시 브라우저가 CORS/리소스 에러를
    콘솔에 직접 기록(JS 억제 불가) → 콘솔 0 달성 불가. 따라서 동일 출처 플래그
    /tp-status.json (enabled:false) 게이트로 조건화: 미승인 동안 외부 요청 0 = 콘솔 0.
    어필리에이트 승인 후 dist/tp-status.json 을 {"enabled": true} 로 1파일 플립하면
    847 전 페이지 일괄 복원 (스크립트 제거 아님 — 조건화만, 로더 본문 보존).

멱등: 신규 마커("tp-status.json" / 신규 인트로 문장) 존재 시 skip — 2회 실행 diff 0.
참조: FLR-20260611-TEC-001 (dist/root divergence — 소스 generate.py 동시 정합 별건 commit),
      FLR-20260428-TEC-001 (한쪽 수정·다른쪽 누락).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

# ── #7 Travelpayouts 로더 조건화 ────────────────────────────────────────────
OLD_TP = (
    "  (function () {\n"
    '      var script = document.createElement("script");\n'
    "      script.async = 1;\n"
    "      script.src = 'https://tpembars.com/NTM4MzMy.js?t=538332';\n"
    "      document.head.appendChild(script);\n"
    "  })();"
)

NEW_TP = (
    "  (function () {\n"
    "      if (!window.location.protocol.startsWith('http') || !window.fetch) return;\n"
    "      fetch('/tp-status.json').then(function (r) { return r.ok ? r.json() : null; }).then(function (cfg) {\n"
    "          if (!cfg || cfg.enabled !== true) return;\n"
    '          var script = document.createElement("script");\n'
    "          script.async = 1;\n"
    "          script.src = 'https://tpembars.com/NTM4MzMy.js?t=538332';\n"
    "          document.head.appendChild(script);\n"
    "      }).catch(function () {});\n"
    "  })();"
)

TP_FLAG_BODY = '{"enabled": false}\n'

# ── #6 sl-7 인트로 (twice ko/en) ────────────────────────────────────────────
OLD_KO = "원정 팬 평균 체류(8.7일) 정합."
NEW_KO = (
    "7박8일은 K-pop 공연을 보러 방한한 외국인 관람객의 평균 체류 기간 "
    "8.7일(문화체육관광부·한국관광공사 2026 조사, BTS 서울 공연 기준)에 맞춘 길이입니다."
)

OLD_EN = "Matched to the average fan stay (8.7 days)."
NEW_EN = (
    "7N8D matches the 8.7-day average stay of international visitors who came to "
    "Korea for a K-pop show (2026 survey by the Ministry of Culture, Sports and "
    "Tourism & Korea Tourism Organization, based on BTS's Seoul show)."
)

INTRO_TARGETS = [
    (DIST / "twice-thisisfor-seoul.html", OLD_KO, NEW_KO),
    (DIST / "en" / "twice-thisisfor-seoul.html", OLD_EN, NEW_EN),
]


def patch_tp() -> tuple[int, int, list[str]]:
    replaced, skipped, anomalies = 0, 0, []
    for p in sorted(DIST.rglob("*.html")):
        html = p.read_text(encoding="utf-8")
        if "tp-status.json" in html:
            skipped += 1
            continue
        n = html.count(OLD_TP)
        if n != 1:
            anomalies.append(f"{p.relative_to(DIST)}: OLD_TP count={n}")
            continue
        p.write_text(html.replace(OLD_TP, NEW_TP), encoding="utf-8")
        replaced += 1
    return replaced, skipped, anomalies


def patch_intro() -> tuple[int, int, list[str]]:
    replaced, skipped, anomalies = 0, 0, []
    for p, old, new in INTRO_TARGETS:
        html = p.read_text(encoding="utf-8")
        if new in html:
            skipped += 1
            continue
        n = html.count(old)
        if n != 1:
            anomalies.append(f"{p.relative_to(DIST)}: OLD intro count={n}")
            continue
        p.write_text(html.replace(old, new), encoding="utf-8")
        replaced += 1
    return replaced, skipped, anomalies


def write_flag() -> str:
    flag = DIST / "tp-status.json"
    if flag.exists() and flag.read_text(encoding="utf-8") == TP_FLAG_BODY:
        return "skip(동일)"
    flag.write_text(TP_FLAG_BODY, encoding="utf-8")
    return "write"


def main() -> int:
    tp_r, tp_s, tp_a = patch_tp()
    in_r, in_s, in_a = patch_intro()
    flag = write_flag()
    print(f"#7 TP 조건화: replaced={tp_r} skipped={tp_s}")
    print(f"#6 인트로: replaced={in_r} skipped={in_s}")
    print(f"tp-status.json: {flag}")
    anomalies = tp_a + in_a
    if anomalies:
        print("ANOMALY (수동 확인 필요):")
        for a in anomalies:
            print(f"  - {a}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
