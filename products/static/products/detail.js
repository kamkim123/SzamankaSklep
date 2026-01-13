const burger = document.querySelector('.burger');
const kategorieNav = document.querySelector('.kategorie-nav');

if (burger && kategorieNav) {
  burger.addEventListener('click', () => {
    burger.classList.toggle('active');
    kategorieNav.classList.toggle('active');
  });

  document.querySelectorAll(".kategorie-nav").forEach(n =>
    n.addEventListener("click", () => {
      burger.classList.remove('active');
      kategorieNav.classList.remove('active');
    })
  );
}


document.querySelectorAll(".kategorie-nav").forEach(n => n.addEventListener("click", () => {
    burger.classList.remove('active');
    kategorieNav.classList.remove('active');
}));


// ===== DROPDOWN – przejście na listę z ?type=... =====
(function () {
  const dropdowns = document.querySelectorAll('.dropdown');
  if (!dropdowns.length) return;

  // Ustal bazowy URL strony listy produktów:
  // 1) <body data-products-url="/produkty/">
  // 2) albo domyślnie /produkty/
  const BASE_LIST_URL = document.body?.dataset?.productsUrl || '/products/products/';

  dropdowns.forEach((dropdown) => {
    const menu = dropdown.querySelector('.menu');
    const options = dropdown.querySelectorAll('.menu li');
    if (!menu || !options.length) return;

    dropdown.addEventListener('mouseenter', () => menu.classList.add('menu-open'));
    dropdown.addEventListener('mouseleave', () => menu.classList.remove('menu-open'));

    options.forEach((option) => {
      option.addEventListener('click', (e) => {
        e.preventDefault();

        // UI
        options.forEach((o) => o.classList.remove('active'));
        option.classList.add('active');
        menu.classList.remove('menu-open');

        // Wartość filtra/kategorii
        const raw = option.getAttribute('data-value');
        const value = (raw !== null ? raw : option.textContent)
          .trim()
          .replace(/\s*\(\d+\)\s*$/, ''); // usuń np. " (12)"

        // Zbuduj URL do listy produktów z parametrem ?type=...
        try {
          const url = new URL(BASE_LIST_URL, window.location.origin);
          if (value) url.searchParams.set('type', value);
          // opcjonalnie: kasuj inne znaczniki sortowania, jeśli chcesz czyste przejście
          url.searchParams.delete('page');
          window.location.assign(url.toString());
        } catch (err) {
          // Fallback gdyby URL() nie zadziałał
          const q = value ? ('?type=' + encodeURIComponent(value)) : '';
          window.location.href = BASE_LIST_URL + q;
        }
      });
    });
  });
})();







document.addEventListener('DOMContentLoaded', () => {
  const menu = document.querySelector('.products-menu');
  if (!menu) return;

  menu.addEventListener('click', (e) => {
    const btn = e.target.closest('.submenu-toggle');
    if (!btn) return;

    const block = btn.closest('.submenu-block');
    const panel = block && block.nextElementSibling;

    if (!panel || !panel.classList.contains('submenu-panel')) return;

    const willOpen = !panel.classList.contains('is-open');
    panel.classList.toggle('is-open', willOpen);
    btn.classList.toggle('is-open', willOpen);
  });
});



const box = document.getElementById('search');
if (box) {
  const btn = box.querySelector('.search__toggle');
  const inp = box.querySelector('.search__input');
  const clearBtn = box.querySelector('.search__clear');

  function openSearch() { ... }
  function closeSearch() { ... }

  btn?.addEventListener('click', () => {
    if (!box.classList.contains('active-search')) openSearch();
    else inp?.focus();
  });
  clearBtn?.addEventListener('click', closeSearch);
  box.addEventListener('keydown', e => { if (e.key === 'Escape') closeSearch(); });
}

const inp = box.querySelector('.search__input');
const clearBtn = box.querySelector('.search__clear');


function openSearch() {
    box.classList.add('active-search');
    inp.disabled = false;
    inp.focus();
}

function closeSearch() {
    box.classList.remove('active-search');
    inp.value = '';
    inp.blur();
    inp.disabled = true;
}

btn.addEventListener('click', () => {
    if (!box.classList.contains('active-search')) openSearch();
    else inp.focus(); // gdy otwarte, tylko focus na input
});
clearBtn.addEventListener('click', closeSearch);
box.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeSearch();
});


const g = document.querySelector('.image-wrapper2');
if (g) {
  const m = g.querySelector(':scope > img');
  if (m) {
    g.addEventListener('click', e => {
      const t = e.target.closest('img');
      if (!t || t === m) return;
      m.src = t.dataset.full || t.src;
      m.alt = t.alt || '';
    });
  }
}



document.querySelectorAll('.mini-photo img').forEach(img => {
  img.addEventListener('click', () => {
    const main = document.querySelector('.main-image');
    if (main) main.src = img.dataset.full;
  });
});







document.addEventListener('DOMContentLoaded', function () {
    // Znajdź przycisk "Dodaj do koszyka" i licznik ilości
      const cartButton = document.querySelector('.cart');
      const quantityInput = document.querySelector('.calc-input');
      if (!cartButton || !quantityInput) return;

  const productId = cartButton.getAttribute('data-product-id');

    // Funkcja do aktualizacji ilości produktu
    function setQty(q) {
        const min  = parseInt(quantityInput?.dataset.min || '1', 10);
        const max  = 9999; // Usuwamy ograniczenie max, ustawiamy na 9999 (brak limitu)

        // Sprawdzamy, żeby ilość była w granicach minimum i maksimum
        const qty  = Math.min(Math.max(q, min), max);

        // Zaktualizowanie wyświetlanej ilości w elemencie calc-input
        quantityInput.textContent = String(qty).padStart(2, '0');
        document.querySelector('input[name="quantity"]').value = String(qty);  // Ustawienie wartości w ukrytym polu formularza
    }

    // Obsługuje kliknięcia przycisków +/-
    document.querySelector('.plus').addEventListener('click', function() {
        // Zwiększamy ilość o 1
        const currentQty = parseInt(quantityInput.textContent);
        setQty(currentQty + 1);
    });

    document.querySelector('.minus').addEventListener('click', function() {
        // Zmniejszamy ilość o 1
        const currentQty = parseInt(quantityInput.textContent);
        setQty(currentQty - 1);
    });

    // Obsługuje kliknięcie w przycisk "Dodaj do koszyka"
    cartButton.addEventListener('click', function (e) {
        e.preventDefault(); // Zapobiegamy domyślnemu zachowaniu formularza

        // Aktualizujemy ilość z licznika
        const quantity = parseInt(quantityInput.textContent);  // Pobieramy ilość z licznika

        console.log("Dodaję do koszyka produkt o ID:", productId);  // Debugowanie
        console.log("Ilość:", quantity);  // Debugowanie

        // Wysyłamy zapytanie do serwera
        fetch(cartAddUrl, {
            method: 'POST',
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,  // CSRF token
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                'product_id': productId,
                'quantity': quantity  // Wysyłamy ilość z licznika
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data);  // Debugowanie odpowiedzi z serwera
            if (data.ok) {
                // Zaktualizowanie liczby produktów w koszyku
                document.querySelector('.cart-count').textContent = data.items;
            }
        })
        .catch(error => {
            console.error("Wystąpił błąd:", error);
        });
    });
});








document.querySelectorAll('.favorite-toggle').forEach(item => {
    item.addEventListener('click', function(event) {
        event.preventDefault();  // Zapobiegamy domyślnemu zachowaniu (czyli przeładowaniu strony)

        let productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
        let icon = this.querySelector('i');  // Pobieramy ikonę serca
        let text = this.querySelector('span');  // Pobieramy tekst w przycisku
        let url = `/u/favorite/${productId}/toggle/`;  // URL do widoku

        // Wykonaj zapytanie AJAX, aby dodać/usunąć produkt z ulubionych
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),  // Pobieramy CSRF token
            },
        })
        .then(response => response.json())  // Odbieramy odpowiedź w formacie JSON
        .then(data => {
            if (data.success) {
                // Jeśli produkt został dodany do ulubionych lub usunięty, zmieniamy klasę
                if (data.is_favorite) {
                    icon.classList.remove('bx-heart');    // Usuwamy puste serce
                    icon.classList.add('bxs-heart');       // Dodajemy pełne serce
                    this.classList.add('active');          // Dodajemy klasę 'active' dla przycisku
                    text.textContent = 'Dodano do ulubionych'; // Zmieniamy tekst
                } else {
                    icon.classList.remove('bxs-heart');   // Usuwamy pełne serce
                    icon.classList.add('bx-heart');        // Dodajemy puste serce
                    this.classList.remove('active');       // Usuwamy klasę 'active' dla przycisku
                    text.textContent = 'Dodaj do ulubionych'; // Zmieniamy tekst
                }
            }
        })
        .catch(error => console.error('Błąd AJAX:', error));  // Obsługujemy błąd AJAX
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











