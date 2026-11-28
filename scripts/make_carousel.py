"""Turns a post page into an Instagram carousel: 1080x1350 (4:5) PNG slides in carousel/<page>/.

Usage:  python scripts/make_carousel.py bruno-fernandes-decline.html [more.html ...]
Needs Python with playwright (pip install playwright && playwright install chromium).

Slides, all built from the post itself (no extra writing needed):
  1  Cover: series line, the question, "Swipe"
  2  The short answer (the stand-first under the headline)
  3  Big numbers (the .figs strip), if the post has one
  4+ One slide per section, in order: a chart slide if the section has a chart,
     otherwise a text slide. "How this was made" is skipped.
  last  "Full post: link in bio", with the logo

Also writes caption.txt: question, short answer, link-in-bio line, credit, a few hashtags.
The carousel/ folder is for uploading only; it's in .gitignore so it never goes on the site.
"""
import asyncio, html, json, pathlib, sys
from playwright.async_api import async_playwright

R = pathlib.Path(__file__).resolve().parent.parent
W, H = 1080, 1350
TAGS = "#ManUtd #MUFC #PremierLeague #FootballData #DataViz"

# Pulls the pieces out of a post page, in reading order.
EXTRACT = r"""() => {
  const t = el => el ? el.textContent.replace(/\s+/g,' ').trim() : '';
  const out = {question: t(document.querySelector('h1')),
               kicker: t(document.querySelector('.pitchband .small')).split(' / ')[0],
               stand: t(document.querySelector('.stand')),
               figs: [...document.querySelectorAll('.figs .fg')].map(f => ({num: t(f.querySelector('.num')),
                       lab: t(f.querySelector('.lab')), red: f.querySelector('.num.red') !== null})),
               sections: []};
  const article = document.querySelector('article .wrap');
  let cur = null, n = 0;
  for (const el of article.children) {
    if (el.matches('.sec')) {
      const h = el.querySelector('h2'); if (!h) continue;          // skips "How this was made" (h3)
      cur = {title: t(h), paras: [...el.querySelectorAll('p')].map(t), chart: null, cap: ''};
      out.sections.push(cur);
    } else if (el.matches('.chart') && cur) {
      el.id = el.id || ('pmpchart' + (n++));
      cur.chart = el.id;
      const cap = el.querySelector('.cap');
      if (cap) {                                   // drop links and hover/tap hints: they mean nothing on a slide
        const c = cap.cloneNode(true); c.querySelectorAll('a').forEach(a => a.remove());
        cur.cap = (t(c).match(/[^.!?]+[.!?]*/g) || []).map(x => x.trim())
                  .filter(x => x.replace(/[.!?\s]/g,'') && !/\b(hover|tap|click)\b/i.test(x)).join(' ');
      }
    }
  }
  return out;
}"""

def page(body, bg="var(--bg)"):
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><link rel="stylesheet" href="file://{R}/site.css">
<style>
body{{margin:0;width:{W}px;height:{H}px;overflow:hidden;background:{bg}}}
.s{{box-sizing:border-box;width:{W}px;height:{H}px;padding:76px 80px 64px;display:flex;flex-direction:column}}
.top{{display:flex;align-items:center;gap:14px;font-family:'Barlow Condensed';font-weight:700;font-size:34px;color:var(--ink)}}
.foot{{display:flex;justify-content:space-between;font-size:24px;color:var(--mute);margin-top:auto;padding-top:28px}}
.kick{{font-size:30px;color:#c9d4cd}}
.big{{font-family:'Barlow Condensed';font-weight:700;line-height:1.0;color:var(--ink);text-wrap:balance;letter-spacing:-.01em}}
.lbl{{font-family:'Barlow Condensed';font-weight:700;font-size:32px;color:var(--red);letter-spacing:.04em;text-transform:uppercase}}
.txt{{font-size:40px;line-height:1.38;color:#d6ddd8;text-wrap:pretty}}
.cap2{{font-size:24px;line-height:1.4;color:var(--mute)}}
</style></head><body>{body}</body></html>"""

def top(): return f'<div class="top"><img src="file://{R}/logo.svg" width="52" height="52">Post-Match Plots</div>'

def foot(i, n, credit=True):
    left = "Data: FotMob / Opta" if credit else ""
    return f'<div class="foot"><span>{left}</span><span>{i} / {n}</span></div>'

def fit(text, sizes):
    """Pick a font size for a block of text by length."""
    for limit, size in sizes:
        if len(text) <= limit: return size
    return sizes[-1][1]

def build(post, charts, n):
    e = html.escape
    slides = []
    pitch = "repeating-linear-gradient(90deg,var(--pitch) 0 90px,var(--pitch2) 90px 180px)"
    # 1 cover
    q = post["question"]
    slides.append(("cover", page(f'''<div class="s">{top()}
      <div style="margin-top:auto"><div class="kick" style="margin-bottom:22px">{e(post["kicker"])}</div>
      <div class="big" style="font-size:{fit(q,[(40,128),(70,108),(999,92)])}px">{e(q)}</div></div>
      <div class="foot" style="margin-top:56px"><span>Swipe for the answer</span><span style="color:var(--ink);font-size:44px;line-height:.6">&rarr;</span></div></div>''', pitch)))
    # 2 short answer
    st = post["stand"]
    slides.append(("answer", f'''<div class="s">{top()}
      <div style="margin:auto 0"><div class="lbl" style="margin-bottom:28px">The short answer</div>
      <div class="txt" style="font-size:{fit(st,[(160,56),(260,48),(999,42)])}px;color:var(--ink)">{e(st)}</div></div>{{foot}}</div>'''))
    # 3 big numbers
    if post["figs"]:
        cells = "".join(f'''<div style="background:var(--bg);padding:34px 32px">
          <div class="big" style="font-size:96px;color:{'var(--red)' if f['red'] else 'var(--ink)'}">{e(f['num'])}</div>
          <div style="font-size:30px;line-height:1.3;color:var(--mute);margin-top:14px">{e(f['lab'])}</div></div>''' for f in post["figs"][:4])
        slides.append(("numbers", f'''<div class="s">{top()}
          <div style="margin:auto 0"><div class="lbl" style="margin-bottom:28px">In numbers</div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:2px;background:var(--rule);border:2px solid var(--rule)">{cells}</div></div>{{foot}}</div>'''))
    # 4+ sections
    for i, s in enumerate(post["sections"]):
        is_answer = s["title"].lower() == "the answer"
        if s["chart"]:
            slides.append((f"chart{i}", f'''<div class="s">{top()}
              <div class="big" style="font-size:72px;margin:44px 0 20px">{e(s["title"])}</div>
              <div style="flex:1;min-height:0;display:flex;align-items:center;justify-content:center;background:var(--bg)">
                <img src="file://{charts[s['chart']]}" style="max-width:100%;max-height:100%;object-fit:contain"></div>
              <div class="cap2" style="margin-top:24px">{e(s["cap"])}</div>{{foot}}</div>'''))
        else:
            body = " ".join(s["paras"])
            slides.append((f"text{i}", f'''<div class="s">{top()}
              <div style="margin:auto 0">{'<div class="lbl" style="margin-bottom:22px">The answer</div>' if is_answer else ''}
              {'' if is_answer else f'<div class="big" style="font-size:76px;margin-bottom:34px">{e(s["title"])}</div>'}
              <div class="txt" style="font-size:{fit(body,[(260,46),(420,40),(600,36),(999,32)])}px{';color:var(--ink)' if is_answer else ''}">{e(body)}</div></div>{{foot}}</div>'''))
    # last: link in bio
    slides.append(("end", f'''<div class="s" style="align-items:center;justify-content:center;text-align:center">
      <img src="file://{R}/logo.svg" width="150" height="150">
      <div class="big" style="font-size:96px;margin-top:44px">Full post: link in bio</div>
      <div class="txt" style="margin-top:26px;color:var(--mute)">Every chart, the method, and the rest of the series</div>
      <div style="font-family:'Barlow Condensed';font-weight:700;font-size:40px;margin-top:70px;color:var(--ink)">Post-Match Plots</div>
      <div style="font-size:28px;color:var(--mute);margin-top:6px">Football, drawn with data.</div></div>'''))
    total = len(slides)
    out = []
    for i, (name, body) in enumerate(slides, 1):
        doc = body if body.startswith("<!DOCTYPE") else page(body.replace("{foot}", foot(i, total, name != "end")))
        out.append((f"{i:02d}-{name}", doc))
    return out

async def run(fname):
    slug = fname.removesuffix(".html")
    dest = R / "carousel" / slug; dest.mkdir(parents=True, exist_ok=True)
    for old in dest.glob("*.png"): old.unlink()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 560, "height": 1400}, device_scale_factor=3)
        await pg.goto(f"file://{R}/{fname}"); await pg.wait_for_timeout(1200)
        await pg.add_style_tag(content=".grow{animation:none!important}.chart .cap{display:none}")
        post = await pg.evaluate(EXTRACT)
        charts = {}
        for s in post["sections"]:
            if s["chart"]:
                path = f"/tmp/carousel_{slug}_{s['chart']}.png"
                await (await pg.query_selector("#" + s["chart"])).screenshot(path=path)
                charts[s["chart"]] = path
        slide = await b.new_page(viewport={"width": W, "height": H})
        for name, doc in build(post, charts, 0):
            tmp = pathlib.Path(f"/tmp/carousel_{slug}_{name}.html"); tmp.write_text(doc)
            await slide.goto(f"file://{tmp}"); await slide.wait_for_timeout(400)
            await slide.screenshot(path=str(dest / f"{name}.png"))
        await b.close()
    url = f"https://postmatchplots.github.io/{fname}"
    (dest / "caption.txt").write_text(f"{post['question']}\n\n{post['stand']}\n\nFull post with every chart: link in bio.\n\nData: FotMob / Opta\n\n{TAGS}\n")
    print(f"{fname}: {len(list(dest.glob('*.png')))} slides in carousel/{slug}/  (post: {url})")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(__doc__)
    for f in sys.argv[1:]: asyncio.run(run(f))
