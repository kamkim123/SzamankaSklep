

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

    var link = e.target.closest('.products-menu-link, .title-link, .products-cat2, .products-menu-p');
    if (!link) return;

    var isSectionTitle = link.classList.contains('title-link') && !link.hasAttribute('data-type');
    if (isSectionTitle) return;

    e.preventDefault();

    var value = (link.getAttribute('data-type') || '').trim();
    if (!value) return; // jeśli brak data-type, nie filtruj


    // Sprawdzamy, czy kliknięto w "Bestsellery"
    var addBestsellers = (value === "Bestsellery");

    // Usuwamy klasę 'active' ze wszystkich linków
    leftMenu.querySelectorAll('.products-menu-link, .title-link').forEach(function (el) {
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


  if (currentType || currentBestsellers || currentNowosci || currentPromocje) {
    leftMenu.querySelectorAll('.products-menu-link, .title-link').forEach(function (el) {
      var val = (el.getAttribute('data-type') || el.textContent).trim();

      // Ustawiamy klasę 'active' jeśli link ma odpowiednią kategorię lub jest to "Bestsellery"
      if (
          val === currentType ||
          (currentBestsellers && val === "Bestsellery") ||
          (currentNowosci && val === "Nowosci") || // Nowa logika dla Nowości
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
  var items = wrapper.querySelectorAll('.sort-list a');
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

    var v = item.textContent.trim();
    var u = new URL(window.location.href);

    // 1) Zawsze czyścimy starą kategorię i wszystkie flagi
    u.searchParams.delete('type');
    u.searchParams.delete('bestsellers');
    u.searchParams.delete('nowosci');
    u.searchParams.delete('promocje');
    u.searchParams.delete('najpopularniejsze');

    // 2) Ustawiamy dokładnie JEDEN filtr
    if (v === "Bestsellery") {
      u.searchParams.set('bestsellers', 'true');
    } else if (v === "Nowości" || v === "Nowosci") {
      u.searchParams.set('nowosci', 'true');
    } else if (v === "Promocje") {
      u.searchParams.set('promocje', 'true');
    } else if (v === "Najpopularniejsze") {
      u.searchParams.set('najpopularniejsze', 'true');
    } else {
      // zwykła kategoria → type
      u.searchParams.set('type', v);
    }

    u.searchParams.delete('page');
    window.location.assign(u.toString());
  });
});


  // Synchronizacja klasy 'active' w zależności od parametru w URL
  (function syncFromQuery() {
    var current = new URLSearchParams(location.search).get('type') || '';
    var matched = false;
    items.forEach(function (a) {
      var val = a.textContent.trim();
      if (val === current) {
        a.classList.add('active');
        label.textContent = a.textContent.trim();
        matched = true;
      }
    });
    if (!matched) label.textContent = 'Produkty';
  })();
});




document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart-icon').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Zapobiegamy domyślnemu wysłaniu formularza i przekierowaniu

            const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu

            console.log("ID produktu przed wysłaniem:", productId);  // Debugowanie
            if (!productId) {
                console.error("Brak ID produktu!");
                return;  // Zatrzymaj dalsze wykonywanie skryptu
            }
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
                    // Możesz przekierować użytkownika do strony koszyka lub odświeżyć stronę
                    document.getElementById('cart-count').textContent = data.items; // Odświeżenie strony, aby backend wygenerował nową wartość cart-items
                }
            })
            .catch(error => {
                console.log("Wystąpił błąd:", error);
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

      // NOWE: brak data-max lub data-max="0" => nielimitowane
      const maxRaw = cell?.dataset.max;              // nie bierzemy pod uwagę data-stock!
      const unlimited = !maxRaw || maxRaw === '0';
      const max = unlimited ? Infinity : parseInt(maxRaw, 10) || Infinity;

      // klamry tylko po min; górny limit tylko gdy nie jest nieskończony
      let qty = Math.max(q, min);
      if (max !== Infinity) qty = Math.min(qty, max);

      if (cell) cell.textContent = String(qty).padStart(2, '0');

      const hidden = productEl.querySelector('input[name="quantity"]');
      if (hidden) hidden.value = String(qty);

      // ARIA – plus nigdy nie będzie disabled, jeśli unlimited
      const minus = productEl.querySelector('.minus');
      const plus  = productEl.querySelector('.plus');
      minus?.setAttribute('aria-disabled', String(qty <= min));
      plus?.setAttribute('aria-disabled', unlimited ? 'false' : String(qty >= max));
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






















