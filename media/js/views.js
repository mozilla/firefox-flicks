$(function() {
    var token = $('body').data('token'),
        add_view_url = $('body').data('add-view-url'),
        video_id = $('body').data('video-id');

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
