# 보스 보류 작업 (보스 손이 필요 — 나머지는 진행됨)

> 아래는 *대표 계정/권한*이 필요해 미뤄둔 일들. 이것만 처리되면 사이트를 라이브로 올릴 수 있음.
> 사이트 콘텐츠·엔진·페이지 10개는 이미 생성 완료(`site/dist/`).

## 1. 도메인 / 호스팅
- [ ] `fandom.100m1s.com` 서브도메인 DNS 추가 (기존 100m1s 호스팅에 연결)
- [ ] `site/dist/` 정적 파일을 해당 서브도메인에 배포 (기존 홈페이지 빌드 파이프라인 재활용 가능)
- [ ] 기존 `privacy.html`·`terms.html` 링크 연결 (이미 "하위 도메인"까지 커버)

## 2. 어필리에이트 가입 (가입 후 ID만 교체하면 전 페이지 일괄 반영)
가입 → `site/events.json`의 `affiliate` 블록 PLACEHOLDER 값 교체 → `python3 generate.py` 재실행.

- [ ] **Stay22** (호텔, 30% split) — stay22.com, 웹사이트 필수(=서브도메인으로 충족)
- [ ] **Travelpayouts** (항공+호텔, Booking 등) — travelpayouts.com, Project 등록
- [ ] **Airalo** (eSIM 10%) — partners.airalo.com (Impact.com 경유)
- [ ] **Klook** (투어 3~8%) — Involve Asia 경유

## 3. 부가 (선택)
- [ ] 뉴스레터 도구 무료티어 가입(beehiiv 등) → 알림 폼 연결
- [ ] PayPal 또는 USD 수령 계좌 (정산용)

## 교체 지점 (참고)
`site/events.json`:
```
"affiliate": {
  "booking_aid": "PLACEHOLDER_BOOKING_AID",
  "stay22_script": "PLACEHOLDER_STAY22_SCRIPT_ID",
  "skyscanner_pid": "PLACEHOLDER_SKYSCANNER_PID",
  "airalo_ref": "PLACEHOLDER_AIRALO_IMPACT_REF",
  "klook_aid": "PLACEHOLDER_KLOOK_AID"
}
```
값만 바꾸고 `python3 generate.py` 실행하면 끝.
