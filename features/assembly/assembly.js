// Scroll-driven assembly: parts fly in from off-stage and lock together as the pinned section scrolls.
const section = document.getElementById('assembly');
if (section) {
  const rig = section.querySelector('.assembly__rig');
  const glow = section.querySelector('.assembly__glow');
  const bar = section.querySelector('.assembly__progress i');
  const steps = [...section.querySelectorAll('.assembly__step')];
  const parts = [...rig.querySelectorAll('.assembly__part')].map(el => {
    const d = el.dataset;
    const [fx, fy] = d.from.split(',').map(Number);
    const [s, e] = d.win.split(',').map(Number);
    return { el, fx, fy, s, e, rot: Number(d.rot || 0), flip: d.flip ? -1 : 1 };
  });
  const stepRanges = [[0, 1 / 3], [1 / 3, 2 / 3], [2 / 3, 1]];
  // Split each step's heading and copy into per-character spans so they can be scrubbed by scroll.
  const stepChars = steps.map(step => [...step.querySelectorAll(':scope > span, h3, p')].flatMap(node => {
    const text = node.textContent;
    node.setAttribute('aria-label', text);
    node.textContent = '';
    return text.split(' ').flatMap((word, wi, all) => {
      const w = document.createElement('span');
      w.className = 'assembly__word';
      w.setAttribute('aria-hidden', 'true');
      const chars = [...word].map(ch => {
        const s = document.createElement('span');
        s.className = 'assembly__char';
        s.textContent = ch;
        w.append(s);
        return s;
      });
      node.append(w);
      if (wi < all.length - 1) node.append(' ');
      return chars;
    });
  }));
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const easeOut = t => 1 - Math.pow(1 - t, 3);
  let unit = rig.offsetWidth / 100;
  const lastStep = stepRanges.length - 1;
  const drawn = [];

  const render = p => {
    let snap = 0;
    for (const { el, fx, fy, s, e, rot, flip } of parts) {
      const t = clamp((p - s) / (e - s));
      const k = easeOut(t);
      const pulse = Math.sin(Math.PI * clamp((t - 0.82) / 0.18)) * 0.05;
      el.style.opacity = clamp(t / 0.3);
      el.style.transform = `translate(${(1 - k) * fx * unit}px,${(1 - k) * fy * unit}px) rotate(${(1 - k) * rot}deg) scale(${flip * (1 + (1 - k) * 0.3 + pulse)},${1 + (1 - k) * 0.3 + pulse})`;
      el.style.filter = t > 0 && t < 1 ? `drop-shadow(0 18px 24px #0009) blur(${(1 - k) * 6}px)` : '';
      if (t > 0.82 && t < 1) snap = Math.max(snap, Math.sin(Math.PI * (t - 0.82) / 0.18));
    }
    glow.style.opacity = 0.35 + snap * 0.65;
    rig.style.transform = `scale(${0.88 + 0.12 * p}) rotate(${(1 - p) * -3}deg)`;
    bar.style.transform = `scaleX(${p})`;
    stepRanges.forEach(([a, b], i) => {
      const u = (p - a) / (b - a);
      const live = u > -0.02 && u < 1.02;
      if (!live && drawn[i] === false) return;
      drawn[i] = live;
      const chars = stepChars[i];
      const n = chars.length;
      chars.forEach((el, j) => {
        const f = j / n;
        const inK = easeOut(clamp((u - 0.02 - f * 0.22) / 0.1));
        // the last step stays on screen; earlier ones rise away character by character
        const outK = i === lastStep ? 0 : easeOut(clamp((u - 0.8 - f * 0.12) / 0.08));
        el.style.opacity = live ? inK * (1 - outK) : 0;
        el.style.transform = `translateY(${(1 - inK) * 1.1 - outK * 1.4}em)`;
      });
    });
  };

  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  let queued = false;
  const update = () => {
    queued = false;
    if (reduced.matches) { stepChars.flat().forEach(el => { el.style.opacity = 1; el.style.transform = ''; }); parts.forEach(({ el }) => { el.style.opacity = 1; el.style.transform = el.dataset.flip ? 'scaleX(-1)' : ''; el.style.filter = ''; }); glow.style.opacity = 1; return; }
    const r = section.getBoundingClientRect();
    render(clamp(-r.top / (r.height - innerHeight)));
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', () => { unit = rig.offsetWidth / 100; queue(); });
  update();
}
