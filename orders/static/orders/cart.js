(function () {
  const list = document.getElementById('cartList');
  const btn = document.getElementById('checkoutBtn');
  const fmt = n => Number(n).toLocaleString('pl-PL', { style: 'currency', currency: 'PLN' });

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
      body: new URLSearchParams(data)
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

    const li = e.target.closest('.item');
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

    const li = e.target.closest('.item');
    if (!li) return;

    const display = li.querySelector('.qty-display');
    const priceEl = li.querySelector('.price');
    const unitPrice = parseFloat(priceEl.dataset.unitPrice);
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
    const items = document.querySelectorAll('.item');
    items.forEach(item => {
      const quantity = parseInt(item.querySelector('.qty-display').textContent, 10) || 1;
      const unitPrice = parseFloat(item.dataset.price);  // Cena jednostkowa
      const totalPrice = unitPrice * quantity;  // Całkowita cena (unitPrice * quantity)

      // Zaktualizuj cenę jednostkową (zależną od ilości)
      const priceEl = item.querySelector('.price');
      priceEl.textContent = fmt(totalPrice);  // Ustaw całkowitą cenę
    });
  })();
})();
