
const burger = document.querySelector('.burger');
const kategorieNav = document.querySelector('.kategorie-nav');


burger.addEventListener('click', () => {
    burger.classList.toggle('active');
    kategorieNav.classList.toggle('active');
})

document.querySelectorAll(".kategorie-nav").forEach(n=> n.
addEventListener("click", ()=>{
    burger.classList.remove('active');
    kategorieNav.classList.remove('active');
}));

const mq = window.matchMedia('(max-width: 1150px)');

mq.addEventListener('change', () => {
    kategorieNav.classList.add('no-anim');
    void kategorieNav.offsetWidth;
    kategorieNav.classList.remove('no-anim');
});






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




document.addEventListener('DOMContentLoaded', function () {
    // Obsługuje kliknięcie w ikonę koszyka dla bestsellerów
    document.querySelectorAll('.cart-icon').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Zapobiegamy domyślnemu wysłaniu formularza i przekierowaniu

            const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
            const quantity = 1;  // Na razie zakładamy, że zawsze dodajemy 1 sztukę

            // Debugowanie - sprawdzenie wartości productId
            console.log("Dodaję do koszyka produkt o ID:", productId);

            // Sprawdzenie, czy productId jest prawidłowe
            if (!productId) {
                console.error("Brak ID produktu!");
                alert("Błąd: Brak ID produktu.");
                return;
            }

            // Pobieramy poprawny token CSRF
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            if (!csrfToken) {
                console.error("Brak tokenu CSRF");
                alert("Błąd: Brak tokenu CSRF.");
                return;
            }

            // Wysyłamy żądanie do serwera
            fetch(cartAddUrl, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": csrfToken,  // CSRF token
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
                    alert("Produkt dodany do koszyka!");
                    // Zaktualizuj liczbę produktów w koszyku
                    const cartCountElement = document.querySelector('.cart-count');
                    if (cartCountElement) {
                        cartCountElement.textContent = data.items; // Zaktualizuj liczbę produktów w koszyku
                    }
                } else {
                    alert("Nie udało się dodać produktu do koszyka!");
                }
            })
            .catch(error => {
                console.error("Wystąpił błąd:", error);
                alert("Wystąpił błąd przy dodawaniu produktu do koszyka.");
            });
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
