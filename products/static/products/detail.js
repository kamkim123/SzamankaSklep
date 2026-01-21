console.log("DETAIL.JS WSTAJE");









const g = document.querySelector('.image-wrapper2');
if (g) {
  const m = g.querySelector('img');
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
      const max  = 9999;

      const qty  = Math.min(Math.max(q, min), max);

      quantityInput.textContent = String(qty).padStart(2, '0');

      const hiddenQty = cartButton.closest('form')?.querySelector('input[name="quantity"]');
      if (hiddenQty) hiddenQty.value = String(qty);
    }


    setQty(parseInt((quantityInput.textContent || '1').replace(/\D/g, ''), 10) || 1);

    // Obsługuje kliknięcia przycisków +/-
    document.querySelector('.plus')?.addEventListener('click', function() {
      const currentQty = parseInt((quantityInput.textContent || '1').replace(/\D/g,''), 10) || 1;
      setQty(currentQty + 1);
    })

    document.querySelector('.minus')?.addEventListener('click', function() {
      const currentQty = parseInt((quantityInput.textContent || '1').replace(/\D/g,''), 10) || 1;
      setQty(currentQty - 1);
    });

    // Obsługuje kliknięcie w przycisk "Dodaj do koszyka"
cartButton.addEventListener('click', function (e) {
  e.preventDefault();

  const quantity = parseInt((quantityInput.textContent || '1').replace(/\D/g, ''), 10) || 1;

  console.log("Dodaję do koszyka produkt o ID:", productId);
  console.log("Ilość:", quantity);

  fetch(cartAddUrl, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      product_id: productId,
      quantity: quantity
    })
  })
  .then(async response => {
      console.log("STATUS:", response.status);
      const text = await response.text();
      try {
        return JSON.parse(text);
      } catch (e) {
        console.error("NIE JSON. Odpowiedź serwera:", text);
        throw e;
      }
})
    .then(data => {
      console.log("DATA:", data);

      if (data.ok) {
        const counter = document.querySelector('.cart-count') || document.getElementById('cart-count');
        if (counter) counter.textContent = data.items;
      } else {
        console.warn("ok=false albo błąd backendu:", data);
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
        let text = this.querySelector('span'); // jeśli masz <span> na tekst
         // Pobieramy tekst w przycisku
        let url = `/u/favorite/${productId}/toggle/`;  // URL do widoku

        // Wykonaj zapytanie AJAX, aby dodać/usunąć produkt z ulubionych
        fetch(url, {
            method: 'POST',
            credentials: 'same-origin',
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
                  icon.classList.remove('bx-heart');
                  icon.classList.add('bxs-heart');
                  this.classList.add('active');
                  if (text) text.textContent = 'Dodano do ulubionych'; // <-- ZMIANA
                } else {
                  icon.classList.remove('bxs-heart');
                  icon.classList.add('bx-heart');
                  this.classList.remove('active');
                  if (text) text.textContent = 'Dodaj do ulubionych'; // <-- ZMIANA
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







