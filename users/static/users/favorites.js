document.querySelectorAll('.btn-remove').forEach(item => {
    item.addEventListener('click', function(event) {
        event.preventDefault();  // Zapobiegamy domyślnemu zachowaniu

        // Pobieramy ID produktu z atrybutu data-product-id
        let productId = this.getAttribute('data-product-id');

        // Generujemy poprawny URL
        let url = `/u/favorite/${productId}/toggle/`;  // Poprawiony URL

        // Wykonaj zapytanie AJAX, aby usunąć produkt z ulubionych
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
                // Jeśli produkt został usunięty, ukrywamy ten produkt na stronie
                let productItem = this.closest('.favorite-item');
                productItem.style.display = 'none';  // Ukrywamy element
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
