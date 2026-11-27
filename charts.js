/* Small hand-drawn SVG charts for Post-Match Plots. No libraries. */
window.PMP = (() => {
  const NS = 'http://www.w3.org/2000/svg';
  const esc = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const RED = '#e3343a', GREY = '#5d6b63', LINE = 'rgba(238,242,238,.55)', RULE = '#24302a';

  function watch(el, draw) {
    const s = el.querySelector('svg');
    const run = () => { const W = s.clientWidth, H = s.clientHeight; if (W && H) s.innerHTML = draw(W, H); };
    const ro = new ResizeObserver(run); ro.observe(s); run();
  }

  /* Half pitch, goal at the top, penalty box and the area outside it as two zones with their numbers */
  function pitch(el, d) {
    watch(el, (W, H) => {
      const pw = 68, pl = 52.5, m = 14;
      const k = Math.min((W - 2 * m) / pw, (H - 2 * m) / pl);
      const ox = (W - pw * k) / 2, oy = (H - pl * k) / 2;
      const X = x => ox + x * k, Y = y => oy + y * k;
      const bx = (pw - 40.3) / 2, sx = (pw - 18.32) / 2, gx = (pw - 7.32) / 2;
      const small = W < 420;
      let o = `<rect x="${X(0)}" y="${Y(0)}" width="${pw*k}" height="${pl*k}" fill="rgba(93,107,99,.22)"/>`;
      o += `<rect x="${X(bx)}" y="${Y(0)}" width="${40.3*k}" height="${16.5*k}" fill="rgba(227,52,58,.30)"/>`;
      o += `<g fill="none" stroke="${LINE}" stroke-width="1.5">`;
      o += `<rect x="${X(0)}" y="${Y(0)}" width="${pw*k}" height="${pl*k}"/>`;
      o += `<rect x="${X(bx)}" y="${Y(0)}" width="${40.3*k}" height="${16.5*k}"/>`;
      o += `<rect x="${X(sx)}" y="${Y(0)}" width="${18.32*k}" height="${5.5*k}"/>`;
      o += `<path d="M${X(pw/2-7.3)} ${Y(16.5)} A ${9.15*k} ${9.15*k} 0 0 0 ${X(pw/2+7.3)} ${Y(16.5)}"/>`;
      o += `<path d="M${X(pw/2-9.15)} ${Y(pl)} A ${9.15*k} ${9.15*k} 0 0 1 ${X(pw/2+9.15)} ${Y(pl)}"/>`;
      o += `</g><rect x="${X(gx)}" y="${Y(0)-4}" width="${7.32*k}" height="4" fill="${LINE}"/>`;
      const big = Math.max(26, Math.min(56, k * 4.2)), lab = small ? 13 : 15;
      const zone = (cy, a, b, line) =>
        `<text x="${X(pw/2)}" y="${cy}" text-anchor="middle" style="stroke:none;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:${big}px">${esc(a)}</text>` +
        `<text x="${X(pw/2)}" y="${cy + lab + 8}" text-anchor="middle" style="stroke:none;font-size:${lab}px">${esc(b)}</text>` +
        (line ? `<text x="${X(pw/2)}" y="${cy + 2*lab + 14}" text-anchor="middle" class="tick" style="stroke:none;fill:#c9d4cd">${esc(line)}</text>` : '');
      const lines = small ? lab + 8 : 2 * lab + 14;
      o += zone(Y(16.5) - lines - 12, d.inside[0], d.inside[1], small ? '' : d.inside[2]);
      o += zone(Y(33), d.outside[0], d.outside[1], small ? '' : d.outside[2]);
      return o;
    });
  }

  /* Scatter: points [{n,x,y,u}], u marks the highlighted team */
  function scatter(el, d) {
    watch(el, (W, H) => {
      const small = W < 520;
      const m = {l: 52, r: small ? 18 : 30, t: 16, b: 48};
      const [x0, x1] = d.xr, [y0, y1] = d.yr;
      const X = v => m.l + (v - x0) / (x1 - x0) * (W - m.l - m.r);
      const Y = v => H - m.b - (v - y0) / (y1 - y0) * (H - m.t - m.b);
      let o = '';
      d.yt.forEach(t => { o += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(t)}" y2="${Y(t)}" stroke="${RULE}"/><text class="tick" x="${m.l - 8}" y="${Y(t) + 4}" text-anchor="end">${esc(d.yf ? d.yf(t) : t)}</text>`; });
      d.xt.filter((t, i) => !small || i % 2 === 0).forEach(t => { o += `<text class="tick" x="${X(t)}" y="${H - m.b + 20}" text-anchor="middle">${esc(d.xf ? d.xf(t) : t)}</text>`; });
      if (d.diag) { const a = Math.max(x0, y0), b = Math.min(x1, y1); o += `<line x1="${X(a)}" y1="${Y(a)}" x2="${X(b)}" y2="${Y(b)}" stroke="${LINE}" stroke-dasharray="4 4"/><text class="tick" x="${X(b) - 6}" y="${Y(b) + 16}" text-anchor="end">${esc(d.diag)}</text>`; }
      if (d.avg) o += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(d.avg)}" y2="${Y(d.avg)}" stroke="${LINE}" stroke-dasharray="4 4"/><text class="tick" x="${W - m.r}" y="${Y(d.avg) - 7}" text-anchor="end">${esc(d.avgLabel)}</text>`;
      o += `<text class="tick" x="${(m.l + W - m.r) / 2}" y="${H - 8}" text-anchor="middle">${esc(d.xl)}</text>`;
      o += `<text class="tick" x="14" y="${(m.t + H - m.b) / 2}" text-anchor="middle" transform="rotate(-90 14 ${(m.t + H - m.b) / 2})">${esc(d.yl)}</text>`;
      const pts = d.pts.slice().sort((a, b) => a.u - b.u);
      pts.forEach(p => { o += `<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="${p.u ? 8 : 5.5}" fill="${p.u ? RED : GREY}" stroke="#0b0f0d" stroke-width="2"><title>${esc(p.n)}: ${esc(p.tip || '')}</title></circle>`; });
      pts.filter(p => p.u || (d.label || []).includes(p.n)).forEach(p => {
        const left = X(p.x) > W - 130;
        o += `<text x="${X(p.x) + (left ? -12 : 12)}" y="${Y(p.y) + 5}" text-anchor="${left ? 'end' : 'start'}" style="${p.u ? 'font-weight:600' : 'fill:#c9d1cc'}">${esc(p.n)}</text>`;
      });
      return o;
    });
  }

  /* HTML bar rows: [{n,v,u}] */
  function rows(el, d) {
    const max = d.max ?? Math.max(...d.rows.map(r => Math.abs(r.v)));
    el.innerHTML = d.rows.map(r =>
      `<div class="row${r.u ? ' u' : ''}"><span>${esc(r.n)}</span><div><div class="bar grow" style="width:${Math.abs(r.v) / max * 100}%"></div></div><span class="v">${esc(d.f ? d.f(r.v) : r.v)}</span></div>`).join('');
  }

  /* Diverging bars around zero, HTML: [{n,v,u}]. Pass max to share a scale across charts, f to format values */
  function diverge(el, d) {
    const max = d.max ?? Math.max(...d.rows.map(r => Math.abs(r.v)));
    el.innerHTML = d.rows.map(r => {
      const w = Math.abs(r.v) / max * 50;
      const bar = r.v === 0 ? '' : `<div class="bar" style="position:absolute;top:0;bottom:0;${r.v > 0 ? 'left:50%' : `right:50%;border-radius:3px 0 0 3px`};width:${w}%"></div>`;
      return `<div class="row${r.u ? ' u' : ''}"><span>${esc(r.n)}</span><div class="zero" style="height:20px">${bar}<div style="position:absolute;left:50%;top:-3px;bottom:-3px;border-left:1px solid ${LINE}"></div></div><span class="v">${r.v > 0 ? '+' : ''}${d.f ? d.f(r.v) : r.v}</span></div>`;
    }).join('');
  }

  /* Slope chart: two seasons of percentiles, [{n,a,b}] */
  function slope(el, d) {
    watch(el, (W, H) => {
      const small = W < 520;
      const m = {l: small ? 118 : 190, r: small ? 118 : 190, t: 30, b: 16};
      const xa = m.l, xb = W - m.r, Y = v => m.t + (100 - v) / 100 * (H - m.t - m.b);
      let o = `<text class="tick" x="${xa}" y="16" text-anchor="middle">${esc(d.la)}</text><text class="tick" x="${xb}" y="16" text-anchor="middle">${esc(d.lb)}</text>`;
      o += `<line x1="${xa}" x2="${xa}" y1="${m.t}" y2="${H - m.b}" stroke="${RULE}"/><line x1="${xb}" x2="${xb}" y1="${m.t}" y2="${H - m.b}" stroke="${RULE}"/>`;
      const place = (vals) => { const ys = vals.map((v, i) => ({i, y: Y(v)})).sort((a, b) => a.y - b.y); for (let j = 1; j < ys.length; j++) if (ys[j].y - ys[j - 1].y < 17) ys[j].y = ys[j - 1].y + 17; const out = []; ys.forEach(p => out[p.i] = p.y); return out; };
      const la = place(d.rows.map(r => r.a)), lb = place(d.rows.map(r => r.b));
      d.rows.forEach((r, i) => {
        const drop = r.b < r.a - 10, col = drop ? RED : GREY;
        o += `<line x1="${xa}" y1="${Y(r.a)}" x2="${xb}" y2="${Y(r.b)}" stroke="${col}" stroke-width="${drop ? 2.5 : 1.5}"/>`;
        o += `<circle cx="${xa}" cy="${Y(r.a)}" r="4" fill="${col}"/><circle cx="${xb}" cy="${Y(r.b)}" r="4" fill="${col}"/>`;
        const nm = small ? r.s : r.n;
        o += `<text x="${xa - 10}" y="${la[i] + 5}" text-anchor="end" style="${drop ? '' : 'fill:#b4bdb7'}">${esc(nm)} ${r.a}</text>`;
        o += `<text x="${xb + 10}" y="${lb[i] + 5}" style="${drop ? '' : 'fill:#b4bdb7'}">${r.b} ${esc(nm)}</text>`;
      });
      return o;
    });
  }

  /* Dumbbell rows: a (hollow) to b (filled). Percentiles by default; pass max, fmt and hi for other scales */
  function dumbbell(el, d) {
    const max = d.max ?? 100, f = d.fmt || (v => v), fa = d.fmtA || f, pc = v => v / max * 100;
    el.innerHTML = d.rows.map(r => {
      const lo = Math.min(r.a, r.b), hi = Math.max(r.a, r.b);
      const red = d.hi ? r.u : r.b < r.a - 10, col = red ? RED : '#c9d4cd';
      return `<div class="row db${r.u ? ' u' : ''}"><span>${esc(r.n)}</span><div class="track"><div class="seg" style="left:${pc(lo)}%;width:${pc(hi - lo)}%;background:${col}"></div><i class="a" style="left:${pc(r.a)}%"></i><i class="b" style="left:${pc(r.b)}%;background:${col}"></i></div><span class="v">${esc(fa(r.a))}<span class="mute"> to </span>${esc(f(r.b))}</span></div>`;
    }).join('') + `<div class="row db axis"><span></span><div class="track" style="background:none;height:auto">${(d.ticks || [0, 50, 100]).map(t => `<span style="left:${pc(t)}%">${t}</span>`).join('')}</div><span></span></div>`;
  }

  /* xG race: cumulative xG step lines for two teams.
     d = {teams: [{n, u, shots: [{m, xg, goal, who}]}, ...], reds: [{m, label}], end}
     m is the match minute to plot (stoppage time already folded in), u marks United. */
  function xgrace(el, d) {
    watch(el, (W, H) => {
      const small = W < 520;
      const m = {l: 40, r: small ? 92 : 128, t: 18, b: 40};
      const end = d.end || 95;
      const top = Math.max(1, ...d.teams.map(t => t.shots.reduce((a, s) => a + s.xg, 0)));
      const step = top > 3 ? 1 : 0.5;
      const ymax = Math.ceil((top + 0.1) / step) * step;
      const X = v => m.l + v / end * (W - m.l - m.r), Y = v => H - m.b - v / ymax * (H - m.t - m.b);
      let o = '';
      for (let v = 0; v <= ymax + 1e-9; v += step) o += `<line x1="${m.l}" x2="${W - m.r}" y1="${Y(v)}" y2="${Y(v)}" stroke="${RULE}"/><text class="tick" x="${m.l - 8}" y="${Y(v) + 4}" text-anchor="end">${v % 1 ? v.toFixed(1) : v}</text>`;
      [0, 15, 30, 45, 60, 75, 90].filter((t, i) => !small || i % 2 === 0 || t === 45).forEach(t => { o += `<text class="tick" x="${X(t)}" y="${H - m.b + 20}" text-anchor="middle">${t}'</text>`; });
      o += `<line x1="${X(45)}" x2="${X(45)}" y1="${m.t}" y2="${H - m.b}" stroke="${RULE}" stroke-dasharray="3 4"/>`;
      o += `<text class="tick" x="${(m.l + W - m.r) / 2}" y="${H - 6}" text-anchor="middle">Minute</text>`;
      (d.reds || []).forEach(r => {
        o += `<line x1="${X(r.m)}" x2="${X(r.m)}" y1="${m.t}" y2="${H - m.b}" stroke="${LINE}" stroke-dasharray="2 3"/>`;
        o += `<text class="tick" x="${X(r.m) + 6}" y="${m.t + 12}">${esc(r.label)}</text>`;
      });
      const order = d.teams.slice().sort((a, b) => a.u - b.u);
      const ends = [];
      order.forEach(t => {
        const col = t.u ? RED : '#c9d4cd';
        let cum = 0, p = `M${X(0)} ${Y(0)}`;
        const marks = [];
        t.shots.slice().sort((a, b) => a.m - b.m).forEach(s => {
          p += ` H${X(s.m)}`; cum += s.xg; p += ` V${Y(cum)}`;
          marks.push({s, y: cum});
        });
        p += ` H${X(end)}`;
        o += `<path d="${p}" fill="none" stroke="${col}" stroke-width="2.5" stroke-linejoin="round"/>`;
        marks.forEach(({s, y}) => {
          const tip = `${s.who}, ${s.label} (${s.xg.toFixed(2)} xG)${s.goal ? ', goal' : ''}`;
          o += s.goal
            ? `<circle cx="${X(s.m)}" cy="${Y(y)}" r="6.5" fill="${col}" stroke="#0b0f0d" stroke-width="2"><title>${esc(tip)}</title></circle>`
            : `<circle cx="${X(s.m)}" cy="${Y(y)}" r="9" fill="transparent"><title>${esc(tip)}</title></circle>`;
        });
        ends.push({t, col, y: Y(cum), v: cum});
      });
      if (ends.length === 2 && Math.abs(ends[0].y - ends[1].y) < 34) {
        const [lo, hi] = ends[0].y > ends[1].y ? [ends[0], ends[1]] : [ends[1], ends[0]];
        const mid = (lo.y + hi.y) / 2; lo.y = mid + 17; hi.y = mid - 17;
      }
      ends.forEach(e => {
        o += `<text x="${X(end) + 8}" y="${e.y - 2}" style="font-weight:600;fill:${e.t.u ? '#fff' : '#c9d4cd'}">${esc(e.t.n)}</text>`;
        o += `<text class="tick" x="${X(end) + 8}" y="${e.y + 14}">${e.v.toFixed(2)} xG</text>`;
      });
      return o;
    });
  }

  /* Shot map: full pitch, one team attacking each way. Coordinates are FotMob's (x 0-105 towards the goal attacked, y 0-68).
     d = {left: {n, u, shots: [{x, y, xg, goal, who, m}]}, right: {...}}  'right' attacks the right-hand goal. */
  function shotmap(el, d) {
    watch(el, (W, H) => {
      const pw = 105, ph = 68, pad = 6;
      const k = Math.min((W - 2 * pad) / pw, (H - 2 * pad) / ph);
      const ox = (W - pw * k) / 2, oy = (H - ph * k) / 2;
      const X = x => ox + x * k, Y = y => oy + y * k;
      let o = `<rect x="${X(0)}" y="${Y(0)}" width="${pw * k}" height="${ph * k}" fill="rgba(93,107,99,.18)"/>`;
      o += `<g fill="none" stroke="${LINE}" stroke-width="1.2" opacity=".7">`;
      o += `<rect x="${X(0)}" y="${Y(0)}" width="${pw * k}" height="${ph * k}"/>`;
      o += `<line x1="${X(pw / 2)}" x2="${X(pw / 2)}" y1="${Y(0)}" y2="${Y(ph)}"/><circle cx="${X(pw / 2)}" cy="${Y(ph / 2)}" r="${9.15 * k}"/>`;
      [0, 1].forEach(side => {
        const bx = side ? pw - 16.5 : 0, sx = side ? pw - 5.5 : 0;
        o += `<rect x="${X(bx)}" y="${Y((ph - 40.3) / 2)}" width="${16.5 * k}" height="${40.3 * k}"/>`;
        o += `<rect x="${X(sx)}" y="${Y((ph - 18.32) / 2)}" width="${5.5 * k}" height="${18.32 * k}"/>`;
      });
      o += `</g>`;
      const R = xg => Math.max(3, Math.sqrt(xg) * k * 4.2);
      ['left', 'right'].forEach(side => {
        const t = d[side]; if (!t) return;
        const col = t.u ? RED : '#c9d4cd';
        const pts = t.shots.map(s => ({...s, px: side === 'right' ? X(s.x) : X(pw - s.x), py: side === 'right' ? Y(s.y) : Y(ph - s.y)}))
          .sort((a, b) => a.goal - b.goal || b.xg - a.xg);
        pts.forEach(s => {
          const tip = `${s.who}, ${s.m}' (${s.xg.toFixed(2)} xG)${s.goal ? ', goal' : ''}`;
          o += s.goal
            ? `<circle cx="${s.px}" cy="${s.py}" r="${R(s.xg)}" fill="${col}" stroke="#0b0f0d" stroke-width="2"><title>${esc(tip)}</title></circle>`
            : `<circle cx="${s.px}" cy="${s.py}" r="${R(s.xg)}" fill="${col}" fill-opacity=".12" stroke="${col}" stroke-opacity=".75" stroke-width="1.5"><title>${esc(tip)}</title></circle>`;
        });
        const lx = side === 'right' ? X(pw / 2) + 14 : X(pw / 2) - 14, anchor = side === 'right' ? 'start' : 'end';
        o += `<text x="${lx}" y="${Y(0) + 22}" text-anchor="${anchor}" style="font-weight:600;fill:${t.u ? '#fff' : '#c9d4cd'}">${esc(t.n)} ${side === 'right' ? '→' : '←'}</text>`;
        if (W > 460) o += `<text class="tick" x="${lx}" y="${Y(0) + 40}" text-anchor="${anchor}">${esc(t.sub || '')}</text>`;
      });
      return o;
    });
  }

  /* Pizza: one player, slices of equal angle, each as long as its percentile.
     d = {slices: [{lab, short, pct, val, tip, cat}]}  short is an optional label for narrow screens;  val is the short label under the name ("6 shots"); cat groups slices. */
  function pizza(el, d) {
    watch(el, (W, H) => {
      const small = W < 520;
      const cx = W / 2, cy = H / 2;
      const R = Math.min(W / 2 - (small ? 74 : 120), H / 2 - 44), r0 = R * 0.12;
      const n = d.slices.length, A = 2 * Math.PI / n;
      const pt = (r, a) => [cx + r * Math.sin(a), cy - r * Math.cos(a)];
      const arc = (r1, r2, a1, a2) => {
        const [x1, y1] = pt(r2, a1), [x2, y2] = pt(r2, a2), [x3, y3] = pt(r1, a2), [x4, y4] = pt(r1, a1);
        return `M${x1} ${y1} A${r2} ${r2} 0 0 1 ${x2} ${y2} L${x3} ${y3} A${r1} ${r1} 0 0 0 ${x4} ${y4}Z`;
      };
      const gap = 0.012;
      let o = '';
      d.slices.forEach((s, i) => {
        const a1 = i * A + gap, a2 = (i + 1) * A - gap;
        o += `<path d="${arc(r0, R, a1, a2)}" fill="${GREY}" fill-opacity=".22"/>`;
      });
      [0.25, 0.5, 0.75].forEach(f => { o += `<circle cx="${cx}" cy="${cy}" r="${r0 + (R - r0) * f}" fill="none" stroke="${RULE}" stroke-width="1"/>`; });
      d.slices.forEach((s, i) => {
        const a1 = i * A + gap, a2 = (i + 1) * A - gap, r = r0 + (R - r0) * Math.max(s.pct, 1.5) / 100;
        o += `<path d="${arc(r0, r, a1, a2)}" fill="${RED}" fill-opacity="${s.pct >= 50 ? 1 : 0.55}"><title>${esc(s.tip)}</title></path>`;
        const am = (i + 0.5) * A, low = s.pct < 30, [bx, by] = pt(low ? r0 + (R - r0) * 0.42 : r - 13, am);
        o += `<text x="${bx}" y="${by + 4}" text-anchor="middle" style="font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:${small ? 13 : 15}px${low ? ';fill:#9aa79f' : ''}">${s.pct}</text>`;
        const [lx, ly] = pt(R + (small ? 10 : 14), am), sx = Math.sin(am);
        const anchor = Math.abs(sx) < 0.2 ? 'middle' : sx > 0 ? 'start' : 'end';
        const dy = Math.cos(am) > 0.8 ? -14 : Math.cos(am) < -0.8 ? 10 : -2;
        o += `<text x="${lx}" y="${ly + dy}" text-anchor="${anchor}" style="font-size:${small ? 12 : 14}px">${esc(small && s.short ? s.short : s.lab)}</text>`;
        o += `<text class="tick" x="${lx}" y="${ly + dy + (small ? 14 : 16)}" text-anchor="${anchor}" style="font-size:${small ? 11 : 13}px">${esc(s.val)}</text>`;
      });
      for (let i = 0; i < n; i++) if (d.slices[i].cat !== d.slices[(i + n - 1) % n].cat) {
        const [x1, y1] = pt(r0, i * A), [x2, y2] = pt(R + 4, i * A);
        o += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${LINE}" stroke-width="1.5"/>`;
      }
      return o;
    });
  }

  /* One player's match against an average, HTML rows. The average always sits at the middle of the track;
     the bar runs to his value on that scale (capped at twice the average, the number shows the rest).
     d = {rows: [{lab, v, avg, vf, af, tip, cat}], cats: {att: 'Attacking', ...}} */
  function versus(el, d) {
    let last = null, o = '';
    d.rows.forEach(r => {
      if (d.cats && r.cat !== last) { o += `<div class="vs-head">${esc(d.cats[r.cat] || '')}</div>`; last = r.cat; }
      const ratio = r.avg > 0 ? r.v / r.avg : (r.v > 0 ? 2 : 1);
      const w = Math.min(ratio, 2) / 2 * 100, over = ratio > 2;
      const up = r.v >= r.avg;
      o += `<div class="row vs${up ? ' u' : ''}" title="${esc(r.tip || '')}"><span>${esc(r.lab)}</span>` +
        `<div class="vs-track"><div class="bar grow" style="width:${w}%;${up ? '' : 'background:var(--grey)'}${over ? ';border-radius:0' : ''}"></div>${over ? '<b class="vs-more">›</b>' : ''}<i class="vs-avg"></i></div>` +
        `<span class="v">${esc(r.vf)}<span class="mute"> / ${esc(r.af)}</span></span></div>`;
    });
    el.innerHTML = o;
  }


  /* The usual "face-off" match stats bars, drawn on purpose for Chart crimes: each row splits 100% between the teams.
     d = {teams: [a, b], rows: [{n, a, b, fa?, fb?}]} */
  function faceoff(el, d) {
    let o = `<div class="fo-head"><span>${esc(d.teams[0])}</span><span>${esc(d.teams[1])}</span></div>`;
    d.rows.forEach(r => {
      const t = r.a + r.b, pa = t ? r.a / t * 100 : 50;
      o += `<div class="fo-row"><div class="fo-lab"><span>${esc(r.fa ?? r.a)}</span><span class="mute">${esc(r.n)}</span><span>${esc(r.fb ?? r.b)}</span></div>` +
        `<div class="fo-bar"><i style="width:${pa}%;${pa >= 50 ? 'background:var(--red)' : ''}"></i><i style="width:${100 - pa}%;${pa < 50 ? 'background:#c9d4cd' : ''}"></i></div></div>`;
    });
    el.innerHTML = o;
  }

  /* Two teams against a normal game: each row is a track from 0 to max times the league average, the average marked.
     d = {max, teams: [{n, u}], rows: [{n, avg, vals: [a, b], f?}]} */
  function dots(el, d) {
    const max = d.max || 3, pc = v => Math.min(v, max) / max * 100;
    let o = '';
    d.rows.forEach(r => {
      const [a, b] = r.vals, f = r.f || (v => v);
      o += `<div class="row dt"><span>${esc(r.n)}</span><div class="dt-track"><i class="dt-avg" style="left:${pc(1)}%"></i>` +
        `<b class="dt-dot" style="left:${pc(b / r.avg)}%;background:#c9d4cd" title="${esc(d.teams[1].n)}: ${esc(f(b))}"></b>` +
        `<b class="dt-dot" style="left:${pc(a / r.avg)}%;background:var(--red)" title="${esc(d.teams[0].n)}: ${esc(f(a))}"></b></div>` +
        `<span class="v"><b style="color:#fff">${esc(f(a))}</b><span class="mute"> / ${esc(f(b))}</span><span class="mute dt-avgv"> / avg ${esc(f(r.avg))}</span></span></div>`;
    });
    o += `<div class="row dt axis"><span></span><div class="dt-track" style="background:none">${[0, 1, 2, 3].filter(t => t <= max).map(t => `<span style="left:${pc(t)}%">${t ? t + '×' : '0'}</span>`).join('')}</div><span></span></div>`;
    el.innerHTML = o;
  }

  /* Stacked horizontal bars, one per team: d = {max, parts: [{n, col}], rows: [{n, u, vals: [..]}], f} */
  function stack(el, d) {
    const f = d.f || (v => v);
    el.innerHTML = d.rows.map(r => {
      const tot = r.vals.reduce((a, v) => a + v, 0);
      return `<div class="row st${r.u ? ' u' : ''}"><span>${esc(r.n)}</span><div style="display:flex;height:26px">` +
        r.vals.map((v, i) => v ? `<div class="grow" title="${esc(d.parts[i].n)}: ${esc(f(v))}" style="width:${v / d.max * 100}%;background:${d.parts[i].col};border-right:2px solid var(--bg);display:flex;align-items:center;justify-content:center;font-size:13px;color:#0b0f0d;font-weight:600">${v / d.max > 0.07 ? esc(f(v)) : ''}</div>` : '').join('') +
        `</div><span class="v">${esc(f(tot))}</span></div>`;
    }).join('');
  }

  return {pitch, scatter, rows, diverge, slope, dumbbell, xgrace, shotmap, pizza, versus, faceoff, dots, stack};
})();
