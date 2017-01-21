$( document ).ready(function() {
    // For toggling photos in photo feeds
    $('.eye-button').on('click', function(e) {
        var id = $(this).attr('data-id'),
            currentFeed = $(this).attr('data-current-feed'),
            feeds = $(this).attr('data-feeds'),
            element = $(this);

        // Add photo back to this feed
        if ($(this).hasClass('removed')) {
            feeds = feeds + currentFeed

            var newFeeds = JSON.parse('[' + feeds + ']'),
                data = {
                    photo_feed: newFeeds
                }

            $.ajax({
                url: '/api/photos/' + id,
                method: 'patch',
                headers: { 'X-CSRFToken': getCSRF() },
                dataType: 'json',
                data: data,
                traditional: true,
                success: function() {
                    element.removeClass('removed');
                }
            });
        }
        // Or remove
        else {
            feeds = feeds.replace(currentFeed + ',', '').replace(/,$/, '');

            var newFeeds = JSON.parse('[' + feeds + ']'),
                data = {
                    photo_feed: newFeeds
                }

            if (data.photo_feed.length == 0)
                data.photo_feed = null;

            $.ajax({
                url: '/api/photos/' + id,
                method: 'patch',
                headers: { 'X-CSRFToken': getCSRF() },
                dataType: 'json',
                data: data,
                traditional: true,
                success: function() {
                    element.addClass('removed');
                }
            });
        }
    });

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