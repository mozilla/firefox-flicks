;(function($, django_browserid, flicks) {
    'use strict';

    var $body = $('body');
    var videoTrackingName = $body.data('videoId') + ': ' + $body.data('videoTitle');
    var csrfToken = $body.data('csrfToken');
    var $details = $('.video-details');

    // Voting and unvoting handlers.
    $details.on('click', '.add-vote', function() {

        var $button = $(this);
        var url = $button.data('url');

        var voteXHR = $.post(url, {csrfmiddlewaretoken: csrfToken});
        if (!django_browserid.isUserAuthenticated()) {
            // Track login attempts to help determine Persona attrition.
            _gaq.push(['_trackEvent', 'Logged in Status', 'Start Login']);

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
                // Track voting action.
                _gaq.push(['_trackEvent', 'Votes', 'Add Vote', videoTrackingName]);

                $button.addClass('hidden');
                $button.siblings('.remove-vote').removeClass('hidden');
                showThanks();
                modifyVoteCount(1);
            });
        }
    });

    // When the page loads, if we just voted (URL hash is #voted) show the
    // share dialog.
    $(function() {
        if (window.location.hash === '#voted') {
            showThanks();

            // If the user just voted (signalled by the cookie 'just_voted'), tell GA and clear
            // the cookie.
            if (document.cookie.indexOf('just_voted=1') !== -1) {
                _gaq.push(['_trackEvent', 'Votes', 'Add Vote', videoTrackingName]);
                document.cookie = 'just_voted=;path=/;expires=Thu, 01 Jan 1970 00:00:01 GMT;';
            }
        }
    });

    $details.on('click', '.remove-vote', function() {
        var $button = $(this);
        var url = $button.data('url');
        $.post(url, {csrfmiddlewaretoken: csrfToken}).done(function() {
            // Track voting actions via GA.
            _gaq.push(['_trackEvent', 'Votes', 'Remove Vote', videoTrackingName])

            $button.addClass('hidden');
            $button.siblings('.add-vote').removeClass('hidden');
            hideThanks();
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

    function showThanks() {
        $('.vote-thanks').slideDown(300);
    }

    function hideThanks() {
        $('.vote-thanks').slideUp(300);
    }
})(jQuery, django_browserid, flicks);
