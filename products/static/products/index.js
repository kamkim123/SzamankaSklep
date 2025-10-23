
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



const swiper = new Swiper('.swiper-reklamy', {
    loop: true,
    slidesPerView: 1,
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
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




document.querySelectorAll('.favorite-toggle').forEach(item => {
    item.addEventListener('click', function(event) {
        event.preventDefault();  // Zapobiegamy domyślnemu zachowaniu

        let productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
        let icon = this.querySelector('i');  // Pobieramy ikonę serca
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
                // Jeśli produkt został dodany do ulubionych lub usunięty, zmieniamy kolor serca
                if (data.is_favorite) {
                    icon.classList.remove('bx-heart');    // Usuwamy puste serce
                    icon.classList.add('bxs-heart');       // Dodajemy pełne serce
                    icon.style.color = 'red';              // Ustawiamy czerwony kolor
                } else {
                    icon.classList.remove('bxs-heart');   // Usuwamy pełne serce
                    icon.classList.add('bx-heart');        // Dodajemy puste serce
                    icon.style.color = '';                 // Resetujemy kolor
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


