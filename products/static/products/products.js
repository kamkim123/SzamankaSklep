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

  function goWithType(value, addBestsellers = false) {
    var url = new URL(window.location.href);


    url.searchParams.delete('nowosci');
    url.searchParams.delete('promocje');
    url.searchParams.delete('najpopularniejsze');

    // Dodajemy lub usuwamy parametr bestsellers
    if (addBestsellers) {
      url.searchParams.set('bestsellers', 'true');
    } else {
      url.searchParams.delete('bestsellers');
    }

    if (value) {
      url.searchParams.set('type', value);
    } else {
      url.searchParams.delete('type');
    }

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

    // Sprawdzamy, czy kliknięto w "Bestsellery"
    var addBestsellers = (value === "Bestsellery");

    // Usuwamy klasę 'active' ze wszystkich linków
    leftMenu.querySelectorAll('.products-menu-link, .products-cat2, .title-link').forEach(function (el) {
      el.classList.remove('active');
    });

    // Dodajemy klasę 'active' tylko do klikniętego linku
    link.classList.add('active');

    // Przekazujemy do funkcji goWithType, czy kliknięto "Bestsellery"
    goWithType(value, addBestsellers);
  });

  var currentType = new URLSearchParams(location.search).get('type') || '';
  var currentBestsellers = new URLSearchParams(location.search).get('bestsellers') === 'true';
  var currentNowosci = new URLSearchParams(location.search).get('nowosci') === 'true'; // Nowy warunek
  var currentPromocje = new URLSearchParams(location.search).get('promocje') === 'true'; // Nowy warunek


  if (currentType || currentBestsellers) {
    leftMenu.querySelectorAll('.products-menu-link, .products-cat2, .title-link').forEach(function (el) {
      var val = (el.getAttribute('data-type') || el.textContent).trim();

      // Ustawiamy klasę 'active' jeśli link ma odpowiednią kategorię lub jest to "Bestsellery"
      if (
          val === currentType ||
          (currentBestsellers && val === "Bestsellery") ||
          (currentNowosci && val === "Nowości") || // Nowa logika dla Nowości
          (currentPromocje && val === "Promocje") // Nowa logika dla Promocji
         ) {
          el.classList.add('active');
         }

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

      label.textContent = item.textContent.trim();  // Zmieniamy tekst w labelu na wybrany typ sortowania
      items.forEach(function (o) { o.classList.remove('active'); });
      item.classList.add('active');
      toggle(false);

      var v = item.textContent.trim(); // Pobieramy tekst z linku, np. 'Nowości', 'Promocje'

      // Tworzymy nowy URL
      var u = new URL(window.location.href);

      // Dodajemy odpowiedni parametr w URL, w zależności od klikniętego linku
      if (v === "Bestsellery") {
        u.searchParams.set('bestsellers', 'true');
      } else {
        u.searchParams.delete('bestsellers');
      }

      if (v === "Nowości") {
        u.searchParams.set('nowosci', 'true');
      } else {
        u.searchParams.delete('nowosci');
      }

      if (v === "Promocje") {
        u.searchParams.set('promocje', 'true');
      } else {
        u.searchParams.delete('promocje');
      }

      if (v === "Najpopularniejsze") {
        u.searchParams.set('najpopularniejsze', 'true');
      } else {
        u.searchParams.delete('najpopularniejsze');
      }

      // Resetujemy paginację przy zmianie sortowania
      u.searchParams.delete('page');
      window.location.assign(u.toString());  // Przekierowanie na nowy URL z parametrami
    });
  });

  // Synchronizacja klasy 'active' w zależności od parametru w URL
  (function syncFromQuery() {
    var current = new URLSearchParams(location.search).get('type') || '';
    var matched = false;
    items.forEach(function (li) {
      var val = li.textContent.trim();
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
    const box = document.getElementById('search');
    const btn = box.querySelector('.search__toggle');
    const inp = box.querySelector('.search__input');
    const clearBtn = box.querySelector('.search__clear');


    function openSearch(){
        box.classList.add('active-search');
        inp.disabled = false; inp.focus();
    }
    function closeSearch(){
        box.classList.remove('active-search');
        inp.value=''; inp.blur(); inp.disabled = true;
    }

    btn.addEventListener('click', () => {
        if (!box.classList.contains('active-search')) openSearch();
        else inp.focus(); // gdy otwarte, tylko focus na input
    });
    clearBtn.addEventListener('click', closeSearch);
    box.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });

});



document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart-icon').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Zapobiegamy domyślnemu wysłaniu formularza i przekierowaniu

            const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
            const productDiv = this.closest('.product'); // Pobieramy najbliższy kontener produktu
            const quantity = parseInt(productDiv.querySelector('.calc-input').textContent);  // Pobieramy ilość z licznika

            console.log("Dodaję do koszyka produkt o ID:", productId);  // Debugowanie
            console.log("Ilość:", quantity);  // Debugowanie

            // Używamy wygenerowanego URL do wysłania żądania
            fetch(cartAddUrl, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,  // CSRF token
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    'product_id': productId,
                    'quantity': quantity  // Wysyłamy ilość pobraną z licznika
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




// ====== ILOŚĆ: plus/minus na kafelkach produktów ======
(function () {
  const pad2 = n => String(Math.max(1, n|0)).padStart(2, '0');

  function setQty(productEl, q) {
    const cell = productEl.querySelector('.calc-input');
    const min  = parseInt(cell?.dataset.min || '1', 10);
    const max  = parseInt(cell?.dataset.max || productEl.dataset.stock || '9999', 10);
    const qty  = Math.min(Math.max(q, min), max);

    if (cell) cell.textContent = pad2(qty);
    const hidden = productEl.querySelector('input[name="quantity"]');
    if (hidden) hidden.value = String(qty);

    // (opcjonalnie) wizualna blokada przy brzegach
    const minus = productEl.querySelector('.minus');
    const plus  = productEl.querySelector('.plus');
    minus?.setAttribute('aria-disabled', String(qty <= min));
    plus?.setAttribute('aria-disabled',  String(qty >= max));
  }

  // Inicjalizacja: ustaw hidden quantity z tego, co w liczniku
  document.querySelectorAll('.product').forEach(card => {
    const cell = card.querySelector('.calc-input');
    const start = parseInt((cell?.textContent || '01').replace(/\D/g, ''), 10) || 1;
    setQty(card, start);
  });

  // Delegacja klików dla +/-
  const productsRoot = document.querySelector('.all-products') || document;
  productsRoot.addEventListener('click', (e) => {
    const plus  = e.target.closest('.plus');
    const minus = e.target.closest('.minus');
    if (!plus && !minus) return;

    const productEl = e.target.closest('.product');
    if (!productEl) return;

    const cell = productEl.querySelector('.calc-input');
    const cur  = parseInt((cell?.textContent || '01').replace(/\D/g, ''), 10) || 1;
    const delta = plus ? 1 : -1;
    setQty(productEl, cur + delta);
  });
})();




document.querySelectorAll('.favorite-toggle').forEach(item => {
  item.addEventListener('click', function(event) {
    event.preventDefault(); // Zapobiegaj domyślnemu zachowaniu linku

    let icon = this.querySelector('i');  // Pobieramy ikonę serca
    let productId = this.getAttribute('data-product-id'); // Pobieramy ID produktu
    let url = `/u/favorite/${productId}/toggle/`; // URL do widoku

    // Wykonaj zapytanie AJAX, aby dodać/usunąć produkt z ulubionych
    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'), // Pobieramy CSRF token
      },
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Błąd serwera: ' + response.status);
      }
      return response.json(); // Jeśli odpowiedź jest ok, zwróć JSON
    })
    .then(data => {
      if (data.success) {
        // Zmieniamy kolor i klasę serca
        if (data.is_favorite) {
          icon.classList.remove('bx-heart');        // Usuwamy puste serce
          icon.classList.add('bxs-heart');           // Dodajemy pełne serce
          icon.style.color = 'red';                   // Ustawiamy czerwony kolor
        } else {
          icon.classList.remove('bxs-heart');       // Usuwamy pełne serce
          icon.classList.add('bx-heart');           // Dodajemy puste serce
          icon.style.color = '';                     // Resetujemy kolor
        }
      } else {
        console.error('Błąd podczas dodawania do ulubionych');
      }
    })
    .catch(error => console.error('Błąd AJAX:', error)); // Błąd w zapytaniu AJAX
  });
});

// Funkcja do pobierania CSRF token z ciasteczek
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}






















