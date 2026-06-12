/* ═══════════════════════════════════════════════════════════════
   ByBias 최애 필터 1단계 — A안 "독립 칩 행 + 바텀 시트" (Q-20260607-130)
   SPEC 정본: favorite-filter-drafts/SPEC.md §①~⑧ (디자인팀 2026-06-12)
   시안: fav-filter-A-chip-row.html (CSS 토글 데모 기법 이식 금지 — 본 파일은 JS 실구현)
   jbar.js 패턴 동형: 단일 모듈 SSOT · IIFE · 의존성 0 · 실패 = 본문 무영향(콘솔 0)
   ──────────────────────────────────────────────────────────────
   매칭 키 (구현 결정 — SPEC §3 data-fav-artists 주입 대체):
     .abadge[title] = events[].artist 원문 — generate.py 기존 출력이 ko/ja/ar 전
     로케일 불변 실측 확인. 별도 속성 주입 = 제2 SSOT + dist 재생성 리스크
     (FLR-20260611-TEC-001 dist/root divergence) → 기존 DOM 키 재사용.
   탭별 규칙 (SPEC §3):
     tp-c: artist 매칭 표시 / festival(배지 🎪, lineup DOM 부재) = 유지+dim
     tp-c 투어 그룹(.ecard-grp): 그룹 단위 표시/숨김 (도시 행 분해 금지)
     tp-m: index DOM에 lineup 데이터 부재 → 전 카드 유지+dim + "라인업 미확정"
           캡션 (숨기면 최애 출연 회차를 놓침 = 서비스 본질 역행)
     tp-u: 매칭 시 표시, 통상 교집합 0 → 빈 상태 (전체 보기 유도)
     tp-s: 면제 — 항상 전체 + 상단 1줄 주석
     아카이브(.w5-archive): 콘서트 동일 + summary 카운트 갱신, 0건 = 섹션째 숨김
   localStorage "bybias_fav" v1 (SPEC §5 verbatim):
     {v:1, artists:[원문 그대로 — 정규화·번역·소문자화 금지], filterOn, updatedAt}
     v 불일치/파싱 실패 = 폐기 + 미선택. 알 수 없는 키 = 매칭만 무시·저장 보존
     (다음 투어 발표 시 부활) — 삭제는 사용자의 명시적 재저장(모두 해제)시에만.
   상주 바 공존 (SPEC §7): 시트 z-45 (jbar 40 < 45 < toast 50 < affbar 60).
     최애 관련 fixed bottom 상주 요소 영구 금지 — 진입점 = 상단 칩 행.
     시트 오픈 = body 스크롤 락 → jbar 44↔28 축소 로직 dy 미발생 = 상태 동결.
   컬러 규율: 빨강 사용 0 (D≤7 임박 전유) · 핑크 #E84A7F 텍스트 금지 (3.52:1
     FAIL) — 하트·보더·선택 그래픽만. [완료 N] CTA 텍스트 #1a1a18 (4.75:1 PASS).
   설정 주입: window.__FAV = {l:'ko'|...11 locale} (jbar __JB 동형)
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  try {
    var FV = window.__FAV || {};
    var LANG = (FV.l || document.documentElement.lang || 'ko').toLowerCase();
    if (document.getElementById('favf-row')) return; /* 멱등 (중복 주입 가드) */
    var KEY = 'bybias_fav';

    /* ── 로케일 문자열 (SPEC §8 키) ──
       W4 노트 (jbar.js L82 관례): ko/en만 직접 반영 — 나머지 9 locale은
       i18n 캐시 경유 W4 재생성 대상. 미보유 locale은 en 폴백 (아티스트명·배지는
       번역 파이프라인 통과 금지 — 데이터 원문 그대로, FLR-20260606-AGT-001). */
    var L10N = {
      ko: {
        chip: '내 최애', hint: '최애를 고르면 모든 탭에서 최애 일정만 모아 봐요',
        all: '전체', sheetTitle: '내 최애', sheetSub: '선택하면 모든 탭에서 최애 일정을 먼저 봐요',
        searchPh: '아티스트 검색', done: '완료', clearAll: '모두 해제',
        upcomingN: '다가오는 일정 {n}건', showAllN: '전체 {n}개 보기', change: '최애 변경',
        emptyConcert: '최애의 다가오는 공연이 아직 없어요',
        emptyLineup: '확정 라인업에 최애가 아직 없어요 — 라인업 미확정 회차는 아래 남겨뒀어요',
        emptyUnderground: '이 탭 라인업에는 최애가 없어요',
        lineupTbd: '라인업 미확정', sportsExempt: '이 탭은 최애 필터가 적용되지 않아요',
        ariaDialog: '내 최애 선택', ariaApplied: '최애 필터 적용, {n}건 표시', ariaCleared: '전체 표시'
      },
      en: {
        chip: 'My bias', hint: 'Pick your bias to see only their schedule in every tab',
        all: 'All', sheetTitle: 'My bias', sheetSub: 'Pick artists to see their schedule first in every tab',
        searchPh: 'Search artists', done: 'Done', clearAll: 'Clear all',
        upcomingN: '{n} upcoming events', showAllN: 'Show all {n}', change: 'Change bias',
        emptyConcert: 'No upcoming shows from your bias yet',
        emptyLineup: "Your bias isn't in a confirmed lineup yet — TBA shows are kept below",
        emptyUnderground: "No bias in this tab's lineups",
        lineupTbd: 'Lineup TBA', sportsExempt: "This tab isn't affected by the bias filter",
        ariaDialog: 'Select my bias', ariaApplied: 'Bias filter on, showing {n}', ariaCleared: 'Showing all'
      }
    };
    var L = L10N[LANG] || L10N.en;
    function fmt(s, n) { return s.replace('{n}', '<bdi>' + n + '</bdi>'); } /* RTL 숫자 bdi 관례 */
    function fmtT(s, n) { return s.replace('{n}', n); } /* textContent용 (aria 등) */

    /* ── localStorage v1 (전 구간 try/catch — 프라이빗 모드 = 세션 메모리 동작) ── */
    var MEM = null; /* storage 실패 시 폴백 */
    function sRead() {
      var raw = null;
      try { raw = localStorage.getItem(KEY); } catch (e) { return MEM; }
      if (raw === null) return MEM;
      try {
        var o = JSON.parse(raw);
        if (!o || o.v !== 1 || Object.prototype.toString.call(o.artists) !== '[object Array]') return null;
        for (var i = 0; i < o.artists.length; i++) { if (typeof o.artists[i] !== 'string') return null; }
        return { v: 1, artists: o.artists, filterOn: !!o.filterOn, updatedAt: o.updatedAt };
      } catch (e2) { return null; } /* v 불일치/파싱 실패 = 폐기 + 미선택 (방어적 초기화) */
    }
    function sWrite(artists, filterOn) {
      var o = { v: 1, artists: artists, filterOn: !!filterOn, updatedAt: new Date().toISOString() };
      MEM = o;
      try { localStorage.setItem(KEY, JSON.stringify(o)); } catch (e) { /* 에러 UI 없음 */ }
      return o;
    }

    /* ── 날짜 (jbar 동형) ── */
    var TODAY = new Date(); TODAY.setHours(0, 0, 0, 0);
    function parseD(s) {
      var p = (s || '').split('-');
      if (p.length !== 3) return null;
      var d = new Date(+p[0], +p[1] - 1, +p[2]); d.setHours(0, 0, 0, 0);
      return d;
    }
    function isPast(card) {
      var dd = card.querySelector('.dday[data-date]');
      if (!dd) return false; /* 날짜 미상(예: "2026-09" 단월 표기) = 다가오는 일정으로 유지 */
      var dt = parseD(dd.getAttribute('data-date'));
      return !!dt && Math.round((dt - TODAY) / 86400000) < 0;
    }

    function boot() {
      try {
        if (document.getElementById('favf-row')) return;
        var tabs = document.querySelector('.tabs');
        if (!tabs) return; /* 탭 없는 페이지 = 무동작 */

        /* ── 카드 스캔 ── */
        function keyOf(card) {
          var b = card.querySelector('.abadge');
          return b ? (b.getAttribute('title') || '') : '';
        }
        function isFest(card) {
          var bs = card.querySelectorAll('.badge');
          for (var i = 0; i < bs.length; i++) { if (bs[i].textContent.indexOf('🎪') >= 0) return true; } /* 🎪 */
          return false;
        }
        function grpOf(card) {
          var p = card.parentNode;
          return (p && p.classList && p.classList.contains('ecard-grp')) ? p : null;
        }
        function collect(sel) {
          var out = [], els = document.querySelectorAll(sel);
          for (var i = 0; i < els.length; i++) {
            out.push({ el: els[i], hide: grpOf(els[i]) || els[i], key: keyOf(els[i]), fest: isFest(els[i]), past: isPast(els[i]) });
          }
          return out;
        }
        var C = collect('.tabs .tp-c .grid .ecard');   /* 콘서트 + festival + 투어 그룹 헤드 */
        var M = collect('.tabs .tp-m .grid .ecard');   /* 방청 — lineup DOM 부재 = 전 카드 미확정 */
        var U = collect('.tabs .tp-u .grid .ecard');   /* 언더 */
        var ARC = collect('.w5-archive .grid .ecard'); /* 지난 일정 아카이브 */

        /* 아티스트 목록 = 다가오는 콘서트(비 festival) 자동 도출 — 수동 큐레이션 금지 (§2).
           일정 수 = 그룹 헤드 1 + 투어 도시 행(.tg-row) 수 (실 카운트). */
        var A = {}, AKEYS = [];
        for (var ci = 0; ci < C.length; ci++) {
          var c = C[ci];
          if (c.past || c.fest || !c.key) continue;
          var n = 1, g = grpOf(c.el);
          if (g) n += g.querySelectorAll('.tg-row').length;
          if (!A[c.key]) {
            var ab = c.el.querySelector('.abadge'), nm = c.el.querySelector('.a');
            A[c.key] = {
              n: 0, disp: nm ? nm.textContent : c.key,
              bg: ab ? ab.style.background : '', fg: ab ? ab.style.color : '',
              abbr: ab ? ab.textContent : c.key
            };
            AKEYS.push(c.key);
          }
          A[c.key].n += n;
        }

        /* 아카이브 섹션 노드 (0건 시 헤더째 숨김 — 빈 섹션 잔해 금지 §4) */
        var arcDetails = document.querySelector('details.w5-archive');
        var arcSummary = arcDetails ? arcDetails.querySelector('summary') : null;
        var arcSumOrig = arcSummary ? arcSummary.textContent : '';
        var arcSection = [];
        if (arcDetails) {
          arcSection.push(arcDetails);
          var sib = arcDetails.previousElementSibling, hop = 0;
          while (sib && hop < 2 && (sib.tagName === 'P' || sib.tagName === 'H2')) {
            arcSection.push(sib); sib = sib.previousElementSibling; hop++;
          }
        }

        /* ── CSS 주입 (페이지 토큰 상속 — W5 rose 토큰: 핑크 = 그래픽·보더·소프트 bg 전유) ── */
        var css = '' +
          '.favf-sr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}' +
          '#favf-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:0 0 12px}' +
          '#favf-chip{display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:8px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-size:13.5px;font-weight:600;color:var(--ink);font-family:inherit}' +
          '#favf-chip:hover{border-color:var(--muted)}' +
          '#favf-chip .favf-heart{width:15px;height:15px;flex:none;color:var(--rose,#E84A7F)}' + /* 핑크 = 그래픽 ≥3:1 */
          '#favf-chip[aria-pressed="true"]{background:var(--rose-soft,#FCEAF1);border-color:var(--rose-line,#F6CBDC)}' +
          '#favf-chip .favf-stack{display:inline-flex;gap:3px;margin-inline-start:3px}' +
          '#favf-chip .favf-mini{width:22px;height:22px;border-radius:7px;font-size:10.5px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;overflow:hidden}' +
          '#favf-hint{font-size:12.5px;color:var(--muted)}' +
          '#favf-all{display:none;min-height:44px;padding:8px 14px;border:1px solid var(--line);border-radius:12px;background:transparent;font-size:13px;color:var(--muted);cursor:pointer;font-family:inherit}' +
          '#favf-all[aria-pressed="true"]{border-color:var(--muted);color:var(--ink)}' +
          'body.favf-sel #favf-all{display:inline-flex;align-items:center}' +
          /* 필터 ON: 숨김/디밍 — pastguard inline display:none과 독립 */
          '.favf-hide{display:none}' +
          'body.favf-on .tabs .tp-c .mdiv{display:none}' + /* 월 구분 행 = 필터 뷰에서 노이즈 */
          '.favf-tbd .ehead,.favf-tbd .c,.favf-tbd .badge,.favf-tbd .ghost{opacity:.45}' + /* 캡션은 dim 제외 (AA 유지 §6) */
          '.favf-cap{display:block;font-size:12px;color:var(--muted);margin-top:8px}' +
          '.favf-showall{display:flex;align-items:center;justify-content:center;min-height:52px;grid-column:1/-1;border:1px dashed var(--line);border-radius:12px;font-size:13.5px;font-weight:600;color:var(--muted);background:transparent;cursor:pointer;font-family:inherit}' +
          '.favf-showall:hover{border-color:var(--muted);color:var(--ink)}' +
          '.favf-empty{text-align:center;padding:24px 16px;margin:0 0 12px;border:1px solid var(--line);border-radius:12px;background:var(--card)}' +
          '.favf-empty p{margin:0 0 12px;font-size:14px}' +
          '.favf-empty .favf-gh{display:inline-flex;align-items:center;min-height:44px;padding:8px 16px;margin:0 4px;border:1px solid var(--line);border-radius:12px;font-size:13.5px;font-weight:600;color:var(--ink);background:transparent;cursor:pointer;font-family:inherit}' +
          '.favf-empty .favf-tx{display:inline-flex;align-items:center;min-height:44px;padding:8px 10px;font-size:13.5px;color:var(--muted);background:none;border:none;cursor:pointer;text-decoration:underline;font-family:inherit}' +
          '.favf-note{display:block;font-size:12.5px;color:var(--muted);margin:0 0 10px}' +
          /* 시트 — z-45 (jbar 40 < 45 < toast 50, SPEC §7) */
          '#favf-scrim{position:fixed;inset:0;z-index:45;background:rgba(0,0,0,.42);opacity:0;pointer-events:none;transition:opacity .22s;border:0;padding:0;margin:0;width:100%;cursor:default}' +
          '#favf-sheet{position:fixed;left:0;right:0;bottom:0;z-index:45;background:var(--card);color:var(--ink);border-radius:16px 16px 0 0;border:1px solid var(--line);border-bottom:none;max-height:72vh;display:flex;flex-direction:column;padding-bottom:max(16px,env(safe-area-inset-bottom));transform:translateY(102%);transition:transform .26s cubic-bezier(.16,1,.3,1);visibility:hidden}' +
          'body.favf-open #favf-scrim{opacity:1;pointer-events:auto}' +
          'body.favf-open #favf-sheet{transform:none;visibility:visible}' +
          '@media(min-width:720px){#favf-sheet{left:50%;right:auto;bottom:50%;transform:translate(-50%,60%);opacity:0;pointer-events:none;width:560px;border-radius:16px;border-bottom:1px solid var(--line);transition:opacity .2s;visibility:hidden}' +
          'body.favf-open #favf-sheet{transform:translate(-50%,50%);opacity:1;pointer-events:auto;visibility:visible}}' +
          '@media(prefers-reduced-motion:reduce){#favf-sheet,#favf-scrim{transition:none}}' +
          '#favf-sheet .favf-grab{width:36px;height:4px;border-radius:2px;background:var(--line);margin:10px auto 2px;flex:none}' +
          '#favf-sheet .favf-head{display:flex;align-items:flex-start;padding:8px 18px 4px;flex:none}' +
          '#favf-sheet h2{font-size:17px;margin:0}' +
          '#favf-sheet .favf-sub{font-size:12.5px;color:var(--muted);margin:2px 0 0}' +
          '#favf-x{margin-inline-start:auto;width:44px;height:44px;flex:none;display:flex;align-items:center;justify-content:center;border:none;background:none;color:var(--muted);font-size:20px;cursor:pointer;border-radius:10px;font-family:inherit}' +
          '#favf-x:hover{background:var(--bg)}' +
          '#favf-search{margin:6px 18px 0;flex:none;min-height:44px;padding:8px 12px;border:1px solid var(--line);border-radius:12px;background:var(--bg);color:var(--ink);font-size:13.5px;font-family:inherit;box-sizing:border-box;display:none;width:calc(100% - 36px)}' +
          '#favf-sheet.favf-srch #favf-search{display:block}' +
          '#favf-list{overflow:auto;padding:10px 18px;display:grid;grid-template-columns:repeat(3,1fr);gap:8px;-webkit-overflow-scrolling:touch}' +
          '@media(min-width:720px){#favf-list{grid-template-columns:repeat(4,1fr)}}' +
          '.favf-cell{position:relative}' +
          '.favf-cell input{position:absolute;opacity:0;inset:0;width:100%;height:100%;cursor:pointer;margin:0}' +
          '.favf-cell label{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:44px;padding:12px 6px 10px;border:2px solid var(--line);border-radius:12px;cursor:pointer;text-align:center}' +
          '.favf-cell .abadge{pointer-events:none}' +
          '.favf-cell .favf-nm{font-size:12.5px;font-weight:600;line-height:1.3;word-break:keep-all}' +
          '.favf-cell .favf-n{font-size:11px;color:var(--muted)}' +
          '.favf-cell .favf-ck{position:absolute;top:6px;inset-inline-end:6px;width:18px;height:18px;border-radius:50%;background:var(--rose,#E84A7F);color:#1a1a18;font-size:11px;font-weight:800;display:none;align-items:center;justify-content:center}' +
          '.favf-cell input:checked+label{border-color:var(--rose,#E84A7F)}' + /* 보더+체크 병행 — 색상 단독 의존 금지 */
          '.favf-cell input:checked+label .favf-ck{display:flex}' +
          '.favf-cell input:focus-visible+label{outline:2px solid var(--accent);outline-offset:2px}' +
          '#favf-foot{display:flex;align-items:center;gap:10px;padding:12px 18px 2px;border-top:1px solid var(--line);flex:none}' +
          '#favf-clear{min-height:44px;padding:8px 14px;border:1px solid var(--line);border-radius:12px;background:transparent;color:var(--muted);font-size:13.5px;font-weight:600;cursor:pointer;font-family:inherit}' +
          '#favf-done{margin-inline-start:auto;min-height:44px;padding:8px 22px;border:none;border-radius:22px;background:var(--rose,#E84A7F);color:#1a1a18;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit}'; /* 텍스트 #1a1a18 = 4.75:1 PASS */
        var st = document.createElement('style');
        st.id = 'favf-css';
        st.textContent = css;
        document.head.appendChild(st);

        /* ── 칩 행 (태그라인↔탭 사이 — 하단 = 여정 바 전유 §7) ── */
        var row = document.createElement('div');
        row.id = 'favf-row';
        var chip = document.createElement('button');
        chip.id = 'favf-chip'; chip.type = 'button';
        chip.setAttribute('aria-haspopup', 'dialog');
        chip.setAttribute('aria-expanded', 'false');
        chip.innerHTML = '<svg class="favf-heart" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 21s-7.5-4.9-10-9.5C.4 8.4 2.3 4.5 6 4.5c2.2 0 3.6 1.2 6 3.8 2.4-2.6 3.8-3.8 6-3.8 3.7 0 5.6 3.9 4 7C19.5 16.1 12 21 12 21z"/></svg>';
        var chipLbl = document.createElement('span');
        chip.appendChild(chipLbl);
        var chipStack = document.createElement('span');
        chipStack.className = 'favf-stack'; chipStack.setAttribute('aria-hidden', 'true');
        chip.appendChild(chipStack);
        row.appendChild(chip);
        var hint = document.createElement('span');
        hint.id = 'favf-hint'; hint.textContent = L.hint;
        chip.setAttribute('aria-describedby', 'favf-hint');
        row.appendChild(hint);
        var allBtn = document.createElement('button');
        allBtn.id = 'favf-all'; allBtn.type = 'button'; allBtn.textContent = L.all;
        row.appendChild(allBtn);
        tabs.parentNode.insertBefore(row, tabs);

        /* aria-live (sr 전용 — 결과 변경 고지 §6) */
        var live = document.createElement('div');
        live.className = 'favf-sr';
        live.setAttribute('aria-live', 'polite');
        tabs.parentNode.insertBefore(live, tabs.nextSibling);

        /* ── 시트 DOM ── */
        var scrim = document.createElement('button');
        scrim.id = 'favf-scrim'; scrim.type = 'button';
        scrim.setAttribute('aria-hidden', 'true'); scrim.tabIndex = -1;
        document.body.appendChild(scrim);
        var sheet = document.createElement('section');
        sheet.id = 'favf-sheet';
        sheet.setAttribute('role', 'dialog');
        sheet.setAttribute('aria-modal', 'true');
        sheet.setAttribute('aria-labelledby', 'favf-title');
        sheet.setAttribute('aria-label', L.ariaDialog);
        sheet.innerHTML = '<div class="favf-grab" aria-hidden="true"></div>' +
          '<div class="favf-head"><div><h2 id="favf-title" tabindex="-1"></h2><p class="favf-sub"></p></div>' +
          '<button id="favf-x" type="button">✕</button></div>' +
          '<input id="favf-search" type="search">' +
          '<div id="favf-list"></div>' +
          '<div id="favf-foot"><button id="favf-clear" type="button"></button><button id="favf-done" type="button"></button></div>';
        document.body.appendChild(sheet);
        sheet.querySelector('#favf-title').textContent = L.sheetTitle;
        sheet.querySelector('.favf-sub').textContent = L.sheetSub;
        sheet.querySelector('#favf-x').setAttribute('aria-label', L.all === 'All' ? 'Close' : '닫기');
        var elSearch = sheet.querySelector('#favf-search');
        elSearch.placeholder = L.searchPh;
        var elList = sheet.querySelector('#favf-list');
        var elClear = sheet.querySelector('#favf-clear');
        var elDone = sheet.querySelector('#favf-done');
        elClear.textContent = L.clearAll;

        /* ── 탭별 보조 DOM (showall 행 · 빈 상태 · 면제 주석) — 항상 생성, on에서만 표시 ── */
        function mkShowAll(grid) {
          var b = document.createElement('button');
          b.type = 'button'; b.className = 'favf-showall'; b.style.display = 'none';
          b.addEventListener('click', function () { setFilterOn(false); }); /* 일시 해제 — 선택 보존 (§1) */
          grid.appendChild(b);
          return b;
        }
        function mkEmpty(grid, msg, withBtns) {
          var d = document.createElement('div');
          d.className = 'favf-empty'; d.style.display = 'none';
          var p = document.createElement('p'); p.textContent = msg; d.appendChild(p);
          var gh = null;
          if (withBtns) {
            gh = document.createElement('button'); gh.type = 'button'; gh.className = 'favf-gh';
            gh.addEventListener('click', function () { setFilterOn(false); });
            d.appendChild(gh);
            var tx = document.createElement('button'); tx.type = 'button'; tx.className = 'favf-tx';
            tx.textContent = L.change;
            tx.addEventListener('click', openSheet);
            d.appendChild(tx);
          }
          grid.parentNode.insertBefore(d, grid);
          return { box: d, gh: gh };
        }
        var gC = tabs.querySelector('.tp-c .grid'), gM = tabs.querySelector('.tp-m .grid'), gU = tabs.querySelector('.tp-u .grid');
        var saC = gC ? mkShowAll(gC) : null, saM = gM ? mkShowAll(gM) : null, saU = gU ? mkShowAll(gU) : null;
        var emC = gC ? mkEmpty(gC, L.emptyConcert, true) : null;
        var emU = gU ? mkEmpty(gU, L.emptyUnderground, true) : null;
        var noteM = null;
        if (gM) { /* 방청 = dim 잔존이 곧 빈 상태 변형 (§4) — 메시지 1줄, 행동 버튼 없음 */
          noteM = document.createElement('p');
          noteM.className = 'favf-note'; noteM.style.display = 'none';
          noteM.textContent = L.emptyLineup;
          gM.parentNode.insertBefore(noteM, gM);
        }
        var noteS = null, pS = tabs.querySelector('.tp-s');
        if (pS) {
          noteS = document.createElement('p');
          noteS.className = 'favf-note'; noteS.style.display = 'none';
          noteS.textContent = L.sportsExempt;
          pS.insertBefore(noteS, pS.firstChild);
        }
        function setCap(item, on) { /* dim 캡션 1줄 — 캡션 자체는 AA 유지 (dim 제외) */
          var cap = item.el.querySelector('.favf-cap');
          if (on && !cap) {
            cap = document.createElement('span');
            cap.className = 'favf-cap'; cap.textContent = L.lineupTbd;
            item.el.appendChild(cap);
          }
          if (cap) cap.style.display = on ? 'block' : 'none';
        }

        /* ── 상태 ── */
        var rec = sRead();
        var S = {
          artists: rec ? rec.artists.slice() : [],
          filterOn: rec ? rec.filterOn : false,
          saved: !!rec /* 유효 레코드 존재 = 힌트 영구 소멸 (재노출 없음 §1) */
        };
        function selSet() {
          var m = {};
          for (var i = 0; i < S.artists.length; i++) m[S.artists[i]] = 1;
          return m;
        }

        /* ── 적용 ── */
        function apply(announce) {
          var sel = selSet(), hasSel = S.artists.length > 0;
          var on = hasSel && S.filterOn;
          document.body.classList.toggle('favf-on', on);
          document.body.classList.toggle('favf-sel', hasSel);

          /* 칩 */
          chip.setAttribute('aria-pressed', on ? 'true' : 'false');
          chipLbl.textContent = hasSel ? L.chip + ' ' + S.artists.length : L.chip;
          chipStack.innerHTML = '';
          if (hasSel) {
            var shown = 0;
            for (var i = 0; i < S.artists.length && shown < 3; i++) {
              var a = A[S.artists[i]];
              if (!a) continue; /* 알 수 없는 키 = 표시만 생략, 저장 보존 (§5) */
              var mi = document.createElement('span');
              mi.className = 'favf-mini';
              mi.style.background = a.bg; mi.style.color = a.fg || '#fff';
              mi.textContent = a.abbr;
              chipStack.appendChild(mi);
              shown++;
            }
            if (S.artists.length > 3) {
              var pl = document.createElement('span');
              pl.className = 'favf-mini';
              pl.style.background = 'var(--line)'; pl.style.color = 'var(--ink)';
              pl.textContent = '+' + (S.artists.length - 3);
              chipStack.appendChild(pl);
            }
          }
          hint.style.display = S.saved ? 'none' : '';
          allBtn.setAttribute('aria-pressed', (hasSel && !S.filterOn) ? 'true' : 'false');

          /* tp-c: 매칭 표시 / festival dim / 그룹 단위 숨김 */
          var i2, it, m, nC = 0, totC = 0, dimC = 0;
          for (i2 = 0; i2 < C.length; i2++) {
            it = C[i2];
            if (it.past) continue;
            totC++;
            if (!on) { it.hide.classList.remove('favf-hide'); it.el.classList.remove('favf-tbd'); setCap(it, false); continue; }
            if (it.fest) { /* lineup 미확정 ≠ 불일치 — 유지+dim (§3) */
              it.hide.classList.remove('favf-hide');
              it.el.classList.add('favf-tbd'); setCap(it, true); dimC++;
            } else {
              m = !!sel[it.key];
              it.el.classList.remove('favf-tbd'); setCap(it, false);
              it.hide.classList.toggle('favf-hide', !m);
              if (m) nC++;
            }
          }
          if (saC) { saC.style.display = on ? 'flex' : 'none'; saC.innerHTML = fmt(L.showAllN, totC); }
          if (emC) {
            emC.box.style.display = (on && nC === 0) ? 'block' : 'none';
            if (emC.gh) emC.gh.innerHTML = fmt(L.showAllN, totC);
          }

          /* tp-m: 전 카드 유지+dim (lineup DOM 부재 — 숨김 금지 §3) */
          var totM = 0;
          for (i2 = 0; i2 < M.length; i2++) {
            it = M[i2];
            if (it.past) continue;
            totM++;
            it.hide.classList.remove('favf-hide');
            it.el.classList.toggle('favf-tbd', on);
            setCap(it, on);
          }
          if (saM) { saM.style.display = on ? 'flex' : 'none'; saM.innerHTML = fmt(L.showAllN, totM); }
          if (noteM) noteM.style.display = on ? 'block' : 'none';

          /* tp-u: 매칭 표시 — 통상 교집합 0 = 빈 상태 (§3/§4) */
          var nU = 0, totU = 0;
          for (i2 = 0; i2 < U.length; i2++) {
            it = U[i2];
            if (it.past) continue;
            totU++;
            m = !on || !!sel[it.key];
            it.hide.classList.toggle('favf-hide', on && !m);
            if (on && m) nU++;
          }
          if (saU) { saU.style.display = (on && nU > 0) ? 'flex' : 'none'; saU.innerHTML = fmt(L.showAllN, totU); }
          if (emU) {
            emU.box.style.display = (on && nU === 0) ? 'block' : 'none';
            if (emU.gh) emU.gh.innerHTML = fmt(L.showAllN, totU);
          }

          /* tp-s: 면제 주석 (§3) */
          if (noteS) noteS.style.display = on ? 'block' : 'none';

          /* 아카이브: 동일 적용 + summary 카운트 갱신, 0건 = 섹션째 숨김 (§3/§4) */
          var nArc = 0;
          for (i2 = 0; i2 < ARC.length; i2++) {
            it = ARC[i2];
            m = !on || !!sel[it.key];
            it.hide.classList.toggle('favf-hide', on && !m);
            if (m) nArc++;
          }
          if (arcSummary) {
            arcSummary.textContent = on ? arcSumOrig.replace(/\d+/, String(nArc)) : arcSumOrig;
          }
          for (i2 = 0; i2 < arcSection.length; i2++) {
            arcSection[i2].style.display = (on && nArc === 0) ? 'none' : '';
          }

          /* 결과 고지 (콘서트 탭 표시 건수 기준) */
          if (announce) live.textContent = on ? fmtT(L.ariaApplied, nC) : L.ariaCleared;
        }

        function setFilterOn(v) {
          S.filterOn = !!v;
          sWrite(S.artists, S.filterOn);
          S.saved = true;
          apply(true);
        }

        /* ── 시트 ── */
        var lastFocus = null, openFlag = false, bodyOv = '', openSnap = '';
        function cells() { return elList.querySelectorAll('.favf-cell input'); }
        function doneCount() {
          var cs = cells(), n = 0;
          for (var i = 0; i < cs.length; i++) { if (cs[i].checked) n++; }
          return n;
        }
        function updDone() {
          var n = doneCount();
          elDone.innerHTML = n > 0 ? L.done + ' <bdi>' + n + '</bdi>' : L.done;
        }
        function renderList() {
          elList.innerHTML = '';
          var sel = selSet();
          /* 정렬: ① 선택됨 ② 다가오는 일정 수 desc ③ 표시명 (§2) */
          var keys = AKEYS.slice().sort(function (x, y) {
            var sx = sel[x] ? 1 : 0, sy = sel[y] ? 1 : 0;
            if (sx !== sy) return sy - sx;
            if (A[y].n !== A[x].n) return A[y].n - A[x].n;
            return A[x].disp.localeCompare(A[y].disp, LANG);
          });
          for (var i = 0; i < keys.length; i++) {
            var k = keys[i], a = A[k];
            var cell = document.createElement('span');
            cell.className = 'favf-cell';
            var id = 'favf-a' + i;
            var inp = document.createElement('input');
            inp.type = 'checkbox'; inp.id = id; inp.checked = !!sel[k];
            inp.setAttribute('data-key', k);
            inp.setAttribute('aria-label', a.disp + ' — ' + fmtT(L.upcomingN, a.n));
            inp.addEventListener('change', updDone);
            var lab = document.createElement('label');
            lab.setAttribute('for', id);
            var bd = document.createElement('span');
            bd.className = 'abadge';
            bd.style.background = a.bg; bd.style.color = a.fg || '#fff';
            bd.setAttribute('aria-hidden', 'true');
            var bdi = document.createElement('bdi'); bdi.textContent = a.abbr;
            bd.appendChild(bdi);
            var nm = document.createElement('span'); nm.className = 'favf-nm';
            var nbdi = document.createElement('bdi'); nbdi.textContent = a.disp;
            nm.appendChild(nbdi);
            var cnt = document.createElement('span'); cnt.className = 'favf-n';
            cnt.textContent = a.n; cnt.setAttribute('aria-hidden', 'true');
            var ck = document.createElement('span'); ck.className = 'favf-ck';
            ck.textContent = '✓'; ck.setAttribute('aria-hidden', 'true');
            lab.appendChild(bd); lab.appendChild(nm); lab.appendChild(cnt); lab.appendChild(ck);
            cell.appendChild(inp); cell.appendChild(lab);
            elList.appendChild(cell);
          }
          sheet.classList.toggle('favf-srch', keys.length >= 25); /* 검색 = ≥25명일 때만 (§2) */
          elSearch.value = '';
          updDone();
        }
        elSearch.addEventListener('input', function () {
          var q = elSearch.value.toLowerCase(), cs = elList.querySelectorAll('.favf-cell');
          for (var i = 0; i < cs.length; i++) {
            var inp = cs[i].querySelector('input');
            var k = (inp.getAttribute('data-key') || '').toLowerCase();
            var d = (A[inp.getAttribute('data-key')] || {}).disp || '';
            cs[i].style.display = (!q || k.indexOf(q) >= 0 || d.toLowerCase().indexOf(q) >= 0) ? '' : 'none';
          }
        });
        function openSheet() {
          if (openFlag) return;
          openFlag = true;
          lastFocus = document.activeElement;
          openSnap = S.artists.slice().sort().join('\u0001'); /* P0-1: 열 때 선택 스냅샷 */
          renderList();
          document.body.classList.add('favf-open');
          chip.setAttribute('aria-expanded', 'true');
          bodyOv = document.body.style.overflow;
          document.body.style.overflow = 'hidden'; /* 스크롤 락 — jbar 축소 로직 상태 동결 (§7) */
          var t = sheet.querySelector('#favf-title');
          setTimeout(function () { t.focus(); }, 60); /* 첫 포커스 = 타이틀 (§6) */
        }
        function closeSheet(save) {
          if (!openFlag) return;
          openFlag = false;
          if (save) { /* 닫기 ≠ 저장 취소 — 시트 내 선택 즉시 반영, 완료 = 닫기 겸용 (§2) */
            var cs = cells(), next = [], i;
            for (i = 0; i < cs.length; i++) {
              if (cs[i].checked) next.push(cs[i].getAttribute('data-key'));
            }
            /* 알 수 없는 키(목록 외) 보존 — 다음 투어 발표 시 부활 (§5) */
            for (i = 0; i < S.artists.length; i++) {
              if (!A[S.artists[i]] && next.indexOf(S.artists[i]) < 0) next.push(S.artists[i]);
            }
            /* P0-1: 자동 ON = 선택 "변경" 시에만 — 무변경 닫기(X/스크림/ESC)가
               사용자가 끈 필터(전체 보기)를 강제 재활성하지 않음 (스냅샷 diff) */
            var changed = next.slice().sort().join('\u0001') !== openSnap;
            S.artists = next;
            if (!next.length) S.filterOn = false; /* 0명 = 필터 소멸 (§1) */
            else if (changed) S.filterOn = true; /* 선택을 바꿨다 = 보고 싶다 — 자동 ON (§1) */
            sWrite(S.artists, S.filterOn);
            S.saved = true;
          }
          document.body.classList.remove('favf-open');
          chip.setAttribute('aria-expanded', 'false');
          document.body.style.overflow = bodyOv;
          apply(save);
          if (lastFocus && lastFocus.focus) lastFocus.focus(); /* 트리거 칩으로 포커스 복귀 (§6) */
        }
        chip.addEventListener('click', openSheet);
        allBtn.addEventListener('click', function () { setFilterOn(!S.filterOn); }); /* 일시 해제 ⇄ 복귀 — 선택 보존 */
        scrim.addEventListener('click', function () { closeSheet(true); });
        sheet.querySelector('#favf-x').addEventListener('click', function () { closeSheet(true); });
        elDone.addEventListener('click', function () { closeSheet(true); });
        elClear.addEventListener('click', function () { /* 모두 해제 = 명시적 재저장 — 알 수 없는 키 포함 전체 삭제 (§5) */
          var cs = cells();
          for (var i = 0; i < cs.length; i++) cs[i].checked = false;
          S.artists = [];
          updDone();
        });
        document.addEventListener('keydown', function (e) {
          if (!openFlag) return;
          if (e.key === 'Escape' || e.keyCode === 27) { e.preventDefault(); closeSheet(true); return; }
          if (e.key === 'Tab' || e.keyCode === 9) { /* 포커스 트랩 (§6) */
            var f = sheet.querySelectorAll('button,input,[tabindex="-1"]');
            var vis = [];
            for (var i = 0; i < f.length; i++) {
              if (f[i].offsetParent !== null || f[i] === sheet.querySelector('#favf-title')) vis.push(f[i]);
            }
            if (!vis.length) return;
            var first = vis[0], last = vis[vis.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            else if (!sheet.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
          }
        });

        apply(false); /* 초기 상태 복원 — 새로고침·언어 전환·재방문 영구 유지 (§1/§5) */
      } catch (e) { /* 필터 실패 = 페이지 본문 무영향 — 사이트는 현행과 동일 (콘솔 0) */ }
    }
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
    else boot();
  } catch (e) { /* no-op */ }
})();
