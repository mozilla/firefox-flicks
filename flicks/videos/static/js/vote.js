;(function($) {
    'use strict';

    var csrfToken = $('body').data('csrfToken');
    var $details = $('.video-details');

    // Voting and unvoting handlers.
    $details.on('click', '.add-vote', function() {
        var $button = $(this);
        var url = $button.data('url');
        $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function() {
            $button.addClass('hidden');
            $button.siblings('.remove-vote').removeClass('hidden');
        });
    });

    $details.on('click', '.remove-vote', function() {
        var $button = $(this);
        var url = $button.data('url');
        $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function() {
            $button.addClass('hidden');
            $button.siblings('.add-vote').removeClass('hidden');
        });
    });
})(jQuery);
