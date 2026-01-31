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

/* ===== KOSZYK (zostaw TYLKO TEN BLOK) ===== */
document.addEventListener('DOMContentLoaded', function () {
  const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrfEl ? csrfEl.value : null;

  document.querySelectorAll('.cart-icon').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();

      // bierz właściwy element z data-product-id (klik może być w img)
      const btn = e.target.closest('.cart-icon') || this;
      const productId = btn.getAttribute('data-product-id');

      // nie wysyłaj requesta z null/undefined/pustym
      if (!productId || productId === 'null' || productId === 'undefined') {
        console.warn('Klik w koszyk bez poprawnego product_id — pomijam.', { productId });
        return;
      }

      const quantity = 1;
      console.log("Dodaję do koszyka produkt o ID:", productId);

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

        if (!response.ok) {
          const text = await response.text();
          throw new Error(`HTTP ${response.status}: ${text.slice(0, 200)}`);
        }

        if (!contentType.includes('application/json')) {
          const text = await response.text();
          throw new Error(`Expected JSON, got ${contentType}. Body: ${text.slice(0, 200)}`);
        }

        return response.json();
      })
      .then(data => {
        console.log(data);
        if (data.ok) {
          const countEl = document.querySelector('.cart-count');
          if (countEl) countEl.textContent = data.items;
        }
      })
      .catch(error => {
        console.error("Wystąpił błąd:", error);
      });
    });
  });
});

/* ===== ULUBIONE ===== */
document.querySelectorAll('.favorite-toggle').forEach(item => {
  item.addEventListener('click', function(event) {
    event.preventDefault();

    let productId = this.getAttribute('data-product-id');
    let icon = this.querySelector('i');
    let url = `/u/favorite/${productId}/toggle/`;

    fetch(url, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCookie('csrftoken'),
      },
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        if (data.is_favorite) {
          icon.classList.remove('bx-heart');
          icon.classList.add('bxs-heart');
          icon.style.color = 'red';
        } else {
          icon.classList.remove('bxs-heart');
          icon.classList.add('bx-heart');
          icon.style.color = '';
        }
      }
    })
    .catch(error => console.error('Błąd AJAX:', error));
  });
});

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
