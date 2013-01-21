// Handles interaction with the upvote button on video detail pages.
$(function() {
    // When the upvote button is clicked, send an upvote request to the server.
    $('body').on('click', 'a.vote', function() {
        var self = $(this),
            token = $('body').data('token'),
            upvote_url = self.data('upvote-url'),
            vote_count = parseInt(self.text(), 10);

        $.ajax({
            url: upvote_url,
            type: 'POST',
            data: {csrfmiddlewaretoken: token},
            success: function() {
                self.addClass('on');
                self.text(vote_count + 1);
            },
            error: function() {
                console.log('error upvoting');
            }
        });
    });
});
