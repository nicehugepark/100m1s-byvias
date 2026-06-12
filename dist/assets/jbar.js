/* ═══════════════════════════════════════════════════════════════
   ByBias 여정 상주 바 — 시안 B "스테이지 라이트" (R46 P1-5 · 2심 조니 확정 spec)
   시안 정본: journey-bar-drafts/journey-bar-B-stage-light.html (브랜딩 2026-06-12)
   마크업·토큰·JS 동작 verbatim 이식 + production 적응 4종:
     (1) #jbar 스코프 클래스 (847페이지 이종 CSS 충돌 봉쇄)
     (2) 물리 margin → 논리 속성 (ar RTL 정합)
     (3) 페이지 토큰(--card/--ink/--line/--muted) 상속 — 시안과 동일 값 (C3 미러링)
     (4) 단일 모듈 SSOT — 페이지별 복제 금지 (fix 누락 재발 차단)
   브랜드 규율 (logo-drafts/SYSTEM.md):
     - bb 글리프 verbatim·컨테이너 없음 (§2) · 렌더 20px = 하한 준수 · 워드마크 금지
     - C2 핑크 전유 #E84A7F: CTA bg + 현재 점 + 점등 라벨은 잉크 (핑크 텍스트 금지)
   WCAG AA 실측 (시안 헤더 동일 — 사이트 토큰 = 시안 토큰):
     CTA #1a1a18 on #E84A7F 4.75 · 임박 레드 L#C62828 5.62 / D#FF6B6B 5.94
     핑크점 L3.67/D4.49(≥3 그래픽) · 라벨 잉크 L17.43/D13.58 · muted 7.49/7.59
   빨강 = 임박 전유: JS 게이트 d<=7 (D-8+ 빨강 0건)
   z-40 (< toast 50 < affbar 60) · 날짜 게이트: 이벤트 날짜 부재/과거 = 바 무렌더 (가짜 값 금지)
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
      ko: { nav: '여정 진행', dots: '여정 5단계',
        steps: ['인지', '티켓', '항공', '숙소', '현지'],
        ariaD: '공연까지 {n}일', ariaDHome: '다음 공연까지 {n}일', ariaLive: '오늘 공연',
        cta: { ticket: '티켓 잡기', flight: '항공 보기', stay: '숙소 보기', local: '현지 보기', course: '코스 보기', book: '예매 보기', localInfo: '현지 정보', next: '임박 공연', liveGuide: '현지 가이드' } },
      en: { nav: 'Journey progress', dots: 'Journey: 5 steps',
        steps: ['Discover', 'Tickets', 'Flights', 'Stay', 'Local'],
        ariaD: '{n} days to the show', ariaDHome: '{n} days to the next show', ariaLive: 'Show day',
        cta: { ticket: 'Get tickets', flight: 'See flights', stay: 'See stays', local: 'Local guide', course: 'See course', book: 'Book now', localInfo: 'Local info', next: 'Next show', liveGuide: 'Local guide' } },
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
      home: { date: null, zones: [], cta: { 1: ['next', null], live: ['next', null] } }
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

    /* ── CSS (시안 B verbatim · #jbar 스코프 · 논리 속성 · 토큰 페어 미러링) ── */
    var css = '' +
      '#jbar{position:fixed;left:0;right:0;bottom:0;z-index:40;background:var(--card);border-top:1px solid var(--line);box-shadow:0 -1px 10px rgba(0,0,0,.05);padding-bottom:env(safe-area-inset-bottom,0px);--jb-imm:#C62828}' +
      '@media(prefers-color-scheme:dark){#jbar{--jb-imm:#FF6B6B}}' +
      '#jbar .row{max-width:760px;margin:0 auto;height:44px;display:flex;align-items:center;gap:9px;padding:0 12px;transition:height .18s ease-out}' +
      '#jbar .dnum{font-size:15px;font-weight:800;font-variant-numeric:tabular-nums;letter-spacing:-.2px;white-space:nowrap;display:flex;align-items:center;gap:5px;transition:font-size .18s ease-out;color:var(--ink);direction:ltr}' +
      '#jbar .dnum.imm{color:var(--jb-imm)}' +
      '#jbar .dnum .pulse{width:6px;height:6px;border-radius:50%;background:var(--jb-imm);animation:jbpl 1.2s ease-in-out infinite}' +
      '@keyframes jbpl{0%,100%{opacity:1}50%{opacity:.25}}' +
      '#jbar .stage{display:flex;align-items:center;gap:0;min-width:0}' +
      '#jbar .dots{display:flex;align-items:center;list-style:none;margin:0;padding:0}' +
      '#jbar .dots li{position:relative;width:6px;height:6px;border-radius:50%;background:#b9b7ac;background:color-mix(in srgb,var(--muted) 40%,transparent);transition:all .18s ease-out}' +
      '#jbar .dots li+li{margin-inline-start:10px}' +
      '#jbar .dots li+li::before{content:"";position:absolute;inset-inline-end:100%;top:50%;width:10px;height:1.5px;margin-top:-.75px;background:var(--line)}' +
      '#jbar .dots li.done{background:var(--muted)}' +
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
      '#jbar.mini::before{content:"";position:absolute;top:-8px;left:0;right:0;height:8px}' +
      'body.has-jbar{padding-bottom:calc(44px + env(safe-area-inset-bottom,0px))}' +
      'body.has-jbar .share-toast{bottom:calc(44px + env(safe-area-inset-bottom,0px) + 8px)}';
    var st = document.createElement('style');
    st.id = 'jbar-css';
    st.textContent = css;
    document.head.appendChild(st);

    /* ── 바 DOM (시안 B 마크업 verbatim · bb 글리프 verbatim) ── */
    var nav = document.createElement('nav');
    nav.id = 'jbar';
    nav.setAttribute('aria-label', L.nav);
    nav.innerHTML =
      '<div class="row">' +
      '<span class="dnum" id="jbDnum"></span>' +
      '<span class="stage"><ol class="dots" id="jbDots" aria-label="' + L.dots + '"></ol><span class="lit" id="jbLit"></span></span>' +
      '<span class="mininfo" id="jbMini"></span>' +
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

    /* ── 렌더 (시안 render() 동작 verbatim — 빨강 d<=7 전유 게이트 포함) ── */
    var elD = document.getElementById('jbDnum'), elDots = document.getElementById('jbDots'),
      elLit = document.getElementById('jbLit'), elMini = document.getElementById('jbMini'),
      elCta = document.getElementById('jbCta');
    var S = { step: 1, mini: false };
    function ctaFor() {
      var cc = (dnum === 0 && T.cta.live) ? T.cta.live : (T.cta[S.step] || T.cta[1]);
      if (!cc) return null;
      if (TYPE === 'home') return homeHref ? { label: L.cta[cc[0]], href: homeHref, el: null } : null;
      var tel = document.querySelector(cc[1]);
      if (!tel && T.cta[1]) { cc = T.cta[1]; tel = document.querySelector(cc[1]); }
      return tel ? { label: L.cta[cc[0]], href: '#', el: tel } : null;
    }
    function render() {
      var live = dnum === 0, imm = dnum <= 7; /* 빨강 = 임박 전유 JS 게이트 */
      elD.className = 'dnum' + (imm ? ' imm' : '');
      elD.innerHTML = live ? '<span class="pulse"></span>LIVE' : 'D-' + dnum;
      elD.setAttribute('aria-label', live ? L.ariaLive :
        (TYPE === 'home' ? L.ariaDHome : L.ariaD).replace('{n}', dnum));
      var h = '';
      for (var i = 1; i <= 5; i++) {
        var c = i < S.step ? 'done' : i === S.step ? 'cur' : '';
        h += '<li class="' + c + '"' + (i === S.step ? ' aria-current="step"' : '') + ' title="' + L.steps[i - 1] + '"></li>';
      }
      elDots.innerHTML = h;
      elLit.innerHTML = L.steps[S.step - 1] + ' <span class="n">' + S.step + '/5</span>';
      elMini.innerHTML = '<span class="n">' + S.step + '/5</span> ' + L.steps[S.step - 1];
      var cc = ctaFor();
      if (cc) { elCta.style.display = ''; elCta.textContent = cc.label; elCta.setAttribute('href', cc.href); }
      else { elCta.style.display = 'none'; }
      nav.classList.toggle('mini', S.mini);
    }

    /* ── 스크롤: 단계 점등 연동 + 44↔28 축소 (시안 동작 verbatim, rAF 스로틀) ── */
    var ly = scrollY, tick = false;
    function onScroll() {
      tick = false;
      var dy = scrollY - ly; ly = scrollY;
      var ns = curStep(), ch = ns !== S.step;
      if (dy > 6 && scrollY > 40 && !S.mini) { S.mini = true; ch = true; }
      else if (dy < -6 && S.mini) { S.mini = false; ch = true; }
      if (ch) { S.step = ns; render(); }
    }
    addEventListener('scroll', function () {
      if (!tick) { tick = true; requestAnimationFrame(onScroll); }
    }, { passive: true });
    nav.addEventListener('click', function () { /* 미니 바 전체 탭 = 확장 (+8px 히트 보정 CSS) */
      if (nav.classList.contains('mini')) { S.mini = false; render(); }
    });
    elCta.addEventListener('click', function (e) {
      if (TYPE === 'home') return; /* 홈 = 임박 공연 페이지로 실제 이동 */
      e.preventDefault();
      var cc = ctaFor();
      if (cc && cc.el) cc.el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
    S.step = curStep();
    render();
  } catch (e) { /* 바 실패 = 페이지 본문 무영향 (콘솔 0) */ }
})();
