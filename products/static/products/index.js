
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





document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.cart-icon').forEach(button => {
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




document.querySelectorAll('.favorite-toggle').forEach(item => {
    item.addEventListener('click', function(event) {
        event.preventDefault();  // Zapobiegamy domyślnemu zachowaniu

        let productId = this.getAttribute('data-product-id');  // Pobieramy ID produktu
        let icon = this.querySelector('i');  // Pobieramy ikonę serca
        let url = `/u/favorite/${productId}/toggle/`;  // URL do widoku

        // Wykonaj zapytanie AJAX, aby dodać/usunąć produkt z ulubionych
        fetch(url, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken'),  // Pobieramy CSRF token
            },
        })
        .then(response => response.json())  // Odbieramy odpowiedź w formacie JSON
        .then(data => {
            if (data.success) {
                // Jeśli produkt został dodany do ulubionych lub usunięty, zmieniamy kolor serca
                if (data.is_favorite) {
                    icon.classList.remove('bx-heart');    // Usuwamy puste serce
                    icon.classList.add('bxs-heart');       // Dodajemy pełne serce
                    icon.style.color = 'red';              // Ustawiamy czerwony kolor
                } else {
                    icon.classList.remove('bxs-heart');   // Usuwamy pełne serce
                    icon.classList.add('bx-heart');        // Dodajemy puste serce
                    icon.style.color = '';                 // Resetujemy kolor
                }
            }
        })
        .catch(error => console.error('Błąd AJAX:', error));  // Obsługujemy błąd AJAX
    });
});

// Funkcja do pobierania CSRF token z ciasteczek
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

