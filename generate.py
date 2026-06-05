#!/usr/bin/env python3
"""
ByBias — 정적 사이트 생성기 (린 MVP)
events.json → dist/index.html + dist/<slug>.html
어필리에이트 링크는 PLACEHOLDER. 보스 가입 후 events.json의 affiliate 값만 교체하면 전 페이지 일괄 반영.
실행: python3 generate.py
"""

import calendar
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

TODAY = date.today()


def event_end_date(date_str):
    """공연일 파싱. 부분 날짜(YYYY / YYYY-MM)는 '아직 안 지남' 쪽으로 보수 판정 위해
    해당 기간의 마지막 날(월말/연말)을 반환한다. 파싱 실패 시 None(=미래 취급)."""
    parts = str(date_str).split("-")
    try:
        y = int(parts[0])
        if len(parts) == 1:  # YYYY → 그 해 12-31
            return date(y, 12, 31)
        m = int(parts[1])
        if len(parts) == 2:  # YYYY-MM → 그 달 말일
            return date(y, m, calendar.monthrange(y, m)[1])
        return date(y, m, int(parts[2]))  # YYYY-MM-DD
    except (ValueError, IndexError):
        return None


def is_past(date_str):
    """공연 종료(월말/연말 보수 기준)가 오늘보다 이전이면 True."""
    end = event_end_date(date_str)
    return end is not None and end < TODAY


def lead_type_of(e):
    """명시 lead_type 우선. 없으면 공연까지 남은 일수로 추정.
    ≤30일=A(발표 골든창), >120일=B(초장기 선점), 그 사이=A 톤이되 임박 경고는 데이터 부재 시 미추정."""
    if e.get("lead_type"):
        return e["lead_type"]
    end = event_end_date(e["date"])
    if end is None:
        return "B"
    days = (end - TODAY).days
    if days <= 30:
        return "A"
    return "B"


def has_signal(v):
    """정량 신호가 실제로 존재하는지. null·빈값·'데이터 없음' 표기는 미표시 처리(placeholder 채움 금지)."""
    if not v:
        return False
    return "데이터 없음" not in str(v)


data = json.loads((ROOT / "events.json").read_text(encoding="utf-8"))
SITE = data["site"]
AFF = data["affiliate"]

LEAD = {
    "A": ("발표 골든창 · 지금이 가장 쌉니다", "#185FA5", "#E6F1FB"),
    "B": ("초장기 선점 · 수개월 전 예약", "#0F6E56", "#E1F5EE"),
    "C": ("임박 경고 · 가격 급등 구간", "#A32D2D", "#FCEBEB"),
}

CSS = """
:root{--ink:#1a1a18;--muted:#6b6a64;--line:#e7e5dd;--bg:#fbfaf6;--card:#fff;--accent:#185FA5}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,'Apple SD Gothic Neo','Noto Sans KR',sans-serif;color:var(--ink);background:var(--bg);line-height:1.6}
a{color:inherit}.wrap{max-width:760px;margin:0 auto;padding:20px 16px}
.top{display:flex;align-items:center;gap:8px;padding:6px 0 16px;border-bottom:1px solid var(--line);margin-bottom:18px}
.top b{font-weight:600}.top span{margin-left:auto;color:var(--muted);font-size:13px}
.top .logo{height:28px;width:auto;display:block}
.badge{display:inline-block;font-size:12px;padding:4px 10px;border-radius:8px;font-weight:500}
h1{font-size:22px;margin:14px 0 2px;font-weight:600}.sub{color:var(--muted);font-size:14px;margin:0 0 16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.ecard{display:block;text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px}
.ecard:hover{border-color:#c9c7bd}.ecard .a{font-weight:600;font-size:15px}.ecard .c{color:var(--muted);font-size:13px;margin:2px 0 8px}
.box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:14px 0}
.outlook{background:#fdf6ec;border:1px solid #f0e4cf}
.metric{font-size:22px;font-weight:600;color:#A32D2D}
.btns{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin-top:6px}
.btn{display:flex;align-items:center;gap:8px;text-decoration:none;padding:11px 12px;border:1px solid #d7d5cb;border-radius:10px;font-size:14px}
.btn:hover{border-color:var(--accent)}.btn small{color:var(--muted)}
ul{margin:8px 0 0;padding-left:18px}li{margin:4px 0}
.news{display:flex;gap:8px;background:#E6F1FB;border-radius:10px;padding:12px;align-items:center;margin-top:14px}
.news input{flex:1;padding:9px;border:1px solid #b9d2ef;border-radius:8px;font-size:14px}
.news button{padding:9px 14px;border:0;background:var(--accent);color:#fff;border-radius:8px;font-size:14px;cursor:pointer}
.foot{color:var(--muted);font-size:12px;margin-top:24px;border-top:1px solid var(--line);padding-top:14px}
.back{font-size:13px;color:var(--muted);text-decoration:none}
.disc{font-size:12px;color:var(--muted);background:#f3f1ea;border:1px solid var(--line);border-radius:8px;padding:9px 11px;margin:8px 0 0;line-height:1.5}
.disc-aff{margin-top:8px}
.gdisc{color:var(--muted);font-size:11px;margin:18px 0 0;padding-top:10px;border-top:1px dashed var(--line);line-height:1.5}
.abadge{display:inline-flex;align-items:center;justify-content:center;min-width:34px;height:34px;padding:0 7px;border-radius:9px;font-weight:700;font-size:13px;letter-spacing:.3px;flex-shrink:0}
.ecard .ehead{display:flex;align-items:center;gap:9px}
.ehead-detail{display:flex;align-items:center;gap:11px;margin-top:10px}
.ehead-detail .abadge{min-width:46px;height:46px;font-size:16px;border-radius:12px}
"""


def esc(s):
    return html.escape(str(s))


def _text_on(bg_hex):
    """배경 명도 기준 가독 텍스트색(흰/검) — WCAG 단순 luminance."""
    h = bg_hex.lstrip("#")
    r, g, b = (int(h[i : i + 2], 16) for i in (0, 2, 4))
    lum = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#1a1a18" if lum > 0.62 else "#ffffff"


def artist_badge(e):
    """자체 생성 배지 = 팬덤 공식 응원색 배경 + 아티스트 약칭 이니셜(지시적 사용, 상표적 사용 아님).
    공식 로고 그래픽·외부 이미지 모방 금지(텍스트 모노그램만). 컨테이너 CSS가 크기 결정."""
    color = e.get("artist_color", "#8A8A8A")
    label = e.get("artist_badge") or e["artist"][:3].upper()
    fg = _text_on(color)
    return f'<span class="abadge" style="background:{color};color:{fg}" title="{esc(e["artist"])}">{esc(label)}</span>'


def aff_hotel(city):
    return f"https://www.booking.com/searchresults.html?ss={esc(city)}&aid={AFF['booking_aid']}"


def aff_flight(city):
    return f"https://www.skyscanner.co.kr/transport/flights/?destination={esc(city)}&associateid={AFF['skyscanner_pid']}"


def aff_esim(country):
    return f"https://www.airalo.com/?country={esc(country)}&ref={AFF['airalo_ref']}"


def aff_tour(city):
    return f"https://www.klook.com/search/?query={esc(city)}&aid={AFF['klook_aid']}"


def page(title, body):
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(SITE["tagline"])}">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<style>{CSS}</style></head><body><div class="wrap">{body}
<p class="gdisc">본 사이트는 아티스트·소속사와 무관한 비공식 일정·여행 정보 서비스이며, 공식 제휴 관계가 없습니다.</p>
</div></body></html>"""


def event_html(e):
    label, fg, bg = LEAD[lead_type_of(e)]
    stays = "".join(f"<li>{esc(s)}</li>" for s in e["stays"])
    # 정량 신호가 있는 항목만 렌더 — null·'데이터 없음'은 영역 생략(placeholder 채움 금지)
    search_row = (
        f'<div class="metric">{esc(e["search_signal"])}</div>'
        if has_signal(e.get("search_signal"))
        else ""
    )
    hotel_row = (
        f'<div style="font-size:14px;margin-top:4px">{esc(e["hotel_signal"])}</div>'
        if has_signal(e.get("hotel_signal"))
        else ""
    )
    body = f"""
<a class="back" href="index.html">← 전체 일정</a>
<div class="ehead-detail">
  {artist_badge(e)}
  <div><h1 style="margin:0">{esc(e["artist"])} — {esc(e["city"])}</h1>
  <p class="sub" style="margin:2px 0 0">{esc(e["event"])} · {esc(e["venue"])} · {esc(e["date"])} · {esc(e["country"])}</p></div>
</div>
<span class="badge" style="color:{fg};background:{bg};margin-top:10px">{esc(label)}</span>

<div class="box outlook">
  <div style="color:var(--muted);font-size:13px">가격·수요 전망 (발표 이후)</div>
  {search_row}
  {hotel_row}
  <p style="margin:10px 0 0;font-size:14px"><b>예약 데드라인:</b> {esc(e["deadline_text"])}</p>
</div>
<p class="disc">가격·잔량 전망은 추정이며 실제와 다를 수 있습니다. 예약·결제 책임은 이용자 본인에게 있습니다.</p>

<p style="font-weight:600;font-size:14px;margin:16px 0 4px">지금 잠그기</p>
<div class="btns">
  <a class="btn" href="{aff_hotel(e["city"])}" rel="sponsored nofollow" target="_blank">🏨 호텔 <small>· Booking</small></a>
  <a class="btn" href="{aff_flight(e["city"])}" rel="sponsored nofollow" target="_blank">✈️ 항공 <small>· Skyscanner</small></a>
  <a class="btn" href="{aff_esim(e["country"])}" rel="sponsored nofollow" target="_blank">📶 eSIM <small>· Airalo</small></a>
  <a class="btn" href="{aff_tour(e["city"])}" rel="sponsored nofollow" target="_blank">🎟 투어·티켓 <small>· Klook</small></a>
</div>
<p class="disc disc-aff">본 페이지의 예약 링크는 제휴(수수료) 링크입니다. 이용자가 추가로 부담하는 비용은 없습니다.</p>

<div class="box">
  <div style="font-weight:600;font-size:14px">근처 숙소 팁</div>
  <ul>{stays}</ul>
  <div style="font-weight:600;font-size:14px;margin-top:12px">공연 후 귀가 동선</div>
  <p style="margin:6px 0 0;font-size:14px">{esc(e["transport"])}</p>
</div>

<div class="news">
  <input placeholder="이메일 — 이 아티스트 가격·매진 알림 받기">
  <button>알림 받기</button>
</div>

<div class="foot">이 페이지의 예약 링크는 제휴(어필리에이트) 링크로, 예약 시 수수료가 발생할 수 있습니다.
수치는 공개 보도 기반 추정이며 실제와 다를 수 있습니다. · {esc(SITE["domain"])}</div>
"""
    return page(
        f"{e['artist']} {e['city']} — 항공·숙박 예약 타이밍 | {SITE['name']}", body
    )


def _card(e):
    label, fg, bg = LEAD[lead_type_of(e)]
    stripe = e.get("artist_color", "#8A8A8A")
    return f"""<a class="ecard" href="{e["slug"]}.html" style="border-left:4px solid {stripe}">
<div class="ehead">{artist_badge(e)}<div class="a">{esc(e["artist"])}</div></div>
<div class="c">{esc(e["city"])} · {esc(e["date"])}</div>
<span class="badge" style="color:{fg};background:{bg};font-size:11px">{esc(label.split(" · ")[0])}</span></a>"""


def _sort_key(e):
    end = event_end_date(e["date"])
    return end or date.max


def index_html(events):
    upcoming = sorted((e for e in events if not is_past(e["date"])), key=_sort_key)
    past = sorted(
        (e for e in events if is_past(e["date"])), key=_sort_key, reverse=True
    )
    cards = "".join(_card(e) for e in upcoming)
    past_section = ""
    if past:
        past_cards = "".join(_card(e) for e in past)
        past_section = f"""
<h2 style="font-size:16px;font-weight:600;margin:28px 0 4px;color:var(--muted)">지난 이벤트</h2>
<p class="sub" style="margin-bottom:10px">이미 끝난 공연 — 언제·얼마나 가격이 올랐는지 참고용 지난 사례입니다.</p>
<div class="grid">{past_cards}</div>"""
    body = f"""
<div class="top"><img class="logo" src="logo.svg" alt="{esc(SITE["name"])}" width="88" height="28"><span>{esc(SITE["domain"])}</span></div>
<h1>{esc(SITE["tagline"])}</h1>
<p class="sub">콘서트·팬미팅이 뜨면 항공·호텔이 먼저 오릅니다. 오르기 전에 잠그세요.</p>
<div class="grid">{cards}</div>
<p class="disc">각 페이지의 예약 링크는 제휴(수수료) 링크입니다. 가격·잔량 전망은 추정이며 실제와 다를 수 있습니다. 예약·결제 책임은 이용자 본인에게 있습니다.</p>
<div class="news"><input placeholder="이메일 — 새 공연 가격 알림 받기"><button>알림 받기</button></div>
{past_section}
<div class="foot">예약 링크는 제휴 링크입니다. · {esc(SITE["domain"])}</div>
"""
    return page(f"{SITE['name']} — {SITE['tagline']}", body)


events = data["events"]
upcoming = [e for e in events if not is_past(e["date"])]
past = [e for e in events if is_past(e["date"])]
# 더 이상 events.json에 없는(슬러그 변경·삭제) 고아 페이지 정리 — orphan 404·중복 노출 방지
current = {e["slug"] for e in events} | {"index"}
for f in DIST.glob("*.html"):
    if f.stem not in current:
        f.unlink()
        print(f"  (정리) 고아 페이지 삭제: {f.name}")
(DIST / "index.html").write_text(index_html(events), encoding="utf-8")
# 페이지는 전 이벤트 생성(지난 이벤트도 회고 링크로 도달 가능). 메인 목록에서만 격리.
for e in events:
    (DIST / f"{e['slug']}.html").write_text(event_html(e), encoding="utf-8")
# 정적 에셋(로고·파비콘) dist 복사 — 빌드 산출 누락 방지
for asset in ("logo.svg", "favicon.svg"):
    if (ROOT / asset).exists():
        shutil.copy(ROOT / asset, DIST / asset)
# GitHub Pages용: 커스텀 도메인(CNAME) + Jekyll 비활성(.nojekyll)
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", DIST / "CNAME")
(DIST / ".nojekyll").touch()

print(
    f"생성 완료(오늘 {TODAY}): 미래 {len(upcoming)} + 지난 {len(past)} = {len(events)}개 이벤트 페이지 → {DIST}"
)
print(f"  메인 목록(미래만): {len(upcoming)}건")
for e in sorted(upcoming, key=_sort_key):
    print(f"    - {e['slug']}.html ({e['artist']} {e['city']} {e['date']})")
print(f"  지난 이벤트(격리): {len(past)}건")
for e in sorted(past, key=_sort_key, reverse=True):
    print(f"    - {e['slug']}.html ({e['artist']} {e['city']} {e['date']})")
