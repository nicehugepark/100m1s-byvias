# Fandom — 정적 사이트 (GitHub Pages 배포용)

팬이 모이는 일정 → 미리 싸게 잡는 법. K-pop 콘서트·팬미팅 등 이벤트별 항공·숙박 예약 타이밍 가이드.

## 구조
- `events.json` — 이벤트 데이터 + 어필리에이트 ID (여기만 고치면 됨)
- `generate.py` — 정적 사이트 생성기 (`python generate.py` → `dist/`)
- `dist/` — 생성된 정적 파일 (배포 대상)
- `CNAME` — 커스텀 도메인 `fandom.100m1s.com`
- `.github/workflows/build.yml` — 푸시 시 자동 생성·배포

## GitHub Pages 배포 (보스 작업, 1회)
1. **새 GitHub 저장소 생성** (예: `fandom-site`), 이 `site/` 폴더 내용을 루트로 푸시
   ```
   git init && git add . && git commit -m "init fandom site"
   git branch -M main
   git remote add origin https://github.com/<계정>/fandom-site.git
   git push -u origin main
   ```
2. 저장소 **Settings → Pages → Source = GitHub Actions** 선택
3. (커스텀 도메인) DNS에 **CNAME 레코드**: `fandom` → `<계정>.github.io`
   - Settings → Pages → Custom domain에 `fandom.100m1s.com` 입력, "Enforce HTTPS" 체크
4. 끝. 이후 `events.json`에 공연 추가 → 푸시하면 **자동 재생성·배포**됩니다.

> 더 간단히 가려면: Actions 없이 Settings → Pages → "Deploy from a branch" → `main` / `/dist` 선택도 가능(단, 매번 로컬에서 `python generate.py` 실행 후 푸시).

## 어필리에이트 활성화
가입 후 `events.json`의 `affiliate` PLACEHOLDER 5개 교체 → 푸시(자동 재빌드). 상세: `BOSS-TODO.md`.

## 한계 (정적 사이트)
- 서버 없음 → 뉴스레터 폼은 외부 서비스(beehiiv·Formspree·Google Form) 연결 필요(선택).
- 어필리에이트 링크는 클라이언트 사이드라 정적으로 OK.
