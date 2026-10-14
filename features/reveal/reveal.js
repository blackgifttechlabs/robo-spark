// Scroll reveals for page sections, plus a gentle hero push-out as you scroll away from it.
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!reduced) {
  const groups = ['.section-heading', '.mission-card', '.how__inner > div:first-child', '.steps li', '.teachers > :not(.btn)', '.teachers > .btn'];
  const io = new IntersectionObserver(entries => entries.forEach(en => {
    if (en.isIntersecting) { en.target.classList.add('is-in'); io.unobserve(en.target); }
  }), { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
  groups.forEach(sel => document.querySelectorAll(sel).forEach((el, i) => {
    el.classList.add('reveal');
    el.style.setProperty('--d', `${(i % 3) * 0.12}s`);
    io.observe(el);
  }));

  const scene = document.querySelector('.hero__scene');
  const content = document.querySelector('.hero__content');
  let queued = false;
  const tick = () => {
    queued = false;
    const y = scrollY, h = innerHeight;
    if (y > h) return;
    const k = y / h;
    scene.style.transform = `translateY(${y * 0.25}px) scale(${1 + k * 0.08})`;
    content.style.opacity = Math.max(0, 1 - k * 1.5);
    content.style.transform = `translateY(${-y * 0.12}px)`;
  };
  addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(tick); } }, { passive: true });
}
