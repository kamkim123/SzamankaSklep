

// Cofnięcie z P24: wymuś odświeżenie checkout (bfcache/back-forward)
window.addEventListener('pageshow', (e) => {
  const nav = performance.getEntriesByType?.('navigation')?.[0];
  const isBackForward = nav && nav.type === 'back_forward';
  if (e.persisted || isBackForward) {
    window.location.reload();
  }
});

document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    // jak wrócisz na kartę/stronę, odśwież stan
    // (minimalnie agresywne, ale skuteczne)
    window.location.reload();
  }
});

(function() {
  /* ===== Helpers ===== */
  const $  = sel => document.querySelector(sel);
  const $$ = sel => Array.from(document.querySelectorAll(sel));
  const fmt = n => (n||0).toFixed(2).replace('.', ',')+' zł';
  const parseMoney = s => s ? (parseFloat(String(s).replace(',', '.').replace(/[^\d.]/g,''))||0) : 0;

  /* ===== Totals ===== */
  const totalsBox = $('#order-totals');
  const subtotalEl = $('#subtotal-amount');
  const shippingEl = $('#shipping-amount');
  const grandEl = $('#grand-amount');
  const getSubtotal = () => totalsBox ? (parseMoney(totalsBox.getAttribute('data-subtotal')) || parseMoney(subtotalEl?.textContent)) : 0;

  const recalc = () => {
    const sub = getSubtotal();
    const shipRadio = $('input[name="shipping_method"]:checked');
    const shipCost = shipRadio ? parseMoney(shipRadio.dataset.price) : 0;
    if (shippingEl) shippingEl.textContent = fmt(shipCost);
    if (grandEl)    grandEl.textContent    = fmt(sub + shipCost);
  };

  /* ===== Accept terms lock ===== */
  const acceptTerms = $('#accept_terms');
  const submitBtn = $('.checkout-btn.pretty');
  const lockSubmit = () => {
    if (!acceptTerms || !submitBtn) return;
    submitBtn.disabled = !acceptTerms.checked;
    submitBtn.classList.toggle('btn--disabled', !acceptTerms.checked);
  };
  acceptTerms?.addEventListener('change', lockSubmit);
  lockSubmit();

  /* ===== Shipping dropdown ===== */
  const shipBtn  = $('#shipBtn');
  const shipMenu = $('#shipMenu');
  const shipRoot = $('#shipSelect');

  const shipGetLabel = (val) => {
    const li = shipMenu?.querySelector(`.ship-option[data-value="${CSS.escape(val)}"]`);
    return { title: li?.querySelector('.title')?.textContent?.trim() || '', sub: li?.querySelector('.price')?.textContent?.trim() || '' };
  };
  const shipUpdateBtn = () => {
    const r = $('input[name="shipping_method"]:checked'); if (!r || !shipBtn) return;
    const { title, sub } = shipGetLabel(r.value);
    shipBtn.querySelector('.ship-select__current-title').textContent = title;
    shipBtn.querySelector('.ship-select__current-price').textContent  = sub;
    shipMenu?.querySelectorAll('.ship-option').forEach(o => o.setAttribute('aria-selected', String(o.dataset.value === r.value)));
  };
  const shipOpen  = () => { if(!shipMenu||!shipBtn||!shipRoot) return; shipMenu.hidden=false; shipBtn.setAttribute('aria-expanded','true'); shipRoot.classList.add('is-open'); shipMenu.focus(); };
  const shipClose = () => { if(!shipMenu||!shipBtn||!shipRoot) return; shipMenu.hidden=true;  shipBtn.setAttribute('aria-expanded','false'); shipRoot.classList.remove('is-open'); };

  shipBtn?.addEventListener('click', () => (shipBtn.getAttribute('aria-expanded')==='true') ? shipClose() : shipOpen());
  shipMenu?.addEventListener('click', e => {
    const li = e.target.closest('.ship-option'); if (!li) return;
    const r = document.querySelector(`input[name="shipping_method"][value="${CSS.escape(li.dataset.value)}"]`);
    if (r){ r.checked = true; r.dispatchEvent(new Event('change', {bubbles:true})); }
    shipUpdateBtn(); recalc(); shipClose(); shipBtn.focus();
  });
  document.addEventListener('click', e => { if (shipRoot && !shipRoot.contains(e.target) && shipBtn?.getAttribute('aria-expanded')==='true') shipClose(); });
  shipMenu?.addEventListener('keydown', e => { if (e.key==='Escape'){ e.preventDefault(); shipClose(); shipBtn.focus(); }});
  $$('input[name="shipping_method"]').forEach(r => r.addEventListener('change', () => { shipUpdateBtn(); recalc(); }));
  shipUpdateBtn(); recalc();

  /* ===== Payment: provider dropdown + channel list (P24, Card, Transfer) ===== */
  const payRoot   = $('#paySelect');
  const payBtn    = $('#payBtn');
  const payMenu   = $('#payMenu');
  const payPicked = $('#payPicked');
  const channelGrid   = $('#channelGrid');
  const channelMore   = $('#channelMore');
  const channelSearch = $('#channelSearch');
  const channelInfo   = $('#channelInfo');
  const channelError  = $('#channelError');
  const hiddenProviderRadios = $$('input[name="payment_provider"]');
  const hiddenChannel = $('#payment_channel');

  const ICON_BASE = channelGrid?.dataset.iconBase || '/static/payments/icons/';

  const CHANNELS = {
    p24: [
      {code:'blik', name:'BLIK'},
      {code:'mbank', name:'mBank'},
      {code:'pko', name:'PKO BP'},
      {code:'pekao', name:'Pekao SA'},
      {code:'santander', name:'Santander'},
      {code:'ing', name:'ING'},
      {code:'alior', name:'Alior Bank'},
      {code:'millennium', name:'Bank Millennium'},
      {code:'bnp', name:'BNP Paribas'},
      {code:'handlowy', name:'Citi Handlowy'},
      {code:'inteligo', name:'Inteligo'},
      {code:'velobank', name:'VeloBank'},
      {code:'pocztowy', name:'Bank Pocztowy'},
      {code:'nest', name:'Nest Bank'},
      {code:'bos', name:'BOŚ Bank'},
      {code:'credit-agricole', name:'Credit Agricole'},
      {code:'revolut', name:'Revolut'},
      {code:'raiffeisen-digital', name:'Raiffeisen Digital'},
      {code:'plusbank', name:'Plus Bank'},
      {code:'skok', name:'SKOK'},
      {code:'toyota', name:'Toyota Bank'},
      {code:'noble', name:'Noble Bank'},
      {code:'sgb', name:'SGB'}
    ],
    card: [
      {code:'visa', name:'Visa'},
      {code:'mastercard', name:'Mastercard'},
      {code:'applepay', name:'Apple Pay'},
      {code:'googlepay', name:'Google Pay'}
    ],
    transfer: []
  };
  const PAY_LIMIT = 12;

  const getProvider = () => (document.querySelector('input[name="payment_provider"]:checked')?.value) || 'p24';

  const payGetLabel = (val) => {
    const li = payMenu?.querySelector(`.pay-option[data-value="${CSS.escape(val)}"]`);
    return { title: li?.querySelector('.title')?.textContent?.trim()||'', sub: li?.querySelector('.desc')?.textContent?.trim()||'' };
  };

  const updatePayButton = () => {
    const provider = getProvider();
    const {title, sub} = payGetLabel(provider);
    payBtn.querySelector('.pay-select__current-title').textContent = title;
    payBtn.querySelector('.pay-select__current-desc').textContent  = sub;
    payMenu?.querySelectorAll('.pay-option').forEach(o => o.setAttribute('aria-selected', String(o.dataset.value === provider)));
  };

  const initials = name => (name.match(/\b\w/g)||['?']).slice(0,2).join('').toUpperCase();
  const makeLogo = (code, name) => {
    const wrap = document.createElement('span'); wrap.className = 'channel-logo';
    const img = document.createElement('img'); img.alt = name; img.src = `${ICON_BASE}${code}.svg`;
    img.onload = () => wrap.classList.add('is-loaded');
    img.onerror = () => { img.onerror = null; img.src = `${ICON_BASE}${code}.png`; };
    const fb = document.createElement('span'); fb.className = 'logo-fallback'; fb.textContent = initials(name);
    wrap.appendChild(img); wrap.appendChild(fb); return wrap;
  };

  const selectChannel = (code, name, {silent=false}={}) => {
    hiddenChannel.value = code;
    $$('#channelGrid .channel-tile').forEach(b => {
      const active = b.dataset.code === code;
      b.classList.toggle('is-active', active);
      b.setAttribute('aria-pressed', String(active));
    });
    payPicked.innerHTML = `Wybrany kanał: <strong>${name}</strong>`;
    if (!silent) channelError.hidden = true;
  };

  const renderChannels = () => {
    const provider = getProvider();
    const requireChannel = CHANNELS[provider]?.length > 0;
    channelGrid.innerHTML = '';
    channelError.hidden = true;

    if (!requireChannel) {
      channelGrid.hidden = true;
      channelMore.hidden = true;
      channelSearch.value = '';
      channelSearch.parentElement.style.display = 'none';
      channelInfo.hidden = false;
      const { title } = payGetLabel(provider);
      payPicked.innerHTML = `Wybrany sposób: <strong>${title}</strong>`;
      hiddenChannel.value = '';
      return;
    }

    channelGrid.hidden = false;
    channelSearch.parentElement.style.display = '';
    channelInfo.hidden = true;

    const items = (CHANNELS[provider] || []).slice();
    const q = channelSearch.value.trim().toLowerCase();
    const filtered = q ? items.filter(i => i.name.toLowerCase().includes(q) || i.code.toLowerCase().includes(q)) : items;

    const needMore = filtered.length > PAY_LIMIT;
    const visible = filtered.slice(0, needMore ? PAY_LIMIT : filtered.length);

    for (const ch of visible) {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'channel-tile';
      btn.dataset.code = ch.code;
      btn.setAttribute('aria-pressed', 'false');

      const left = makeLogo(ch.code, ch.name);
      const right = document.createElement('span');
      right.innerHTML = `<span class="channel-name">${ch.name}</span><br><span class="channel-sub">${provider.toUpperCase()} • ${ch.code}</span>`;
      btn.append(left, right);

      if (hiddenChannel.value && hiddenChannel.value === ch.code) {
        btn.classList.add('is-active'); btn.setAttribute('aria-pressed','true');
      }
      btn.addEventListener('click', () => selectChannel(ch.code, ch.name));
      channelGrid.appendChild(btn);
    }

    if (needMore) {
      channelMore.hidden = false;
      channelMore.dataset.state = 'collapsed';
      const hiddenCount = filtered.length - PAY_LIMIT;
      channelMore.textContent = `Pokaż więcej kanałów (${hiddenCount})`;

      channelMore.onclick = () => {
        const expanded = channelMore.dataset.state === 'expanded';
        if (!expanded) {
          for (const ch of filtered.slice(PAY_LIMIT)) {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'channel-tile';
            btn.dataset.code = ch.code;
            btn.setAttribute('aria-pressed','false');

            const left = makeLogo(ch.code, ch.name);
            const right = document.createElement('span');
            right.innerHTML = `<span class="channel-name">${ch.name}</span><br><span class="channel-sub">${provider.toUpperCase()} • ${ch.code}</span>`;
            btn.append(left, right);
            btn.addEventListener('click', () => selectChannel(ch.code, ch.name));
            channelGrid.appendChild(btn);
          }
          channelMore.dataset.state = 'expanded';
          channelMore.textContent = 'Pokaż mniej';
        } else {
          renderChannels();
          channelGrid.scrollIntoView({behavior:'smooth', block:'start'});
        }
      };
    } else {
      channelMore.hidden = true;
    }

    if (!hiddenChannel.value && filtered.length) {
      selectChannel(filtered[0].code, filtered[0].name, {silent:true});
    } else if (hiddenChannel.value) {
      const chosen = filtered.find(c => c.code === hiddenChannel.value);
      if (chosen) payPicked.innerHTML = `Wybrany kanał: <strong>${chosen.name}</strong>`;
    }
  };

  /* Provider dropdown open/close */
  const payOpen  = () => { payMenu.hidden=false; payBtn.setAttribute('aria-expanded','true'); payRoot.classList.add('is-open'); payMenu.focus(); };
  const payClose = () => { payMenu.hidden=true;  payBtn.setAttribute('aria-expanded','false'); payRoot.classList.remove('is-open'); };

  updatePayButton();
  renderChannels();

  payBtn?.addEventListener('click', () => (payBtn.getAttribute('aria-expanded')==='true') ? payClose() : payOpen());
  payMenu?.addEventListener('click', e => {
    const li = e.target.closest('.pay-option'); if (!li) return;
    const val = li.dataset.value;
    const radio = document.querySelector(`input[name="payment_provider"][value="${CSS.escape(val)}"]`);
    if (radio){ radio.checked = true; radio.dispatchEvent(new Event('change', {bubbles:true})); }
    updatePayButton();
    hiddenChannel.value = '';
    renderChannels();
    payClose(); payBtn.focus();
  });
  document.addEventListener('click', e => { if (payRoot && !payRoot.contains(e.target) && payBtn?.getAttribute('aria-expanded')==='true') payClose(); });
  payMenu?.addEventListener('keydown', e => { if (e.key==='Escape'){ e.preventDefault(); payClose(); payBtn.focus(); }});
  hiddenProviderRadios.forEach(r => r.addEventListener('change', () => { updatePayButton(); renderChannels(); }));
  channelSearch?.addEventListener('input', () => renderChannels());

  /* ===== Order list: Show more (>10) ===== */
  const list = $('#order-list');
  const toggleBtn = $('#order-toggle');
  if (list && toggleBtn) {
    const items = $$('.order-item').filter(li => !li.classList.contains('order-item--empty'));
    const LIMIT = 10;
    if (items.length > LIMIT) {
      items.slice(LIMIT).forEach(li => li.classList.add('is-hidden'));
      toggleBtn.hidden = false;
      toggleBtn.dataset.state = 'collapsed';
      const hiddenCount = items.length - LIMIT;
      toggleBtn.textContent = `Pokaż więcej (${hiddenCount})`;
      toggleBtn.addEventListener('click', () => {
        const collapsed = toggleBtn.dataset.state !== 'expanded';
        if (collapsed) {
          items.slice(LIMIT).forEach(li => li.classList.remove('is-hidden'));
          toggleBtn.dataset.state = 'expanded';
          toggleBtn.textContent = 'Pokaż mniej';
        } else {
          items.slice(LIMIT).forEach(li => li.classList.add('is-hidden'));
          toggleBtn.dataset.state = 'collapsed';
          toggleBtn.textContent = `Pokaż więcej (${hiddenCount})`;
          list.scrollIntoView({ behavior:'smooth', block:'start' });
        }
      });
    }
  }

  /* ===== Submit validation: channel required for providers with channels ===== */
  const form = document.querySelector('form.checkout-form') || document.querySelector('form');
  form?.addEventListener('submit', (e) => {
    const provider = getProvider();
    const requiresChannel = CHANNELS[provider]?.length > 0;
    if (requiresChannel && !hiddenChannel.value) {
      e.preventDefault();
      channelError.hidden = false;
      document.getElementById('paymentCard').scrollIntoView({behavior:'smooth', block:'start'});
    }
  });
})();

// >>> DODAJ GDZIEŚ OBOK INNYCH FUNKCJI (po zdefiniowaniu getProvider / hiddenChannel):
function updatePaymentUI() {
  const provider = (document.querySelector('input[name="payment_provider"]:checked')?.value) || 'p24';
  const channel  = document.getElementById('payment_channel')?.value || '';

  const payNotice   = document.getElementById('payNotice');
  const noticeProv  = document.getElementById('noticeProvider');
  const transferBox = document.getElementById('transferBox');
  const blikBox     = document.getElementById('blikBox'); // jeśli kiedyś użyjesz widgetu – odkomentuj w HTML

  // domyślnie schowaj
  if (payNotice)   payNotice.hidden = true;
  if (transferBox) transferBox.hidden = true;
  if (blikBox)     blikBox.hidden = true;

  // Provider: p24 -> informacja o przekierowaniu (i ewentualny BLIK inline)
  if (provider === 'p24') {
    if (payNotice) {
      payNotice.hidden = false;
      if (noticeProv) noticeProv.textContent = 'Przelewy24';
    }
    // Przykład: pokaż BLIK input tylko jeśli wdrożysz SDK i wybrano kanał 'blik'
    // if (channel === 'blik' && blikBox) blikBox.hidden = false;
  }

  // Provider: card -> informacja o przekierowaniu do bramki kartowej
  if (provider === 'card') {
    if (payNotice) {
      payNotice.hidden = false;
      if (noticeProv) noticeProv.textContent = 'operatora kartowego';
    }
  }

  // Provider: transfer -> instrukcja przelewu, bez przekierowania
  if (provider === 'transfer') {
    if (transferBox) transferBox.hidden = false;
  }

  // Uaktualnij kwotę w instrukcji przelewu (gdy przeliczy się dostawa)
  const g = document.getElementById('grand-amount');
  const t = document.getElementById('transferAmountCalc');
  if (g && t) t.textContent = ' ' + g.textContent;
}

// >>> PODŁĄCZ WYWOŁANIA (masz już nasłuchy – dopisz tylko te linie):
document.querySelectorAll('input[name="payment_provider"]').forEach(r =>
  r.addEventListener('change', updatePaymentUI)
);
document.getElementById('channelGrid')?.addEventListener('click', (e) => {
  if (e.target.closest('.channel-tile')) updatePaymentUI();
});

// Po inicjalizacji płatności i po recalc:
updatePaymentUI();
// …a w Twojej funkcji recalc() – dodaj na końcu:
try { updatePaymentUI(); } catch(_) {}


document.addEventListener("DOMContentLoaded", function () {
    const lockerField = document.getElementById("locker-field");
    const shippingRadios = document.querySelectorAll('input[name="shipping_method"]');

    function updateLockerVisibility() {
      const checked = document.querySelector('input[name="shipping_method"]:checked');
      if (checked && checked.value === "inpost_locker") {
        lockerField.style.display = "block";
      } else {
        lockerField.style.display = "none";
      }
    }

    shippingRadios.forEach(radio => {
      radio.addEventListener("change", updateLockerVisibility);
    });

    // na start – żeby było dobrze ustawione po załadowaniu
    updateLockerVisibility();
});




// == PACZKOMATY INPOST (Epaka /v1/points) ==

$(function () {
  const $lockerBox = $("#lockerBox");
  const $lockerSearch = $("#locker_search");
  const $lockerResults = $("#locker_results");
  const $lockerCode = $("#inpost_locker_code");
  const $lockerDesc = $("#inpost_locker_description");
  const $lockerPicked = $("#lockerPicked");
  const $lockerPickedName = $("#lockerPickedName");
  const $lockerPickedAddress = $("#lockerPickedAddress");

  function toggleLockerBox() {
    const method = $('input[name="shipping_method"]:checked').val();
    if (method === "inpost_locker") {
      $lockerBox.show();
    } else {
      $lockerBox.hide();
    }
  }

  // wywołaj przy starcie
  toggleLockerBox();

  // reaguj na zmianę metody dostawy (Twoje radio inputy)
  $(document).on("change", 'input[name="shipping_method"]', function () {
    toggleLockerBox();
  });

  $("#locker_search_btn").on("click", function () {
    const q = $lockerSearch.val().trim();
    if (!q) {
      $lockerResults.html("<p>Wpisz miasto, kod pocztowy lub kod paczkomatu.</p>");
      return;
    }

    $lockerResults.html("<p>Szukam paczkomatów…</p>");

    $.getJSON("/epaka/points/", { q: q })
      .done(function (data) {
        const points = data.points || [];
        if (!points.length) {
          $lockerResults.html("<p>Brak paczkomatów dla podanego zapytania.</p>");
          return;
        }

        const $ul = $('<ul class="locker-list"></ul>');
        points.forEach(function (p) {
          const desc = p.name || "";
          const addr = [
            p.postCode || "",
            p.city || "",
            (p.street || "") + " " + (p.number || "")
          ].join(" ").replace(/\s+/g, " ").trim();

          const $li = $('<li class="locker-item"></li>');
          $li.text(desc + " – " + addr);
          $li.data("pointId", p.id);
          $li.data("description", desc);
          $li.data("address", addr);
          $ul.append($li);
        });

        $lockerResults.empty().append($ul);
      })
      .fail(function (xhr) {
        $lockerResults.html(
          "<p>Błąd podczas pobierania paczkomatów (" +
          xhr.status +
          ").</p>"
        );
      });
  });

  // kliknięcie w konkretny paczkomat
  $(document).on("click", ".locker-item", function () {
    const $li = $(this);
    const pointId = $li.data("pointId");
    const desc = $li.data("description");
    const addr = $li.data("address");

    $lockerCode.val(pointId);
    $lockerDesc.val(desc);
    $lockerPickedName.text(desc);
    $lockerPickedAddress.text(addr);
    $lockerPicked.show();

    $(".locker-item").removeClass("is-active");
    $li.addClass("is-active");
  });
});


// == WALIDACJA: Paczkomaty InPost – bez wyboru paczkomatu nie puszczamy zamówienia ==

$(function () {
  const $form = $(".checkout-form");
  const $lockerBox = $("#lockerBox");
  const $lockerCode = $("#inpost_locker_code");
  const $lockerError = $("#locker_error");

  $form.on("submit", function (e) {
    const shippingMethod = $('input[name="shipping_method"]:checked').val();

    // jeśli wybrano "Paczkomaty InPost"
    if (shippingMethod === "inpost_locker") {
      // ale nie ma żadnego wybranego paczkomatu:
      if (!$lockerCode.val()) {
        e.preventDefault();          // blokujemy wysłanie formularza
        $lockerError.show();         // pokazujemy czerwony komunikat

        // przewiń stronę do boxa paczkomatu, żeby user widział, co poprawić
        const offsetTop = $lockerBox.offset().top - 120;
        $("html, body").animate({ scrollTop: offsetTop }, 350);
      }
    }
  });
});
