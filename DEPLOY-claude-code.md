# ByBias 사이트 배포 지시서 (Claude Code / 보스 맥에서 실행)

> Cowork 샌드박스는 GitHub 인증·네트워크가 없어 푸시 불가. 이 파일을 **Claude Code(보스 맥, SSH 인증됨)** 에 넘기거나 보스가 직접 실행.
> 권고: 기존 `100m1s` repo가 아니라 **별도 repo `fandom-site`** 로 분리 (Pages는 repo당 사이트 1개).

## 1. 별도 repo로 복사 + 초기화
현재 `site/`는 100m1s repo 작업트리 안에 있으므로, 별도 디렉토리로 복사해 새 repo로 만든다.
```
cp -r ~/company/100m1s/projects/fandom-demand-radar/site ~/company/fandom-site
cd ~/company/fandom-site
git init && git add . && git commit -m "init: fandom static site"
git branch -M main
```

## 2. GitHub repo 생성 + 푸시 (gh CLI)
```
gh repo create nicehugepark/fandom-site --public --source=. --remote=origin --push
```
(또는 github.com에서 빈 repo 생성 후 `git remote add origin … && git push -u origin main`)

## 3. GitHub Pages 활성화 (Actions 방식)
- repo **Settings → Pages → Source = GitHub Actions**
- 포함된 `.github/workflows/build.yml` 이 푸시 시 `generate.py` 실행 → `dist/` 배포
- (CLI로도 가능) `gh api -X POST repos/nicehugepark/fandom-site/pages -f 'build_type=workflow'`

## 4. 커스텀 도메인 연결
- 100m1s.com DNS에 **CNAME 레코드**: `bybias` → `nicehugepark.github.io`
- repo Settings → Pages → Custom domain = `bybias.100m1s.com` → "Enforce HTTPS" 체크
- (`CNAME` 파일은 이미 repo에 포함됨)

## 5. 검증
- Actions 탭에서 build·deploy 성공 확인
- `https://bybias.100m1s.com` 접속 → index + 이벤트 페이지(미래분) 확인

## 이후 운영
- `events.json`에 공연 추가 → 커밋·푸시하면 **자동 재생성·배포**
- 어필리에이트 가입 후 `events.json`의 PLACEHOLDER 5개 교체 → 푸시 (상세 `BOSS-TODO.md`)

---
주의(회사 룰): 신규 repo 생성·push는 publish 동작이므로 lead/대표 승인 후 진행. cron/SSOT 파이프라인과 무관한 **별도 repo**라 100m1s 파이프라인에 영향 없음.
