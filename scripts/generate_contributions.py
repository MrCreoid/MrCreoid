from __future__ import annotations
import os
import datetime as dt
from pathlib import Path
import requests
from bs4 import BeautifulSoup

USER = os.environ.get("GITHUB_USERNAME", "mrcreoid")
OUT = Path("assets/contribution-grid.svg")
html = requests.get(
    f"https://github.com/users/{USER}/contributions",
    timeout=30,
    headers={"User-Agent": "Mozilla/5.0"},
).text
soup = BeautifulSoup(html, "html.parser")
cells = soup.select("td.ContributionCalendar-day[data-date]")
if not cells:
    cells = soup.select("[data-date][data-level]")
data = {c.get("data-date"): int(c.get("data-level", "0")) for c in cells if c.get("data-date")}
if not data:
    raise SystemExit("Could not read GitHub contribution calendar")

end = dt.date.today()
start = end - dt.timedelta(days=364)
start -= dt.timedelta(days=(start.weekday() + 1) % 7)
days = []
d = start
while d <= end:
    days.append(d)
    d += dt.timedelta(days=1)

palette = ["#151922", "#14313A", "#005B66", "#00A9B8", "#00F0FF"]
svg = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="190" viewBox="0 0 1100 190">
<defs><style>.cell{{animation:pulse 3.8s ease-in-out infinite}}@keyframes pulse{{0%,100%{{opacity:.72}}50%{{opacity:1}}}}</style></defs>
<rect width="1100" height="190" rx="4" fill="#07090D" stroke="#00F0FF" stroke-opacity=".65"/>
<path d="M0 38H1100" stroke="#FF003C" stroke-opacity=".65"/>
<text x="26" y="26" fill="#FCE300" font-family="monospace" font-size="12" letter-spacing="3">CONTRIBUTION NETWORK // 365D SIGNAL MAP</text>
<text x="1070" y="26" text-anchor="end" fill="#00F0FF" font-family="monospace" font-size="10">USER: {USER.upper()}</text>
<g transform="translate(30 52)">''']

for i, day in enumerate(days):
    w, r = i // 7, i % 7
    level = data.get(day.isoformat(), 0)
    svg.append(f'<rect class="cell" style="animation-delay:{(i % 37) * 0.04:.2f}s" x="{w*19}" y="{r*17}" width="13" height="13" rx="1" fill="{palette[level]}"/>')

svg.append('''</g>
<g font-family="monospace" font-size="9" fill="#8B949E">
<text x="30" y="178">LESS</text><rect x="65" y="169" width="11" height="11" fill="#151922"/><rect x="82" y="169" width="11" height="11" fill="#14313A"/><rect x="99" y="169" width="11" height="11" fill="#005B66"/><rect x="116" y="169" width="11" height="11" fill="#00A9B8"/><rect x="133" y="169" width="11" height="11" fill="#00F0FF"/><text x="151" y="178">MORE</text>
</g></svg>''')
OUT.write_text("".join(svg), encoding="utf-8")
