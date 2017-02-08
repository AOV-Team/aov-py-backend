$( document ).ready(function() {
    // Schedule text box
//    $('#schedule').dateRangePicker({
//        format: 'YYYY-MM-DD HH:mm',
//        singleDate: true,
//        singleMonth: true,
//        startDate: moment().format("YYYY-MM-DD"),
//        time: {
//            enabled: true
//        }
//    });

    // Push message textarea
    $('#push-message').keyup(updateCount);
    $('#push-message').keydown(updateCount);
    $('#push-message').on('input', updateCount);

    function updateCount() {
        var count = $(this).val().length;

        // Show how many characters are in text area
        $('#characters').text(count);

        // Disable submit if length == 0
        if (count == 0)
            $('#send-button').attr('disabled','disabled');
        else
            $('#send-button').removeAttr('disabled');
    }

    // Search for devices
    $('#searchbar').keypress(function(e) {
        if (e.which == 13) {
            e.preventDefault();

            searchForDevices($(this).val());
        }
    });

    $('#search-button').click(function(e) {
        e.preventDefault();

        searchForDevices($('#searchbar').val());
    });

    function searchForDevices(query) {
        $.ajax({
            url: '/api/devices?q=' + query,
            method: 'get',
            success: function(data) {
                displayDevices(data.results);
            }
        });
    }

    function getUser(userId) {
        return $.ajax({
            url: '/api/users/' + userId,
            method: 'get'
        });
    }

    function displayDevices(data) {
        var table = $('#result_list tbody');

        // Clear table
        table.html('');

        for (var d in data) {
            // Get user data
            (function(device) {
                $.when(getUser(device['user'])).then(function(data) {
                    var html = '<tr class="device" data-id="' + device['id'] + '" data-email="' + data.email + '">'
                        + '<td>' + data.email + '</td><td><span id="add-device" class="fa fa-plus"></span></td></tr>'

                    table.append(html);
                });
            })(data[d]);
        }
    }

    // Add device to recipients
    $('#result_list').on('click', '#add-device', function(e) {
        var recipients = $('#recipient-container'),
            recipient = $(this).parents('.device');

        var html = '<div class="recipient">'
            + '<input type="hidden" name="recipient-list[]" value="' + recipient.attr('data-id') + '">'
            + recipient.attr('data-email')
            + '<span class="remove-recipient fa fa-times"></span>'
            + '</div>';

        recipients.append(html);
        // Remove from list so it can no longer be added
        recipient.remove()
    });

    // Remove recipient
    $('#recipient-container').on('click', '.remove-recipient', function(e) {
        $(this).parents('.recipient').remove()
    });
});