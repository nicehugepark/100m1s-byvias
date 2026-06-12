/* ═══════════════════════════════════════════════════════════════
   ByBias 상주 바 — 시안 B "스테이지 라이트" (R46 P1-5 · 조니 R2 fix 2026-06-12)
   시안 정본: journey-bar-drafts/journey-bar-B-stage-light.html (브랜딩 2026-06-12)
   점등 메타포 (R2 P0-2 재정의): "현재 읽는 단계" 단일 점등 — done 누적 없음.
     zones는 문서 순서(리치 3→5→4→2)로 단계 번호와 독립 — 누적 표시는 역행 시각 유발.
   마크업·토큰·JS 동작 시안 이식 + production 적응 실측 5건 (제거-2 정정: 구 "verbatim+4종" 과소 선언):
     (1) #jbar 스코프 클래스 (847페이지 이종 CSS 충돌 봉쇄)
     (2) 물리 margin → 논리 속성 (ar RTL 정합)
     (3) 페이지 토큰(--card/--ink/--line/--muted) 상속 — 시안과 동일 값 (C3 미러링)
     (4) 단일 모듈 SSOT — 페이지별 복제 금지 (fix 누락 재발 차단)
     (5) color-mix 미지원 구형 폴백 light/dark 분리 — #b9b7ac / #5b5950 실측 (시안에 없는 production 분기)
   R2 fix wave (조니 NO 9건 반영): P0-1 캡처 절차(verify 도구) · P0-2 단일 점등 ·
     P1-1 affbar 명시 yield · P1-2 D-DAY 어휘 통일 · P1-3 다크 폴백 ·
     P1-4 리듬(패딩 45/toast 동적/미니 히트 44) · 제거(홈 무점등·헤더 정정)
   브랜드 규율 (logo-drafts/SYSTEM.md):
     - bb 글리프 verbatim·컨테이너 없음 (§2) · 렌더 20px = 하한 준수 · 워드마크 금지
     - C2 핑크 전유 #E84A7F: CTA bg + 현재 점 + 점등 라벨은 잉크 (핑크 텍스트 금지)
   WCAG AA 실측 (시안 헤더 동일 — 사이트 토큰 = 시안 토큰):
     CTA #1a1a18 on #E84A7F 4.75 · 임박 레드 L#C62828 5.62 / D#FF6B6B 5.94
     핑크점 L3.67/D4.49(≥3 그래픽) · 라벨 잉크 L17.43/D13.58 · muted 7.49/7.59
   빨강 = 임박 전유: JS 게이트 d<=7 (D-8+ 빨강 0건)
   z-40 (< toast 50 < affbar 60 — affbar 표시 중 jbar 명시 yield, P1-1)
   날짜 게이트: 이벤트 날짜 부재/과거 = 바 무렌더 (가짜 값 금지)
   설정 주입: window.__JB = {t:'home'|'rich'|'event', l:'ko'|...11 locale}
   ═══════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  try {
    var JB = window.__JB || {};
    var TYPE = JB.t, LANG = JB.l || (document.documentElement.lang || 'ko').toLowerCase();
    if (!TYPE) return;
    if (document.getElementById('jbar')) return; /* 멱등 (중복 주입 가드) */

    /* ── 로케일 문자열 (11언어) ───────────────────────────── */
    var L10N = {
      ko: { nav: '현재 단계', navHome: '공연 일정', dots: '여정 5단계',
        steps: ['인지', '티켓', '항공', '숙소', '현지'],
        ariaD: '공연까지 {n}일', ariaDHome: '다음 공연까지 {n}일', ariaLive: '오늘 공연',
        cta: { ticket: '티켓 잡기', flight: '항공 보기', stay: '숙소 보기', local: '현지 보기', course: '코스 보기', book: '예매 보기', localInfo: '현지 정보', next: '임박 공연', today: '오늘 공연', liveGuide: '현지 가이드' } },
      en: { nav: 'Current stage', navHome: 'Show schedule', dots: 'Journey: 5 steps',
        steps: ['Discover', 'Tickets', 'Flights', 'Stay', 'Local'],
        ariaD: '{n} days to the show', ariaDHome: '{n} days to the next show', ariaLive: 'Show day',
        cta: { ticket: 'Get tickets', flight: 'See flights', stay: 'See stays', local: 'Local guide', course: 'See course', book: 'Book now', localInfo: 'Local info', next: 'Next show', today: "Today's show", liveGuide: 'Local guide' } },
      ja: { nav: '旅程の進行', dots: '旅程5ステップ',
        steps: ['発見', 'チケット', '航空券', '宿泊', '現地'],
        ariaD: '公演まで{n}日', ariaDHome: '次の公演まで{n}日', ariaLive: '本日公演',
        cta: { ticket: 'チケットへ', flight: '航空券を見る', stay: '宿を見る', local: '現地ガイド', course: 'コースを見る', book: '予約へ', localInfo: '現地情報', next: '直近の公演', liveGuide: '現地ガイド' } },
      'zh-cn': { nav: '行程进度', dots: '行程5步',
        steps: ['发现', '门票', '机票', '住宿', '当地'],
        ariaD: '距演出{n}天', ariaDHome: '距最近演出{n}天', ariaLive: '今日演出',
        cta: { ticket: '抢门票', flight: '看机票', stay: '看住宿', local: '当地指南', course: '看路线', book: '立即预订', localInfo: '当地信息', next: '临近演出', liveGuide: '当地指南' } },
      'zh-tw': { nav: '行程進度', dots: '行程5步',
        steps: ['發現', '門票', '機票', '住宿', '當地'],
        ariaD: '距演出{n}天', ariaDHome: '距最近演出{n}天', ariaLive: '今日演出',
        cta: { ticket: '搶門票', flight: '看機票', stay: '看住宿', local: '當地指南', course: '看路線', book: '立即預訂', localInfo: '當地資訊', next: '臨近演出', liveGuide: '當地指南' } },
      es: { nav: 'Progreso del viaje', dots: 'Viaje: 5 pasos',
        steps: ['Descubre', 'Entradas', 'Vuelos', 'Hotel', 'Local'],
        ariaD: '{n} días para el show', ariaDHome: '{n} días para el próximo show', ariaLive: 'Hoy es el show',
        cta: { ticket: 'Entradas', flight: 'Ver vuelos', stay: 'Ver hoteles', local: 'Guía local', course: 'Ver ruta', book: 'Reservar', localInfo: 'Info local', next: 'Próximo show', liveGuide: 'Guía local' } },
      th: { nav: 'ความคืบหน้าการเดินทาง', dots: 'การเดินทาง 5 ขั้น',
        steps: ['ค้นหา', 'ตั๋ว', 'เที่ยวบิน', 'ที่พัก', 'หน้างาน'],
        ariaD: 'อีก {n} วันถึงวันโชว์', ariaDHome: 'อีก {n} วันถึงโชว์ถัดไป', ariaLive: 'วันโชว์',
        cta: { ticket: 'จองตั๋ว', flight: 'ดูเที่ยวบิน', stay: 'ดูที่พัก', local: 'หน้างาน', course: 'ดูคอร์ส', book: 'จองเลย', localInfo: 'ข้อมูลพื้นที่', next: 'โชว์ถัดไป', liveGuide: 'ไกด์หน้างาน' } },
      id: { nav: 'Progres perjalanan', dots: 'Perjalanan 5 langkah',
        steps: ['Temukan', 'Tiket', 'Pesawat', 'Hotel', 'Lokal'],
        ariaD: '{n} hari menuju show', ariaDHome: '{n} hari menuju show terdekat', ariaLive: 'Hari show',
        cta: { ticket: 'Beli tiket', flight: 'Cek pesawat', stay: 'Cek hotel', local: 'Info lokal', course: 'Lihat rute', book: 'Pesan', localInfo: 'Info lokal', next: 'Show terdekat', liveGuide: 'Info lokal' } },
      pt: { nav: 'Progresso da viagem', dots: 'Viagem: 5 etapas',
        steps: ['Descubra', 'Ingressos', 'Voos', 'Hotel', 'Local'],
        ariaD: '{n} dias para o show', ariaDHome: '{n} dias para o próximo show', ariaLive: 'Hoje é o show',
        cta: { ticket: 'Ingressos', flight: 'Ver voos', stay: 'Ver hotéis', local: 'Guia local', course: 'Ver roteiro', book: 'Reservar', localInfo: 'Info local', next: 'Próximo show', liveGuide: 'Guia local' } },
      ar: { nav: 'تقدم الرحلة', dots: 'الرحلة: 5 خطوات',
        steps: ['اكتشف', 'تذاكر', 'طيران', 'إقامة', 'محلي'],
        ariaD: '{n} يومًا حتى الحفل', ariaDHome: '{n} يومًا حتى أقرب حفل', ariaLive: 'الحفل اليوم',
        cta: { ticket: 'احجز التذاكر', flight: 'عرض الطيران', stay: 'عرض الإقامة', local: 'دليل محلي', course: 'عرض المسار', book: 'احجز الآن', localInfo: 'معلومات محلية', next: 'أقرب حفلة', liveGuide: 'دليل محلي' } },
      vi: { nav: 'Tiến trình hành trình', dots: 'Hành trình 5 bước',
        steps: ['Khám phá', 'Vé', 'Vé bay', 'Chỗ ở', 'Tại chỗ'],
        ariaD: 'Còn {n} ngày đến show', ariaDHome: 'Còn {n} ngày đến show gần nhất', ariaLive: 'Show hôm nay',
        cta: { ticket: 'Săn vé', flight: 'Xem vé bay', stay: 'Xem chỗ ở', local: 'Tại chỗ', course: 'Xem lịch trình', book: 'Đặt ngay', localInfo: 'Tại chỗ', next: 'Show sắp tới', liveGuide: 'Tại chỗ' } }
    };
    var L = L10N[LANG] || L10N.ko;
    /* R2 W4 노트: P0-2 nav('현재 단계' 계열)·NEW-3 navHome('공연 일정' 계열)·P1-2
       cta.today('오늘 공연' 계열)는 ko/en만 직접 반영 — 나머지 9 locale 문자열은
       i18n 캐시 경유 W4 재생성 대상.
       today 부재 locale은 ctaFor()에서 cta.next 폴백 (undefined 라벨 봉쇄),
       navHome 부재 locale은 aria-label에서 nav 폴백. */

    /* ── 페이지 유형별 여정 구성 (zones 문서 순서 · cta = 현 단계의 다음 행동) ── */
    var TYPES = {
      rich: {
        date: '.hero-dd-num[data-date]',
        zones: [[3, '.steps5'], [5, '#sec-arrive'], [4, '#sec-stays'], [2, '#sec-ticketing']],
        cta: { 1: ['ticket', '#sec-ticketing'], 2: ['flight', '.steps5'], 3: ['stay', '#sec-stays'], 4: ['local', '#sec-arrive'], 5: ['course', '#sec-c4'], live: ['liveGuide', '#sec-arrive'] }
      },
      event: {
        date: '.ehead-detail .dday[data-date]',
        zones: [[2, '.btns'], [5, '.linfo-box']],
        cta: { 1: ['book', '.btns'], 2: ['localInfo', '.linfo-box'], 5: ['book', '.btns'], live: ['localInfo', '.linfo-box'] }
      },
      home: { date: null, zones: [], cta: { 1: ['next', null], live: ['today', null] } } /* P1-2: 당일 CTA '오늘 공연' */
    };
    var T = TYPES[TYPE];
    if (!T) return;

    /* ── 날짜 게이트 (기존 페이지 D-DAY 데이터 재사용 · 부재/과거 = 무렌더) ── */
    var TODAY = new Date(); TODAY.setHours(0, 0, 0, 0);
    function parseD(s) {
      var p = (s || '').split('-');
      if (p.length !== 3) return null;
      var d = new Date(+p[0], +p[1] - 1, +p[2]); d.setHours(0, 0, 0, 0);
      return d;
    }
    function diffD(dt) { return Math.round((dt - TODAY) / 86400000); }
    var dnum = null, homeHref = null;
    if (TYPE === 'home') {
      var best = null, bestEl = null, els = document.querySelectorAll('.dday[data-date]');
      for (var i = 0; i < els.length; i++) {
        var dt = parseD(els[i].getAttribute('data-date'));
        if (!dt) continue;
        var k = diffD(dt);
        if (k >= 0 && (best === null || k < best)) { best = k; bestEl = els[i]; }
      }
      if (best === null) return; /* 미래 이벤트 0건 → 바 무렌더 */
      dnum = best;
      var card = bestEl.closest('a');
      homeHref = card ? card.getAttribute('href') : null;
    } else {
      var src = document.querySelector(T.date);
      if (!src) return;                       /* 날짜 데이터 부재 → 무렌더 */
      var edt = parseD(src.getAttribute('data-date'));
      if (!edt) return;
      dnum = diffD(edt);
      if (dnum < 0) return;                   /* 종료 공연(아카이브) → 무렌더 */
    }

    /* ── CSS (시안 B 기반 + 실측 적응 — 헤더 '실측 5건' 선언 참조 · #jbar 스코프 · 논리 속성 · 토큰 페어 미러링) ── */
    var css = '' +
      '#jbar{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--card);border-top:1px solid var(--line);box-shadow:0 -1px 10px rgba(0,0,0,.05);padding-bottom:env(safe-area-inset-bottom,0px);--jb-imm:#C62828}' +
      /* R2 웨일 동적 툴바 가림 보정 — CSS dvh 주 해법 (R1 JS transform은 dvh 미지원 폴백으로 강등).
         웨일류: fixed 앵커가 layout viewport(큰 쪽) 고정인데 JS 측정치(clientHeight)는 vv와
         동조 감소 → JS로는 차이 측정 불가(R1 무효 확정). dvh/lvh는 CSS 엔진 내부 진실값이라
         측정치 거짓말과 무관. 분기 시뮬:
           툴바 숨김·데스크톱:        dvh=lvh        → bottom:0   (무변화)
           웨일 추정(하단 툴바 표시): dvh<lvh        → bottom:+툴바높이 → 바 가시 하단으로 상승
           모바일 크롬(URL바 표시):   dvh<lvh인데 네이티브 추적도 작동 → 부유 갭 → 하단 JS 갭 가드가
                                      실측(rect.bottom vs vv 하단) 후 bottom:0 중화
           dvh 미지원 구형:           @supports 블록 미적용 → JS 폴백(R1 transform) 경로 */
      '@supports (height:1dvh){#jbar{bottom:calc(100lvh - 100dvh)}}' +
      '@media(prefers-color-scheme:dark){#jbar{--jb-imm:#FF6B6B}}' +
      '#jbar .row{max-width:760px;margin:0 auto;height:44px;display:flex;align-items:center;gap:9px;padding:0 12px;transition:height .18s ease-out}' +
      '#jbar .dnum{font-size:15px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.2px;white-space:nowrap;display:flex;align-items:center;gap:5px;transition:font-size .18s ease-out;color:var(--ink);direction:ltr}' +
      '#jbar .dnum.imm{color:var(--jb-imm)}' +
      '#jbar .dnum .pulse{width:6px;height:6px;border-radius:50%;background:var(--jb-imm);animation:jbpl 1.2s ease-in-out infinite}' +
      '@keyframes jbpl{0%,100%{opacity:1}50%{opacity:.25}}' +
      '#jbar .stage{display:flex;align-items:center;gap:0;min-width:0}' +
      '#jbar .dots{display:flex;align-items:center;list-style:none;margin:0;padding:0}' +
      '#jbar .dots li{position:relative;width:6px;height:6px;border-radius:50%;background:#b9b7ac;background:color-mix(in srgb,var(--muted) 40%,transparent);transition:all .18s ease-out}' +
      /* P1-3: color-mix 미지원 구형 폴백 light/dark 분리 — 라이트 폴백 #b9b7ac가 다크에
         그대로 노출되면 muted(#B3B0A5)와 Δ(6,7,7)/채널로 사실상 동일 톤이던 결함.
         다크 실측 폴백 #5b5950 = muted 40% on card(#211f18) 합성값 (비적색 — 빨강 d<=7 전유 무관).
         base 룰 뒤 선언 = 다크에서 cascade 우선, color-mix 지원 브라우저는 후속 선언이 재적용. */
      '@media(prefers-color-scheme:dark){#jbar .dots li{background:#5b5950;background:color-mix(in srgb,var(--muted) 40%,transparent)}}' +
      '#jbar .dots li+li{margin-inline-start:10px}' +
      '#jbar .dots li+li::before{content:"";position:absolute;inset-inline-end:100%;top:50%;width:10px;height:1.5px;margin-top:-.75px;background:var(--line)}' +
      '#jbar .dots li.cur{width:8px;height:8px;background:#E84A7F;box-shadow:0 0 0 3px rgba(232,74,127,.26);box-shadow:0 0 0 3px color-mix(in srgb,#E84A7F 26%,transparent)}' +
      '#jbar .lit{display:flex;align-items:center;gap:4px;margin-inline-start:8px;font-size:12px;font-weight:700;white-space:nowrap;animation:jbin .25s ease-out;color:var(--ink)}' +
      '#jbar .lit .n{color:var(--muted);font-weight:600;font-size:11px}' +
      /* 점등 슬라이드 — opacity 페이드 제외 (cr_audit가 opacity 합성 실측: 일시 페이드도 CR 위반 판정) */
      '@keyframes jbin{from{transform:translateX(-3px)}to{transform:none}}' +
      '@media(prefers-reduced-motion:reduce){#jbar .dnum .pulse{animation:none}#jbar .lit{animation:none}}' +
      '#jbar .mininfo{display:none;font-size:12.5px;font-weight:700;white-space:nowrap;color:var(--ink)}' +
      '#jbar .mininfo .n{color:var(--muted);font-weight:600}' +
      '#jbar .sp{flex:1}' +
      '#jbar .bb{height:20px;width:auto;display:block;color:var(--ink);flex:none}' +
      '#jbar .cta{position:relative;flex:none;display:flex;align-items:center;height:32px;padding:0 14px;border-radius:16px;background:#E84A7F;color:#1a1a18;font-size:13px;font-weight:700;text-decoration:none;white-space:nowrap;transition:opacity .18s ease-out}' +
      '#jbar .cta::after{content:"";position:absolute;inset:-6px -4px}' +
      '#jbar.mini .row{height:28px}' +
      '#jbar.mini .dnum{font-size:13px}' +
      '#jbar.mini .stage{display:none}' +
      '#jbar.mini .mininfo{display:block}' +
      '#jbar.mini .cta{opacity:0;width:0;padding:0;overflow:hidden;pointer-events:none}' +
      '#jbar.mini{cursor:pointer}' +
      /* P1-4(iii): 미니 탭 타깃 — 시각 28px 유지, ::before 상향 16px 확장 = 히트 28+16=44px (HIG 하한) */
      '#jbar.mini::before{content:"";position:absolute;top:-16px;left:0;right:0;height:16px}' +
      /* P1-4(i): 바 총높이 = row 44 + border-top 1 = 45px — padding 44가 본문 1px 점유하던 결함 해소 */
      'body.has-jbar{padding-bottom:calc(45px + env(safe-area-inset-bottom,0px))}' +
      /* P1-4(ii): toast 바닥 = 활성 바닥 표면 동적 참조 — 기본 jbar 45px, affbar 표시 중엔
         P1-1 setYield가 --bb-toast-b=(affbar 실측 높이+8)px 설정 (50px affbar 위 2px 붕괴 해소) */
      'body.has-jbar .share-toast{bottom:var(--bb-toast-b,calc(45px + env(safe-area-inset-bottom,0px) + 8px))}';
    var st = document.createElement('style');
    st.id = 'jbar-css';
    st.textContent = css;
    document.head.appendChild(st);

    /* ── 바 DOM (시안 B 마크업 기반 · bb 글리프 verbatim) ── */
    /* 제거-1: 홈(zones 0건) = 점 5개·점등 라벨 무렌더 — 스크롤과 무관하게 "인지 1/5"
       고정인 지시기는 진행 정보가 아니라 장식. 홈 바 = D-num + CTA만. */
    var HAS_STAGE = T.zones.length > 0;
    var nav = document.createElement('nav');
    nav.id = 'jbar';
    /* NEW-3: 홈 = stage 무렌더(HAS_STAGE=false)인데 '현재 단계' 명명은 자기모순 —
       홈 바 실내용(D-num + CTA)에 정직한 명칭으로 분기. navHome 미보유 locale은 nav 폴백. */
    nav.setAttribute('aria-label', HAS_STAGE ? L.nav : (L.navHome || L.nav));
    nav.innerHTML =
      '<div class="row">' +
      '<span class="dnum" id="jbDnum"></span>' +
      (HAS_STAGE ?
        '<span class="stage"><ol class="dots" id="jbDots" aria-label="' + L.dots + '"></ol><span class="lit" id="jbLit"></span></span>' +
        '<span class="mininfo" id="jbMini"></span>' : '') +
      '<span class="sp"></span>' +
      '<svg class="bb" viewBox="-10 -10 236 165" role="img" aria-label="ByBias">' +
      '<path fill="none" stroke="currentColor" stroke-width="28" stroke-linecap="round" stroke-linejoin="round" d="M14 14L14 131M86 95A36 36 0 1 1 14 95A36 36 0 1 1 86 95"/>' +
      '<path fill="none" stroke="#E84A7F" stroke-width="28" stroke-linecap="round" stroke-linejoin="round" d="M130 14L130 131M202 95A36 36 0 1 1 130 95A36 36 0 1 1 202 95"/>' +
      '</svg>' +
      '<a class="cta" id="jbCta" href="#"></a>' +
      '</div>';
    document.body.appendChild(nav);
    document.body.classList.add('has-jbar');

    /* ── 스크롤 zone 해석 (문서 순서 · 부재 selector 자연 skip — 가짜 점등 금지) ── */
    var zones = [];
    for (var z = 0; z < T.zones.length; z++) {
      var zel = document.querySelector(T.zones[z][1]);
      if (zel) zones.push({ s: T.zones[z][0], el: zel });
    }
    function curStep() {
      var lim = innerHeight * 0.4, s = 1;
      for (var i = 0; i < zones.length; i++) {
        if (zones[i].el.getBoundingClientRect().top <= lim) s = zones[i].s;
      }
      return s;
    }

    /* ── 렌더 (시안 render() 기반 + R2 fix — 빨강 d<=7 전유 게이트 포함) ── */
    var elD = document.getElementById('jbDnum'), elDots = document.getElementById('jbDots'),
      elLit = document.getElementById('jbLit'), elMini = document.getElementById('jbMini'),
      elCta = document.getElementById('jbCta');
    var S = { step: 1, mini: false };
    function ctaFor() {
      var cc = (dnum === 0 && T.cta.live) ? T.cta.live : (T.cta[S.step] || T.cta[1]);
      if (!cc) return null;
      var lbl = L.cta[cc[0]] || L.cta.next; /* P1-2: today 미보유 locale 폴백 (W4 재생성 전) */
      if (TYPE === 'home') return homeHref ? { label: lbl, href: homeHref, el: null } : null;
      var tel = document.querySelector(cc[1]);
      if (!tel && T.cta[1]) { cc = T.cta[1]; tel = document.querySelector(cc[1]); lbl = L.cta[cc[0]] || L.cta.next; }
      return tel ? { label: lbl, href: '#', el: tel } : null;
    }
    function render() {
      var live = dnum === 0, imm = dnum <= 7; /* 빨강 = 임박 전유 JS 게이트 */
      elD.className = 'dnum' + (imm ? ' imm' : '');
      /* P1-2: 당일 어휘 = D-DAY 단일 통일 — 홈 카드 dlabel()·.dday 렌더와 정합 (LIVE 이중 어휘 폐기) */
      elD.innerHTML = live ? '<span class="pulse"></span>D-DAY' : 'D-' + dnum;
      elD.setAttribute('aria-label', live ? L.ariaLive :
        (TYPE === 'home' ? L.ariaDHome : L.ariaD).replace('{n}', dnum));
      if (HAS_STAGE) { /* 제거-1: 홈 = stage DOM 자체가 없음 */
        var h = '';
        for (var i = 1; i <= 5; i++) {
          /* P0-2: 현 단계 단일 점등 — done 누적 폐기. zones는 문서 순서(리치 3→5→4→2)로
             단계 번호와 독립이라 누적 표시가 역행(점등 후퇴) 시각을 만들었음. 스테이지
             라이트 본질 = 지금 서 있는 무대만 켠다. */
          var c = i === S.step ? 'cur' : '';
          h += '<li class="' + c + '"' + (i === S.step ? ' aria-current="step"' : '') + ' title="' + L.steps[i - 1] + '"></li>';
        }
        elDots.innerHTML = h;
        elLit.innerHTML = L.steps[S.step - 1] + ' <span class="n">' + S.step + '/5</span>';
        elMini.innerHTML = '<span class="n">' + S.step + '/5</span> ' + L.steps[S.step - 1];
      }
      var cc = ctaFor();
      if (cc) { elCta.style.display = ''; elCta.textContent = cc.label; elCta.setAttribute('href', cc.href); }
      else { elCta.style.display = 'none'; }
      nav.classList.toggle('mini', S.mini);
    }

    /* ── 스크롤: 단계 점등 연동 + 44↔28 축소 (시안 동작 + P1-1 yield 가드, rAF 스로틀) ── */
    var ly = scrollY, tick = false;
    function onScroll() {
      tick = false;
      if (yielding) return; /* P1-1: affbar 양보 중 = 스크롤 연산 중지 */
      var dy = scrollY - ly; ly = scrollY;
      var ns = curStep(), ch = ns !== S.step;
      if (dy > 6 && scrollY > 40 && !S.mini) { S.mini = true; ch = true; }
      else if (dy < -6 && S.mini) { S.mini = false; ch = true; }
      if (ch) { S.step = ns; render(); }
    }
    addEventListener('scroll', function () {
      if (!tick) { tick = true; requestAnimationFrame(onScroll); }
    }, { passive: true });
    nav.addEventListener('click', function () { /* 미니 바 전체 탭 = 확장 (+16px 히트 확장 CSS = 44px, P1-4 iii) */
      if (nav.classList.contains('mini')) { S.mini = false; render(); }
    });
    elCta.addEventListener('click', function (e) {
      if (TYPE === 'home') return; /* 홈 = 임박 공연 페이지로 실제 이동 */
      e.preventDefault();
      var cc = ctaFor();
      if (cc && cc.el) cc.el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    /* ── P1-1: affbar(z-60, 이벤트 페이지 inline 주입) 명시 yield ──
       기존엔 z 40<60 우연한 점거에 의존 — 이제 의도된 양보를 코드로 선언:
       .affbar.show 감지 시 (a) 바 visibility 숨김 (b) 스크롤 연산 중지(onScroll 가드)
       (c) toast 바닥 기준면을 affbar 실측 높이로 전환(--bb-toast-b, P1-4 ii).
       affbar 닫힘(.affbar-x → .show 제거 + body inline padding 해제) 시 즉시 복귀 + 단계 재동기.
       affbar 없는 페이지(홈·리치)는 전 로직 자연 무동작. */
    var yielding = false;
    function affEl() {
      var a = document.querySelector('.affbar');
      return (a && a.classList.contains('show')) ? a : null;
    }
    function setYield(a) {
      var on = !!a;
      if (yielding === on) return;
      yielding = on;
      nav.style.visibility = on ? 'hidden' : ''; /* 명시 전환 (a11y 트리에서도 제외) */
      if (on) {
        document.body.style.setProperty('--bb-toast-b', Math.round(a.getBoundingClientRect().height + 8) + 'px');
      } else {
        document.body.style.removeProperty('--bb-toast-b');
        ly = scrollY; S.step = curStep(); render(); /* 복귀 즉시 재동기 (중지 구간 보상) */
      }
    }
    if (window.MutationObserver) {
      new MutationObserver(function () { setYield(affEl()); })
        .observe(document.body, { subtree: true, attributes: true, attributeFilter: ['class'] });
    }
    S.step = curStep();
    render();
    setYield(affEl());

    /* ── 웨일 동적 툴바 가림 보정 R2 (CSS dvh 주 해법 — 상단 css 문자열 @supports 블록) ──
       R1(JS visualViewport transform) 실기기 무효 확정 — 웨일에서 clientHeight가 vv와
       동조 감소해 보정값 0인데 fixed 앵커는 layout viewport(큰 쪽) 고정 → JS 측정으로는
       차이 자체가 안 보임. 주 해법을 CSS dvh로 전환 (엔진 내부 진실값 — JS 측정치 무관).

       이중 보정 차단 증명 (벡터 0):
         DVH_OK = CSS.supports('height','1dvh') — @supports (height:1dvh)와 동일 엔진 판정.
         · DVH_OK=true  → CSS calc 활성 + JS transform 분기 진입 자체 차단 (아래 if/else 상호배타)
         · DVH_OK=false → @supports 블록 CSS 미적용 + JS R1 폴백만 동작
         (dvh 지원 엔진(2022+)은 전부 CSS.supports 보유 — "JS API 부재 + @supports dvh 지원"
          조합은 존재 불가 → 두 경로 동시 활성 불가능.)

       DVH_OK 경로의 갭 가드 (네이티브 추적 브라우저 부유 중화 — 보정 추가 아님, 축소 단방향):
         모바일 크롬류는 fixed 앵커가 툴바를 네이티브 추적 + dvh도 동조 → CSS calc와 이중
         상승 = 바가 가시 하단 위로 부유. 실측 rect.bottom < (vv.offsetTop+vv.height)−1 이면
         inline bottom:0 으로 CSS calc 중화. 반대 방향(잔존 가림) 추가 보정은 하지 않음 —
         R1에서 vv 측정치 거짓말 확인된 만큼 측정 기반 상향 보정은 재도입 금지.
       분기 시뮬 (jsdom 불가 — 정적 검증, lv=800/dv=744/툴바 56 가정):
         데스크톱·툴바 숨김: calc=0, rect.bottom=744=vv하단 → gap 0 → 무동작
         웨일(앵커 800 고정): calc=56 → rect.bottom=800−56=744 = vv하단 744 → gap 0 → CSS 유지(가림 해소)
         모바일 크롬(앵커 744 추적): calc=56 → rect.bottom=744−56=688 < 744 → gap +56 → bottom:0 중화
         키보드(innerH−vv.h>150): 상태 변경 없이 return (R1 가드 계승)
         dvh 미지원: else 분기 = R1 transform 폴백 원형 그대로 (크롬0/웨일−56/키보드 가드)
       toast 기준면(--bb-toast-b)·body padding 무수정. fav-filter 독립 fixed 레이어 — 영향 0. */
    var DVH_OK = !!(window.CSS && CSS.supports && CSS.supports('height', '1dvh'));
    if (window.visualViewport) {
      var vv = window.visualViewport, vvTick = false, vvFix;
      if (DVH_OK) {
        vvFix = function () { /* 갭 가드 — CSS calc 부유 시에만 중화 */
          vvTick = false;
          if (innerHeight - vv.height > 150) return; /* 가상 키보드 가드 */
          nav.style.bottom = ''; /* CSS calc 기준 실측 (rAF 내 — 중간 페인트 없음) */
          var gap = (vv.offsetTop + vv.height) - nav.getBoundingClientRect().bottom;
          if (gap > 1) nav.style.bottom = '0px';
        };
      } else {
        vvFix = function () { /* R1 transform — dvh 미지원 폴백 강등 (수식 원형 유지) */
          vvTick = false;
          if (innerHeight - vv.height > 150) { nav.style.transform = ''; return; } /* 가상 키보드 가드 */
          var d = (vv.offsetTop + vv.height) - document.documentElement.clientHeight;
          nav.style.transform = d ? 'translateY(' + d + 'px)' : '';
        };
      }
      var vvQ = function () { /* rAF 스로틀 — 기존 onScroll 패턴 동형 */
        if (!vvTick) { vvTick = true; requestAnimationFrame(vvFix); }
      };
      vv.addEventListener('resize', vvQ);
      vv.addEventListener('scroll', vvQ);
      vvFix();
    }

    /* ── 계측 모드 (?jbdebug=1) — 다음 라운드 가림 시 대표가 숫자만 읽으면 확정 진단 ──
       평시(파라미터 없음) = 이 블록 전체 미진입: DOM·스타일·타이머·리스너 0 (완전 무동작·무렌더).
       항목: vv.h / vv.top / innerH / clientH / dvh실측·lvh실측(CSS 엔진 화면높이 probe) /
             적용보정값(fixB=computed bottom, fixT=inline transform). 진단표:
         dvh<lvh + fixB>0 + 가림 지속  → 웨일 dvh도 거짓 (R3: 다른 신호원 필요)
         dvh=lvh + 가림                → 웨일 dvh 미동조 (CSS 해법 자체 무효 확정)
         fixB=0 + 가림                 → 갭 가드 오발동 또는 @supports 미적용 */
    if (/[?&]jbdebug=1(&|$)/.test(location.search)) {
      var dbgP = function (h) { /* CSS 단위 실측 probe — 미지원 단위는 style 무시 → 0 표기 */
        var p = document.createElement('div');
        p.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;visibility:hidden;pointer-events:none';
        p.style.height = h;
        document.body.appendChild(p);
        return p;
      };
      var pDvh = dbgP('100dvh'), pLvh = dbgP('100lvh');
      var dbg = document.createElement('div');
      dbg.style.cssText = 'position:absolute;bottom:100%;left:0;right:0;z-index:1;font:10px/1.5 ui-monospace,Menlo,monospace;background:rgba(0,0,0,.78);color:#7CFC00;padding:2px 8px;white-space:nowrap;overflow:hidden;pointer-events:none;direction:ltr;text-align:left';
      nav.appendChild(dbg); /* #jbar(fixed) 기준 absolute = 바 바로 위 고정 */
      var dbgUpd = function () {
        var v = window.visualViewport;
        dbg.textContent =
          'vv.h:' + (v ? Math.round(v.height) : '-') +
          ' vv.top:' + (v ? Math.round(v.offsetTop) : '-') +
          ' inH:' + innerHeight +
          ' clH:' + document.documentElement.clientHeight +
          ' dvh:' + pDvh.offsetHeight +
          ' lvh:' + pLvh.offsetHeight +
          ' fixB:' + getComputedStyle(nav).bottom +
          ' fixT:' + (nav.style.transform || '0');
      };
      dbgUpd();
      setInterval(dbgUpd, 300); /* 계측 모드 한정 — vv 이벤트 미발화 브라우저(웨일 의심)도 포착 */
    }
  } catch (e) { /* 바 실패 = 페이지 본문 무영향 (콘솔 0) */ }
})();
