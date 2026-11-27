# Post-Match Plots

Football, drawn with data. Live at https://postmatchplots.github.io

A static site on GitHub Pages: plain HTML, CSS, a small charts script and self-hosted fonts. No build step, no trackers, no cookies.

## What's here

**Pages**
- `index.html`: the homepage. The post list between `<!-- posts:start -->` and `<!-- posts:end -->` is filled in automatically.
- `united-*.html`, `bruno-fernandes-decline.html`: the "United at 11 games" series. New posts are more HTML files alongside them.
- `404.html`: the "page not found" page.

**Look and feel**
- `site.css`: all the styling, including the font setup.
- `charts.js`: chart helpers (`PMP.pitch`, `PMP.scatter`, `PMP.rows`, `PMP.diverge`, `PMP.dumbbell`, `PMP.xgrace`, `PMP.shotmap`, `PMP.pizza`).
- `logo.svg`: the logo, also the browser-tab icon. `apple-touch-icon.png` is the iPhone home-screen version.
- `barlow-*.woff2`, `OFL.txt`: the fonts and their licence, hosted here so visitors' browsers never contact Google Fonts.
- `social/`: the 1200x630 preview images shown when a page is shared, one per page, named after it.

**Generated automatically (don't edit by hand)**
- `feed.xml`: the RSS feed.
- `sitemap.xml`: the page list for search engines.
- The homepage post list.

`scripts/update_site.py` rebuilds all three on every push, run by `.github/workflows/update-site.yml`. It reads each post's `<head>` tags, so those tags are what matter.

**Leave alone**
- `google521f82c2bf5ada73.html`: Google Search Console verification. Delete it and Search Console stops working.
- `robots.txt`: points search engines at the sitemap.

**Scripts**
- `scripts/build_united_series.py`: regenerates the six series pages. Their words and data live in this file, so edit there rather than in the HTML.
- `scripts/pull_match.js` and `scripts/build_match_post.py`: the Match in one chart template (see below).
- `scripts/make_social_cards.py`: makes the preview images (name a card to make just that one). Needs Python with playwright (`pip install playwright && playwright install chromium`). Run it on your own machine.

## Adding a post

1. Copy an existing post page and rename it: lowercase, hyphens, ending `.html`.
2. Change the words and the data arrays in the script at the bottom.
3. Update these `<head>` tags:
   - `og:title` and `og:description`
   - `article:published_time`, the date, like `2026-12-02`
   - `pmp:summary`, the one-line answer shown on the homepage
   - `pmp:series` and `pmp:part` if it's part of a series (delete both if not)
   - the canonical link, `og:url`, `og:image` and the structured-data block, all pointing at the new file name
4. Add a line for the page to the list at the top of `scripts/make_social_cards.py`, run it, and check the new image in `social/`.
5. Push (or Add file > Upload files). Within a couple of minutes the homepage list, feed and sitemap update themselves. The Actions tab shows a green tick when it's done.

## Match in one chart (every Monday)

An xG race, a shot map and a star performer pizza for United's latest league game, built from a template.

1. Open the match on fotmob.com and copy its address.
2. Paste the address into `URL` at the top of `scripts/pull_match.js`, run the script in the browser console on any fotmob.com page, and save what it returns as a `.json` file **outside this repo** (raw data never goes on the site).
3. Write a short words file next to it (title as a question, one-line summary, description, the answer up front, a paragraph for each chart, "The answer"). The format is at the top of `scripts/build_match_post.py`.
4. Run `python scripts/build_match_post.py match.json words.json`. It writes the page, adds and makes the share image, and prints checks (score, xG and shot counts against FotMob's own numbers). Fix anything it flags.
5. Open the page to check it, then push. The posts group on the homepage as "Match in one chart", newest first.

The star performer pizza picks United's highest-rated outfielder by FotMob match rating (60+ minutes). To choose someone else, set `STAR` in `pull_match.js` to their name. Each slice ranks his match numbers, per 90, against the season averages of PL players in his position with 450+ minutes.

## House rules

- Everything here, history included, is public. Deleting a file later doesn't remove it from history.
- No passwords, API keys or raw data exports. Charts only.
- Keep personal details out.
- Credit "Data: FotMob / Opta" on every chart. No club badges or player photos.
- Visitor stats, if ever added, must be cookie-free (GoatCounter or Plausible), so there's no cookie banner.

Data: FotMob / Opta.
