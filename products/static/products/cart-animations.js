// fallback na URL
window.cartAddUrl = window.cartAddUrl || "{% url 'orders:cart_add' %}";

if (!window.__cartAnimInit) {
  window.__cartAnimInit = true;

  // zadbaj o licznik (dodaj, jeśli brak)
  function ensureBadge() {
    const wrap = document.querySelector('.nav-cart') || document.querySelector('#cart-icon')?.parentElement;
    if (!wrap) return null;
    wrap.classList.add('nav-cart');
    let badge = document.querySelector('#cart-count');
    if (!badge) {
      badge = document.createElement('span');
      badge.id = 'cart-count';
      badge.textContent = '0';
      wrap.appendChild(badge);
    }
    return badge;
  }

  function setCount(n) {
    const b = ensureBadge();
    if (b) b.textContent = String(Math.max(0, n | 0));
  }

  function incCount(delta = 1) {
    const b = ensureBadge();
    if (!b) return;
    const cur = parseInt(b.textContent || '0', 10) || 0;
    b.textContent = String(cur + delta);
  }

  // Funkcja do animacji koszyka
  function bumpCart() {
    const cart = document.querySelector('#cart-icon');
    if (!cart) return;
    cart.classList.add('bump');
    cart.addEventListener('animationend', () => cart.classList.remove('bump'), { once: true });
  }

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('button[type="submit"][data-product-id]');
    if (!btn) return;  // Sprawdzenie, czy kliknięto przycisk "dodaj do koszyka"

    e.preventDefault(); // Zatrzymanie domyślnej akcji (wysyłania formularza)

    const form = btn.closest('form');
    const fd = new FormData(form);

    // Zablokowanie przycisku, aby zapobiec wielokrotnemu klikaniu
    btn.disabled = true;

    // Animacja: koszyk zostaje "wstrząśnięty"
    bumpCart();

    // Zwiększenie liczby w koszyku
    incCount(1);

    // Dodanie animacji kropki do ikony koszyka
    const cart = document.querySelector('#cart-icon');
    if (!cart) return;
    const br = btn.getBoundingClientRect(), cr = cart.getBoundingClientRect();
    const dot = document.createElement('div');
    dot.className = 'fly-dot';
    dot.style.left = (br.left + br.width / 2) + 'px';
    dot.style.top = (br.top + br.height / 2) + 'px';
    dot.style.setProperty('--dx', (cr.left + cr.width / 2 - (br.left + br.width / 2)) + 'px');
    dot.style.setProperty('--dy', (cr.top + cr.height / 2 - (br.top + br.height / 2)) + 'px');
    dot.style.setProperty('--lift', '120px'); // wysokość łuku (zmień np. na 80px/160px)
    document.body.appendChild(dot);
    dot.addEventListener('animationend', () => dot.remove());

    // Ponowne włączenie przycisku po zakończeniu animacji
    setTimeout(() => {
      btn.disabled = false;
    }, 1000); // czas animacji (np. 1000 ms)
  });

  // upewnij się, że licznik istnieje na starcie
  ensureBadge();
}
