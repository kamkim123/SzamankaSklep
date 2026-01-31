// ===== SWIPER =====
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


// ===== KOSZYK (AJAX) =====
document.addEventListener('DOMContentLoaded', function () {
  const csrfEl = document.querySelector('[name=csrfmiddlewaretoken]');
  const csrfToken = csrfEl ? csrfEl.value : null;

  // Jeden listener na dokument: brak dubli z img/button
  document.addEventListener('click', function (e) {
    // interesuje nas klik w button koszyka albo w coś w środku (np. img)
    const btn = e.target.closest('button.cart-icon');
    if (!btn) return;

    // blokuj normalny submit formularza (żeby nie było 2 requestów)
    e.preventDefault();
    e.stopPropagation();

    // blokada wielokliku / podwójnych eventów
    if (btn.dataset.loading === "1") return;
    btn.dataset.loading = "1";
    btn.disabled = true;

    // 1) najpierw z data-product-id
    let productId = btn.getAttribute('data-product-id');

    // 2) fallback: z hidden input w tym samym formularzu
    if (!productId || productId === 'null' || productId === 'undefined') {
      const form = btn.closest('form');
      const hidden = form ? form.querySelector('input[name="product_id"]') : null;
      productId = hidden ? hidden.value : productId;
    }

    // jeśli nadal brak — po prostu odpuść (bez logów i bez 500)
    if (!productId || productId === 'null' || productId === 'undefined') {
      btn.dataset.loading = "0";
      btn.disabled = false;
      return;
    }

    fetch(cartAddUrl, {
      method: 'POST',
      headers: {
        ...(csrfToken ? { "X-CSRFToken": csrfToken } : {}),
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: new URLSearchParams({
        product_id: productId,
        quantity: 1
      })
    })
    .then(async (response) => {
      const ct = response.headers.get('content-type') || '';

      // przy błędzie backend może zwrócić HTML — nie parsuj jako JSON
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
    .then((data) => {
      if (!data || !data.ok) return;

      // aktualizacja licznika (jeśli istnieje)
      const countEl = document.querySelector('.cart-count');
      if (countEl) countEl.textContent = data.items;
    })
    .catch(() => {
      // cicho: nie spamuj konsoli na produkcji
    })
    .finally(() => {
      btn.dataset.loading = "0";
      btn.disabled = false;
    });
  }, true); // <-- capture: wyłapujemy zanim submit "poleci"
});


// ===== ULUBIONE =====
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.favorite-toggle').forEach(item => {
    item.addEventListener('click', function(event) {
      event.preventDefault();

      const productId = this.getAttribute('data-product-id');
      const icon = this.querySelector('i');
      const url = `/u/favorite/${productId}/toggle/`;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        },
      })
      .then(response => response.json())
      .then(data => {
        if (!data || !data.success) return;

        if (data.is_favorite) {
          icon.classList.remove('bx-heart');
          icon.classList.add('bxs-heart');
          icon.style.color = 'red';
        } else {
          icon.classList.remove('bxs-heart');
          icon.classList.add('bx-heart');
          icon.style.color = '';
        }
      })
      .catch(() => {
        // cicho
      });
    });
  });
});


// ===== COOKIE HELPER =====
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
