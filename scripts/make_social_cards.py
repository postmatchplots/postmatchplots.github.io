"""Makes the 1200x630 social preview images in social/ by screenshotting each page's main chart.
Needs Python with playwright (pip install playwright && playwright install chromium). Run locally, then upload social/.
Pass card names to make only those, e.g. python scripts/make_social_cards.py kobbie-mainoo"""
import asyncio, html, sys
from playwright.async_api import async_playwright
import pathlib
R=str(pathlib.Path(__file__).resolve().parent.parent)+"/"
cards=[("home","index.html","#quality","Football, drawn with data.","One question at a time, answered with charts"),
("united-shot-quality","united-shot-quality.html","#quality","Why don't United's 203 shots add up to more?","United at 11 games, part 1"),
("united-finishing-luck","united-finishing-luck.html","#gxg","Are United unlucky in front of goal?","United at 11 games, part 2"),
("united-chances-conceded","united-chances-conceded.html","#forag","Why do United concede so many goals from so few shots?","United at 11 games, part 3"),
("united-set-pieces","united-set-pieces.html","#sp","How much are set pieces costing United?","United at 11 games, part 4"),
("bruno-fernandes-decline","bruno-fernandes-decline.html","#bruno","Is Bruno Fernandes getting worse?","United at 11 games, part 5"),
("united-expected-points","united-expected-points.html","#xpts","So where should United actually be?","United at 11 games, part 6"),
("kobbie-mainoo","kobbie-mainoo.html","#both","Is Kobbie Mainoo the one thing going right?","Passing, dribbling, winning it back"),
("what-is-xg","what-is-xg.html","#gxg","What is xG?","Guide: how the numbers work"),
("what-are-percentiles","what-are-percentiles.html","#pct","What are percentiles?","Guide: how the numbers work"),
("what-are-expected-points","what-are-expected-points.html","#matches","What are expected points?","Guide: how the numbers work"),
("how-to-read-match-in-one-chart","how-to-read-match-in-one-chart.html","#race","How to read a Match in one chart","Guide: how the numbers work"),
("stat-glossary","stat-glossary.html","#norms","Stat glossary","Guide: every stat in plain English")]
async def main(only=None):
    todo=[c for c in cards if not only or c[0] in only]
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for slug,f,sel,title,kick in todo:
            w = 680 if sel in ("#bruno","#gxg","#quality","#forag","#xpts","#both","#race","#pct") else 1180
            pg=await b.new_page(viewport={"width":w,"height":900})
            await pg.goto("file://"+R+f); await pg.wait_for_timeout(900)
            await pg.add_style_tag(content=".grow{animation:none!important}")
            el=await pg.query_selector(sel)
            await el.screenshot(path=f"/tmp/chart_{slug}.png")
        card=await b.new_page(viewport={"width":1200,"height":630})
        for slug,f,sel,title,kick in todo:
            doc=f'''<html><head><link rel="stylesheet" href="file://{R}site.css"></head><body style="margin:0;width:1200px;height:630px;overflow:hidden;background:#0b0f0d">
<div style="display:grid;grid-template-columns:470px 1fr;gap:36px;height:630px;box-sizing:border-box;padding:48px 52px;background:repeating-linear-gradient(90deg,#10291c 0 90px,#0d2318 90px 180px)">
<div style="display:flex;flex-direction:column;justify-content:space-between">
<div style="display:flex;align-items:center;gap:14px;font-family:'Barlow Condensed';font-weight:700;font-size:34px;color:#eef2ee"><img src="file://{R}logo.svg" width="52" height="52">Post-Match Plots</div>
<div><div style="font-family:Barlow;font-size:22px;color:#c9d4cd;margin-bottom:14px">{html.escape(kick)}</div>
<div style="font-family:'Barlow Condensed';font-weight:700;font-size:62px;line-height:1.02;color:#eef2ee">{html.escape(title)}</div></div>
<div style="font-family:Barlow;font-size:18px;color:#9aa79f">Data: FotMob / Opta</div></div>
<div style="background:#0b0f0d;border-radius:10px;display:flex;align-items:center;justify-content:center;padding:18px;overflow:hidden"><img src="file:///tmp/chart_{slug}.png" style="max-width:100%;max-height:100%;object-fit:contain"></div>
</div></body></html>'''
            open(f"/tmp/card_{slug}.html","w").write(doc)
            await card.goto(f"file:///tmp/card_{slug}.html"); await card.wait_for_timeout(500)
            await card.screenshot(path=R+f"social/{slug}.png")
        await b.close()
if __name__ == "__main__":
    # No arguments: remake every card. Or name the cards to make: python scripts/make_social_cards.py kobbie-mainoo
    asyncio.run(main(sys.argv[1:] or None))
