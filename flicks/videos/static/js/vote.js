;(function($, django_browserid) {
    'use strict';

    var csrfToken = $('body').data('csrfToken');
    var $details = $('.video-details');

    // Voting and unvoting handlers.
    $details.on('click', '.add-vote', function() {
        var $button = $(this);
        var url = $button.data('url');

        var voteXHR = $.post(url, {csrfmiddlewaretoken: csrfToken});
        if (!django_browserid.isUserAuthenticated()) {
            django_browserid.getAssertion(function(assertion) {
                if (!assertion) {
                    return;
                }

                // The server will save the vote after they auth.
                var next = window.location.pathname + '#voted';
                django_browserid.verifyAssertion(assertion, next);
            });
        } else {
            $button.addClass('hidden');
            $button.siblings('.remove-vote').removeClass('hidden');
        }
    });

    $details.on('click', '.remove-vote', function() {
        var $button = $(this);
        var url = $button.data('url');
        $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function() {
            $button.addClass('hidden');
            $button.siblings('.add-vote').removeClass('hidden');
        });
    });
})(jQuery, django_browserid);
