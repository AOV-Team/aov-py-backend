$( document ).ready(function() {
    $('#push-message').keyup(updateCount);
    $('#push-message').keydown(updateCount);
    $('#push-message').on('input', updateCount);

    function updateCount() {
        var cs = $(this).val().length;
        $('#characters').text(cs);
    }
});