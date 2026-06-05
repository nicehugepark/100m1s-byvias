#!/usr/bin/env python3
"""
Fandom — 정적 사이트 생성기 (린 MVP)
events.json → dist/index.html + dist/<slug>.html
어필리에이트 링크는 PLACEHOLDER. 보스 가입 후 events.json의 affiliate 값만 교체하면 전 페이지 일괄 반영.
실행: python3 generate.py
"""

import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DIST = ROOT / "dist"
DIST.mkdir(exist_ok=True)

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
"""


def esc(s):
    return html.escape(str(s))


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
<style>{CSS}</style></head><body><div class="wrap">{body}</div></body></html>"""


def event_html(e):
    label, fg, bg = LEAD[e["lead_type"]]
    stays = "".join(f"<li>{esc(s)}</li>" for s in e["stays"])
    body = f"""
<a class="back" href="index.html">← 전체 일정</a>
<div style="display:flex;align-items:flex-start;gap:10px;margin-top:10px">
  <div><h1>{esc(e["artist"])} — {esc(e["city"])}</h1>
  <p class="sub">{esc(e["event"])} · {esc(e["venue"])} · {esc(e["date"])} · {esc(e["country"])}</p></div>
</div>
<span class="badge" style="color:{fg};background:{bg}">{esc(label)}</span>

<div class="box outlook">
  <div style="color:var(--muted);font-size:13px">가격·수요 전망 (발표 이후)</div>
  <div class="metric">{esc(e["search_signal"])}</div>
  <div style="font-size:14px;margin-top:4px">{esc(e["hotel_signal"])}</div>
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
    return page(f"{e['artist']} {e['city']} — 항공·숙박 예약 타이밍 | Fandom", body)


def index_html(events):
    cards = ""
    for e in events:
        label, fg, bg = LEAD[e["lead_type"]]
        cards += f"""<a class="ecard" href="{e["slug"]}.html">
<div class="a">{esc(e["artist"])}</div><div class="c">{esc(e["city"])} · {esc(e["date"])}</div>
<span class="badge" style="color:{fg};background:{bg};font-size:11px">{esc(label.split(" · ")[0])}</span></a>"""
    body = f"""
<div class="top"><b>{esc(SITE["name"])}</b><span>{esc(SITE["domain"])}</span></div>
<h1>{esc(SITE["tagline"])}</h1>
<p class="sub">콘서트·팬미팅이 뜨면 항공·호텔이 먼저 오릅니다. 오르기 전에 잠그세요.</p>
<div class="grid">{cards}</div>
<p class="disc">각 페이지의 예약 링크는 제휴(수수료) 링크입니다. 가격·잔량 전망은 추정이며 실제와 다를 수 있습니다. 예약·결제 책임은 이용자 본인에게 있습니다.</p>
<div class="news"><input placeholder="이메일 — 새 공연 가격 알림 받기"><button>알림 받기</button></div>
<div class="foot">예약 링크는 제휴 링크입니다. · {esc(SITE["domain"])}</div>
"""
    return page(f"Fandom — {SITE['tagline']}", body)


events = data["events"]
(DIST / "index.html").write_text(index_html(events), encoding="utf-8")
for e in events:
    (DIST / f"{e['slug']}.html").write_text(event_html(e), encoding="utf-8")
# GitHub Pages용: 커스텀 도메인(CNAME) + Jekyll 비활성(.nojekyll)
if (ROOT / "CNAME").exists():
    shutil.copy(ROOT / "CNAME", DIST / "CNAME")
(DIST / ".nojekyll").touch()

print(f"생성 완료: index.html + {len(events)}개 이벤트 페이지 → {DIST}")
for e in events:
    print(f"  - {e['slug']}.html ({e['artist']} {e['city']})")
