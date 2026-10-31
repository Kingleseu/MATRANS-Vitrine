const menuButton = document.querySelector('.menu-toggle');
const menu = document.querySelector('.main-nav');
if (menuButton && menu) {
  menuButton.addEventListener('click', () => {
    const opened = menu.classList.toggle('open');
    menuButton.setAttribute('aria-expanded', String(opened));
    menuButton.setAttribute('aria-label', opened ? 'Fermer le menu' : 'Ouvrir le menu');
  });
  menu.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    menu.classList.remove('open');
    menuButton.setAttribute('aria-expanded', 'false');
  }));
}
const elements = document.querySelectorAll('[data-reveal]');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if ('IntersectionObserver' in window && !reducedMotion) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .1 });
  elements.forEach(element => observer.observe(element));
} else {
  elements.forEach(element => element.classList.add('visible'));
}

// Les valeurs viennent du serveur ; seul leur affichage est animé à chaque visite.
if (!reducedMotion) {
  const formatter = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
  const counters = [...document.querySelectorAll('[data-countup]')];
  const animateCounter = element => {
    const finalText = element.textContent.trim();
    const match = finalText.match(/^(-?)(\d[\d\s\u00a0\u202f]*)(\+?)(\s*%)?$/);
    if (!match) return;
    const value = Number(match[2].replace(/\s/g, ''));
    if (!Number.isFinite(value)) return;
    const sign = match[1];
    const suffix = `${match[3]}${match[4] || ''}`;
    const duration = 1100;
    let start;
    const frame = timestamp => {
      if (start === undefined) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const formatted = formatter.format(Math.round(value * eased)).replace(/[\u00a0\u202f]/g, ' ');
      element.textContent = progress === 1 ? finalText : `${sign}${formatted}${suffix}`;
      if (progress < 1) window.requestAnimationFrame(frame);
    };
    window.requestAnimationFrame(frame);
  };
  if ('IntersectionObserver' in window) {
    const counterObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          counterObserver.unobserve(entry.target);
        }
      });
    }, { threshold: .35 });
    counters.forEach(counter => counterObserver.observe(counter));
  } else {
    counters.forEach(animateCounter);
  }
}
