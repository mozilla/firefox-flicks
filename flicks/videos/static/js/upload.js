;(function($) {
    $(function() {
        var ERROR_URL = '/' + $('html').attr('lang') + '/video/upload/error/';

        var $uploadForm = $('#vimeo-file-upload');
        var $videoForm = $('#video-form');
        var $progress = $videoForm.find('.progress');

        var uploadXHR = null;

        $uploadForm.fileupload({
            dataType: 'text',
            done: function(e, data) {
                $videoForm.find('button').removeAttr('disabled')
                          .removeClass('disabled');
            },
            fail: function(e, data) {
                if (data.textStatus !== 'abort') {
                    window.location.replace(ERROR_URL);
                }
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $progress.find('.bar').css('width', progress + '%');

            },
            add: function(e, data) {
                var file = data.files[0];
                uploadXHR = data.submit();
                $uploadForm.fadeOut(500, function() {
                    $videoForm.find('.filename').text(file.name);
                    $videoForm.find('input[name="filename"]').val(file.name);
                    $videoForm.find('input[name="filesize"]').val(file.size);
                    $videoForm.fadeIn(500);
                });
            }
        });

        // Disable submit button and cancel button once video is submitted to
        // allow for backend to take time to contact Vimeo.
        $videoForm.on('submit', function(e) {
            $buttons = $videoForm.find('button');
            $buttons.attr('disabled', 'disabled').addClass('disabled loading');
        });

        // When the remove link is clicked, cancel the ongoing upload and go
        // back to the file selection screen.
        $videoForm.on('click', '.remove', function(e) {
            e.preventDefault();
            if (uploadXHR !== null) {
                uploadXHR.abort();

                var $next = $videoForm.find('button.next');
                $next.attr('disabled', 'disabled').addClass('disabled');

                $videoForm.fadeOut(500, function() {
                    $uploadForm.fadeIn(500);
                });
            }
        });
    });
})(jQuery);
