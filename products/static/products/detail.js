const burger = document.querySelector('.burger');
const kategorieNav = document.querySelector('.kategorie-nav');


burger.addEventListener('click', () => {
    burger.classList.toggle('active');
    kategorieNav.classList.toggle('active');
})

document.querySelectorAll(".kategorie-nav").forEach(n => n.addEventListener("click", () => {
    burger.classList.remove('active');
    kategorieNav.classList.remove('active');
}));


const dropdowns = document.querySelectorAll('.dropdown');

dropdowns.forEach((dropdown) => {

    const menu = dropdown.querySelector('.menu');
    const options = dropdown.querySelectorAll('.menu li');

    dropdown.addEventListener('mouseenter', () => {
        menu.classList.add('menu-open');
    });

    dropdown.addEventListener('mouseleave', () => {

        menu.classList.remove('menu-open');
    });

    options.forEach(option => {
        option.addEventListener('click', () => {


            options.forEach(o => o.classList.remove('active'));
            option.classList.add('active');


            menu.classList.remove('menu-open');
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const menu = document.querySelector('.products-menu');


    menu.addEventListener('click', (e) => {
        const btn = e.target.closest('.submenu-toggle');
        if (!btn) return;

        const block = btn.closest('.submenu-block');
        const panel = block && block.nextElementSibling;

        if (!panel || !panel.classList.contains('submenu-panel')) return;

        const willOpen = !panel.classList.contains('is-open');

        panel.classList.toggle('is-open', willOpen);
        btn.classList.toggle('is-open', willOpen);
    });
});


const box = document.getElementById('search');
const btn = box.querySelector('.search__toggle');
const inp = box.querySelector('.search__input');
const clearBtn = box.querySelector('.search__clear');


function openSearch() {
    box.classList.add('active-search');
    inp.disabled = false;
    inp.focus();
}

function closeSearch() {
    box.classList.remove('active-search');
    inp.value = '';
    inp.blur();
    inp.disabled = true;
}

btn.addEventListener('click', () => {
    if (!box.classList.contains('active-search')) openSearch();
    else inp.focus(); // gdy otwarte, tylko focus na input
});
clearBtn.addEventListener('click', closeSearch);
box.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeSearch();
});


const g = document.querySelector('.image-wrapper2');
const m = g.querySelector(':scope > img');
if(g){
    g.addEventListener('click', e => {
        const t = e.target.closest('img');
        if (!t || t === m) return;
        m.src = t.dataset.full || t.src;
        m.alt = t.alt || '';
    });
}





document.querySelectorAll('.mini-photo img').forEach(img => {
    img.addEventListener('click', () => {
      document.querySelector('.main-image').src = img.dataset.full;
    });
  });

  // Kalkulator ilości
  document.querySelectorAll('.calc-container').forEach(calc => {
    const minus = calc.querySelector('.minus');
    const plus = calc.querySelector('.plus');
    const input = calc.querySelector('.calc-input');
    let qty = parseInt(input.textContent);
    minus.addEventListener('click', () => { if(qty>1) input.textContent=--qty; });
    plus.addEventListener('click', () => { input.textContent=++qty; });
  });



document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault(); // Zapobiegamy domyślnemu wysłaniu formularza i przekierowaniu

            const productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
            const quantity = 1;  // Zakładamy, że zawsze dodajemy 1 sztukę

            console.log("Dodaję do koszyka produkt o ID:", productId);  // Debugowanie

            // Używamy wygenerowanego URL do wysłania żądania
            fetch(cartAddUrl, {
                method: 'POST',
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,  // CSRF token
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    'product_id': productId,
                    'quantity': quantity
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log(data);  // Debugowanie odpowiedzi z serwera
                if (data.ok) {

                    document.querySelector('.cart-count').textContent = data.items; // Zaktualizuj liczbę produktów w koszyku
                }
            })
            .catch(error => {
                console.error("Wystąpił błąd:", error);
            });
        });
    });
});