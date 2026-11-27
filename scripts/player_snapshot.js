// Every number behind a United player post (first used for kobbie-mainoo.html), in one pull.
// Run in a browser tab on fotmob.com (devtools console, or Claude's built-in browser).
// Returns JSON. Keep it OUTSIDE this repo: raw data never goes on the site.
//
// What it gives you:
//  - player: his per-90 numbers, rank and percentile in his position group (450+ league minutes),
//    including line-breaking passes from every group member's player page
//    Percentile = the share of the group below him, counting ties as half (so the top of 47 is 99).
//  - scatter: every player in the group with completed passes and recoveries per 90
//  - onoff: United's xG and goals per 90 with him on and off the pitch, for every minute and for
//    11 v 11 only (every minute after a red card for either side removed)
//  - table: United's league position and points
const PLAYER = 1292810;   // FotMob player id (Kobbie Mainoo)
const UTD = 10260, SEASON = 36781, MIN_MINS = 450;
const groupOf = c => c === 11 ? 'GK' : c >= 33 && c <= 37 ? 'CB' : [32, 38, 51, 59, 62, 68, 71, 79].includes(c) ? 'FB'
  : (c >= 63 && c <= 67) || (c >= 72 && c <= 78) ? 'CM' : (c >= 82 && c <= 88) || c === 103 || c === 107 ? 'AM/W' : c >= 100 ? 'ST' : null;
const page = async u => JSON.parse((await fetch(u).then(r => r.text())).match(/<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s)[1]);
const board = async s => (await fetch(`https://data.fotmob.com/stats/47/season/${SEASON}/${s}.json`).then(r => r.json())).TopLists[0].StatList;

// ---- league numbers for his position group
// [label, leaderboard, use SubStatValue?, missing counts as zero?]
const STATS = [
  ['Pass accuracy', 'accurate_pass', true, false], ['Passes completed', 'accurate_pass', false, true],
  ['Dribbles', 'won_contest', false, true], ['Dribble success', 'won_contest', true, false],
  ['Ball recoveries', 'ball_recovery', false, true], ['Defensive actions', 'defensive_contributions', false, true],
  ['Interceptions', 'interception', false, true], ['Tackles', 'total_tackle', false, true],
  ['xA', 'expected_assists_per_90', false, true], ['Shots', 'total_scoring_att', false, true],
  ['xG', 'expected_goals_per_90', false, true], ['Big chances created', 'big_chance_created', false, true],
  ['Distance covered', 'phys_tdc_per_90', false, false], ['Sprints', 'phys_sprints_per_90', false, true],
  ['Goals', 'goals', false, true], ['Chances created', 'total_att_assist', true, true],
];
const minsList = await board('mins_played');
const me = minsList.find(x => x.ParticiantId === PLAYER);
const grp = groupOf(me.Positions?.[0]);
const pool = minsList.filter(x => x.MinutesPlayed >= MIN_MINS && groupOf(x.Positions?.[0]) === grp);
const ids = pool.map(x => x.ParticiantId);
const cache = {};
const player = {name: me.ParticipantName, group: grp, minutes: me.MinutesPlayed, apps: me.MatchesPlayed, groupSize: ids.length, stats: {}};
for (const [lab, s, sub, zero] of STATS) {
  cache[s] ??= await board(s);
  // goals and big_chance_created hold season totals: turn them into per 90 like the rest
  const total = s === 'goals' || s === 'big_chance_created';
  const by = Object.fromEntries(cache[s].map(x => [x.ParticiantId, total ? x.StatValue * 90 / x.MinutesPlayed : sub ? x.SubStatValue : x.StatValue]));
  const vals = ids.map(id => by[id] ?? (zero ? 0 : null)).filter(v => v != null);
  const mine = by[PLAYER] ?? (zero ? 0 : null);
  if (mine == null) { player.stats[lab] = null; continue; }
  const below = vals.filter(v => v < mine).length, same = vals.filter(v => v === mine).length;
  player.stats[lab] = {value: +(+mine).toFixed(3), rank: 1 + vals.filter(v => v > mine).length, outOf: vals.length,
    percentile: Math.round(100 * (below + 0.5 * same) / vals.length)};
}
// Line-breaking passes aren't in the league lists: read them from each player's page (per 90)
const lb = {};
await Promise.all(ids.map(async id => {
  try {
    const t = JSON.stringify((await page(`https://www.fotmob.com/en-GB/players/${id}`)).props.pageProps);
    const m = t.match(/"localizedTitleId":"line_breaking_passes","per90":([\d.]+)/);
    if (m) lb[id] = +m[1];
  } catch (e) { /* page didn't load: left out */ }
}));
if (lb[PLAYER] != null) {
  const vals = Object.values(lb), mine = lb[PLAYER];
  player.stats['Line-breaking passes'] = {value: +mine.toFixed(3), rank: 1 + vals.filter(v => v > mine).length, outOf: vals.length,
    percentile: Math.round(100 * (vals.filter(v => v < mine).length + 0.5 * vals.filter(v => v === mine).length) / vals.length)};
}
const pass = Object.fromEntries(cache['accurate_pass'].map(x => [x.ParticiantId, x.StatValue]));
const rec = Object.fromEntries(cache['ball_recovery'].map(x => [x.ParticiantId, x.StatValue]));
const scatter = pool.map(x => [x.ParticipantName, pass[x.ParticiantId] ?? 0, rec[x.ParticiantId] ?? 0]);

// ---- on/off for every United league game so far
const team = await page('https://www.fotmob.com/en-GB/teams/10260/fixtures/manchester-united');
const fixtures = team.props.pageProps.fallback['team-10260'].fixtures.allFixtures.fixtures
  .filter(f => f.tournament?.leagueId === 47 && f.status?.finished);
const games = [];
for (const f of fixtures) {
  const j = await page('https://www.fotmob.com/en-GB' + f.pageUrl.split('#')[0]);
  const c = j.props.pageProps.content, g = j.props.pageProps.general;
  const uh = g.homeTeam.id === UTD, side = uh ? c.lineup.homeTeam : c.lineup.awayTeam;
  const evs = c.matchFacts.events.events;
  let on = side.starters.some(p => p.id === PLAYER) ? 0 : null, off = null;
  for (const e of evs) {
    if (e.type === 'Substitution' && e.isHome === uh) {
      if (Number(e.swap?.[0]?.id) === PLAYER) on = e.time;   // swap[0] comes on
      if (Number(e.swap?.[1]?.id) === PLAYER) off = e.time;  // swap[1] goes off
    }
    if (e.type === 'Card' && (e.card === 'Red' || e.card === 'YellowRed') && Number(e.player?.id) === PLAYER) off = e.time;
  }
  games.push({opp: (uh ? g.awayTeam : g.homeTeam).name, date: g.matchTimeUTCDate.slice(0, 10), on, off,
    reds: evs.filter(e => e.type === 'Card' && (e.card === 'Red' || e.card === 'YellowRed')).map(e => ({t: e.time, utd: e.isHome === uh, n: e.nameStr})),
    goals: evs.filter(e => e.type === 'Goal').map(e => [Math.min(e.time, 89), e.isHome === uh]),  // isHome = scoring side; scores on the event are BEFORE the goal
    shots: c.shotmap.shots.filter(s => !s.isOwnGoal).map(s => [Math.min(s.min, 89), s.teamId === UTD, s.expectedGoals || 0])});
}
const split = mode => {
  const S = {on: {min: 0, xf: 0, xa: 0, gf: 0, ga: 0}, off: {min: 0, xf: 0, xa: 0, gf: 0, ga: 0}};
  for (const m of games) {
    const end = m.off ?? 91;
    const cut = mode === 'all' ? 999 : Math.min(999, ...m.reds.map(r => r.t));
    const st = t => t >= cut ? null : (m.on != null && m.on <= t && t < end ? 'on' : 'off');
    for (let t = 0; t < 90; t++) { const s = st(t); if (s) S[s].min++; }
    for (const [t, u, x] of m.shots) { const s = st(t); if (s) S[s][u ? 'xf' : 'xa'] += x; }
    for (const [t, u] of m.goals) { const s = st(t); if (s) S[s][u ? 'gf' : 'ga']++; }
  }
  const r = v => ({minutes: v.min, xgFor90: +(v.xf * 90 / v.min).toFixed(2), xgAgainst90: +(v.xa * 90 / v.min).toFixed(2),
    xgDiff90: +((v.xf - v.xa) * 90 / v.min).toFixed(2), goals: `${v.gf}-${v.ga}`});
  return {with: r(S.on), without: r(S.off)};
};
const onoff = {games: games.length, minutesCheck: games.reduce((a, m) => a + (m.on == null ? 0 : Math.min(m.off ?? 90, 90) - m.on), 0),
  every: split('all'), elevenVeleven: split('any'),
  redsWhileOn: games.flatMap(m => m.reds.filter(r => m.on != null && r.t >= m.on && r.t < (m.off ?? 91)).map(r => `${r.n} (${r.utd ? 'United' : m.opp}) ${r.t}', ${m.off ?? 90} - ${r.t} min left for him`))};

// ---- league table
const tbl = (await page('https://www.fotmob.com/en-GB/leagues/47/table/premier-league')).props.pageProps.table[0].data.table.all;
const u = tbl.find(r => r.id === UTD);

JSON.stringify({pulled: new Date().toISOString().slice(0, 10), lastGame: games.at(-1)?.date, player, onoff,
  table: {position: u.idx, points: u.pts, played: u.played}, scatter});
