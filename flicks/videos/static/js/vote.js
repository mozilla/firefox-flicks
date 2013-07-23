;(function($, django_browserid, flicks) {
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
                voteXHR.done(function() {
                    var next = window.location.pathname + '#voted';
                    django_browserid.verifyAssertion(assertion, next);
                });
            });
        } else {
            voteXHR.done(function() {
                $button.addClass('hidden');
                $button.siblings('.remove-vote').removeClass('hidden');
                showShareDialog();
                modifyVoteCount(1);
            });
        }
    });

    // When the page loads, if we just voted (URL hash is #voted) show the
    // share dialog.
    $(function() {
        if (window.location.hash === '#voted') {
            showShareDialog();
        }
    });

    $details.on('click', '.remove-vote', function() {
        var $button = $(this);
        var url = $button.data('url');
        $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function() {
            $button.addClass('hidden');
            $button.siblings('.add-vote').removeClass('hidden');
            modifyVoteCount(-1);
        });
    });

    function modifyVoteCount(mod) {
        var $countContainer = $('.vote-count');
        var $count = $countContainer.find('b');
        var newCount = 0;
        if ($count.length) {
            newCount = parseInt($count.text(), 10) || 0;
        }
        newCount += mod;
        $countContainer.html(voteCountText(newCount));
    }

    function voteCountText(count) {
        if (count < 1) {
            return flicks.trans('voteCountNone');
        } else if (count === 1) {
            return flicks.trans('voteCountOne', {vote_count: count});
        } else {
            return flicks.trans('voteCountSome', {vote_count: count});
        }
    }

    function showShareDialog() {
        $('.share .popup').fadeIn(200);
    }
})(jQuery, django_browserid, flicks);
