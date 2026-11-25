# Post-Match Plots

Football, drawn with data. A static site for GitHub Pages: no build step, just HTML, CSS, a small charts script and bundled fonts.

## Structure
- `index.html`: homepage
- `posts/`: one HTML file per post
- `assets/site.css`: all styling, including the font setup
- `assets/charts.js`: chart helpers (pitch, scatter, bar rows, diverging bars, dumbbells)
- `assets/logo.svg`: the Four-pass P logo, also used as the browser-tab icon
- `assets/fonts/`: Barlow and Barlow Condensed (SIL Open Font Licence, see OFL.txt). Hosted here so visitors' browsers don't contact Google Fonts.

## Going live

### 1. Set up and lock down the account
1. Sign up at github.com. The username becomes the web address, so `postmatchplots` gives `postmatchplots.github.io`.
2. Turn on two-factor authentication: Settings > Password and authentication > Enable two-factor authentication. Use an authenticator app rather than SMS, and save the recovery codes somewhere safe.
3. Hide your email: Settings > Emails > tick "Keep my email addresses private". Also tick "Block command line pushes that expose my email".

### 2. Create the repository
1. Click + (top right) > New repository.
2. Name it exactly `yourusername.github.io`, set it to Public, leave README, .gitignore and licence unticked.
3. Click Create repository.

### 3. Upload the site
1. Unzip `postmatchplots.zip`. Upload the contents of the `postmatchplots` folder, not the folder itself.
2. On the repository page click "uploading an existing file", then drag in `index.html`, `README.md`, and the `assets` and `posts` folders. Use Chrome or Firefox; Safari can refuse folders.
3. Check the list includes `assets/logo.svg`, the five files in `assets/fonts/` (four fonts plus OFL.txt), and `posts/united-shoot-more-than-anyone.html`. Click Commit changes.

### 4. Switch on Pages and HTTPS
1. Settings > Pages. Under Build and deployment, set Source to "Deploy from a branch", branch `main`, folder `/ (root)`, Save.
2. Once the site has built, tick "Enforce HTTPS" on the same page (it can take a few minutes to become available).
3. Visit `https://yourusername.github.io`. The Actions tab shows a green tick when it's published.

## Updating
Add file > Upload files, and drop in the changed files. A file with the same name replaces the old one. The site updates within a minute or two.

To add a post: copy `posts/united-shoot-more-than-anyone.html`, rename it, swap the words and the data arrays in the script at the bottom, and add a card for it in the Posts section of `index.html`.

## Rules for what goes in the repo
- The repo and its whole history are public. Deleting a file later doesn't remove it from history.
- Never upload passwords, API keys, or raw data exports. Charts only.
- Keep personal details light: no employer, home town or family.
- Credit "Data: FotMob / Opta" on every post. No club badges or player photos.
- If you add visitor stats, use a cookie-free service (GoatCounter or Plausible) so no cookie banner is needed.

## Moving to your own domain later
1. Buy the domain and turn on WHOIS privacy at the registrar.
2. Verify it first: GitHub Settings (your account, not the repo) > Pages > Add a domain. This stops anyone else claiming it on GitHub.
3. Add the DNS records GitHub's docs list for an apex domain (four A records) and/or a CNAME for `www`.
4. Repo Settings > Pages > Custom domain: enter it, Save, then tick Enforce HTTPS once it's offered.
5. Old `github.io` links redirect automatically. Don't let the domain lapse while it still points at GitHub.

Data: FotMob / Opta.
