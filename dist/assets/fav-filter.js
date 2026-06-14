/* ═══════════════════════════════════════════════════════════════
   ByVias 최애 필터 1단계 — A안 "독립 칩 행 + 바텀 시트" (Q-20260607-130)
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
   localStorage "byvias_fav" v1 (SPEC §5 verbatim):
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
    var KEY = 'byvias_fav';

    /* ── 로케일 문자열 (SPEC §8 키, 11 locale — jbar.js L10N 11언어 선례 동형) ──
       P0-2: index 11언어 wiring 선반영에 맞춰 9 locale 직접 추가. ko/en = 정본,
       나머지 9 locale(_w4_review: true 마커) = 표준 UI 어휘 + 팬덤 호칭(推し·本命·
       bias·เมน) — W4 재생성 시 i18n.py 캐시 경유 재검증 트리거. 미보유 locale은
       en 폴백 (아티스트명·배지는 번역 파이프라인 통과 금지 — 데이터 원문 그대로,
       FLR-20260606-AGT-001). */
    var L10N = {
      ko: {
        chip: '내 최애', hint: '최애를 고르면 모든 탭에서 최애 일정만 모아 봐요',
        all: '전체', sheetTitle: '내 최애', sheetSub: '선택하면 모든 탭에서 최애 일정을 먼저 봐요',
        searchPh: '아티스트 검색', done: '완료', clearAll: '모두 해제', close: '닫기',
        upcomingN: '다가오는 일정 {n}건', showAllN: '전체 {n}개 보기', change: '최애 변경',
        emptyConcert: '최애의 다가오는 공연이 아직 없어요',
        emptyLineup: '확정 라인업에 최애가 아직 없어요 — 라인업 미확정 회차는 아래 남겨뒀어요',
        emptyUnderground: '이 탭 라인업에는 최애가 없어요',
        lineupTbd: '라인업 미확정', sportsExempt: '이 탭은 최애 필터가 적용되지 않아요',
        ariaApplied: '최애 필터 적용, {n}건 표시', ariaCleared: '전체 표시'
      },
      en: {
        chip: 'My bias', hint: 'Pick your bias to see only their schedule in every tab',
        all: 'All', sheetTitle: 'My bias', sheetSub: 'Pick artists to see their schedule first in every tab',
        searchPh: 'Search artists', done: 'Done', clearAll: 'Clear all', close: 'Close',
        upcomingN: '{n} upcoming events', showAllN: 'Show all {n}', change: 'Change bias',
        emptyConcert: 'No upcoming shows from your bias yet',
        emptyLineup: "Your bias isn't in a confirmed lineup yet — TBA shows are kept below",
        emptyUnderground: "No bias in this tab's lineups",
        lineupTbd: 'Lineup TBA', sportsExempt: "This tab isn't affected by the bias filter",
        ariaApplied: 'Bias filter on, showing {n}', ariaCleared: 'Showing all'
      },
      ja: {
        _w4_review: true,
        chip: '推し', hint: '推しを選ぶと全タブで推しの予定だけまとめて見られます',
        all: 'すべて', sheetTitle: 'マイ推し', sheetSub: '選ぶと全タブで推しの予定を先に見られます',
        searchPh: 'アーティスト検索', done: '完了', clearAll: 'すべて解除', close: '閉じる',
        upcomingN: '今後の予定{n}件', showAllN: '全{n}件を見る', change: '推しを変更',
        emptyConcert: '推しの今後の公演はまだありません',
        emptyLineup: '確定ラインナップに推しはまだいません — ラインナップ未確定の回は下に残しています',
        emptyUnderground: 'このタブのラインナップに推しはいません',
        lineupTbd: 'ラインナップ未確定', sportsExempt: 'このタブには推しフィルターは適用されません',
        ariaApplied: '推しフィルター適用、{n}件表示', ariaCleared: 'すべて表示'
      },
      'zh-cn': {
        _w4_review: true,
        chip: '我的本命', hint: '选好本命后，所有标签页只看本命的日程',
        all: '全部', sheetTitle: '我的本命', sheetSub: '选择后在所有标签页优先查看本命日程',
        searchPh: '搜索艺人', done: '完成', clearAll: '全部取消', close: '关闭',
        upcomingN: '即将到来的日程 {n} 场', showAllN: '查看全部 {n} 场', change: '更换本命',
        emptyConcert: '本命暂时没有即将到来的演出',
        emptyLineup: '确定阵容中暂时没有本命 — 阵容未定的场次保留在下方',
        emptyUnderground: '此标签页的阵容中没有本命',
        lineupTbd: '阵容待定', sportsExempt: '此标签页不受本命筛选影响',
        ariaApplied: '本命筛选已开启，显示 {n} 场', ariaCleared: '显示全部'
      },
      'zh-tw': {
        _w4_review: true,
        chip: '我的本命', hint: '選好本命後，所有分頁只看本命的行程',
        all: '全部', sheetTitle: '我的本命', sheetSub: '選擇後在所有分頁優先查看本命行程',
        searchPh: '搜尋藝人', done: '完成', clearAll: '全部取消', close: '關閉',
        upcomingN: '即將到來的行程 {n} 場', showAllN: '查看全部 {n} 場', change: '更換本命',
        emptyConcert: '本命暫時沒有即將到來的演出',
        emptyLineup: '確定陣容中暫時沒有本命 — 陣容未定的場次保留在下方',
        emptyUnderground: '此分頁的陣容中沒有本命',
        lineupTbd: '陣容待定', sportsExempt: '此分頁不受本命篩選影響',
        ariaApplied: '本命篩選已開啟，顯示 {n} 場', ariaCleared: '顯示全部'
      },
      es: {
        _w4_review: true,
        chip: 'Mi bias', hint: 'Elige a tu bias para ver solo su agenda en todas las pestañas',
        all: 'Todo', sheetTitle: 'Mi bias', sheetSub: 'Elige artistas para ver su agenda primero en todas las pestañas',
        searchPh: 'Buscar artistas', done: 'Listo', clearAll: 'Quitar todo', close: 'Cerrar',
        upcomingN: '{n} eventos próximos', showAllN: 'Ver los {n}', change: 'Cambiar bias',
        emptyConcert: 'Tu bias aún no tiene shows próximos',
        emptyLineup: 'Tu bias aún no está en un lineup confirmado — los shows por anunciar quedan abajo',
        emptyUnderground: 'No hay bias en los lineups de esta pestaña',
        lineupTbd: 'Lineup por anunciar', sportsExempt: 'El filtro de bias no afecta esta pestaña',
        ariaApplied: 'Filtro de bias activado, mostrando {n}', ariaCleared: 'Mostrando todo'
      },
      pt: {
        _w4_review: true,
        chip: 'Meu bias', hint: 'Escolha seu bias para ver só a agenda dele em todas as abas',
        all: 'Tudo', sheetTitle: 'Meu bias', sheetSub: 'Escolha artistas para ver a agenda deles primeiro em todas as abas',
        searchPh: 'Buscar artistas', done: 'Concluir', clearAll: 'Limpar tudo', close: 'Fechar',
        upcomingN: '{n} eventos em breve', showAllN: 'Ver todos os {n}', change: 'Trocar bias',
        emptyConcert: 'Seu bias ainda não tem shows em breve',
        emptyLineup: 'Seu bias ainda não está em um lineup confirmado — shows a anunciar ficam abaixo',
        emptyUnderground: 'Nenhum bias nos lineups desta aba',
        lineupTbd: 'Lineup a anunciar', sportsExempt: 'Esta aba não é afetada pelo filtro de bias',
        ariaApplied: 'Filtro de bias ativado, mostrando {n}', ariaCleared: 'Mostrando tudo'
      },
      th: {
        _w4_review: true,
        chip: 'เมนของฉัน', hint: 'เลือกเมนเพื่อดูเฉพาะตารางของเมนในทุกแท็บ',
        all: 'ทั้งหมด', sheetTitle: 'เมนของฉัน', sheetSub: 'เลือกศิลปินเพื่อดูตารางของเมนก่อนในทุกแท็บ',
        searchPh: 'ค้นหาศิลปิน', done: 'เสร็จสิ้น', clearAll: 'ล้างทั้งหมด', close: 'ปิด',
        upcomingN: 'ตารางที่กำลังมาถึง {n} รายการ', showAllN: 'ดูทั้งหมด {n} รายการ', change: 'เปลี่ยนเมน',
        emptyConcert: 'เมนยังไม่มีโชว์ที่กำลังมาถึง',
        emptyLineup: 'เมนยังไม่อยู่ในไลน์อัปที่ยืนยันแล้ว — รอบที่ยังไม่ประกาศไลน์อัปอยู่ด้านล่าง',
        emptyUnderground: 'ไม่มีเมนในไลน์อัปของแท็บนี้',
        lineupTbd: 'ไลน์อัปยังไม่ประกาศ', sportsExempt: 'แท็บนี้ไม่ใช้ฟิลเตอร์เมน',
        ariaApplied: 'เปิดฟิลเตอร์เมนแล้ว แสดง {n} รายการ', ariaCleared: 'แสดงทั้งหมด'
      },
      id: {
        _w4_review: true,
        chip: 'Bias-ku', hint: 'Pilih bias untuk melihat jadwalnya saja di semua tab',
        all: 'Semua', sheetTitle: 'Bias-ku', sheetSub: 'Pilih artis untuk melihat jadwal mereka lebih dulu di semua tab',
        searchPh: 'Cari artis', done: 'Selesai', clearAll: 'Hapus semua', close: 'Tutup',
        upcomingN: '{n} jadwal mendatang', showAllN: 'Lihat semua {n}', change: 'Ganti bias',
        emptyConcert: 'Bias-mu belum punya show mendatang',
        emptyLineup: 'Bias-mu belum ada di lineup yang dikonfirmasi — show TBA tetap di bawah',
        emptyUnderground: 'Tidak ada bias di lineup tab ini',
        lineupTbd: 'Lineup TBA', sportsExempt: 'Tab ini tidak terpengaruh filter bias',
        ariaApplied: 'Filter bias aktif, menampilkan {n}', ariaCleared: 'Menampilkan semua'
      },
      vi: {
        _w4_review: true,
        chip: 'Bias của tôi', hint: 'Chọn bias để chỉ xem lịch của bias ở mọi tab',
        all: 'Tất cả', sheetTitle: 'Bias của tôi', sheetSub: 'Chọn nghệ sĩ để xem lịch của họ trước ở mọi tab',
        searchPh: 'Tìm nghệ sĩ', done: 'Xong', clearAll: 'Bỏ chọn tất cả', close: 'Đóng',
        upcomingN: '{n} lịch sắp tới', showAllN: 'Xem tất cả {n}', change: 'Đổi bias',
        emptyConcert: 'Bias của bạn chưa có show sắp tới',
        emptyLineup: 'Bias của bạn chưa có trong lineup đã xác nhận — các show chưa công bố lineup vẫn ở bên dưới',
        emptyUnderground: 'Không có bias trong lineup của tab này',
        lineupTbd: 'Lineup chưa công bố', sportsExempt: 'Tab này không áp dụng bộ lọc bias',
        ariaApplied: 'Đã bật bộ lọc bias, hiển thị {n}', ariaCleared: 'Hiển thị tất cả'
      },
      ar: {
        _w4_review: true,
        chip: 'البياس', hint: 'اختر البياس لترى جدوله فقط في كل التبويبات',
        all: 'الكل', sheetTitle: 'البياس الخاص بي', sheetSub: 'اختر الفنانين لترى جدولهم أولًا في كل التبويبات',
        searchPh: 'ابحث عن فنان', done: 'تم', clearAll: 'إلغاء الكل', close: 'إغلاق',
        upcomingN: '{n} فعاليات قادمة', showAllN: 'عرض الكل {n}', change: 'تغيير البياس',
        emptyConcert: 'لا توجد حفلات قادمة للبياس بعد',
        emptyLineup: 'البياس ليس ضمن تشكيلة مؤكدة بعد — العروض غير المعلنة تبقى بالأسفل',
        emptyUnderground: 'لا يوجد بياس في تشكيلات هذا التبويب',
        lineupTbd: 'التشكيلة لم تُعلن', sportsExempt: 'هذا التبويب لا يتأثر بفلتر البياس',
        ariaApplied: 'فلتر البياس مفعّل، عرض {n}', ariaCleared: 'عرض الكل'
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
          /* P1-4 결합 주석: generate.py festival 배지 이모지(🎪) 텍스트 스니핑 —
             배지 텍스트 변경 시 본 함수 동반 수정 필요 (현 dist 제약상 유지).
             TODO(차기 dist 재생성): .badge-fest 류 클래스 마커 승격 → 스니핑 제거 */
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
        /* P1-1: 매칭 키 0건(.abadge[title] 부재·전손 등 keyOf()='' 일괄) =
           칩 행 자체 미생성 — 필터 ON 시 전 카드 침묵 숨김보다 기능 부재가 정직 */
        if (!AKEYS.length) return;

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
          '#favf-row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin:-6px 0 12px}' + /* R3 픽셀 P1-2: 위 18px(.hubfilter mb16+.hf-chips pb2) → 마진 상쇄 16-6=10+2=12px, 아래 12px 균일. 인접 행 무접촉 */
          '#favf-chip{display:inline-flex;align-items:center;gap:7px;min-height:44px;padding:8px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-size:13.5px;font-weight:600;color:var(--ink);font-family:inherit}' +
          '#favf-chip:hover{border-color:var(--muted)}' +
          '#favf-chip .favf-heart{width:15px;height:15px;flex:none;color:var(--rose,#E84A7F)}' + /* 핑크 = 그래픽 ≥3:1 */
          'body.favf-on #favf-chip{background:var(--rose-soft,#FCEAF1);border-color:var(--rose-line,#F6CBDC)}' + /* R3 DQA P1-3: aria-pressed 제거 → body.favf-on 동치 셀렉터 (on 토글 동일 조건) */
          '#favf-chip .favf-stack{display:inline-flex;gap:3px;margin-inline-start:3px}' +
          '#favf-chip .favf-mini{width:22px;height:22px;border-radius:7px;font-size:10.5px;font-weight:700;display:inline-flex;align-items:center;justify-content:center;overflow:hidden}' +
          '#favf-hint{font-size:12.5px;color:var(--muted)}' +
          '#favf-all{display:none;min-height:44px;padding:8px 14px;border:1px solid var(--line);border-radius:12px;background:transparent;font-size:13px;color:var(--muted);cursor:pointer;font-family:inherit}' +
          '#favf-all[aria-pressed="true"]{border-color:var(--muted);color:var(--ink)}' +
          'body.favf-sel #favf-all{display:inline-flex;align-items:center}' +
          /* 필터 ON: 숨김/디밍 — pastguard inline display:none과 독립 */
          '.favf-hide{display:none}' +
          'body.favf-on .tabs .tp-c .mdiv{display:none}' + /* 월 구분 행 = 필터 뷰에서 노이즈 */
          '.favf-tbd .ehead,.favf-tbd .badge,.favf-tbd .ghost{opacity:.45}' + /* R3 DQA P1-2: 캡션+날짜 행(.c) dim 제외 — 날짜·임박도 = cap이 대체 못 하는 판단 정보 (페스티벌 카드 유지 취지) */
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
          /* R3 P0: minmax(0,1fr) — 1fr 단독 = min-content 하한으로 장명("PARK JI HOON") 셀이 칼럼 확장 (실측 107/122/107) */
          /* R3 픽셀 P1-1: grid-auto-rows:1fr — 전 행 트랙 균등화 (105/106 1px 콘텐츠 편차 제거) */
          '#favf-list{overflow:auto;padding:10px 18px;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:1fr;gap:8px;-webkit-overflow-scrolling:touch}' +
          '@media(min-width:720px){#favf-list{grid-template-columns:repeat(4,minmax(0,1fr))}}' +
          '.favf-cell{position:relative}' +
          '.favf-cell input{position:absolute;opacity:0;inset:0;width:100%;height:100%;cursor:pointer;margin:0}' +
          '.favf-cell label{display:flex;flex-direction:column;align-items:center;gap:6px;min-height:44px;padding:12px 6px 10px;border:2px solid var(--line);border-radius:12px;cursor:pointer;text-align:center}' +
          '.favf-cell .abadge{pointer-events:none}' +
          '.favf-cell .favf-nm{font-size:12.5px;font-weight:600;line-height:1.3;word-break:keep-all}' +
          '.favf-cell .favf-n{font-size:12px;color:var(--muted)}' + /* R3 DQA P1-1: 11→12px (셀 높이 114px 여백 충분) */
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
        sheet.setAttribute('aria-labelledby', 'favf-title'); /* aria-label 미병기 — labelledby 항상 우선 */
        sheet.innerHTML = '<div class="favf-grab" aria-hidden="true"></div>' +
          '<div class="favf-head"><div><h2 id="favf-title" tabindex="-1"></h2><p class="favf-sub"></p></div>' +
          '<button id="favf-x" type="button">✕</button></div>' +
          '<input id="favf-search" type="search">' +
          '<div id="favf-list"></div>' +
          '<div id="favf-foot"><button id="favf-clear" type="button"></button><button id="favf-done" type="button"></button></div>';
        document.body.appendChild(sheet);
        sheet.querySelector('#favf-title').textContent = L.sheetTitle;
        sheet.querySelector('.favf-sub').textContent = L.sheetSub;
        sheet.querySelector('#favf-x').setAttribute('aria-label', L.close);
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

          /* 칩 — R3 DQA P1-3: aria-pressed 제거. pressed = #favf-all 전유,
             칩은 haspopup="dialog"/expanded만 (SR "토글" 오인 차단). 시각 상태 = body.favf-on CSS */
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
          var i2, it, m, nC = 0, totC = 0;
          for (i2 = 0; i2 < C.length; i2++) {
            it = C[i2];
            if (it.past) continue;
            totC++;
            if (!on) { it.hide.classList.remove('favf-hide'); it.el.classList.remove('favf-tbd'); setCap(it, false); continue; }
            if (it.fest) { /* lineup 미확정 ≠ 불일치 — 유지+dim (§3) */
              it.hide.classList.remove('favf-hide');
              it.el.classList.add('favf-tbd'); setCap(it, true);
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
            /* P1-2: (N) 괄호 앵커 — 제목 내 다른 숫자(연도 등) 오치환 방지 */
            arcSummary.textContent = on ? arcSumOrig.replace(/\(\d+\)/, '(' + nArc + ')') : arcSumOrig;
          }
          for (i2 = 0; i2 < arcSection.length; i2++) {
            arcSection[i2].style.display = (on && nArc === 0) ? 'none' : '';
          }

          /* P1-3: 결과 고지 = 활성 탭 기준 실 표시 건수 (콘서트 고정 → 탭별).
             tp-m = 전 카드 유지(dim)라 totM, tp-s = 면제 문구 그대로 고지 */
          if (announce) {
            if (!on) { live.textContent = L.ariaCleared; }
            else {
              var rM = document.getElementById('tab-m'), rU = document.getElementById('tab-u'), rS = document.getElementById('tab-s');
              if (rS && rS.checked) live.textContent = L.sportsExempt;
              else live.textContent = fmtT(L.ariaApplied, (rM && rM.checked) ? totM : (rU && rU.checked) ? nU : nC);
            }
          }
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
