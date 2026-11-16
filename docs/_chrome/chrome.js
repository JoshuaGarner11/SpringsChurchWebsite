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
  const open = () => {
    lastFocus = document.activeElement;
    menu.hidden = false;
    requestAnimationFrame(() => menu.classList.add('sc-open'));
    burger.setAttribute('aria-expanded', 'true');
    document.documentElement.classList.add('sc-lock');
    menu.querySelector('.sc-close').focus();
  };
  const close = () => {
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
