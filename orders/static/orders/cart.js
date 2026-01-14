(function () {
  const list = document.getElementById('cartList');
  const btn = document.getElementById('checkoutBtn');
  const fmt = n => Number(n).toLocaleString('pl-PL', { style: 'currency', currency: 'PLN' });

    const toNum = (v) => {
    if (v == null) return 0;
    return Number(String(v).replace(/\s/g, '').replace(',', '.')) || 0;
  };


  const els = {
    subtotal: document.getElementById('subtotal'),
    shipping: document.getElementById('shipping'),
    grand: document.getElementById('grand')
  };

  // --- CSRF z cookie ---
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  // fetch POST z opcjonalnym AbortController.signal
function post(url, data, signal) {
  return fetch(url, {
    method: 'POST',
    signal,
    headers: {
      'X-CSRFToken': csrftoken,
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    },
    body: new URLSearchParams(data),
    credentials: 'same-origin', // sesja/cookie
    keepalive: true,            // nie ubijaj przy nawigacji
    cache: 'no-store'           // (opcjonalnie) bez cache
  }).then(async r => {
    const json = await r.json().catch(() => ({}));
    if (!r.ok || json.ok === false) {
      const msg = (json && json.error) ? json.error : 'Błąd żądania.';
      throw new Error(msg);
    }
    return json;
  });
}






  function updateTotalsUI(data) {
    const subtotal = parseFloat(data.subtotal);
    const shipping = parseFloat(data.shipping);
    const grand = parseFloat(data.grand);
    els.subtotal.textContent = fmt(subtotal);
    els.shipping.textContent = fmt(shipping);
    els.grand.textContent = fmt(grand);
    btn.disabled = subtotal === 0;
  }

  // --- USUWANIE pozycji ---
  list.addEventListener('click', (e) => {
    if (!e.target.classList.contains('remove')) return;

    const li = e.target.closest('.item3');
    if (!li || li.dataset.locked === '1') return;
    li.dataset.locked = '1';

    const pid = li.dataset.productId;
    const removeUrl = e.target.getAttribute('data-url');

    post(removeUrl, { product_id: pid })
      .then(data => {
        li.remove();
        const totals = data.totals ?? {
          subtotal: data.subtotal,
          shipping: data.shipping,
          grand: data.grand
        };
        updateTotalsUI(totals);
      })
      .catch(err => alert(err.message || 'Wystąpił problem podczas usuwania.'))
      .finally(() => { li.dataset.locked = '0'; });
  });

  // ====== ZMIANA ILOŚCI: optymistycznie + debounce + anulowanie poprzednich ======
  const state = new Map(); // pid -> {timer, desired, inflightCtrl, seq}

  function getItemState(pid) {
    if (!state.has(pid)) state.set(pid, { timer: null, desired: null, inflightCtrl: null, seq: 0 });
    return state.get(pid);
  }

  function scheduleSend(li, pid, desiredQty) {
    const st = getItemState(pid);
    st.desired = desiredQty;
    st.seq += 1;
    const seq = st.seq;

    if (st.timer) clearTimeout(st.timer);
    st.timer = setTimeout(() => {
      st.timer = null;

      // Anuluj poprzedni request, jeśli jeszcze leci
      if (st.inflightCtrl) {
        try { st.inflightCtrl.abort(); } catch (_) {}
        st.inflightCtrl = null;
      }

      const updateUrl = li.dataset.updateUrl;
      const removeUrl = li.querySelector('.remove')?.getAttribute('data-url');

      const ctrl = new AbortController();
      st.inflightCtrl = ctrl;

      const req = (desiredQty === 0)
        ? post(removeUrl, { product_id: pid }, ctrl.signal)
        : post(updateUrl, { product_id: pid, quantity: desiredQty }, ctrl.signal);

      req.then(data => {
        if (seq !== getItemState(pid).seq) return;

        if (desiredQty === 0) {
          li.remove();
        } else {
          const display = li.querySelector('.qty-display');
          const priceEl = li.querySelector('.price');

          // Preferuj total z backendu
          if (data.item_total != null) {
            const itemTotal = parseFloat(data.item_total);
            if (!Number.isNaN(itemTotal)) priceEl.textContent = fmt(itemTotal);
          }
          if (typeof data.items_quantity === 'number') {
            display.textContent = String(data.items_quantity);
          }
        }

        const totals = data.totals ?? {
          subtotal: data.subtotal,
          shipping: data.shipping,
          grand: data.grand
        };
        if (totals) updateTotalsUI(totals);
      }).catch(err => {
        if (err.name === 'AbortError') return;
        console.error(err);
        alert(err.message || 'Nie udało się zaktualizować ilości.');
      }).finally(() => {
        const cur = getItemState(pid);
        if (cur.inflightCtrl === ctrl) cur.inflightCtrl = null;
      });
    }, 250);
  }

list.addEventListener('click', (e) => {
    if (!e.target.classList.contains('qty-btn')) return;

    const li = e.target.closest('.item3');
    if (!li) return;

    const display = li.querySelector('.qty-display');
    const priceEl = li.querySelector('.price');
    const unitPrice = toNum(priceEl.dataset.unitPrice);
    const pid = li.dataset.productId;

    const currentQty = parseInt(display.textContent, 10) || 1;
    let desiredQty = currentQty;

    if (e.target.classList.contains('qty-minus')) desiredQty = Math.max(0, currentQty - 1);
    else if (e.target.classList.contains('qty-plus')) desiredQty = currentQty + 1;

    // Optymistycznie zaktualizuj wyświetlaną ilość
    display.textContent = String(desiredQty);
    priceEl.textContent = fmt(unitPrice * desiredQty);

    // Wyślij po debounce
    scheduleSend(li, pid, desiredQty);
});


  // Inicjalne ustawienie przycisku „Przejdź do płatności”
  const parsePLN = el => parseFloat(String(el.textContent).replace(/[^\d,.-]/g, '').replace(',', '.')) || 0;
  (function boot() {
    updateTotalsUI({
      subtotal: String(parsePLN(els.subtotal)),
      shipping: String(parsePLN(els.shipping)),
      grand: String(parsePLN(els.grand))
    });

    // Pętla po produktach w koszyku
    const items = document.querySelectorAll('.item3');
    items.forEach(item => {
      const quantity = parseInt(item.querySelector('.qty-display').textContent, 10) || 1;
      const unitPrice = toNum(item.dataset.price);  // Cena jednostkowa
      const totalPrice = unitPrice * quantity;  // Całkowita cena (unitPrice * quantity)

      // Zaktualizuj cenę jednostkową (zależną od ilości)
      const priceEl = item.querySelector('.price');
      priceEl.textContent = fmt(totalPrice);  // Ustaw całkowitą cenę
    });
  })();
})();



document.addEventListener('DOMContentLoaded', function () {
  let lastAddPromise = null;  // Zmienna globalna przechowująca obiecane żądanie

  document.querySelectorAll('.cart-icon').forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();  // Zapobiegamy domyślnemu wysłaniu formularza

      const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
      const productDiv = this.closest('.product');  // Pobieramy najbliższy kontener produktu
      const quantity = parseInt(productDiv.querySelector('.calc-input').textContent);  // Pobieramy ilość z licznika

      console.log("Dodaję do koszyka produkt o ID:", productId);  // Debugowanie
      console.log("Ilość:", quantity);  // Debugowanie

      // Blokujemy przycisk, by zapobiec wielokrotnemu kliknięciu
      this.disabled = true;

      // Wyślij żądanie do serwera, aby dodać produkt do koszyka
      lastAddPromise = fetch(cartAddUrl, {
        method: 'POST',
        headers: {
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,  // CSRF token
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          'product_id': productId,
          'quantity': quantity  // Wysyłamy ilość pobraną z licznika
        })
      })
      .then(response => response.json())
      .then(data => {
        console.log(data);  // Debugowanie odpowiedzi z serwera
        if (data.ok) {
          // Zaktualizuj liczbę produktów w koszyku
          document.querySelector('.cart-count').textContent = data.items;
          bumpCart();  // Animacja koszyka po dodaniu
        }
      })
      .catch(error => {
        console.error("Wystąpił błąd:", error);
      })
      .finally(() => {
        this.disabled = false;  // Odblokuj przycisk po zakończeniu operacji
      });
    });
  });

  // Synchronizacja z nawigacją do koszyka
  const cartLink = document.querySelector('a[href$="/cart/"], a[href$="/koszyk/"]');
  if (cartLink) {
    cartLink.addEventListener('click', (e) => {
      if (!lastAddPromise) return;  // Jeśli nie ma aktualnego żądania, pozwól nawigować
      e.preventDefault();  // Zatrzymujemy nawigację do koszyka

      // Po zakończeniu dodawania do koszyka, przejdź do koszyka
      lastAddPromise.finally(() => {
        window.location.assign(cartLink.href);  // Przejdź do koszyka
      });
    });
  }
});

// Funkcja animacji koszyka
function bumpCart() {
  const cart = document.querySelector('#cart-icon');
  if (!cart) return;
  cart.classList.add('bump');
  cart.addEventListener('animationend', () => cart.classList.remove('bump'), { once: true });
}
