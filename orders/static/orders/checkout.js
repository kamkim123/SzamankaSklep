// Reload checkout TYLKO gdy wracamy strzałką wstecz po próbie płatności (P24)

if (!(window.CSS && CSS.escape)) {
  window.CSS = window.CSS || {};
  CSS.escape = function (value) {
    return String(value).replace(/[^a-zA-Z0-9_\-]/g, (ch) => "\\" + ch);
  };
}

(() => {
  const KEY = "checkout_submitted";

  window.addEventListener("pageshow", (e) => {
    const nav = performance.getEntriesByType?.("navigation")?.[0];
    const isBackForward = nav?.type === "back_forward";

    if ((e.persisted || isBackForward) && sessionStorage.getItem(KEY) === "1") {
      sessionStorage.removeItem(KEY);
      window.location.reload();
    }
  });

  // ustawiamy flagę tylko przy wysłaniu checkout (czyli przejściu do P24)
  document.addEventListener(
    "submit",
    (evt) => {
      const form = evt.target;
      if (!form || !form.classList.contains("checkout-form")) return;
      if (evt.defaultPrevented) return;
      sessionStorage.setItem(KEY, "1");
    },
    true
  );
})();

(function () {
  /* ===== Helpers ===== */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => Array.from(document.querySelectorAll(sel));
  const fmt = (n) => (n || 0).toFixed(2).replace(".", ",") + " zł";
  const parseMoney = (s) =>
    s ? parseFloat(String(s).replace(",", ".").replace(/[^\d.]/g, "")) || 0 : 0;

  /* ===== Totals ===== */
  const totalsBox = $("#order-totals");
  const subtotalEl = $("#subtotal-amount");
  const shippingEl = $("#shipping-amount");
  const grandEl = $("#grand-amount");

  const getSubtotal = () =>
    totalsBox
      ? parseMoney(totalsBox.getAttribute("data-subtotal")) ||
        parseMoney(subtotalEl?.textContent)
      : 0;

  /* ===== Payment UI (notice + transferBox) ===== */
  function getProvider() {
    return (
      document.querySelector('input[name="payment_provider"]:checked')?.value ||
      "p24"
    );
  }

  function updatePaymentUI() {
    const provider = getProvider();

    const payNotice = document.getElementById("payNotice");
    const noticeProv = document.getElementById("noticeProvider");
    const transferBox = document.getElementById("transferBox");

    // domyślnie schowaj
    if (payNotice) payNotice.hidden = true;
    if (transferBox) transferBox.hidden = true;

    // p24 / card -> pokazujemy informację o przekierowaniu
    if (provider === "p24") {
      if (payNotice) {
        payNotice.hidden = false;
        if (noticeProv) noticeProv.textContent = "Przelewy24";
      }
    }

    if (provider === "card") {
      if (payNotice) {
        payNotice.hidden = false;
        if (noticeProv) noticeProv.textContent = "Przelewy24";
      }
    }

    // transfer -> pokazujemy instrukcję przelewu
    if (provider === "transfer") {
      if (transferBox) transferBox.hidden = false;
    }

    // Uaktualnij kwotę w instrukcji przelewu (gdy przeliczy się dostawa)
    const g = document.getElementById("grand-amount");
    const t = document.getElementById("transferAmountCalc");
    if (g && t) t.textContent = " " + g.textContent;
  }

  const recalc = () => {
    const sub = getSubtotal();
    const shipRadio = $('input[name="shipping_method"]:checked');
    const shipCost = shipRadio ? parseMoney(shipRadio.dataset.price) : 0;

    if (shippingEl) shippingEl.textContent = fmt(shipCost);
    if (grandEl) grandEl.textContent = fmt(sub + shipCost);

    // po przeliczeniu aktualizujemy też UI płatności (kwota w przelewie + notice)
    try {
      updatePaymentUI();
    } catch (_) {}
  };

  /* ===== Accept terms lock ===== */
  const acceptTerms = $("#accept_terms");
  const submitBtn = $(".checkout-btn.pretty");
  const lockSubmit = () => {
    if (!acceptTerms || !submitBtn) return;
    submitBtn.disabled = !acceptTerms.checked;
    submitBtn.classList.toggle("btn--disabled", !acceptTerms.checked);
  };
  acceptTerms?.addEventListener("change", lockSubmit);
  lockSubmit();

  /* ===== Shipping dropdown ===== */
  const shipBtn = $("#shipBtn");
  const shipMenu = $("#shipMenu");
  const shipRoot = $("#shipSelect");

  const shipGetLabel = (val) => {
    const li = shipMenu?.querySelector(
      `.ship-option[data-value="${CSS.escape(val)}"]`
    );
    return {
      title: li?.querySelector(".title")?.textContent?.trim() || "",
      sub: li?.querySelector(".price")?.textContent?.trim() || "",
    };
  };

  const shipUpdateBtn = () => {
    const r = $('input[name="shipping_method"]:checked');
    if (!r || !shipBtn) return;
    const { title, sub } = shipGetLabel(r.value);
    shipBtn.querySelector(".ship-select__current-title").textContent = title;
    shipBtn.querySelector(".ship-select__current-price").textContent = sub;
    shipMenu
      ?.querySelectorAll(".ship-option")
      .forEach((o) =>
        o.setAttribute("aria-selected", String(o.dataset.value === r.value))
      );
  };

  const shipOpen = () => {
    if (!shipMenu || !shipBtn || !shipRoot) return;
    shipMenu.hidden = false;
    shipBtn.setAttribute("aria-expanded", "true");
    shipRoot.classList.add("is-open");
    shipMenu.focus();
  };

  const shipClose = () => {
    if (!shipMenu || !shipBtn || !shipRoot) return;
    shipMenu.hidden = true;
    shipBtn.setAttribute("aria-expanded", "false");
    shipRoot.classList.remove("is-open");
  };

  shipBtn?.addEventListener("click", () =>
    shipBtn.getAttribute("aria-expanded") === "true" ? shipClose() : shipOpen()
  );

  shipMenu?.addEventListener("click", (e) => {
    const li = e.target.closest(".ship-option");
    if (!li) return;
    const r = document.querySelector(
      `input[name="shipping_method"][value="${CSS.escape(li.dataset.value)}"]`
    );
    if (r) {
      r.checked = true;
      r.dispatchEvent(new Event("change", { bubbles: true }));
    }
    shipUpdateBtn();
    recalc();
    shipClose();
    shipBtn.focus();
  });

  document.addEventListener("click", (e) => {
    if (
      shipRoot &&
      !shipRoot.contains(e.target) &&
      shipBtn?.getAttribute("aria-expanded") === "true"
    )
      shipClose();
  });

  shipMenu?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      shipClose();
      shipBtn.focus();
    }
  });

  $$('input[name="shipping_method"]').forEach((r) =>
    r.addEventListener("change", () => {
      shipUpdateBtn();
      recalc();
    })
  );

  shipUpdateBtn();
  recalc();

  /* ===== Payment provider dropdown (P24 / Card / Transfer) ===== */
  const payRoot = $("#paySelect");
  const payBtn = $("#payBtn");
  const payMenu = $("#payMenu");
  const hiddenProviderRadios = $$('input[name="payment_provider"]');

  const payGetLabel = (val) => {
    const li = payMenu?.querySelector(`.pay-option[data-value="${CSS.escape(val)}"]`);
    return {
      title: li?.querySelector(".title")?.textContent?.trim() || "",
      sub: li?.querySelector(".desc")?.textContent?.trim() || "",
    };
  };

  const updatePayButton = () => {
    const provider = getProvider();
    const { title, sub } = payGetLabel(provider);
    if (payBtn) {
      payBtn.querySelector(".pay-select__current-title").textContent = title;
      payBtn.querySelector(".pay-select__current-desc").textContent = sub;
    }
    payMenu
      ?.querySelectorAll(".pay-option")
      .forEach((o) =>
        o.setAttribute("aria-selected", String(o.dataset.value === provider))
      );
  };

  const payOpen = () => {
    if (!payMenu || !payBtn || !payRoot) return;
    payMenu.hidden = false;
    payBtn.setAttribute("aria-expanded", "true");
    payRoot.classList.add("is-open");
    payMenu.focus();
  };

  const payClose = () => {
    if (!payMenu || !payBtn || !payRoot) return;
    payMenu.hidden = true;
    payBtn.setAttribute("aria-expanded", "false");
    payRoot.classList.remove("is-open");
  };

  payBtn?.addEventListener("click", () =>
    payBtn.getAttribute("aria-expanded") === "true" ? payClose() : payOpen()
  );

  payMenu?.addEventListener("click", (e) => {
    const li = e.target.closest(".pay-option");
    if (!li) return;
    const val = li.dataset.value;

    const radio = document.querySelector(
      `input[name="payment_provider"][value="${CSS.escape(val)}"]`
    );
    if (radio) {
      radio.checked = true;
      radio.dispatchEvent(new Event("change", { bubbles: true }));
    }

    updatePayButton();
    updatePaymentUI();
    payClose();
    payBtn.focus();
  });

  document.addEventListener("click", (e) => {
    if (
      payRoot &&
      !payRoot.contains(e.target) &&
      payBtn?.getAttribute("aria-expanded") === "true"
    )
      payClose();
  });

  payMenu?.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      e.preventDefault();
      payClose();
      payBtn.focus();
    }
  });

  hiddenProviderRadios.forEach((r) =>
    r.addEventListener("change", () => {
      updatePayButton();
      updatePaymentUI();
    })
  );

  updatePayButton();
  updatePaymentUI();

  /* ===== Order list: Show more (>10) ===== */
  const list = $("#order-list");
  const toggleBtn = $("#order-toggle");
  if (list && toggleBtn) {
    const items = $$(".order-item").filter(
      (li) => !li.classList.contains("order-item--empty")
    );
    const LIMIT = 10;
    if (items.length > LIMIT) {
      items.slice(LIMIT).forEach((li) => li.classList.add("is-hidden"));
      toggleBtn.hidden = false;
      toggleBtn.dataset.state = "collapsed";
      const hiddenCount = items.length - LIMIT;
      toggleBtn.textContent = `Pokaż więcej (${hiddenCount})`;
      toggleBtn.addEventListener("click", () => {
        const collapsed = toggleBtn.dataset.state !== "expanded";
        if (collapsed) {
          items.slice(LIMIT).forEach((li) => li.classList.remove("is-hidden"));
          toggleBtn.dataset.state = "expanded";
          toggleBtn.textContent = "Pokaż mniej";
        } else {
          items.slice(LIMIT).forEach((li) => li.classList.add("is-hidden"));
          toggleBtn.dataset.state = "collapsed";
          toggleBtn.textContent = `Pokaż więcej (${hiddenCount})`;
          list.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
    }
  }
})();

/* ===== Paczkomaty: widoczność boxa + wyszukiwanie Epaka /v1/points ===== */

document.addEventListener("DOMContentLoaded", function () {
  const lockerField = document.getElementById("lockerBox");
  if (!lockerField) return;

  const shippingRadios = document.querySelectorAll('input[name="shipping_method"]');
  function updateLockerVisibility() {
    const checked = document.querySelector('input[name="shipping_method"]:checked');
    lockerField.style.display =
      checked && checked.value === "inpost_locker" ? "block" : "none";
  }
  shippingRadios.forEach((r) => r.addEventListener("change", updateLockerVisibility));
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

  toggleLockerBox();

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
        let msg = "Nie udało się pobrać listy paczkomatów. Spróbuj ponownie za chwilę.";

        if (xhr.status === 404) {
          msg = "Nie udało się wyszukać paczkomatów. Sprawdź wpisane miasto/kod i spróbuj ponownie.";
        } else if (xhr.status === 403) {
          msg = "Wyszukiwarka paczkomatów jest niedostępna (brak autoryzacji).";
        } else if (xhr.status === 400) {
          msg = "Podaj poprawne miasto lub kod pocztowy (np. 00-001).";
        } else if (xhr.status >= 500) {
          msg = "Błąd serwera podczas pobierania paczkomatów. Spróbuj ponownie za chwilę.";
        }

        try {
          const data = xhr.responseJSON;
          if (data && (data.error || data.details)) {
            msg = data.error || data.details;
          }
        } catch (_) {}

        $lockerResults.html(`<p class="locker-error-msg">${msg}</p>`);
      });
  });

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

    if (shippingMethod === "inpost_locker") {
      if (!$lockerCode.val()) {
        e.preventDefault();
        $lockerError.show();

        const offsetTop = $lockerBox.offset().top - 120;
        $("html, body").animate({ scrollTop: offsetTop }, 350);
      }
    }
  });
});
