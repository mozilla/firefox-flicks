$(function() {
    var token = $('body').data('token'),
        add_view_url = $('#view-count').data('add-view-url'),
        video_id = $('#view-count').data('video-id');

    $.ajax({
        url: add_view_url,
        type: 'POST',
        data: {csrfmiddlewaretoken: token, video_id: video_id},
        success: function() {
            console.log('added view successfully');
        },
        error: function() {
            console.log('error adding view');
        }
    });
});
