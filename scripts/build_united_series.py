"""Regenerates the six 'United at 11 games' post pages from the text and data in this file. Run: python scripts/build_united_series.py
Builds the 'United at 11 games' series for Post-Match Plots (flat layout)."""
import sys, html, json
BASE = "https://postmatchplots.github.io/"
OUT = sys.argv[1] if len(sys.argv) > 1 else str(__import__("pathlib").Path(__file__).resolve().parent.parent)

LOGO = '<a class="brand" href="index.html"><img src="logo.svg" alt="" width="40" height="40">Post-Match Plots</a>'

SERIES = [
    ("united-shot-quality.html", "Why don't United's 203 shots add up to more?", "Shot quality"),
    ("united-finishing-luck.html", "Are United unlucky in front of goal?", "Finishing"),
    ("united-chances-conceded.html", "Why do United concede so many goals from so few shots?", "Defending"),
    ("united-set-pieces.html", "How much are set pieces costing United?", "Set pieces"),
    ("bruno-fernandes-decline.html", "Is Bruno Fernandes getting worse?", "Bruno"),
    ("united-expected-points.html", "So where should United actually be?", "Expected points"),
]

TEAMS = '''const T = [["Man City",165,22.0,21.9,13.5],["Brighton",184,20.4,21.6,15.4],["Bournemouth",152,20.3,20.9,13.2],["Brentford",156,18.3,17.2,15.0],["Liverpool",176,17.7,20.2,13.8],["Man Utd",203,17.0,18.2,22.2],["Arsenal",151,16.9,17.6,9.3],["Leeds",143,16.9,16.0,13.2],["Nott'm Forest",177,16.8,17.7,13.9],["Tottenham",172,15.2,15.1,12.5],["Sunderland",122,14.2,15.8,17.4],["Everton",144,14.2,14.1,16.8],["Chelsea",150,14.0,14.6,17.8],["Crystal Palace",117,13.8,15.5,23.9],["Fulham",134,13.7,15.2,15.8],["Aston Villa",138,13.4,14.8,18.9],["Newcastle",134,12.4,13.2,18.2],["Ipswich",120,12.4,14.0,22.1],["Coventry",123,10.9,11.6,16.9],["Hull",114,10.6,11.3,16.7]];
  const U = n => n === 'Man Utd';'''

SUMMARY = {
    "united-shot-quality.html": "Nearly half come from outside the box.",
    "united-finishing-luck.html": "A little: four goals short, spread thinly.",
    "united-chances-conceded.html": "They give away the best chances in the league.",
    "united-set-pieces.html": "About six goals: one scored, seven conceded.",
    "bruno-fernandes-decline.html": "At creating, yes. At scoring, no.",
    "united-expected-points.html": "About 15th: unlucky, but not unlucky enough to be good.",
}

METHOD = '''<div class="sec read">
  <h3>How this was made</h3>
  <p class="small">Data from FotMob (Opta), Premier League 2026/27 up to 24 November 2026{extra}. {detail} Eleven games is a small sample, so treat every number here as a direction, not a verdict.</p>
</div>'''

def page(fname, title, kicker, h1, stand, figs, body, script, desc):
    i = [s[0] for s in SERIES].index(fname)
    ld = json.dumps({"@context":"https://schema.org","@type":"Article","headline":h1,"description":desc,"datePublished":"2026-11-25","dateModified":"2026-11-25","image":f"{BASE}social/{fname[:-5]}.png","mainEntityOfPage":f"{BASE}{fname}","author":{"@type":"Organization","name":"Post-Match Plots","url":BASE},"publisher":{"@type":"Organization","name":"Post-Match Plots","logo":{"@type":"ImageObject","url":f"{BASE}logo.svg"}},"isPartOf":{"@type":"CreativeWorkSeries","name":"United at 11 games"}}, ensure_ascii=False).replace("</","<\\/")
    nav = ''.join(
        f'<a class="card" href="{f}"{" aria-current=\"page\"" if f == fname else ""}><div class="meta">Part {n+1} &nbsp;/&nbsp; {html.escape(tag)}</div><h3 style="font-size:19px;margin:0">{html.escape(q)}</h3></a>'
        for n, (f, q, tag) in enumerate(SERIES))
    figs_html = ''.join(f'<div class="fg"><div class="num{" red" if red else ""}">{n}</div><div class="lab">{l}</div></div>' for n, l, red in figs)
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(h1)} | Post-Match Plots</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{BASE}{fname}">
<link rel="icon" type="image/svg+xml" href="logo.svg">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Post-Match Plots" href="feed.xml">
<meta property="og:type" content="article">
<meta property="article:published_time" content="2026-11-25">
<meta name="pmp:series" content="United at 11 games">
<meta name="pmp:part" content="{i+1}">
<meta name="pmp:summary" content="{html.escape(SUMMARY[fname])}">
<meta property="og:site_name" content="Post-Match Plots">
<meta property="og:title" content="{html.escape(h1)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{BASE}{fname}">
<meta property="og:image" content="{BASE}social/{fname[:-5]}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(h1)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{BASE}social/{fname[:-5]}.png">
<script type="application/ld+json">{ld}</script>
<link rel="stylesheet" href="site.css">
</head>
<body>
<header class="top"><div class="wrap">
  {LOGO}
  <nav><a href="index.html#posts">Posts</a><a href="index.html#guides">Guides</a><a href="index.html#about">About</a><a href="feed.xml">RSS</a></nav>
</div></header>

<main>
<section class="band pitchband"><div class="wrap">
  <p class="small" style="color:#c9d4cd;margin-bottom:10px">United at 11 games, part {i+1} of {len(SERIES)} &nbsp;/&nbsp; {kicker} &nbsp;/&nbsp; 25 November 2026</p>
  <h1 style="max-width:900px">{h1}</h1>
  <p class="stand">{stand}</p>
</div></section>

<section class="band" style="padding-top:0"><div class="wrap">
  <div class="figs">{figs_html}</div>
</div></section>

<article class="band" style="padding-top:8px"><div class="wrap">
{body}
</div></article>

<section class="band" style="background:var(--panel)"><div class="wrap">
  <h2>The rest of the series</h2>
  <div class="series">{nav}</div>
</div></section>
</main>

<footer class="band"><div class="wrap">
  <span>Post-Match Plots. Football, drawn with data.</span>
  <span>Data: FotMob / Opta</span>
</div></footer>

<script src="charts.js"></script>
<script>
{{
  {script}
}}
</script>
</body>
</html>
'''

posts = {}

# 1. Shot quality
posts["united-shot-quality.html"] = page(
    "united-shot-quality.html", "Why United's shots don't add up",
    "Shot quality", "Why don't United's 203 shots add up to more?",
    "Because so many of them are bad shots. United take more shots than anyone, but the average one is worth less than any other team's, and nearly half come from outside the box, where goals almost never happen.",
    [("203", "shots, most in the league", False), ("0.084", "non-penalty xG per shot, lowest in the league", True), ("46%", "of shots from outside the box, highest share", True), ("3", "goals from 93 long shots", False)],
    '''<div class="sec read">
  <h2>More shots than anyone, worth less than anyone's</h2>
  <p>Nobody has shot more than United. But divide their expected goals by their shots and they come out bottom: the average United shot is worth 0.084 xG, against a league average of 0.105.</p>
  <p>Man City take 38 fewer shots and create five more expected goals. That's the gap between working the ball into the box and having a dig because nothing else is on.</p>
</div>
<div class="chart">
  <div class="fig" id="quality"><svg role="img" aria-label="Scatter of total shots against non-penalty xG per shot for all 20 Premier League teams. United take the most shots but have the lowest xG per shot."></svg></div>
  <p class="cap">Non-penalty xG divided by total shots, all 20 PL teams. Hover a dot for the team.</p>
</div>

<div class="sec">
  <div class="post">
    <div>
      <h2>The reason: nearly half come from outside the box</h2>
      <p>United have taken 93 shots from outside the area. Nobody else has more than 65. That's 46% of all their shots, the highest share in the league, where the average is 34%. City sit at 22%.</p>
      <p>Three of those 93 have gone in, 3.2% against a league rate of 4.5%. That's roughly what the chances were worth (3.3 xG), so United aren't unlucky from distance. They're just shooting from places where goals rarely happen.</p>
      <p class="callout">Bruno Fernandes has had 21 shots from outside the box. None have gone in.</p>
    </div>
    <div class="fig tall" id="pitch"><svg role="img" aria-label="Half pitch. Inside the penalty box United have 10 goals from 110 shots. Outside it, 3 goals from 93 shots."></svg></div>
  </div>
</div>
<div class="chart">
  <h3>Shots from outside the box</h3>
  <div class="rows" id="long"></div>
  <p class="cap">All 20 PL teams. From FotMob match shot maps.</p>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>United's shot count is mostly noise. Strip out the long-range efforts and their chance creation is mid-table: 9th for non-penalty xG from inside the box, 10th for big chances. A team that settles for 25-yard shots this often is usually struggling to get the ball into the box, and that's the real problem in attack.</p>
</div>
''' + METHOD.format(extra="", detail="Shot locations and xG per shot come from the shot maps of all 110 league matches so far, with own goals left out. Team totals come from FotMob's league leaderboards."),
    TEAMS + '''
  const avg = T.reduce((a, t) => a + t[2], 0) / T.reduce((a, t) => a + t[1], 0);
  PMP.scatter(document.getElementById('quality'), {
    pts: T.map(t => ({n: t[0], x: t[1], y: t[2] / t[1], u: U(t[0]), tip: `${t[1]} shots, ${(t[2] / t[1]).toFixed(3)} npxG per shot`})),
    xr: [105, 212], yr: [0.075, 0.142], xt: [110, 130, 150, 170, 190, 210], yt: [0.08, 0.10, 0.12, 0.14],
    yf: v => v.toFixed(2), xl: 'Total shots', yl: 'Non-penalty xG per shot',
    avg, avgLabel: 'League average ' + avg.toFixed(3), label: ['Man City', 'Bournemouth', 'Brighton', "Nott'm Forest", 'Hull']
  });
  PMP.pitch(document.getElementById('pitch'), {
    inside: ['10 from 110', 'goals from shots inside the box', '9.1% scored, incl. 2 penalties'],
    outside: ['3 from 93', 'goals from shots outside the box', '3.2% scored, league 4.5%']
  });
  const L = [["Man Utd",93],["Brighton",65],["Nott'm Forest",65],["Liverpool",61],["Tottenham",60],["Newcastle",56],["Chelsea",54],["Bournemouth",54],["Leeds",49],["Ipswich",49],["Arsenal",48],["Hull",45],["Coventry",45],["Sunderland",44],["Aston Villa",44],["Everton",41],["Crystal Palace",38],["Man City",37],["Fulham",36],["Brentford",36]];
  PMP.rows(document.getElementById('long'), {rows: L.map(r => ({n: r[0], v: r[1], u: U(r[0])}))});''',
    "United take more shots than any Premier League team, but nearly half come from outside the box and the average one is worth the least.")

# 2. Finishing
posts["united-finishing-luck.html"] = page(
    "united-finishing-luck.html", "Are United unlucky in front of goal?",
    "Finishing", "Are United unlucky in front of goal?",
    "A little, but less than you'd think. United have scored about four goals fewer than their chances were worth. They're finishing big chances at exactly the league rate, and the shortfall is spread thinly across lots of players rather than one wasteful striker.",
    [("14", "goals scored", False), ("18.2", "expected goals", False), ("-4.2", "goals below xG, joint 3rd worst", True), ("32%", "of big chances scored, league 32.5%", False)],
    '''<div class="sec read">
  <h2>Four goals short, which is a lot but not unusual</h2>
  <p>United's chances were worth 18.2 goals. They've scored 14. Only Forest (-8.7) and Sunderland (-7.8) are clearly further behind, and Fulham are level with United on -4.2.</p>
</div>
<div class="chart">
  <h3>Goals minus expected goals</h3>
  <div class="rows" id="gxg"></div>
  <p class="cap">All 20 PL teams, 2026/27 to 24 November. Positive means scoring more than the chances were worth.</p>
</div>

<div class="sec read">
  <h2>The big chances are going in</h2>
  <p>United have had 28 big chances and missed 19, so they've scored 32% of them. The league as a whole scores 32.5%. The clear-cut ones are going in at a perfectly normal rate. The gap is in the harder chances: about 9 of United's 14 goals came from big chances, leaving roughly 5 from everything else.</p>
</div>

<div class="sec read">
  <h2>No single culprit</h2>
  <p>Look player by player and almost everyone is a little under. The regulars are close to par; it's the players coming off the bench who've been wasteful.</p>
  <div class="scroll"><table>
    <thead><tr><th>Player</th><th>Goals</th><th>xG</th><th>Difference</th></tr></thead>
    <tbody>
      <tr><td>Bryan Mbeumo</td><td>4</td><td>4.6</td><td class="down">-0.6</td></tr>
      <tr><td>Bruno Fernandes</td><td>4 (2 pens)</td><td>4.4</td><td class="down">-0.4</td></tr>
      <tr><td>Matheus Cunha</td><td>1</td><td>1.5</td><td class="down">-0.5</td></tr>
      <tr><td>Amad Diallo</td><td>0</td><td>~1.1</td><td class="down">-1.1</td></tr>
      <tr><td>Patrick Dorgu</td><td>1</td><td>~1.1</td><td class="down">-0.1</td></tr>
      <tr><td>Youri Tielemans</td><td>1</td><td>1.0</td><td>0.0</td></tr>
      <tr><td>Mason Mount</td><td>0</td><td>~0.9</td><td class="down">-0.9</td></tr>
      <tr><td>Marcus Rashford</td><td>0</td><td>~0.8</td><td class="down">-0.8</td></tr>
      <tr><td>Joshua Zirkzee</td><td>1</td><td>~0.6</td><td class="up">+0.4</td></tr>
      <tr><td>Benjamin Šeško</td><td>1</td><td>~0.4</td><td class="up">+0.6</td></tr>
    </tbody>
  </table></div>
  <p class="small" style="margin-top:8px">Values marked ~ are worked out from per-90 figures and minutes, so they're approximate. United's 14 includes one own goal.</p>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>Yes, slightly. Four goals spread across ten players is the kind of shortfall that usually evens out, and it's worth a few points over a season. But it doesn't explain 19th. The bigger problems are the quality of chances United create and the quality of the ones they give away.</p>
</div>
''' + METHOD.format(extra="", detail="Team goals, xG and big chances come from FotMob's league leaderboards; player xG from player leaderboards."),
    '''const G = [["Chelsea",5.4],["Brighton",4.4],["Brentford",2.8],["Newcastle",1.8],["Hull",1.7],["Coventry",1.4],["Ipswich",1.0],["Man City",0.1],["Arsenal",-0.6],["Aston Villa",-0.8],["Leeds",-2.0],["Everton",-2.1],["Liverpool",-2.2],["Bournemouth",-2.9],["Tottenham",-3.1],["Crystal Palace",-3.5],["Fulham",-4.2],["Man Utd",-4.2],["Sunderland",-7.8],["Nott'm Forest",-8.7]];
  PMP.diverge(document.getElementById('gxg'), {rows: G.map(r => ({n: r[0], v: r[1], u: r[0] === 'Man Utd'}))});''',
    "Manchester United have scored about four goals fewer than their xG. Here's whether that's bad luck or bad finishing.")

# 3. Chances conceded
posts["united-chances-conceded.html"] = page(
    "united-chances-conceded.html", "Why United concede so many",
    "Defending", "Why do United concede so many goals from so few shots?",
    "Because the shots they allow are the best in the league. United face an average number of shots, but each one is worth more than against any other team. Opponents are walking into the box in normal open play, not just catching United on the break.",
    [("146", "shots conceded, league average 149", False), ("0.153", "xG per shot conceded, highest in the league", True), ("22.2", "xG conceded, 2nd most", True), ("23", "goals conceded, 2nd most", True)],
    '''<div class="sec read">
  <h2>Not many shots, but very good ones</h2>
  <p>United have faced 146 shots, bang on the league average. But the shots they allow are worth 0.153 xG each, the highest in the league. Opponents barely bother shooting from distance against them (4th fewest long shots faced) because they don't need to.</p>
  <p>Put that next to the attack and United are doing the reverse of what works: they take bad shots and give up good ones. Only Crystal Palace, who are bottom, have conceded more expected goals.</p>
</div>
<div class="chart">
  <div class="fig" id="forag"><svg role="img" aria-label="Scatter of xG created against xG conceded for all 20 PL teams. United create 18.2 and concede 22.2, the second-highest."></svg></div>
  <div class="key"><span><i style="background:#e3343a"></i>Manchester United</span><span><i style="background:#5d6b63"></i>Other PL teams</span><span>Further right creates more, lower concedes less</span></div>
</div>

<div class="sec">
  <div class="post">
    <div>
      <h2>It isn't mainly counter-attacks</h2>
      <p>The obvious theory is that United push up and get caught on the break. The shot maps don't really back that up. Only 2.9 xG has come from fast breaks against them, and they've conceded once that way.</p>
      <p>Most of the damage is in normal open play: 84 shots worth 12.0 xG, and 12 goals. That points more to how United defend their own box than to how they defend transitions. Set pieces are the other leak, which gets its own post.</p>
    </div>
    <div>
      <h3>Where United's xG conceded comes from</h3>
      <div class="rows" id="sit"></div>
      <p class="cap">xG conceded by situation, from FotMob shot maps of United's 11 league games.</p>
    </div>
  </div>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>United's problem isn't how often teams shoot, it's where from. Opponents are getting clean looks inside the box in ordinary open play. Shots conceded is an average number; chance quality conceded is the worst in the league. That, more than the finishing, is why they're 19th.</p>
</div>
''' + METHOD.format(extra="", detail="Shots and xG conceded, situations and shot locations come from FotMob match shot maps, with own goals left out. Team totals come from FotMob's league leaderboards."),
    TEAMS + '''
  PMP.scatter(document.getElementById('forag'), {
    pts: T.map(t => ({n: t[0], x: t[3], y: t[4], u: U(t[0]), tip: `${t[3]} xG for, ${t[4]} against`})),
    xr: [10, 23.5], yr: [8, 25.5], xt: [10, 12, 14, 16, 18, 20, 22], yt: [10, 15, 20, 25],
    xl: 'xG created', yl: 'xG conceded', label: ['Arsenal', 'Man City', 'Crystal Palace', 'Ipswich']
  });
  const S = [["Open play",12.0,1],["Fast breaks",2.9,0],["Set pieces",2.8,0],["Corners",2.1,0],["Penalties",1.6,0],["Throw-ins",0.6,0],["Free kicks",0.2,0],["Solo runs",0.2,0]];
  PMP.rows(document.getElementById('sit'), {rows: S.map(r => ({n: r[0], v: r[1], u: r[2]})), f: v => v.toFixed(1)});''',
    "Manchester United face an average number of shots but concede the best chances in the Premier League. Here's where they come from.")

# 4. Set pieces
posts["united-set-pieces.html"] = page(
    "united-set-pieces.html", "United's set-piece problem",
    "Set pieces", "How much are set pieces costing United?",
    "About six goals. United have scored one set-piece goal and conceded seven, the worst record in the league by a distance. That's two-thirds of their entire goal difference, and the aerial numbers show why.",
    [("1", "set-piece goal scored", False), ("7", "set-piece goals conceded, most in the league", True), ("-6", "set-piece goal difference, next worst is -3", True), ("2/3", "of United's -9 goal difference", False)],
    '''<div class="sec">
  <div class="post">
    <div>
      <h2>Worst in the league, by a distance</h2>
      <p>United have scored one set-piece goal and conceded seven. The next worst teams are at -3, so United are twice as bad as anyone else. Six goals is two-thirds of their whole -9 goal difference.</p>
      <p>Their own corners aren't working either: 39 shots from corners, worth 2.0 xG between them, and one goal.</p>
    </div>
    <div>
      <h3>Set-piece goal difference</h3>
      <div class="rows" id="sp"></div>
    </div>
  </div>
</div>

<div class="sec">
  <div class="post">
    <div>
      <h2>One man winning headers</h2>
      <p>Harry Maguire wins 73% of his aerial duels, top 10% for a Premier League centre-back. After him it falls off a cliff. Lisandro Martínez is in the bottom 10% of centre-backs for headers won, and Bryan Mbeumo, Matheus Cunha and Bruno Fernandes all win almost nothing in the air for their positions.</p>
      <p>That matters at both ends: no one to aim at when United have a corner, and not enough height when they're defending one.</p>
    </div>
    <div>
      <h3>Aerial win %, percentile for position</h3>
      <div class="rows" id="aer"></div>
      <p class="cap">Against PL players in the same position with 450+ minutes. 50 is the league median.</p>
    </div>
  </div>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>Roughly six goals in eleven games, which on its own is the difference between 19th and mid-table. Unlike the finishing, this isn't bad luck: it's a squad short of aerial presence and a set-piece routine that isn't creating anything. It's also the quickest problem to fix, whether with a coach, a centre-back or both.</p>
</div>
''' + METHOD.format(extra="", detail="Set-piece goals come from FotMob's team leaderboards and match shot maps. Aerial duel figures come from individual FotMob player pages, ranked against players with 450+ league minutes in the same position."),
    '''const S = [["Brentford",5],["Leeds",5],["Man City",3],["Brighton",3],["Hull",3],["Liverpool",2],["Fulham",0],["Tottenham",0],["Aston Villa",0],["Everton",0],["Newcastle",0],["Sunderland",-1],["Chelsea",-1],["Coventry",-1],["Bournemouth",-2],["Arsenal",-2],["Ipswich",-2],["Nott'm Forest",-3],["Crystal Palace",-3],["Man Utd",-6]];
  PMP.diverge(document.getElementById('sp'), {rows: S.map(r => ({n: r[0], v: r[1], u: r[0] === 'Man Utd'}))});
  const A = [["Maguire",91],["Dalot",78],["Mainoo",48],["Tielemans",30],["Martínez",16],["Fernandes",10],["Cunha",5],["Mbeumo",2]];
  PMP.rows(document.getElementById('aer'), {rows: A.map(r => ({n: r[0], v: r[1], u: false})), max: 100});''',
    "Manchester United have the worst set-piece record in the Premier League: one scored, seven conceded. Here's what it's costing them.")

# 5. Bruno
posts["bruno-fernandes-decline.html"] = page(
    "bruno-fernandes-decline.html", "Is Bruno getting worse?",
    "Bruno", "Is Bruno Fernandes getting worse?",
    "At creating, yes. At scoring, no. He's making far fewer chances than last season and doing much less without the ball, while shooting more, mostly from distance. But last season's 21 assists were never repeatable, so the drop looks bigger than it is.",
    [("0.40", "big chances created per 90, down from 0.97", True), ("-36%", "xA per 90 against last season", True), ("3.5", "shots per 90, up from 2.5", False), ("21", "assists last season from 12.3 xA", False)],
    '''<div class="sec read">
  <h2>Less creating, more shooting</h2>
  <p>Last season he created about one big chance a game. This season it's under half that. His chances created are down 30% and his xA is down 36%. He's shooting more instead, 3.5 a game against 2.5, and 21 of his roughly 35 shots have come from outside the box, none of them goals. He's also doing a lot less without the ball: his defensive actions have dropped from the 86th percentile to the 32nd.</p>
</div>
<div class="chart">
  <div class="key" style="margin-bottom:6px"><span><i style="border:2px solid #9aa79f;background:transparent"></i>2025/26</span><span><i style="background:#e3343a"></i>2026/27, down 10+ points</span><span><i style="background:#c9d4cd"></i>2026/27, other</span></div>
  <div class="rows" id="bruno" role="img" aria-label="Bruno Fernandes's percentiles among PL attacking midfielders and wingers, 2025/26 against 2026/27. Big chances created fell from 99 to 60, defensive actions from 86 to 32, recoveries from 91 to 56, assists from 99 to 64. Shots rose from 85 to 98."></div>
  <p class="cap">Percentile against PL attacking midfielders and wingers with 450+ minutes that season (98 players last season, 49 this). Each row runs from last season to this one.</p>
</div>

<div class="sec read">
  <h2>Last season was too good to last</h2>
  <p>Before anyone writes him off: last season's 21 assists came from 12.3 xA, which means teammates scored far more of his chances than you'd ever expect. That wasn't going to happen twice. At last season's creation rate he'd have about 3.5 assists by now rather than 2. The drop is real, just not as dramatic as the headline numbers make it look.</p>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>He's a less creative, less active player than a year ago, and more of a shooter. Whether that's a change of role, with Cunha and Mbeumo taking more of the creative load, or simply that he's 32, is something the data can't tell you. Ten games is a short run, so this is one to check again at Christmas.</p>
</div>
''' + METHOD.format(extra=", and 2025/26 for comparison", detail="Per-90 figures come from FotMob's league leaderboards for both seasons; long shots from match shot maps. Percentiles compare him with PL attacking midfielders and wingers with 450+ minutes that season."),
    '''PMP.dumbbell(document.getElementById('bruno'), {
    rows: [
      {n: 'Shots', a: 85, b: 98}, {n: 'xG', a: 89, b: 97}, {n: 'Chances created', a: 99, b: 92},
      {n: 'xA', a: 98, b: 83}, {n: 'Assists', a: 99, b: 64}, {n: 'Big chances created', a: 99, b: 60},
      {n: 'Recoveries', a: 91, b: 56}, {n: 'Non-pen goals', a: 49, b: 56}, {n: 'Defensive actions', a: 86, b: 32}, {n: 'Sprints', a: 29, b: 7}
    ]
  });''',
    "Bruno Fernandes is creating far fewer chances than last season and shooting more. Here's how much is decline and how much was a freak season.")

# 6. Expected points
posts["united-expected-points.html"] = page(
    "united-expected-points.html", "Where should United be?",
    "Expected points", "So where should United actually be?",
    "About 15th, with 13 points rather than 8. Replay every match from the quality of its chances and United have dropped around five points more than they deserved, the third-biggest shortfall in the league. But 15th is still poor: bad luck explains the gap to the bottom three, not the gap to the top half.",
    [("8", "points, 19th in the table", True), ("12.9", "expected points, 15th", False), ("-4.9", "points below expected, 3rd biggest shortfall", True), ("0", "points from the 2-0 at Hull, where they were 55% to win", False)],
    """<div class="sec read">
  <h2>How expected points works</h2>
  <p>Every shot has an xG: the chance a shot like it goes in. Treat each shot in a match as its own roll of the dice, work out the odds of every possible scoreline, and you get each team's chance of winning, drawing and losing. Three points for each win chance plus one for each draw chance gives the points a performance was "worth". Add them up over 11 games and you get a table of how teams have played, not how the dice landed.</p>
</div>
<div class="chart">
  <h3>Actual points against expected points, all 20 teams</h3>
  <div class="key" style="margin-bottom:6px"><span><i style="border:2px solid #9aa79f;background:transparent"></i>Expected points</span><span><i style="background:#c9d4cd"></i>Actual points</span><span><i style="background:#e3343a"></i>Manchester United</span></div>
  <div class="rows" id="xpts" role="img" aria-label="Expected against actual points for all 20 PL teams, sorted by expected points. United have 12.9 expected points, 15th, but 8 actual points."></div>
  <p class="cap">Sorted by expected points. Actual points from the official table.</p>
</div>
<div class="read">
  <p>Arsenal are the opposite story: 28 points from chances worth 21, the luckiest side in the league. Forest (-7.4) and Sunderland (-5.7) are the only teams who've been hit harder than United.</p>
</div>

<div class="sec">
  <div class="post">
    <div>
      <h2>Where the points went</h2>
      <p>Most of United's missing points come from three games. They lost 2-0 at Hull in a match they'd have won 55% of the time on the chances. They lost 1-0 at home to City in what was close to a coin toss. And they drew 4-4 with Villa in a game they were more likely to win than not.</p>
      <p>It hasn't all gone against them. The 1-1 with Tottenham was a point they barely deserved: they'd have won that game only 16% of the time.</p>
      <p>The rest went roughly as the chances said. United were well beaten at Liverpool, Chelsea and at home to Bournemouth, and no amount of luck changes those.</p>
    </div>
    <div>
      <h3>United, match by match</h3>
      <div class="rows" id="matches" role="img" aria-label="United's expected against actual points in each of their 11 league games."></div>
      <p class="cap">Hollow: expected points from the chances. Filled: points actually won.</p>
    </div>
  </div>
</div>

<div class="sec read">
  <h2>The answer</h2>
  <p>United are a 15th-placed team having a 19th-placed season. Some of the gap will close as the finishing evens out, as part 2 showed. But the long shots, the chances they give away and the set pieces are already baked into these numbers, and expected points can't rescue those. Waiting for luck gets United to 15th. Getting higher means fixing the things the rest of this series is about.</p>
</div>
""" + METHOD.format(extra="", detail="Expected points come from the shot maps of all 110 league matches so far: each team's shots are treated as independent chances with a probability equal to their xG, and every scoreline's odds are worked out exactly. Own goals are left out of expected points. Actual points come from the official table, because a few shot maps are missing a goal."),
    """const X = [["Arsenal",21.4,28],["Man City",21.3,22],["Bournemouth",19.9,18],["Brighton",19.0,22],["Leeds",18.0,17],["Liverpool",17.3,21],["Tottenham",17.0,15],["Nott'm Forest",16.4,9],["Brentford",16.2,17],["Sunderland",14.7,9],["Fulham",14.5,11],["Everton",13.7,16],["Aston Villa",13.6,14],["Chelsea",13.1,16],["Man Utd",12.9,8],["Coventry",11.4,12],["Newcastle",11.3,13],["Ipswich",10.9,11],["Hull",10.6,14],["Crystal Palace",10.6,7]];
  const f1 = v => Number.isInteger(v) ? String(v) : v.toFixed(1);
  PMP.dumbbell(document.getElementById('xpts'), {rows: X.map(r => ({n: r[0], a: r[1], b: r[2], u: r[0] === 'Man Utd'})), max: 30, ticks: [0, 10, 20, 30], fmt: f1, fmtA: v => v.toFixed(1), hi: true});
  const M = [["Hull (a) 0-2",1.90,0],["Ipswich (h) 5-2",2.84,3],["Everton (a) 2-2",1.06,1],["Man City (h) 0-1",1.22,0],["Fulham (a) 1-1",1.33,1],["Tottenham (h) 1-1",0.73,1],["Leeds (a) 1-1",0.95,1],["Bournemouth (h) 0-3",0.69,0],["Chelsea (a) 0-2",0.37,0],["Aston Villa (h) 4-4",1.77,1],["Liverpool (a) 0-4",0.06,0]];
  PMP.dumbbell(document.getElementById('matches'), {rows: M.map(r => ({n: r[0], a: r[1], b: r[2], u: r[2] < r[1] - 0.75})), max: 3, ticks: [0, 1, 2, 3], fmt: f1, fmtA: v => v.toFixed(1), hi: true});""",
    "Replay every match from its chances and Manchester United should have 13 points, not 8. Where the points went, and why that only gets them to 15th.")

for f, s in posts.items():
    open(f"{OUT}/{f}", "w").write(s)
print("wrote", len(posts))
