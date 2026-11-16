/* Springs Care: shared content for every option.
   Anything wrapped in <span class="tbd"> still needs Michael Fratt's confirmation.
   Toggle the yellow marks with the "Show to-confirm" switch (bottom right). */
(function () {
  const T = (s) => `<span class="tbd" title="Confirm with Michael">${s}</span>`;

  /* ---------- dates ---------- */
  function secondWednesday(y, m) {
    const d = new Date(y, m, 1);
    const off = (3 - d.getDay() + 7) % 7; // first Wednesday
    return new Date(y, m, 1 + off + 7);
  }
  function nextMembershipClass(now = new Date()) {
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    let d = secondWednesday(now.getFullYear(), now.getMonth());
    if (d < today) d = secondWednesday(now.getFullYear(), now.getMonth() + 1);
    return d;
  }
  const fmt = (d, o) => d.toLocaleDateString('en-US', o);
  const next = nextMembershipClass();
  const isToday = next.toDateString() === new Date().toDateString();
  const nextLabel = isToday ? 'Tonight' : fmt(next, { weekday: 'long', month: 'long', day: 'numeric' });
  const nextShort = isToday ? 'Tonight' : fmt(next, { month: 'short', day: 'numeric' });

  /* GriefShare seminars from springs.church/events. Each hides itself once it's over. */
  const seminars = [
    { title: 'Loss of a Spouse Seminar', start: '2026-10-26T18:30', end: '2026-10-26T20:30',
      when: 'Monday, October 26 · 6:30–8:30 PM', where: 'Classroom 1',
      blurb: 'A 35-minute video from counselors, pastors and widowed men and women, then conversation with others who understand. No pressure to share. Everyone takes home a booklet of short readings.',
      url: 'https://find.griefshare.org/groups/299682/registrations/new' },
    { title: 'Surviving the Holidays', start: '2026-11-07T13:00', end: '2026-11-07T15:00',
      when: 'Saturday, November 7 · 1:00–3:00 PM', where: 'Classroom 1',
      blurb: 'Practical help for facing the holidays after a loss, in a safe, nonjudgmental room. You’ll leave with a Holiday Survival Guide.',
      url: 'https://find.griefshare.org/groups/299683/registrations/new' },
  ].filter((e) => new Date(e.end) > new Date());

  /* ---------- form choices (become the ChurchCo form dropdown) ---------- */
  const needs = [
    ['membership', 'Membership class'],
    ['counseling', 'Pastoral counseling'],
    ['mentoring', 'Men’s mentoring'],
    ['wedding', 'Planning a wedding'],
    ['baby', 'New baby'],
    ['visit', 'Hospital or home visit'],
    ['memorial', 'Memorial or funeral service'],
    ['griefshare', 'GriefShare'],
    ['help', 'Practical help'],
    ['prayer', 'Prayer'],
    ['other', 'Something else'],
  ];

  /* ---------- the services ---------- */
  const services = [
    {
      id: 'membership', need: 'membership', name: 'Membership',
      season: 'When you’re ready to call Springs home',
      ask: 'I want to become a member',
      line: 'Say “this is my church,” and let this family say it back.',
      body: [
        'Membership is how you commit to this church family, and how this family commits to you: to know you, pray for you, and walk with you in every season on this page.',
        'It starts with our membership class. We’ll share our story, what we believe, how the church is led and cared for, and how you can find your place to serve. Afterward you’ll sit down with a pastor or elder to share your story and ask anything.',
      ],
      facts: [
        ['When', `The 2nd Wednesday of every month, ${T('6:30 PM')}`],
        ['Where', 'The Green Room'],
        ['Next class', nextLabel],
      ],
      cta: 'Save my seat',
      photo: 'img/community.jpg', pos: '50% 35%',
    },
    {
      id: 'counseling', need: 'counseling', name: 'Counseling & Mentoring',
      season: 'When you need someone to talk to',
      ask: 'I need someone to talk to',
      line: 'Biblical counseling with a pastor, and men who will invest in you.',
      body: [
        'Sometimes you just need someone to sit with you, listen, pray, and help you see the next step. Our pastors offer free, short-term biblical counseling for individuals, couples and families.',
        'When a need calls for longer-term or clinical care, we’ll help you connect with trusted Christian licensed counselors, and we’ll keep caring for you along the way.',
      ],
      facts: [
        ['Cost', 'Free'],
        ['Length', `A few sessions, ${T('usually 3–5')}`],
        ['For', 'Individuals, couples & families'],
      ],
      sub: {
        id: 'mentoring', need: 'mentoring', name: 'Men’s Mentoring',
        ask: 'I’m looking for a mentor',
        body: 'A ministry that pairs seasoned men with younger men, so they can invest in them through faith, work, marriage, fatherhood and the ordinary stuff of life. Want a mentor, or ready to be one? Let us know and we’ll make the match.',
        verse: ['As iron sharpens iron, so a friend sharpens a friend.', 'Proverbs 27:17 NLT'],
        extra: 'Also: Springs Men’s Breakfast, the 1st Saturday of every month, 8 AM in Classroom 1.',
        cta: 'Connect me',
      },
      note: 'Pastoral counseling isn’t an emergency service. If you’re in crisis, call or text 988.',
      cta: 'Request counseling',
      photo: 'img/missions.jpg', pos: '50% 45%',
    },
    {
      id: 'weddings', need: 'wedding', name: 'Weddings',
      season: 'When you’re getting married',
      ask: 'We’re getting married',
      line: 'Build your marriage on Jesus from the very first day.',
      body: [
        'We love celebrating weddings, and we care even more about the marriage that follows. Springs pastors officiate weddings for members and regular attenders, and every couple walks through premarital counseling before the big day.',
        `Our building can host your ceremony and your reception. ${T('Reach out at least 6 months ahead')} so we can talk dates, rooms and next steps.`,
      ],
      facts: [
        ['Who', 'Members & regular attenders'],
        ['Required', `Premarital counseling (${T('6 sessions')})`],
        ['Receptions', `Available in our building · ${T('fees & rooms TBD')}`],
      ],
      cta: 'Start the conversation',
      photo: null,
    },
    {
      id: 'baby', need: 'baby', name: 'New Baby',
      season: 'When a baby arrives',
      ask: 'We’re having a baby',
      line: 'Meals, a visit, a gift, and a church that will help you raise them.',
      body: [
        'A new baby changes everything, and you shouldn’t have to cook through it. Let us know when your little one is on the way or has arrived, and we’ll set up a meal train, come by to visit and pray over your family, and bring a welcome gift.',
        `When you’re ready, you can dedicate your child on a Sunday morning, promising before your church family to raise them to know and love Jesus. ${T('Dedications happen a few times a year.')}`,
      ],
      facts: [
        ['We bring', 'Meals, a visit & a welcome gift'],
        ['Baby dedication', T('Next date TBD')],
      ],
      verse: ['Children are a gift from the LORD; they are a reward from him.', 'Psalm 127:3 NLT'],
      cta: 'Tell us about your baby',
      photo: null,
    },
    {
      id: 'visitation', need: 'visit', name: 'Visitation',
      season: 'When someone is sick or can’t get out',
      ask: 'Someone is in the hospital',
      line: 'Hospitals don’t always tell us. Please do.',
      body: [
        'If you or someone you love is in the hospital, recovering from surgery, homebound, or living in a nursing or assisted living facility, we want to come to you. A pastor or member of our care team will visit, listen and pray.',
        'Because of privacy laws, hospitals won’t let us know you’re there, so a quick note from you or a family member is how we find out.',
      ],
      facts: [
        ['Hospital', 'Stays, surgery & recovery'],
        ['At home', 'Homebound members'],
        ['Care facilities', 'Nursing & assisted living'],
      ],
      cta: 'Request a visit',
      photo: null,
    },
    {
      id: 'memorial', need: 'memorial', name: 'Memorial Services',
      season: 'When you lose someone',
      ask: 'I lost someone',
      line: 'We’ll help you say goodbye, and we’ll stay close after.',
      body: [
        'Losing someone you love is one of the hardest things you’ll ever walk through. Our pastors will help you plan a funeral or memorial service that honors your loved one and points to the hope we have in Jesus. We can officiate, host the service in our building, and help with the reception afterward.',
        'And when the service is over and the casseroles stop coming, we’re still here.',
      ],
      facts: [
        ['We help with', 'Planning, officiating & hosting'],
        ['Reception', T('Room + meal help available')],
      ],
      verse: ['The LORD is close to the brokenhearted; he rescues those whose spirits are crushed.', 'Psalm 34:18 NLT'],
      cta: 'Talk with a pastor',
      photo: null,
    },
  ];

  const griefshare = {
    name: 'GriefShare',
    ask: 'I’m grieving',
    line: 'A weekly group for anyone grieving the death of someone close.',
    body: 'GriefShare is a support group where you’ll watch a short video, then talk (or just listen) with others who understand. Each week stands on its own, so you can start anytime.',
    facts: [
      ['When', T('Weekly · day & time TBD')],
      ['Where', T('Classroom 1')],
    ],
    seminars,
    events: 'events@springs.church',
  };

  const more = [
    { id: 'help', need: 'help', name: 'Practical Help', ask: 'We need practical help',
      body: `When life suddenly falls apart (a job loss, an emergency, a bill you didn’t see coming), tell us. Requests are kept confidential and ${T('reviewed by our deacons')}.`,
      cta: 'Ask for help' },
    { id: 'prayer', need: 'prayer', name: 'Prayer', ask: 'I need prayer',
      body: 'We are a praying church. Send a request and our prayer team will lift it up, or join us for Wednesday Night Prayer.',
      cta: 'Send a prayer request', href: '/prayer' },
  ];

  window.CARE = {
    T, services, griefshare, more, needs, nextLabel, nextShort,
    verse: ['Share each other’s burdens, and in this way obey the law of Christ.', 'Galatians 6:2 NLT'],
    events: 'events@springs.church',
    crisis: 'In an emergency, call 911. If you’re thinking about suicide or are in emotional crisis, call or text 988 any time.',
  };

  /* ---------- shared UI: mock form, option switcher, tbd toggle ---------- */
  window.careForm = function (id = 'care-form') {
    const opts = needs.map(([v, l]) => `<option value="${v}">${l}</option>`).join('');
    return `
<form class="cf" id="${id}" onsubmit="event.preventDefault();this.classList.add('sent')">
  <div class="cf-row"><label>First name<input required autocomplete="given-name"></label><label>Last name<input required autocomplete="family-name"></label></div>
  <div class="cf-row"><label>Email<input type="email" required autocomplete="email"></label><label>Phone<input type="tel" autocomplete="tel"></label></div>
  <label>What can we help with?<select name="need" required><option value="" disabled selected>Choose one</option>${opts}</select></label>
  <fieldset><legend>Who is this for?</legend><label class="r"><input type="radio" name="who" checked> Me / my family</label><label class="r"><input type="radio" name="who"> Someone I care about</label></fieldset>
  <label>Anything you’d like us to know? <i>Optional</i><textarea rows="4" placeholder="Names, dates, the hospital, or just what’s on your heart."></textarea></label>
  <button class="cf-btn" type="submit">Send to our care team</button>
  <p class="cf-fine">Only our care team sees this. ${T('Someone will reach out within 1–2 business days.')}</p>
  <div class="cf-done" role="status"><b>Thank you.</b> Our care team has your note and will reach out soon. <span>(Preview only, nothing was sent.)</span></div>
</form>`;
  };

  /* Pick a need in the form and scroll to it. Any element with data-need="x" calls this. */
  window.pickNeed = function (need) {
    const f = document.querySelector('.cf');
    if (!f) return;
    const s = f.querySelector('select[name=need]');
    if (need) s.value = need;
    const top = f.getBoundingClientRect().top + scrollY - 110;
    scrollTo({ top, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
    s.classList.remove('flash'); void s.offsetWidth; s.classList.add('flash');
  };
  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-need]');
    if (!a) return;
    e.preventDefault();
    pickNeed(a.dataset.need);
  });

  document.addEventListener('DOMContentLoaded', () => {
    const cur = (location.pathname.match(/option-(\w)/) || [])[1] || 'a';
    const sw = document.createElement('div');
    sw.className = 'sw';
    sw.innerHTML = `<span>Care page</span>${['a', 'b', 'c', 'd', 'e', 'f', 'g'].map((k) =>
      `<a href="option-${k}.html" ${k === cur ? 'aria-current="page"' : ''}>${k.toUpperCase()}</a>`).join('')}
      <label><input type="checkbox" id="tbdt" checked> Show to-confirm</label>`;
    document.body.appendChild(sw);
    const t = sw.querySelector('#tbdt');
    try { if (localStorage.getItem('care-tbd') === '0') t.checked = false; } catch (_) {}
    const apply = () => { document.documentElement.classList.toggle('hide-tbd', !t.checked); try { localStorage.setItem('care-tbd', t.checked ? '1' : '0'); } catch (_) {} };
    t.addEventListener('change', apply); apply();
  });
})();
