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


  // Zmiana ilości (zwiększ/zmniejsz) i aktualizacja ceny
list.addEventListener('click', e => {
  if (e.target.classList.contains('qty-btn')) { // Sprawdź, czy kliknięto przycisk zmiany ilości
    const li = e.target.closest('.item'); // Znajdź element listy
    const display = li.querySelector('.qty-display'); // Element wyświetlający ilość
    const priceElement = li.querySelector('.price'); // Element wyświetlający cenę
    const unitPrice = parseFloat(priceElement.dataset.unitPrice); // Cena jednostkowa
    let newQuantity = parseInt(display.textContent); // Bieżąca ilość

    // Zwiększ lub zmniejsz ilość
    if (e.target.classList.contains('qty-minus')) {
      newQuantity = Math.max(1, newQuantity - 1); // Upewnij się, że ilość nie jest mniejsza niż 1
    } else if (e.target.classList.contains('qty-plus')) {
      newQuantity = newQuantity + 1;
    }

    display.textContent = newQuantity; // Zaktualizuj wyświetlaną ilość

    // Oblicz nową cenę
    const newPrice = (unitPrice * newQuantity).toFixed(2);
    priceElement.textContent = `${newPrice} zł`; // Wyświetl zaktualizowaną cenę

    const pid = li.dataset.productId; // ID produktu

    // Zapisz ilość w localStorage
    const cart = JSON.parse(localStorage.getItem('cart')) || [];
    const productIndex = cart.findIndex(item => item.productId === pid);

    if (productIndex !== -1) {
      cart[productIndex].quantity = newQuantity; // Zaktualizuj ilość produktu w koszyku
    } else {
      cart.push({
        productId: pid,
        quantity: newQuantity,
        unitPrice: unitPrice // Zapisywanie ceny jednostkowej
      });
    }

    localStorage.setItem('cart', JSON.stringify(cart)); // Zapisz zaktualizowany koszyk

    // Zaktualizuj podsumowanie koszyka
    updateCartSummary();
  }
});


  // start
  updateTotalsUI({
    subtotal: parseFloat(els.subtotal.textContent.replace(" zł", "")),
    shipping: parseFloat(els.shipping.textContent.replace(" zł", "")),
    grand: parseFloat(els.grand.textContent.replace(" zł", ""))
  });
})();
