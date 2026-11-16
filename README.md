# New springs.church, assembled as one site (draft for staff review)

`python3 build.py` builds the whole redesigned site from the page projects on the Desktop into `docs/`, which GitHub Pages serves:
https://joshuagarner11.github.io/SpringsChurchWebsite/ (repo https://github.com/JoshuaGarner11/SpringsChurchWebsite, main:/docs).
It opens on the Home page (Option I) and every page sits at its real springs.church address (/about/, /plan-a-visit/, /events/ …),
joined by the shared header and footer in `chrome/` (Option I menu + SPRINGS. footer, Springs mark centered). Pages that are already
live and unchanged (Sermons, Podcasts, Stories, Media, Bible App, Kids/Youth/YA sites) link to the real ones. noindex on every page,
robots.txt blocks crawlers, a 404 page, and a key/token scan that stops the build if anything secret shows up.
Local preview: launch.json "springs-new-pages" → http://localhost:5220/review/ (scratchpad web root links `review` → `docs/`).
History: started 11/15/2026 as a review hub; Josh asked the same night to "put the site together as if it was whole," so the hub is gone.

## Pages
The page list (site folder, source project, entry file) is `PAGES` in build.py. Trello card links are in NOTES.local.md (kept off GitHub).

## How the build treats links
`href="/groups"` and `https://www.springs.church/groups` links point inside the site when the page is part of the redesign
(`../groups/`), otherwise at the live page (`https://www.springs.church/sermons`). Option I's link map in shared.js gets the same treatment. The Team mock's `/contributor/<slug>` stubs are copied in and its fetch path made relative.
Fonts: the Typekit kit (ktn0utw) is domain-locked, so on a new domain Gotham/Proxima fall back to Montserrat/system fonts
unless the review domain is added to the kit's allowed domains in Adobe Fonts.

## Publishing
- GitHub repo under JoshuaGarner11 (or a Springs org account), GitHub Pages serving `site/`.
- GitHub Pages sites are public even from a private repo. noindex + robots.txt keep it out of search, but anyone with the link can open it.
- Everything here is already public on springs.church or its review copies, but git keeps history, so anything pushed stays retrievable.
- Update = `python3 build.py` (secret scan must say clean) → commit → push.
- Later (Josh 11/15): the plan is to move springs.church off ChurchCo; this repo can grow into the real site project.

## CCB sync (calendar + groups)
CCB is the master calendar. `.github/workflows/ccb-sync.yml` runs `scripts/ccb_sync.py` every hour (and on demand from the
Actions tab) with the login in repo secrets `CCB_API_USER` / `CCB_API_PASS` (a website-only API user; the secrets are entered
by Josh in GitHub settings and are never in the code). It calls `public_calendar_listing` (today + 120 days) and
`group_search`, and writes `docs/data/events.json` and `docs/data/groups.json` only when the content changed.
Served at https://joshuagarner11.github.io/SpringsChurchWebsite/data/events.json (GitHub Pages allows cross-site reads,
so the ChurchCo Events block can use it via `data-events-src`).

Public-safe rules (the repo and the job logs are public): whitelisted fields only; no leader names, phones or emails;
events at a home (home groups, "Residence", or a non-church street address) dropped; venues are names only; descriptions
lose HTML and any email/phone that isn't the church's; kids and student groups left out of groups.json; the log prints counts.
Test the rules offline: `python3 scripts/test_ccb_sync.py scripts/ccb_sync.py`.
Before a local build + push, run `git pull --rebase` (the sync job commits to main). build.py keeps docs/data.

## Sermon sync (Home's featured sermon)
`.github/workflows/sermon-sync.yml` runs `scripts/sermon_sync.py` every two hours on Sundays and Mondays and twice a day the rest of the
week (no secrets). It reads the public "Sunday Sermons" playlist (newest first) and the top four videos' pages, and writes
`docs/data/sermons.json` when something changed. Home (option-i.html) fetches that file and swaps in the newest sermon (title, speaker,
date, player) and the three before it; without the file it shows what's in shared.js. If YouTube answers oddly, the script keeps the last list.
