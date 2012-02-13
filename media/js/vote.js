// Handles interaction with the upvote button on video detail pages.
$(function() {
    // When the upvote button is clicked, send an upvote request to the server.
    $('body').on('click', 'a.vote', function() {
        var $self = $(this),
            token = $('body').data('token'),
            upvote_url = button.data('upvote-url'),
            vote_count = $self.find('#vote-count');

        $.ajax({
            url: upvote_url,
            type: 'POST',
            data: {csrfmiddlewaretoken: token},
            success: function() {
                vote_button.addClass('on');
                vote_count.text(vote_count.data('votes') + 1);
            },
            error: function() {
                console.log('error upvoting');
            }
        });
    });
});
