console.log("navbar.js załadowany!");


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




const resultsBox = document.getElementById('live-results'); // Kontener dla wyników wyszukiwania
const btn = document.querySelector('.search__toggle'); // Przycisk do otwierania wyszukiwarki
const clearBtn = document.querySelector('.search__clear'); // Przycisk do czyszczenia wyszukiwania

// Funkcja wyświetlająca wyniki wyszukiwania


// Aktywacja wyszukiwania po kliknięciu w przycisk otwierający wyszukiwarkę
btn.addEventListener('click', () => {
        console.log('search clicked')
        if (!searchInput.disabled) {
        searchInput.disabled = false;
        searchInput.focus();
        document.getElementById('search').classList.add('active-search');
    }
});



// Wyczyść wyniki po kliknięciu w przycisk czyszczenia
clearBtn.addEventListener('click', () => {
        console.log('X search clicked')
     resultsBox.classList.add('not-visible');
     searchInput.value = '';
     resultsBox.innerHTML = '';
     console.log('hello')

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
  console.log("API URL:", apiUrl);  // Logowanie URL API
  let lastController = null;
  let activeIndex = -1;
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
  console.log("Rendering results: ", results);  // Logowanie wyników
  if (!results.length) { clearBox(); return; }
  box.innerHTML = results.map(r => `
    <div class="live-result">${escapeHtml(r.product_name)}</div>
  `).join("");
  box.style.display = "block";
}

  function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, s => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    }[s]));
  }

const fetchLive = debounce(async function(q) {
  if (!q) {
    clearBox();
    return;
  }
  console.log("Fetching API with query: ", q);  // Sprawdzenie, czy zapytanie jest wysyłane
  try {
    if (lastController) lastController.abort();
    lastController = new AbortController();
    const url = `${apiUrl}?q=${encodeURIComponent(q)}&limit=8`;
    console.log("Request URL: ", url);  // Logowanie pełnego URL
    const res = await fetch(url, { signal: lastController.signal, headers: { "Accept": "application/json" }});
    console.log("API response status: ", res.status);  // Sprawdzamy status odpowiedzi
    if (!res.ok) throw new Error("HTTP " + res.status);
    const data = await res.json();
    console.log("API response data: ", data);  // Logowanie odpowiedzi z API
    render(data.results || []);
  } catch (e) {
    console.error("API fetch error: ", e);  // Logowanie błędów
    if (e.name !== "AbortError") {
      clearBox();
    }
  }
}, 250);

  input.addEventListener("input", (e) => {
    console.log("Input value:", e.target.value);  // Logowanie wartości wejściowej
    fetchLive(e.target.value.trim());  // Wysyłanie zapytania
  });

  input.addEventListener("blur", () => setTimeout(clearBox, 120));

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












