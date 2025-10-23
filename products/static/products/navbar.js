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
      const raw   = option.getAttribute('data-value');
      const value = (raw !== null ? raw : option.textContent)
                      .replace(/\s*\(\d+\)\s*$/, '')
                      .trim();

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





const inp = document.querySelector('.search__input'); // Pole wyszukiwania
const resultsBox = document.getElementById('search-results'); // Kontener dla wyników wyszukiwania
const btn = document.querySelector('.search__toggle'); // Przycisk do otwierania wyszukiwarki
const clearBtn = document.querySelector('.search__clear'); // Przycisk do czyszczenia wyszukiwania

// Funkcja wyświetlająca wyniki wyszukiwania
function showResults() {
    const query = inp.value.trim(); // Pobieramy tekst z inputa
    if (query.length > 0) {
        // Wysyłamy zapytanie do backendu za pomocą AJAX (fetch)
        fetch(`/products/search/?q=${query}`)
            .then(response => response.json())
            .then(data => {
                resultsBox.innerHTML = ''; // Czyszczenie poprzednich wyników
                if (data.results.length > 0) {
                    // Jeśli są wyniki, wyświetlamy je w kontenerze
                    data.results.forEach(product => {
                        const resultItem = document.createElement('div');
                        resultItem.textContent = product.name; // Nazwa produktu
                        resultsBox.appendChild(resultItem);
                    });
                } else {
                    resultsBox.innerHTML = '<div>Brak wyników</div>'; // Jeśli brak wyników
                }
            })
            .catch(error => console.error('Błąd wyszukiwania:', error));
    } else {
        resultsBox.innerHTML = '';  // Usuwa wyniki, gdy pole jest puste
    }
}

// Aktywacja wyszukiwania po kliknięciu w przycisk otwierający wyszukiwarkę
btn.addEventListener('click', () => {
    if (!inp.disabled) {
        inp.disabled = false;  // Odblokowanie input po kliknięciu
        inp.focus();  // Ustawienie kursora w input
        document.getElementById('search').classList.add('active-search');  // Dodanie klasy do rozwinięcia wyszukiwarki
    }
});

// Wyczyść wyniki po kliknięciu w przycisk czyszczenia
clearBtn.addEventListener('click', () => {
    inp.value = '';  // Wyczyść pole
    resultsBox.innerHTML = '';  // Wyczyść wyniki
    inp.focus();  // Ustawienie kursora w input
});

// Reagowanie na każde wpisanie tekstu w pole wyszukiwania
inp.addEventListener('input', showResults);  // Zainicjowanie funkcji pokazującej wyniki




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
                alert("hbgjfsbjbfbbsgr!");
                document.querySelector('.cart-count').textContent = data.items; // Zaktualizuj liczbę produktów w koszyku
            }
        })
        .catch(error => {
            console.error("Wystąpił błąd:", error);
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


document.addEventListener('DOMContentLoaded', function () {
  const loginLink = document.querySelector('#burger-icon1 a');
  const logoutLink = document.querySelector('#burger-icon2 form');

  if (loginLink && logoutLink) {
    // Warunek, który sprawdza czy użytkownik jest zalogowany
    {% if user.is_authenticated %}
        // Jeśli zalogowany, zmień "Zaloguj" na "Mój profil"
        loginLink.textContent = 'Mój profil';

        // Jeśli zalogowany, pokazujemy formularz wylogowania
        logoutLink.style.display = 'block'; // Pokaż wylogowanie w menu
    {% else %}
        // Jeśli niezalogowany, pokazujemy formularz logowania
        loginLink.textContent = 'Zaloguj';
        logoutLink.style.display = 'none'; // Ukryj wylogowanie w menu
    {% endif %}
  }
});






function() {
  const input = document.getElementById("search__input");
  const box = document.getElementById("live-results");
  const apiUrl = "{% url 'product_search_api' %}";
  let lastController = null;
  let activeIndex = -1; // do nawigacji klawiaturą
  let items = [];

  function debounce(fn, delay) {
    let t;
    return function(...args) {
      clearTimeout(t);
      t = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function clearBox() {
    box.innerHTML = "";
    box.style.display = "none";
    items = [];
    activeIndex = -1;
  }

  function render(results) {
    if (!results.length) { clearBox(); return; }
    box.innerHTML = results.map(r => `
    <div class="live-result">${escapeHtml(r.name)}</div>
    `).join("");
    box.style.display = "block";
  }

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, s => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[s]));
  }

  function formatPrice(val) {
    try {
      return new Intl.NumberFormat('pl-PL', { style: 'currency', currency: 'PLN' }).format(val);
    } catch {
      return val;
    }
  }

  const fetchLive = debounce(async function(q) {
    if (!q) { clearBox(); return; }
    try {
      // anuluj poprzedni request, by uniknąć wyścigów
      if (lastController) lastController.abort();
      lastController = new AbortController();
      const url = `${apiUrl}?q=${encodeURIComponent(q)}&limit=8`;
      const res = await fetch(url, { signal: lastController.signal, headers: { "Accept": "application/json" }});
      if (!res.ok) throw new Error("HTTP " + res.status);
      const data = await res.json();
      render(data.results || []);
    } catch (e) {
      if (e.name !== "AbortError") {
        clearBox();
        // opcjonalnie pokaż komunikat błędu
      }
    }
  }, 250);

  input.addEventListener("input", (e) => {
    fetchLive(e.target.value.trim());
  });

  // zamykanie po wyjściu z pola
  input.addEventListener("blur", () => setTimeout(clearBox, 120));

  // nawigacja klawiaturą
  input.addEventListener("keydown", (e) => {
    if (!items.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      activeIndex = (activeIndex + 1) % items.length;
      updateActive();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      activeIndex = (activeIndex - 1 + items.length) % items.length;
      updateActive();
    } else if (e.key === "Enter") {
      if (activeIndex >= 0 && items[activeIndex]) {
        const url = items[activeIndex].getAttribute("data-url");
        if (url) { e.preventDefault(); window.location.href = url; }
      }
    } else if (e.key === "Escape") {
      clearBox();
    }
  });

  function updateActive() {
    items.forEach((el, i) => el.setAttribute("aria-selected", i === activeIndex ? "true" : "false"));
    if (items[activeIndex]) items[activeIndex].scrollIntoView({ block: "nearest" });
  }
}();




