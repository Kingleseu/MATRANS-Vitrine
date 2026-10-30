const mapRoot = document.querySelector('[data-map-root]');

if (mapRoot) {
  const selectors = [...mapRoot.querySelectorAll('[data-map-select]')];
  const panels = [...mapRoot.querySelectorAll('[data-map-panel]')];

  function selectZone(id) {
    selectors.forEach(button => {
      const active = button.dataset.mapSelect === id;
      button.classList.toggle('is-active', active);
      button.setAttribute('aria-pressed', String(active));
    });
    panels.forEach(panel => {
      panel.hidden = panel.dataset.mapPanel !== id;
    });
  }

  selectors.forEach(button => button.addEventListener('click', () => {
    selectZone(button.dataset.mapSelect);
    if (button.classList.contains('map-pin') && window.matchMedia('(max-width: 960px)').matches) {
      mapRoot.querySelector('.map-directory').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }));
}
