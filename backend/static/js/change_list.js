$( document ).ready(function() {
    $('.star-button').on('click', function(e) {
        var id = $(this).attr('data-id'),
            contentType = $(this).attr('data-content-type');

        // If starred, unstar
        // Else, star
        if ($(this).hasClass('starred')) {
            $.ajax({
                url: '/api/' + contentType + '/' + id + '/stars',
                method: 'delete',
                headers: { 'X-CSRFToken': getCSRF() },
                dataType: 'json',
                traditional: true
            });

            $(this).removeClass('starred');
        } else {
            $.ajax({
                url: '/api/' + contentType + '/' + id + '/stars',
                method: 'post',
                headers: { 'X-CSRFToken': getCSRF() },
                dataType: 'json',
                traditional: true
            });

            $(this).addClass('starred');
        }
    });
});