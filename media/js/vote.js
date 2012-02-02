// Handles interaction with the upvote button on video detail pages.
$(function() {
    var button = $('#upvote'),
        has_voted = $.cookie(button.data('shortlink')) !== null;

    // Disable voting button if the user has already voted.
    if (has_voted) {
        button.attr('disabled', 'disabled').text('Already voted!');
    } else {
        // During testing, Firefox seemed to 'remember' if a button was
        // disabled despite nothing disabling it on the page. O_o
        button.removeAttr('disabled');
    }

    // When the upvote button is clicked, send an upvote request to the server.
    $('body').on('click', '#upvote', function() {
        var $self = $(this),
            token = button.data('token'),
            upvote_url = button.data('upvote-url'),
            vote_count = $self.find('#vote-count');

        $.ajax({
            url: upvote_url,
            type: 'POST',
            data: {csrfmiddlewaretoken: token},
            success: function() {
                button.attr('disabled', 'disabled').text('Upvoted!');
                vote_count.text(vote_count.data('votes') + 1);
            },
            error: function() {
                alert('error upvoting');
            }
        });
    });
});
