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
const heroCarousel = document.querySelector('[data-hero-carousel]');
if (heroCarousel) {
  const slides = [...heroCarousel.querySelectorAll('[data-hero-slide]')];
  let selected = 0;
  let timer;
  const showSlide = index => {
    selected = index;
    slides.forEach((slide, position) => slide.classList.toggle('is-active', position === index));
  };
  const stop = () => window.clearInterval(timer);
  const start = () => {
    stop();
    if (reducedMotion || document.hidden) return;
    timer = window.setInterval(() => showSlide((selected + 1) % slides.length), 6500);
  };
  document.addEventListener('visibilitychange', start);
  start();
}
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

const homeMap = document.querySelector('[data-home-map]');
if (homeMap) {
  const pins = [...homeMap.querySelectorAll('[data-home-zone]')];
  const panels = [...homeMap.querySelectorAll('[data-home-panel]')];
  pins.forEach(pin => pin.addEventListener('click', () => {
    const selected = pin.dataset.homeZone;
    pins.forEach(item => {
      const active = item.dataset.homeZone === selected;
      item.classList.toggle('is-active', active);
      item.setAttribute('aria-pressed', String(active));
    });
    panels.forEach(panel => {
      panel.hidden = panel.dataset.homePanel !== selected;
    });
    if (window.matchMedia('(max-width: 750px)').matches) {
      homeMap.querySelector('.home-map-directory').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }));
}

// Les valeurs viennent du serveur ; seul leur affichage est animé à chaque visite.
if (!reducedMotion) {
  const formatter = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 0 });
  const counters = [...document.querySelectorAll('[data-countup]')];
  const animateCounter = element => {
    const finalText = element.textContent.trim();
    const match = finalText.match(/^([+\-≈]?\s*)(\d[\d\s\u00a0\u202f]*)(\+?)(\s*%)?$/);
    if (!match) return;
    const value = Number(match[2].replace(/\s/g, ''));
    if (!Number.isFinite(value)) return;
    const prefix = match[1];
    const suffix = `${match[3]}${match[4] || ''}`;
    const duration = 1100;
    let start;
    const frame = timestamp => {
      if (start === undefined) start = timestamp;
      const progress = Math.min((timestamp - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const formatted = formatter.format(Math.round(value * eased)).replace(/[\u00a0\u202f]/g, ' ');
      element.textContent = progress === 1 ? finalText : `${prefix}${formatted}${suffix}`;
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
