$(document).ready(function() {
  // Pokazanie formularza edycji po kliknięciu "Edytuj dane"
  $('#edit-user-data-btn').on('click', function(e) {
    e.preventDefault();
    $('#edit-user-data-form').show();  // Pokazuje formularz
    $('#edit-user-data-btn').hide();   // Ukrywa przycisk edycji
  });

  // Anulowanie edycji
  $('#cancel-edit').on('click', function() {
    $('#edit-user-data-form').hide();
    $('#edit-user-data-btn').show();
  });

  // Obsługa submit formularza (AJAX)
  $('#profile-form').on('submit', function(e) {
    e.preventDefault();

    const formData = $(this).serialize(); // Zbieranie danych formularza

    $.ajax({
      url: '{% url "users:edit_profile" %}',  // Endpoint do edycji danych użytkownika
      type: 'POST',
      data: formData,
      success: function(response) {
        // Jeśli odpowiedź jest pozytywna, zaktualizuj dane na stronie
        $('#user-data [data-field="first_name"]').text(response.first_name);
        $('#user-data [data-field="last_name"]').text(response.last_name);
        $('#user-data [data-field="email"]').text(response.email);
        $('#user-data [data-field="phone"]').text(response.phone || '-');
        
        // Ukryj formularz edycji i pokaż przycisk "Edytuj dane"
        $('#edit-user-data-form').hide();
        $('#edit-user-data-btn').show();
      },
      error: function(xhr) {
        alert('Wystąpił błąd przy zapisywaniu danych.');
      }
    });
  });
});