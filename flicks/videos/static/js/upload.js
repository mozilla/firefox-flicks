;(function($) {
    $(function() {
        var ERROR_URL = '/video/upload/error/';

        var $uploadForm = $('#vimeo-file-upload');
        var $videoForm = $('#video-form');
        var $progress = $videoForm.find('.progress');

        var uploadXHR = null;

        $uploadForm.fileupload({
            dataType: 'text',
            done: function(e, data) {
                $videoForm.find('button').removeAttr('disabled');
            },
            fail: function(e, data) {
                if (data.textStatus !== 'abort') {
                    window.location.replace(ERROR_URL);
                }
            },
            progressall: function (e, data) {
                var progress = parseInt(data.loaded / data.total * 100, 10);
                $progress.find('.bar').css('width', progress + '%').text(progress + '%');

            },
            add: function(e, data) {
                var file = data.files[0];
                uploadXHR = data.submit();
                $uploadForm.fadeOut(500, function() {
                    $videoForm.find('.filename').text(file.name);
                    $videoForm.find('input[name="filename"]').val(file.name);
                    $videoForm.fadeIn(500);
                });
            }
        });

        $videoForm.on('click', '.remove', function(e) {
            e.preventDefault();
            if (uploadXHR !== null) {
                uploadXHR.abort();
                $videoForm.find('button').attr('disabled', 'disabled');
                $videoForm.fadeOut(500, function() {
                    $uploadForm.fadeIn(500);
                });
            }
        });
    });
})(jQuery);
