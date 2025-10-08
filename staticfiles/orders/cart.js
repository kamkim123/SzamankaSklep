(function () {
  const list = document.getElementById('cartList');
  const btn = document.getElementById('checkoutBtn');
  const fmt = n => n.toLocaleString('pl-PL', {style: 'currency', currency: 'PLN'});
  const els = {
    subtotal: document.getElementById('subtotal'),
    shipping: document.getElementById('shipping'),
    grand: document.getElementById('grand')
  };

  // --- CSRF z ciasteczka ---
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  function post(url, data) {
    return fetch(url, {
      method: "POST",
      headers: {
        "X-CSRFToken": csrftoken,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
      },
      body: new URLSearchParams(data)
    }).then(r => r.json());
  }

  function updateTotalsUI({subtotal, shipping, grand}) {
    els.subtotal.textContent = fmt(subtotal);
    els.shipping.textContent = fmt(shipping);
    els.grand.textContent = fmt(grand);
    btn.disabled = subtotal === 0;
  }

  // Usuwanie pozycji
  list.addEventListener('click', e => {
    if (!e.target.classList.contains('remove')) return;  // Jeśli nie kliknięto przycisku "Usuń"

    const li = e.target.closest('.item');  // Znajdź element listy
    const pid = li.dataset.productId;  // Pobierz ID produktu

    // Pobierz URL do usuwania z atrybutu data-url
    const removeUrl = e.target.getAttribute('data-url');

    // Wysłanie żądania do backendu, aby usunąć produkt
    post(removeUrl, {product_id: pid})
      .then(data => {
        if (!data.ok) throw new Error('Nie udało się usunąć pozycji.');

        // Usuwanie elementu z listy
        li.remove();

        // Zaktualizowanie UI
        updateTotalsUI({
          subtotal: parseFloat(data.subtotal),
          shipping: parseFloat(data.shipping),
          grand: parseFloat(data.grand)
        });
      })
      .catch(error => {
        // Jeśli wystąpi błąd, pokaż komunikat
        alert('Wystąpił problem podczas usuwania produktu.');
        console.error('Błąd:', error);
      });
  });

  // start
  updateTotalsUI({
    subtotal: parseFloat(els.subtotal.textContent.replace(" zł", "")),
    shipping: parseFloat(els.shipping.textContent.replace(" zł", "")),
    grand: parseFloat(els.grand.textContent.replace(" zł", ""))
  });
})();
