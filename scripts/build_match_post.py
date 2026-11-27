"""Builds a "Match in one chart" post from one match's data and a short words file.

Usage:
    python scripts/build_match_post.py path/to/match.json path/to/words.json [--no-card]

match.json   what scripts/pull_match.js returns (keep it OUTSIDE this repo: no raw data on the site)
words.json   the words for the post, e.g.
    {
      "slug": "match-liverpool-united-2026-11-22",     # file name, without .html
      "title": "Was Liverpool 4-0 United as one-sided as it looked?",
      "summary": "Worse. Liverpool made 4.35 xG to United's 0.65.",   # one line for the homepage
      "description": "...",                            # one or two sentences for sharing and feeds
      "stand": "...",                                  # the answer, up front, under the title
      "race": ["paragraph", "..."],                    # words above the xG race
      "shots": ["paragraph", "..."],                   # words above the shot map
      "star": ["paragraph", "..."],                    # words above the star performer chart
      "answer": "...",                                 # 'The answer' paragraph
      "published": "2026-12-07",                       # optional, defaults to today
      "opp_short": "Forest"                            # optional, shorter opponent name (keeps chart labels tidy)
    }

Writes <slug>.html, adds the share card to scripts/make_social_cards.py and makes social/<slug>.png
(needs playwright; --no-card skips the image). Prints checks: shots against FotMob's headline numbers.
"""
import html
import json
import pathlib
import re
import subprocess
import sys
from datetime import date, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://postmatchplots.github.io/"
SERIES = "Match in one chart"
e = html.escape


def minute(t, add):
    """Plot position: first-half stoppage squeezed before 46', second-half stoppage after 90'."""
    if t == 45 and add:
        return 45 + min(add, 5) * 0.18
    if t >= 90:
        return 90 + add
    return t


def label(t, add):
    return f"{t}+{add}'" if add else f"{t}'"


GROUPS = {"ST": "strikers", "AM/W": "attacking midfielders and wingers", "CM": "central midfielders",
          "FB": "full-backs", "CB": "centre-backs"}
CATS = {"att": "Attacking", "pos": "On the ball", "def": "Without the ball", "phy": "Running"}


def fmt(k, v, mine):
    """His number as it happened; the average to one more decimal place."""
    if k == "km":
        return f"{v / 1000:.1f} km" if mine else f"{v / 1000:.1f}"
    if k == "passpct":
        return f"{v:.0f}%"
    if k in ("xg", "xa"):
        return f"{v:.2f}"
    return f"{v:.0f}" if mine else f"{v:.1f}"



def build(match, words):
    opp = words.get("opp_short") or match["opp"]
    home = match["home"]
    shots = [s for s in match["shots"] if not s["og"]]
    gf = sum(1 for g in match["goals"] if g["utd"])
    ga = sum(1 for g in match["goals"] if not g["utd"])
    xgf = sum(s["xg"] for s in shots if s["utd"])
    xga = sum(s["xg"] for s in shots if not s["utd"])
    sf = sum(1 for s in shots if s["utd"])
    sa = sum(1 for s in shots if not s["utd"])
    top = match.get("top", {})
    bc = top.get("big_chance", ["?", "?"])
    poss = top.get("BallPossesion", ["?", "?"])

    # ---- checks, printed for whoever runs this
    print(f"Score from goal events: United {gf}-{ga} {opp}")
    shot_goals = (sum(1 for s in shots if s["utd"] and s["r"] == "Goal"), sum(1 for s in shots if not s["utd"] and s["r"] == "Goal"))
    if shot_goals != (gf - sum(1 for g in match["goals"] if g["utd"] and g["og"]), ga - sum(1 for g in match["goals"] if not g["utd"] and g["og"])):
        print(f"  CHECK: shot map has {shot_goals[0]}-{shot_goals[1]} goals (own goals aside). A goal may be missing from the shot map.")
    if top.get("expected_goals"):
        fx = [float(v) for v in top["expected_goals"]]
        if abs(fx[0] - xgf) > 0.06 or abs(fx[1] - xga) > 0.06:
            print(f"  CHECK: shot xG {xgf:.2f}-{xga:.2f} vs FotMob headline {fx[0]:.2f}-{fx[1]:.2f}")
        else:
            print(f"  xG {xgf:.2f}-{xga:.2f}, within 0.06 of FotMob's headline {fx[0]:.2f}-{fx[1]:.2f} (rounding on their side)")
    if top.get("total_shots") and [int(v) for v in top["total_shots"]] != [sf, sa]:
        print(f"  CHECK: {sf}-{sa} shots in the shot map vs FotMob's {top['total_shots']}")

    # ---- chart data
    def race_shots(utd):
        out = [{"m": round(minute(s["t"], s["add"]), 2), "xg": s["xg"], "goal": s["r"] == "Goal", "who": s["n"], "label": label(s["t"], s["add"])}
               for s in shots if s["utd"] == utd]
        out += [{"m": round(minute(g["t"], g["add"]), 2), "xg": 0, "goal": True, "who": g["n"] + " (own goal)", "label": label(g["t"], g["add"])}
                for g in match["goals"] if g["og"] and g["utd"] == utd]
        return out

    end = max([95] + [90 + s["add"] + 1 for s in match["shots"] if s["t"] >= 90])
    reds = [{"m": minute(r["t"], 0), "label": f"{r['n'].split()[-1]} sent off"} for r in match["reds"]]
    race = {"end": end, "reds": reds, "teams": [
        {"n": opp, "u": False, "shots": race_shots(False)},
        {"n": "United", "u": True, "shots": race_shots(True)}]}

    def map_shots(utd):
        return [{"x": s["x"], "y": s["y"], "xg": s["xg"], "goal": s["r"] == "Goal", "who": s["n"], "m": label(s["t"], s["add"])}
                for s in shots if s["utd"] == utd]

    shotmap = {
        "left": {"n": opp, "u": False, "shots": map_shots(False), "sub": f"{ga} goals, {xga:.2f} xG, {sa} shots"},
        "right": {"n": "United", "u": True, "shots": map_shots(True), "sub": f"{gf} goals, {xgf:.2f} xG, {sf} shots"}}

    paras = lambda ps: "\n".join(f"  <p>{p}</p>" for p in ps)
    star = match.get("star")
    star_html, star_js = "", ""
    if star:
        grp = GROUPS.get(star["grp"], "players in his position")
        mins = star["mins"]
        rows = []
        for x in star["slices"]:
            if x.get("avg90") is None:
                continue
            avg = x["avg90"] if x["isRate"] else x["avg90"] * mins / 90
            vf, af = fmt(x["k"], x["raw"], True), fmt(x["k"], avg, False)
            tip = f"{x['lab']}: {vf} against an average of {af} for PL {grp}" + ("" if x["isRate"] or mins >= 89 else f" over {mins} minutes")
            rows.append({"lab": x["lab"], "v": x["raw"], "avg": round(avg, 3), "vf": vf, "af": af, "tip": tip, "cat": x["cat"]})
        above = sum(1 for r in rows if r["v"] >= r["avg"])
        print(f"Star performer: {star['n']} ({star['grp']}, {mins} mins, rating {star['rating']}), above average on {above} of {len(rows)}")
        mins_note = "" if mins >= 89 else f" He played {mins} minutes, so the average is scaled to {mins} minutes too."
        star_html = f"""
<div class="sec read">
  <h2>{e(words.get('star_title') or 'Star performer: ' + star['n'])}</h2>
{paras(words.get('star', []))}
</div>
<div class="chart">
  <div class="key" style="margin-bottom:8px"><span><i style="background:#e3343a;border-radius:2px"></i>his game, above average</span><span><i style="background:#5d6b63;border-radius:2px"></i>below average</span><span><i style="width:2px;height:16px;border-radius:0;background:#eef2ee"></i>average for PL {e(grp)}</span></div>
  <div class="rows" id="star" style="max-width:860px" role="img" aria-label="{e(f"{star['n']}'s numbers from the match against the average for Premier League {grp}: " + '; '.join(f"{r['lab']} {r['vf']} against {r['af']}" for r in rows))}"></div>
  <p class="cap">His numbers from this match, then the season average per game for the {star['pool']} PL {e(grp)} with 450+ minutes. The marker in the middle is that average; a bar reaching the end is at least double it. FotMob match rating {star['rating']}.{e(mins_note)} xG includes penalties.</p>
</div>
"""
        star_js = f"\n  PMP.versus(document.getElementById('star'), {json.dumps({'rows': rows, 'cats': CATS}, ensure_ascii=False)});"

    # ---- page
    d = datetime.strptime(match["date"], "%Y-%m-%d")
    nice_date = f"{d.day} {d.strftime('%B %Y')}"
    scoreline = f"United {gf}-{ga} {opp}" if home else f"{opp} {ga}-{gf} United"
    published = words.get("published") or date.today().isoformat()
    slug = words["slug"]
    url = BASE + slug + ".html"
    img = BASE + "social/" + slug + ".png"
    desc = words["description"]
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": words["title"], "description": desc,
          "datePublished": published, "dateModified": published, "image": img, "mainEntityOfPage": url,
          "author": {"@type": "Organization", "name": "Post-Match Plots", "url": BASE},
          "publisher": {"@type": "Organization", "name": "Post-Match Plots", "logo": {"@type": "ImageObject", "url": BASE + "logo.svg"}},
          "isPartOf": {"@type": "CreativeWorkSeries", "name": SERIES}}
    red_note = ""
    if match["reds"]:
        red_note = " Dotted line: " + ", ".join(f"{r['n']} sent off ({label(r['t'], 0)})" for r in match["reds"]) + "."

    page = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(words['title'])} | Post-Match Plots</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/svg+xml" href="logo.svg">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Post-Match Plots" href="feed.xml">
<meta property="og:type" content="article">
<meta property="article:published_time" content="{published}">
<meta name="pmp:series" content="{SERIES}">
<meta name="pmp:part" content="{int(match['round'])}">
<meta name="pmp:series-order" content="newest">
<meta name="pmp:summary" content="{e(words['summary'])}">
<meta property="og:site_name" content="Post-Match Plots">
<meta property="og:title" content="{e(words['title'])}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(words['title'])}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{img}">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<link rel="stylesheet" href="site.css">
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="index.html"><img src="logo.svg" alt="" width="40" height="40">Post-Match Plots</a>
  <nav><a href="index.html#posts">Posts</a><a href="index.html#about">About</a><a href="feed.xml">RSS</a></nav>
</div></header>

<main>
<section class="band pitchband"><div class="wrap">
  <p class="small" style="color:#c9d4cd;margin-bottom:10px">{SERIES} &nbsp;/&nbsp; {e(scoreline)} &nbsp;/&nbsp; {nice_date}</p>
  <h1 style="max-width:900px">{e(words['title'])}</h1>
  <p class="stand">{words['stand']}</p>
</div></section>

<section class="band" style="padding-top:0"><div class="wrap">
  <div class="figs"><div class="fg"><div class="num">{gf}-{ga}</div><div class="lab">United's score first</div></div><div class="fg"><div class="num{' red' if xgf < xga else ''}">{xgf:.2f}-{xga:.2f}</div><div class="lab">expected goals (xG)</div></div><div class="fg"><div class="num">{sf}-{sa}</div><div class="lab">shots, with {poss[0]}% of the ball</div></div><div class="fg"><div class="num">{bc[0]}-{bc[1]}</div><div class="lab">big chances</div></div></div>
</div></section>

<article class="band" style="padding-top:8px"><div class="wrap">
<div class="sec read">
  <h2>How the chances piled up</h2>
{paras(words['race'])}
</div>
<div class="chart">
  <div class="fig" id="race"><svg role="img" aria-label="{e(f'Cumulative expected goals over the match. United finish on {xgf:.2f} xG and {gf} goals, {opp} on {xga:.2f} xG and {ga} goals.')}"></svg></div>
  <p class="cap">Each step is a shot, the height of the step its xG. Dots are goals. Hover for the shot.{e(red_note)}</p>
</div>

<div class="sec read">
  <h2>Where the shots came from</h2>
{paras(words['shots'])}
</div>
<div class="chart">
  <div class="fig" id="shots" style="min-height:0;aspect-ratio:105/68;max-width:900px"><svg role="img" aria-label="{e(f'Shot map. United attack the right-hand goal with {sf} shots, {opp} the left with {sa}. Bigger circles are better chances; filled circles are goals.')}"></svg></div>
  <p class="cap">United shoot right, {e(opp)} left. Bigger circle, better chance. Filled circles are goals. Own goals left out.</p>
</div>

{star_html}
<div class="sec read">
  <h2>The answer</h2>
  <p>{words['answer']}</p>
</div>
<div class="sec read">
  <h3>How this was made</h3>
  <p class="small">Data from FotMob (Opta): the match shot map, with xG for every shot. Penalties are included at their xG; own goals are left out of xG and the shot map but counted in the score. One match is a tiny sample, so read xG as how good the chances were, not who deserved to win.</p>
</div>
</div></article>

<section class="band" style="background:var(--panel)"><div class="wrap">
  <h2>More from Post-Match Plots</h2>
  <p><a href="index.html#posts">Every post</a> &nbsp;/&nbsp; <a href="feed.xml">Follow by RSS</a></p>
</div></section>
</main>

<footer class="band"><div class="wrap">
  <span>Post-Match Plots. Football, drawn with data.</span>
  <span>Data: FotMob / Opta</span>
</div></footer>

<script src="charts.js"></script>
<script>
{{
  PMP.xgrace(document.getElementById('race'), {json.dumps(race, ensure_ascii=False)});
  PMP.shotmap(document.getElementById('shots'), {json.dumps(shotmap, ensure_ascii=False)});{star_js}
}}
</script>
</body>
</html>
"""
    (ROOT / f"{slug}.html").write_text(page, encoding="utf-8")
    print(f"Wrote {slug}.html")
    return slug, words["title"], f"{SERIES}: {scoreline}"


def add_card(slug, title, kicker):
    p = ROOT / "scripts" / "make_social_cards.py"
    s = p.read_text(encoding="utf-8")
    if f'("{slug}",' not in s:
        entry = f'("{slug}","{slug}.html","#race",{json.dumps(title, ensure_ascii=False)},{json.dumps(kicker, ensure_ascii=False)})'
        s = re.sub(r"\)\]\nasync def main", ")," + "\n" + entry + "]\nasync def main", s, count=1)
        p.write_text(s, encoding="utf-8")
        print("Added the share card to scripts/make_social_cards.py")
    subprocess.run([sys.executable, str(p), slug], check=True)
    print(f"Made social/{slug}.png")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    match = json.loads(pathlib.Path(args[0]).read_text(encoding="utf-8"))
    words = json.loads(pathlib.Path(args[1]).read_text(encoding="utf-8"))
    slug, title, kicker = build(match, words)
    if "--no-card" not in sys.argv:
        add_card(slug, title, kicker)
