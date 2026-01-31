







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





document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.cart-icon').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();

      // klik może być w img albo w button — bierz najbliższy element z data-product-id
      const el = e.target.closest('[data-product-id]');
      const productId = el ? el.getAttribute('data-product-id') : null;

      // fallback: weź product_id z ukrytego inputa w tym samym formularzu (u Ciebie jest)
      let finalId = productId;
      if (!finalId) {
        const form = this.closest('form');
        const hidden = form ? form.querySelector('input[name="product_id"]') : null;
        finalId = hidden ? hidden.value : null;
      }

      // jeśli dalej brak — nic nie rób (bez 500)
      if (!finalId) return;

      fetch(cartAddUrl, {
        method: 'POST',
        headers: {
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          product_id: finalId,
          quantity: 1
        })
      })
      .then(async (response) => {
        // nie parsuj HTML jako JSON
        const ct = response.headers.get('content-type') || '';
        if (!response.ok) {
          await response.text();
          return null;
        }
        if (!ct.includes('application/json')) {
          await response.text();
          return null;
        }
        return response.json();
      })
      .then(data => {
        if (!data || !data.ok) return;
        const countEl = document.querySelector('.cart-count');
        if (countEl) countEl.textContent = data.items;
      })
      .catch(() => {
        // cicho
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

