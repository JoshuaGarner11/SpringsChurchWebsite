/* Shared content for the three home-page mockups.
   Everything here is a snapshot of the live site / YouTube / events page (sermons + events refreshed 2026-11-15).
   On ChurchCo these would come from native blocks (sermon, events), not hard-coded. */
window.SPRINGS = {
  latest: {
    title: 'The Imageless God', speaker: 'Michael Petillo', date: 'November 15, 2026',
    id: 'Pux9AYf6dO8', watch: 'https://youtu.be/Pux9AYf6dO8', img: 'img/preach-petillo-1115.jpg',
    // hero photo = the one on the live springs.church hero that week; service = that Sunday's Full Service stream
    heroImg: 'img/sermon-imageless-god.jpg', service: 'WjxighRMbW8'
  },
  // Newest first, from the "Sunday Sermons" playlist (springs-sermons-site/fetch_sermons.py, 11/15/2026)
  sermons: [
    { t: "You Can't Scare the Hell Out of People", s: 'Michael Petillo', id: 'F4lEL8bnik0' },
    { t: 'Disruption', s: 'Nicky Cruz', id: 'zOvP-KGQ0eA' },
    { t: 'The Cost of a Comfortable Church', s: 'Michael Petillo', id: 'u_kH54cwvpY' }
  ],
  // From springs.church/stories (real quotes from the testimony videos)
  stories: [
    { n: 'Mike & Laurie Reed', t: 'Never Too Late', q: 'It’s never too late to turn your life over to God.', img: 'img/s-reed-embrace.jpg', yt: 'fNgoZLjsRdo' },
    { n: 'Amanda & Carlos Cruz', t: 'It Starts Where You Are', q: 'Missions always start where you are.', img: 'img/s-cruz-portrait-close.jpg', yt: 'R94vPBhjr68' },
    { n: 'Matthew Martinez', t: 'A Cup of Coffee', q: 'I’ve always turned my back on Him, but He hasn’t ever turned His back on me.', img: 'img/s-matthew-interview.jpg', yt: 'fBGed4fRW_M' },
    { n: 'Sarah Conquest', t: 'Out of the Miry Clay', q: 'God doesn’t answer the question why. But He does answer who.', img: 'img/s-conquest-smile.jpg', yt: '0u4JIfprhQw' },
    { n: 'Becky Phipps', t: 'Baptize, Not Bury', q: 'God promised me that I would baptize my child in this church, and not bury him.', img: 'img/s-becky.jpg', yt: 'nDEIRV-PPYA' },
    { n: 'Michael & Mary, with Nick', t: 'The Ice Cream Aisle', q: 'He injected my soul with His love through the words of a total stranger.', img: 'img/s-michael-mary.jpg', yt: 'uPBct6TKpOM' }
  ],
  // From springs.church/events (ChurchCo events block, 11/15/2026)
  events: [
    { d: '2026-11-19', time: '3:00 PM', t: 'Feeding Friends', where: 'Main Parking' },
    { d: '2026-12-01', time: '10:00 AM', t: 'Moms Group', where: 'Kids Auditorium' },
    { d: '2026-12-05', time: '8:00 AM', t: 'Springs Men Breakfast', where: 'Classroom 1' },
    { d: '2026-12-05', time: '1:00 PM', t: 'Springs Women | Christmas Tea', where: 'Main Lobby & Sanctuary' },
    { d: '2026-12-09', time: '6:30 PM', t: 'Membership Class', where: 'Green Room', step: true },
    { d: '2027-01-15', time: '5:00 PM', t: 'Youth | Here I Am Winter Retreat', where: 'Camp Elim', big: true }
  ],
  links: {
    media: 'https://www.springs.church/media',
    events: 'events/',
    sermons: 'https://www.youtube.com/playlist?list=PL0-75bzYYynk7GXBRfMBT-JD0AyuKTZIo',
    live: 'https://www.youtube.com/@springs.church/live',
    connectForm: 'https://springschurch.ccbchurch.com/goto/forms/569/responses/new',
    prayer: 'prayer/',
    give: 'give/',
    app: 'download-app/',
    groups: 'groups/',
    serve: 'serve/',
    kids: 'https://kids.springs.church/',
    youth: 'https://youth.springs.church/',
    ya: 'https://ya.springs.church/',
    missions: 'missions/',
    about: 'about/',
    stories: 'https://www.springs.church/stories',
    beliefs: 'our-beliefs/',
    team: 'our-staff/',
    contact: 'contact-us/',
    newsletter: 'https://eepurl.com/iUfGPA',
    iconnect: 'https://springschurch.ccbchurch.com/goto/login',
    directions: 'https://maps.google.com/?q=Springs+Church,+1515+Auto+Mall+Loop,+Colorado+Springs,+CO+80920',
    facebook: 'https://www.facebook.com/springschurch.co/',
    instagram: 'https://www.instagram.com/springs__church/',
    youtube: 'https://www.youtube.com/@springs.church'
  },
  address: ['1515 Auto Mall Loop', 'Colorado Springs, CO 80920'],
  phone: '(719) 488-8331', email: 'info@springs.church', hours: 'Tue to Thu, 9 AM to 5 PM'
};

/* Helpers */
(function () {
  const S = window.SPRINGS;
  const MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
  const DOW = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  S.fmt = (iso) => {
    const [y, m, d] = iso.split('-').map(Number);
    const dt = new Date(y, m - 1, d);
    return { mon: MON[m - 1], day: d, dow: DOW[dt.getDay()], monthLong: dt.toLocaleString('en-US', { month: 'long' }) };
  };
  S.upcoming = (n) => {
    const today = new Date(); today.setHours(0, 0, 0, 0);
    return S.events.filter(e => new Date(e.d + 'T12:00') >= today).slice(0, n || 99);
  };
  S.thumb = (id) => `img/yt-${id}.jpg`;

  // Live status, in Mountain Time. Live window: Sunday 9:55 AM to 11:45 AM.
  S.live = () => {
    const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Denver', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
    }).formatToParts(new Date()).map(x => [x.type, x.value]));
    const wd = DOW.indexOf(p.weekday);
    const mins = (Number(p.hour) % 24) * 60 + Number(p.minute);
    const isLive = wd === 0 && mins >= 595 && mins < 705;
    let until = ((7 - wd) % 7) * 1440 + (600 - mins);
    if (until <= 0) until += 7 * 1440;
    const d = Math.floor(until / 1440), h = Math.floor((until % 1440) / 60), m = until % 60;
    const label = d > 0 ? `${d}d ${h}h` : h > 0 ? `${h}h ${m}m` : `${m}m`;
    return { isLive, label };
  };

  // Next gathering (Sun 10:00, Wed 18:30 MT). Live window ~ first 110 min.
  S.nextGathering = () => {
    const p = Object.fromEntries(new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Denver', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
    }).formatToParts(new Date()).map(x => [x.type, x.value]));
    const now = DOW.indexOf(p.weekday) * 1440 + (Number(p.hour) % 24) * 60 + Number(p.minute);
    const slots = [{ at: 600, name: 'Sunday Worship', when: 'Sunday at 10 AM' },
                   { at: 3 * 1440 + 1110, name: 'Wednesday Night', when: 'Wednesday at 6:30 PM' }];
    for (const s of slots) if (now >= s.at && now < s.at + 110) return { ...s, live: true, label: 'Live now' };
    let best = null;
    for (const s of slots) { let d = s.at - now; if (d <= 0) d += 7 * 1440; if (!best || d < best.d) best = { ...s, d }; }
    const d = Math.floor(best.d / 1440), h = Math.floor((best.d % 1440) / 60), m = best.d % 60;
    best.label = d > 0 ? `in ${d}d ${h}h` : h > 0 ? `in ${h}h ${m}m` : `in ${m}m`;
    best.today = d === 0 && best.d < 1440;
    return best;
  };
  S.storyOfWeek = () => {
    const wk = Math.floor((Date.now() / 864e5 + 4) / 7); // changes every Sunday-ish
    return S.stories[wk % S.stories.length];
  };

  // Option switcher (mockup chrome only)
  document.addEventListener('DOMContentLoaded', () => {
    const here = location.pathname.split('/').pop() || 'index.html';
    const opts = [['option-j.html', 'J', 'Front Door'], ['option-i.html', 'I', 'Open Door refined'], ['option-h.html', 'H', 'Embers'], ['option-g.html', 'G', 'Ignite + Open Door'], ['option-d.html', 'D', 'Ignite'], ['option-e.html', 'E', 'Open Door'], ['option-f.html', 'F', 'This Week'],
                  ['option-a.html', 'A', ''], ['option-b.html', 'B', ''], ['option-c.html', 'C', '']];
    const bar = document.createElement('nav');
    bar.className = 'mock-switch';
    bar.setAttribute('aria-label', 'Mockup options');
    bar.innerHTML = opts.map(([f, k, n]) =>
      `<a href="${f}" ${here === f ? 'aria-current="page"' : ''} ${n ? '' : 'class="old" title="Round 1"'}><b>${k}</b>${n ? `<span>${n}</span>` : ''}</a>`).join('').replace('<a href="option-a.html"', '<i></i><a href="option-a.html"');
    const st = document.createElement('style');
    st.textContent = `.mock-switch{position:fixed;left:50%;bottom:16px;transform:translateX(-50%);z-index:9999;display:flex;gap:2px;padding:4px;border-radius:999px;background:rgba(20,20,18,.82);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);box-shadow:0 8px 30px rgba(0,0,0,.25);font:600 12px/1 system-ui,sans-serif;max-width:calc(100vw - 24px);overflow-x:auto;scrollbar-width:none}
.mock-switch::-webkit-scrollbar{display:none}
.mock-switch a{display:flex;align-items:center;gap:6px;padding:8px 12px;border-radius:999px;color:rgba(255,255,255,.7);text-decoration:none;white-space:nowrap}
.mock-switch a b{display:grid;place-items:center;width:18px;height:18px;border-radius:50%;background:rgba(255,255,255,.14);font-size:11px}
.mock-switch i{width:1px;margin:6px 4px;background:rgba(255,255,255,.2)}.mock-switch a.old{padding:8px 5px;opacity:.6}.mock-switch a.old:hover{opacity:1}
.mock-switch a:hover{color:#fff}.mock-switch a[aria-current]{background:#FAF6F1;color:#1b1b19}.mock-switch a[aria-current] b{background:#C87F44;color:#fff}
@media (max-width:1399px){.mock-switch a:not([aria-current]) span{display:none}.mock-switch a:not([aria-current]):not(.old){padding:8px}}
@media (max-width:700px){.mock-switch a span{display:none}.mock-switch a{padding:8px}}`;
    document.head.appendChild(st);
    document.body.appendChild(bar);
    const cur = bar.querySelector('[aria-current]');
    if (cur && bar.scrollWidth > bar.clientWidth) bar.scrollLeft = cur.offsetLeft - (bar.clientWidth - cur.offsetWidth) / 2;
  });
})();
