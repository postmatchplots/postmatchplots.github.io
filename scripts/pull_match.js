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
// ---- Star performer: United's best-rated outfielder (60+ minutes), unless STAR names someone.
// His numbers from the match, beside his own season average per 90 (and, as a fallback for players
// with few minutes, the average per 90 of PL players in his position group with 450+ minutes).
// A player missing from a list has a genuine zero, except for rates and tracking data.
const STAR = '';  // e.g. 'Kobbie Mainoo' to choose the player yourself
const SEASON = 36781;
const groupOf = c => c === 11 ? 'GK' : c >= 33 && c <= 37 ? 'CB' : [32, 38, 51, 59, 62, 68, 71, 79].includes(c) ? 'FB'
  : (c >= 63 && c <= 67) || (c >= 72 && c <= 78) ? 'CM' : (c >= 82 && c <= 88) || c === 103 || c === 107 ? 'AM/W' : c >= 100 ? 'ST' : null;
// slice label, FotMob leaderboard (#sub = use its second figure: chances created keeps per 90 there), match value, slice group, is-a-rate
const SL = {
  goals: ['Goals', 'goals_per_90', s => s['Goals'], 'att'],
  xg: ['xG', 'expected_goals_per_90', s => s['Expected goals (xG)'], 'att'],
  shots: ['Shots', 'total_scoring_att', s => s['Total shots'], 'att'],
  xa: ['xA', 'expected_assists_per_90', s => s['Expected assists (xA)'], 'att'],
  chances: ['Chances created', 'total_att_assist#sub', s => s['Chances created'], 'att'],
  dribbles: ['Dribbles', 'won_contest', s => s['Successful dribbles'], 'pos'],
  passes: ['Passes completed', 'accurate_pass', s => s['Accurate passes'], 'pos'],
  passpct: ['Pass accuracy', 'accurate_pass#sub', s => s['Accurate passes#total'] ? 100 * s['Accurate passes'] / s['Accurate passes#total'] : null, 'pos', true],
  longballs: ['Long balls', 'accurate_long_balls', s => s['Accurate long balls'], 'pos'],
  tackles: ['Tackles', 'total_tackle', s => s['Tackles'], 'def'],
  ints: ['Interceptions', 'interception', s => s['Interceptions'], 'def'],
  clears: ['Clearances', 'effective_clearance', s => s['Clearances'], 'def'],
  blocks: ['Blocks', 'outfielder_block', s => s['Blocks'], 'def'],
  recov: ['Recoveries', 'ball_recovery', s => s['Recoveries'], 'def'],
  defacts: ['Defensive actions', 'defensive_contributions', s => s['Defensive actions'], 'def'],
  sprints: ['Sprints', 'phys_sprints_per_90', s => s['Number of sprints'], 'phy'],
  km: ['Distance covered', 'phys_tdc_per_90', s => s['Distance covered'], 'phy'],
};
const TEMPLATE = {
  'ST': ['goals', 'xg', 'shots', 'xa', 'chances', 'dribbles', 'passes', 'passpct', 'recov', 'defacts', 'sprints', 'km'],
  'AM/W': ['goals', 'xg', 'shots', 'xa', 'chances', 'dribbles', 'passes', 'passpct', 'recov', 'defacts', 'sprints', 'km'],
  'CM': ['xg', 'shots', 'xa', 'chances', 'dribbles', 'passes', 'passpct', 'tackles', 'ints', 'recov', 'defacts', 'km'],
  'FB': ['xa', 'chances', 'dribbles', 'passes', 'passpct', 'tackles', 'ints', 'clears', 'recov', 'defacts', 'sprints', 'km'],
  'CB': ['passes', 'passpct', 'longballs', 'tackles', 'ints', 'clears', 'blocks', 'recov', 'defacts', 'sprints', 'km'],
};
const flat = p => { const o = {}; for (const g of p.stats || []) for (const [k, v] of Object.entries(g.stats || {})) { if (v?.stat?.value != null && o[k] == null) { o[k] = v.stat.value; if (v.stat.total != null) o[k + '#total'] = v.stat.total; } } return o; };
const mine = Object.values(c.playerStats || {}).filter(p => p.teamId === UTD && !p.isGoalkeeper).map(p => ({p, s: flat(p)}));
const pick = STAR ? mine.find(x => x.p.name === STAR) : mine.filter(x => (x.s['Minutes played'] || 0) >= 60).sort((a, b) => (b.s['FotMob rating'] || 0) - (a.s['FotMob rating'] || 0))[0];
let star = null;
if (pick) {
  const grp = groupOf(pick.p.positionId) || groupOf(pick.p.usualPosition?.[0] ?? pick.p.usualPosition);
  const keys = TEMPLATE[grp] || TEMPLATE['CM'];
  const board = async s => (await fetch(`https://data.fotmob.com/stats/47/season/${SEASON}/${s}.json`).then(r => r.json())).TopLists[0].StatList;
  const minsList = await board('mins_played');
  const pool = minsList.filter(x => x.MinutesPlayed >= 450 && groupOf(x.Positions?.[0]) === grp).map(x => x.ParticiantId);
  const pid = Number(pick.p.id), seasonMins = minsList.find(x => x.ParticiantId === pid)?.MinutesPlayed || 0;
  const mins = pick.s['Minutes played'];
  const slices = [];
  for (const k of keys) {
    const [lab, stat, read, cat, isRate] = SL[k];
    const [name, sub] = stat.split('#');
    const list = await board(name);
    const by = Object.fromEntries(list.map(x => [x.ParticiantId, sub ? x.SubStatValue : x.StatValue]));
    const raw = read(pick.s) ?? 0;
    const val = isRate ? raw : raw * 90 / mins;
    // Missing from a list: a genuine zero for counts, but not for rates or tracking data (not every player is tracked)
    const others = pool.map(id => by[id] ?? (isRate || name.startsWith('phys_') ? null : 0)).filter(v => v != null);
    const avg = others.length ? others.reduce((a, v) => a + v, 0) / others.length : null;
    const own = by[pid] ?? (isRate || name.startsWith('phys_') || !seasonMins ? null : 0);
    slices.push({k, lab, cat, raw: +(+raw).toFixed(2), p90: +val.toFixed(2), own90: own == null ? null : +(+own).toFixed(3), avg90: avg == null ? null : +avg.toFixed(3), isRate: !!isRate});
  }
  star = {n: pick.p.name, grp, mins, seasonMins, rating: pick.s['FotMob rating'], pool: pool.length, slices};
}

JSON.stringify({
  star,
  url: URL,
  date: g.matchTimeUTCDate.slice(0, 10),
  round: g.matchRound,
  home: uh, opp: (uh ? g.awayTeam : g.homeTeam).name,
  goals: evs.filter(e => e.type === 'Goal').map(e => ({t: e.time, add: e.overloadTime || 0, utd: e.isHome === uh, n: e.nameStr, og: !!e.ownGoal})),
  reds: evs.filter(e => e.type === 'Card' && (e.card === 'Red' || e.card === 'YellowRed')).map(e => ({t: e.time, utd: e.isHome === uh, n: e.nameStr})),
  shots: c.shotmap.shots.map(s => ({t: s.min, add: s.minAdded || 0, utd: s.teamId === UTD, x: +s.x.toFixed(1), y: +s.y.toFixed(1), xg: +(s.expectedGoals || 0).toFixed(3), r: s.eventType, n: s.playerName, sit: s.situation, og: s.isOwnGoal, ot: s.isOnTarget})),
  top
});
