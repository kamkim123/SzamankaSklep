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
  const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrfEl ? csrfEl.value : null;

  document.querySelectorAll('.cart-icon').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();

      // Klik może być w <img> albo w <button> – bierzemy najbliższy przycisk koszyka
      const btn = e.target.closest('button.cart-icon') || e.target.closest('.cart-icon') || this;

      // 1) Spróbuj z data-product-id
      let productId = btn.getAttribute('data-product-id');

      // 2) Fallback: weź z formularza obok (u Ciebie jest hidden input product_id)
      if (!productId || productId === 'null' || productId === 'undefined') {
        const form = btn.closest('form');
        const hidden = form ? form.querySelector('input[name="product_id"]') : null;
        productId = hidden ? hidden.value : productId;
      }

      // Jeśli nadal brak – dopiero wtedy nic nie rób (to oznacza naprawdę brak danych)
      if (!productId || productId === 'null' || productId === 'undefined') {
        return; // cicho, bez logów i bez błędów
      }

      const quantity = 1;

      fetch(cartAddUrl, {
        method: 'POST',
        headers: {
          ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
          "X-Requested-With": "XMLHttpRequest",
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          product_id: productId,
          quantity: quantity
        })
      })
      .then(async (response) => {
        const contentType = response.headers.get('content-type') || '';

        // jeśli błąd i serwer zwróci HTML (np. strona błędu), nie parsuj JSON
        if (!response.ok) {
          await response.text();
          return null;
        }

        if (!contentType.includes('application/json')) {
          await response.text();
          return null;
        }

        return response.json();
      })
      .then(data => {
        if (!data) return;
        if (data.ok) {
          const countEl = document.querySelector('.cart-count');
          if (countEl) countEl.textContent = data.items;
        }
      })
      .catch(() => {
        // cicho — bez spamowania konsoli na produkcji
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

