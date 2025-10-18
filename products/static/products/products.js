document.addEventListener('DOMContentLoaded', function () {
  // ===== BURGER =====
  var burger = document.querySelector('.burger');
  var kategorieNav = document.querySelector('.kategorie-nav');

  if (burger && kategorieNav) {
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

  // ===== IKONA KOSZYKA - Dodaj produkt do koszyka =====
  document.querySelectorAll('.cart-icon').forEach(button => {
    button.addEventListener('click', function () {
        const productId = this.getAttribute('data-product-id'); // Pobieramy ID produktu
        const quantity = 1; // Na razie zakładamy, że zawsze dodajemy 1 sztukę

        // Wysyłamy żądanie do backendu, żeby dodać produkt do koszyka
        fetch("{% url 'orders:cart_add' %}", {
            method: 'POST',
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                'product_id': productId,
                'quantity': quantity
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.ok) {
                // Zaktualizuj UI – np. wyświetl komunikat, zaktualizuj liczbę w koszyku w nagłówku

                document.querySelector('.cart-count').textContent = data.items; // Zaktualizuj liczbę produktów w koszyku
            }
        })
        .catch(error => {
            console.error("Wystąpił błąd:", error);
        });
    });
  });

  // ===== DROPDOWNY =====
  var dropdowns = document.querySelectorAll('.dropdown');
  dropdowns.forEach(function (dropdown) {
    var menu = dropdown.querySelector('.menu');
    var options = dropdown.querySelectorAll('.menu li');
    if (!menu || !options.length) return;

    // Otwieranie/zamykanie na hover
    dropdown.addEventListener('mouseenter', function () {
      menu.classList.add('menu-open');
    });
    dropdown.addEventListener('mouseleave', function () {
      menu.classList.remove('menu-open');
    });

    // Klik w opcję
    options.forEach(function (option) {
      option.addEventListener('click', function (e) {
        e.preventDefault();

        // UI jak wcześniej
        options.forEach(function (o) { o.classList.remove('active'); });
        option.classList.add('active');
        menu.classList.remove('menu-open');

        // Pobierz wartość filtra
        var raw = option.getAttribute('data-value');
        var value = (raw !== null ? raw : option.textContent).trim().replace(/\s*\(\d+\)\s*$/, '');

        // Zbuduj nowy URL
        try {
          var url = new URL(window.location.href);
          if (value) url.searchParams.set('type', value);
          else url.searchParams.delete('type');
          url.searchParams.delete('page');
          window.location.assign(url.toString());
        } catch (err) {
          var q = value ? ('?type=' + encodeURIComponent(value)) : '';
          window.location.href = window.location.pathname + q;
        }
      });
    });
  });

  // ===== LEWE MENU – rozwijane panele =====
  var menuLeft = document.querySelector('.products-menu');
  if (menuLeft) {
    menuLeft.addEventListener('click', function (e) {
      var btn = e.target.closest('.submenu-toggle');
      if (!btn) return;

      var block = btn.closest('.submenu-block');
      var panel = block && block.nextElementSibling;
      if (!panel || !panel.classList.contains('submenu-panel')) return;

      var willOpen = !panel.classList.contains('is-open');
      panel.classList.toggle('is-open', willOpen);
      btn.classList.toggle('is-open', willOpen);
    });
  }

  // ===== LEWE MENU -> filtr ?type=... =====
  (function () {
    var leftMenu = document.querySelector('.products-menu');
    if (!leftMenu) return;

    function goWithType(value) {
      var url = new URL(window.location.href);
      if (value) url.searchParams.set('type', value);
      else url.searchParams.delete('type');
      url.searchParams.delete('page'); // reset paginacji przy zmianie filtra
      window.location.assign(url.toString());
    }

    leftMenu.addEventListener('click', function (e) {
      if (e.target.closest('.submenu-toggle')) return;

      var link = e.target.closest('.products-menu-link, .products-cat2, .title-link');
      if (!link) return;

      var isSectionTitle = link.classList.contains('title-link') && !link.hasAttribute('data-type');
      if (isSectionTitle) return;

      e.preventDefault();

      var raw = link.getAttribute('data-type');
      var value = (raw !== null ? raw : link.textContent).trim();

      leftMenu.querySelectorAll('.products-menu-link, .products-cat2, .title-link').forEach(function (el) {
        el.classList.remove('active');
      });
      link.classList.add('active');

      goWithType(value);
    });

    var currentType = new URLSearchParams(location.search).get('type') || '';
    if (currentType) {
      leftMenu.querySelectorAll('.products-menu-link, .products-cat2, .title-link').forEach(function (el) {
        var val = (el.getAttribute('data-type') || el.textContent).trim();
        el.classList.toggle('active', val === currentType);
      });
    }
  })();

  // ===== SORTOWANIE =====
  document.querySelectorAll('.sort-wrapper').forEach(function (wrapper) {
    var list  = wrapper.querySelector('.sort-list');
    var items = wrapper.querySelectorAll('.sort-list li');
    var label = wrapper.querySelector('.sort');
    var caret = wrapper.querySelector('.caret');
    if (!list || !label || !caret) return;

    function toggle(open) {
      var willOpen = (open !== undefined) ? open : !list.classList.contains('sort-list-open');
      list.classList.toggle('sort-list-open', willOpen);
      caret.classList.toggle('caret-rotate', willOpen);
    }

    label.addEventListener('click', function (e) { e.stopPropagation(); toggle(); });
    caret.addEventListener('click', function (e) { e.stopPropagation(); toggle(); });
    document.addEventListener('click', function () { toggle(false); });

    items.forEach(function (item) {
      item.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        label.textContent = item.textContent.trim();
        items.forEach(function (o) { o.classList.remove('active'); });
        item.classList.add('active');
        toggle(false);

        var v = item.getAttribute('data-type'); // Pobieraj tylko jeśli istnieje

        try {
          var u = new URL(window.location.href);
          if (v) u.searchParams.set('type', v); else u.searchParams.delete('type');
          u.searchParams.set('bestsellers', 'true'); // Ustaw 'bestsellers=true'
          u.searchParams.delete('page');
          window.location.assign(u.toString());
        } catch (_) {
          var q = (v ? ('?type=' + encodeURIComponent(v)) : '') + '&bestsellers=true'; // Dodaj 'bestsellers=true'
          window.location.href = window.location.pathname + q;
        }
      });
    });



    (function syncFromQuery() {
      var current = new URLSearchParams(location.search).get('type') || '';
      var matched = false;
      items.forEach(function (li) {
        var val = (li.getAttribute('data-type') || li.textContent).trim();
        if (val === current) {
          li.classList.add('active');
          label.textContent = li.textContent.trim();
          matched = true;
        }
      });
      if (!matched) label.textContent = 'Produkty';
    })();
  });

  // ===== WYSZUKIWARKA =====
  var box = document.getElementById('search');
  if (box) {
    var btn = box.querySelector('.search__toggle');
    var inp = box.querySelector('.search__input');
    var clearBtn = box.querySelector('.search__clear');

    function openSearch() {
      box.classList.add('active-search');
      if (inp) { inp.disabled = false; inp.focus(); }
    }
    function closeSearch() {
      box.classList.remove('active-search');
      if (inp) { inp.value = ''; inp.blur(); inp.disabled = true; }
    }

    if (btn) {
      btn.addEventListener('click', function () {
        if (!box.classList.contains('active-search')) openSearch();
        else if (inp) inp.focus();
      });
    }
    if (clearBtn) clearBtn.addEventListener('click', closeSearch);
    box.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeSearch(); });
  }
});



document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart-icon').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Zapobiegamy domyślnemu wysłaniu formularza i przekierowaniu

            const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
            const quantity = 1;  // Zakładamy, że zawsze dodajemy 1 sztukę

            console.log("Dodaję do koszyka produkt o ID:", productId);  // Debugowanie

            // Używamy wygenerowanego URL do wysłania żądania
            fetch(cartAddUrl, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,  // CSRF token
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    'product_id': productId,
                    'quantity': quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);  // Debugowanie odpowiedzi z serwera
                if (data.ok) {

                    document.querySelector('.cart-count').textContent = data.items; // Zaktualizuj liczbę produktów w koszyku
                }
            })
            .catch(error => {
                console.error("Wystąpił błąd:", error);
            });
        });
    });
});






