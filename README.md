# Springs site review (all redesigned pages in one place)

`python3 build.py` collects every page under review from its Desktop project into `docs/` (static HTML, no build tools):
the hub page (`docs/index.html`), one folder per page with its preview and images, noindex on every page, robots.txt that
blocks crawlers, and a key/token scan that stops the build if anything secret shows up. Local preview:
launch.json "springs-new-pages" → http://localhost:5220/review/ (the scratchpad web root links `review` → `docs/`).

Started 11/15/2026 after Josh asked about putting the whole site under review up on GitHub so people could review it.
Published 11/15/2026 to GitHub Pages from https://github.com/JoshuaGarner11/SpringsChurchWebsite (main, /docs).
Review site: https://joshuagarner11.github.io/SpringsChurchWebsite/

## Pages
The page list (title, source project, status) is `PAGES` in build.py. Trello card links are in NOTES.local.md, which stays off GitHub.

## How the build treats links
`href="/groups"` style site links point at the review copy when one exists (`../groups/`), otherwise at the live page
(`https://www.springs.church/sermons`). The Team mock's `/contributor/<slug>` stubs are copied in and its fetch path made relative.
Fonts: the Typekit kit (ktn0utw) is domain-locked, so on a new domain Gotham/Proxima fall back to Montserrat/system fonts
unless the review domain is added to the kit's allowed domains in Adobe Fonts.

## Publishing
- GitHub repo under JoshuaGarner11 (or a Springs org account), GitHub Pages serving `site/`.
- GitHub Pages sites are public even from a private repo. noindex + robots.txt keep it out of search, but anyone with the link can open it.
- Everything here is already public on springs.church or its review copies, but git keeps history, so anything pushed stays retrievable.
- Update = `python3 build.py` (secret scan must say clean) → commit → push.
- Later (Josh 11/15): the plan is to move springs.church off ChurchCo; this repo can grow into the real site project.
