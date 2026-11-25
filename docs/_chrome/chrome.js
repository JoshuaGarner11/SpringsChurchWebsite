(function () {
  /* header goes solid after a little scroll; menu opens full screen; footer SPRINGS. letters rise in */
  const hdr = document.getElementById('sc-hdr'), menu = document.getElementById('sc-menu');
  if (!hdr || hdr.dataset.ready) return;
  hdr.dataset.ready = '1';
  document.documentElement.classList.add('sc-js');
  const onScroll = () => hdr.classList.toggle('sc-solid', scrollY > 40);
  addEventListener('scroll', onScroll, { passive: true }); onScroll();

  const burger = hdr.querySelector('.sc-burger');
  let lastFocus = null;
  // The header icon travels into the menu's corner as it opens, and back as it closes. Transform only.
  const fromIc = hdr.querySelector('.sc-mark img'), toIc = menu.querySelector('.sc-menu-top .sc-mark img');
  let fly;
  const flyIcon = opening => {
    if (!fromIc || !toIc || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (fly) fly.cancel();
    fromIc.getAnimations().forEach(x => x.cancel());
    const a = fromIc.getBoundingClientRect(), t = toIc.getBoundingClientRect();
    if (!a.width || !t.width) return;
    toIc.style.transformOrigin = '0 0';
    const away = `translate(${a.left - t.left}px, ${a.top - t.top}px) scale(${a.width / t.width})`, home = 'translate(0, 0) scale(1)';
    fly = toIc.animate(opening ? [{ transform: away }, { transform: home }] : [{ transform: home }, { transform: away }],
      { duration: opening ? 560 : 300, easing: opening ? 'cubic-bezier(.22,1,.36,1)' : 'cubic-bezier(.4,0,.2,1)' });
    if (opening) fromIc.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 360, fill: 'forwards' });
  };
  const open = () => {
    lastFocus = document.activeElement;
    menu.hidden = false;
    flyIcon(true);
    requestAnimationFrame(() => menu.classList.add('sc-open'));
    burger.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.add('sc-lock');
    menu.querySelector('.sc-close').focus();
  };
  const close = () => {
    flyIcon(false);
    menu.classList.remove('sc-open');
    burger.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('sc-lock');
    setTimeout(() => { menu.hidden = true; }, 300);
    if (lastFocus) lastFocus.focus();
  };
  burger.addEventListener('click', open);
  menu.querySelector('.sc-close').addEventListener('click', close);
  addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) close(); });
  menu.addEventListener('keydown', e => {   // keep Tab inside the open menu
    if (e.key !== 'Tab') return;
    const f = [...menu.querySelectorAll('a,button')]; const a = f[0], z = f[f.length - 1];
    if (e.shiftKey && document.activeElement === a) { e.preventDefault(); z.focus(); }
    else if (!e.shiftKey && document.activeElement === z) { e.preventDefault(); a.focus(); }
  });

  const wm = document.querySelector('.sc-wordmark');
  if (wm) {
    wm.innerHTML = [...'SPRINGS'].map((ch, i) => `<span style="--i:${i}">${ch}</span>`).join('') + '<span style="--i:7"><em>.</em></span>';
    if ('IntersectionObserver' in window) {
      const io = new IntersectionObserver(es => { if (es.some(x => x.isIntersecting)) { wm.classList.add('sc-in-view'); io.disconnect(); } }, { threshold: .3 });
      io.observe(wm);
    } else wm.classList.add('sc-in-view');
  }
})();
