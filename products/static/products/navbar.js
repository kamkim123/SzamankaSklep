console.log("navbar.js załadowany!");


document.addEventListener('DOMContentLoaded', function () {
  // ===== BURGER =====
  var burger = document.querySelector('.burger');
  var kategorieNav = document.querySelector('.kategorie-nav');

  if (burger && kategorieNav) {
  console.log("burger exists?", !!burger, "kategorieNav exists?", !!kategorieNav);

    burger.addEventListener('click', function () {
      burger.classList.toggle('active');
      kategorieNav.classList.toggle('active');
    });

    document.querySelectorAll('.kategorie-nav').forEach(function (n) {
      n.addEventListener('click', function () {
        burger.classList.remove('active');
        kategorieNav.classList.remove('active');
      });
    });
  }




const dropdowns = document.querySelectorAll('.dropdown');

dropdowns.forEach((dropdown) => {
  const select  = dropdown.querySelector('.select');
  const menu    = dropdown.querySelector('.menu');
  const options = dropdown.querySelectorAll('.menu li');
  // UWAGA: nie bierzemy .pasek1 jako "selected" – nie będziemy zmieniać napisu

  const form     = document.getElementById('navFilterForm');
  const typeInput= document.getElementById('navTypeInput');

  dropdown.addEventListener('mouseenter', () => {
    select && select.classList.add('select-clicked');
    menu && menu.classList.add('menu-open');
  });

  dropdown.addEventListener('mouseleave', () => {
    select && select.classList.remove('select-clicked');
    menu && menu.classList.remove('menu-open');
  });

  options.forEach(option => {
    option.addEventListener('click', (e) => {
      e.preventDefault();

      // --- UI: tylko aktywna klasa + zamknięcie; NIE zmieniamy napisu „Produkty”
      options.forEach(o => o.classList.remove('active'));
      option.classList.add('active');
      select && select.classList.remove('select-clicked');
      menu && menu.classList.remove('menu-open');

      // --- Wartość filtra z data-value lub z tekstu (bez " (123)")
      const raw = option.getAttribute('data-value');
      const value = (raw || '').trim();

      if (!value) return;

      // --- Preferencja: submit ukrytego formularza (ładnie przechodzi do listy)
      if (form && typeInput) {
        typeInput.value = value;
        form.submit();
        return;
      }

      // --- Fallback: zbuduj URL do listy produktów
      // 1) jeśli masz data-target na .dropdown, np. data-target="/products/"
      const targetAttr = dropdown.getAttribute('data-target');
      const targetPath = targetAttr || window.location.pathname; // użyj własnej ścieżki, jeśli chcesz

      try {
        const url = new URL(targetPath, window.location.origin);
        if (value) url.searchParams.set('type', value);
        else       url.searchParams.delete('type');
        url.searchParams.delete('page');
        window.location.assign(url.toString());
      } catch (_) {
        // fallback dla bardzo starych przeglądarek
        const q = value ? ('?type=' + encodeURIComponent(value)) : '';
        window.location.href = targetPath + q;
      }
    });
  });
});










// --- User popover toggle (mobile + a11y) ---
(function(){
  const popover = document.querySelector('.user-popover');
  if (!popover) return;
  const trigger = popover.querySelector('.user-trigger');
  const panel   = popover.querySelector('.user-panel');

  function open()  { popover.classList.add('open');  trigger.setAttribute('aria-expanded','true'); }
  function close() { popover.classList.remove('open'); trigger.setAttribute('aria-expanded','false'); }

  trigger.addEventListener('click', (e) => {
    // klik na mobile przełącza, ale nie psuje hovera na desktopie
    e.stopPropagation();
    if (popover.classList.contains('open')) close(); else open();
  });

  // zamykanie kliknięciem poza
  document.addEventListener('click', (e) => {
    if (!popover.contains(e.target)) close();
  });

  // Esc zamyka
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') close();
  });
})();








  // ===== SEARCH (tylko otwórz/zamknij) =====
  const searchBox = document.getElementById('search');
  if (searchBox) {
    const btn = searchBox.querySelector('.search__toggle');
    const inp = searchBox.querySelector('.search__input');
    const clearBtn = searchBox.querySelector('.search__clear');
    const resultsBox = document.getElementById('live-results');

    function openSearch() {
      searchBox.classList.add('active-search');
      if (inp) { inp.disabled = false; inp.focus(); }
    }

    function closeSearch() {
      searchBox.classList.remove('active-search');
      if (inp) { inp.value = ''; inp.blur(); inp.disabled = true; }
      if (resultsBox) { resultsBox.classList.add('not-visible'); resultsBox.innerHTML = ''; }
    }

    if (btn) btn.addEventListener('click', () => {
      if (!searchBox.classList.contains('active-search')) openSearch();
      else inp && inp.focus();
    });

    if (clearBtn) clearBtn.addEventListener('click', closeSearch);

    searchBox.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeSearch();
    });
  }

}); // <-- to jest koniec DOMContentLoaded














