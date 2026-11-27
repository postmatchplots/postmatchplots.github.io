// Pulls one United match from FotMob for a "Match in one chart" post.
// Run in a browser tab on fotmob.com (devtools console, or Claude's built-in browser).
// Set URL to the match page, run it, and save what it returns as data/<anything>.json
// outside this repo (raw data never goes on the site). Then run scripts/build_match_post.py.
const URL = 'https://www.fotmob.com/en-GB/matches/liverpool-vs-manchester-united/2ygkcb';
const UTD = 10260;
const h = await fetch(URL).then(r => r.text());
const j = JSON.parse(h.match(/<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s)[1]);
const pp = j.props.pageProps, c = pp.content, g = pp.general;
const uh = g.homeTeam.id === UTD;
const evs = c.matchFacts.events.events;
const top = {};
for (const s of (c.stats?.Periods?.All?.stats?.find(x => x.key === 'top_stats' || x.title === 'Top stats')?.stats || []))
  if (Array.isArray(s.stats)) top[s.key || s.title] = uh ? s.stats : [s.stats[1], s.stats[0]];
JSON.stringify({
  url: URL,
  date: g.matchTimeUTCDate.slice(0, 10),
  round: g.matchRound,
  home: uh, opp: (uh ? g.awayTeam : g.homeTeam).name,
  goals: evs.filter(e => e.type === 'Goal').map(e => ({t: e.time, add: e.overloadTime || 0, utd: e.isHome === uh, n: e.nameStr, og: !!e.ownGoal})),
  reds: evs.filter(e => e.type === 'Card' && (e.card === 'Red' || e.card === 'YellowRed')).map(e => ({t: e.time, utd: e.isHome === uh, n: e.nameStr})),
  shots: c.shotmap.shots.map(s => ({t: s.min, add: s.minAdded || 0, utd: s.teamId === UTD, x: +s.x.toFixed(1), y: +s.y.toFixed(1), xg: +(s.expectedGoals || 0).toFixed(3), r: s.eventType, n: s.playerName, sit: s.situation, og: s.isOwnGoal, ot: s.isOnTarget})),
  top
});
