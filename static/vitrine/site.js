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
if ('IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
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
