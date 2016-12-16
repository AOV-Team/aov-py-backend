function getCSRF() {
    return $('input[name="csrfmiddlewaretoken"]').attr('value');
}