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

  return {pitch, scatter, rows, diverge, slope, dumbbell};
})();
