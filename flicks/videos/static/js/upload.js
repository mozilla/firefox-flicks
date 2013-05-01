;(function($, flicks) {
    $(function() {
        var ERROR_URL = '/' + $('html').attr('lang') + '/video/upload/error/';

        var $uploadForm = $('#vimeo-file-upload');
        var $videoForm = $('#video-form');
        var $progress = $videoForm.find('.progress');

        var uploadXHR = null;
        var submittingForm = false;

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

                // If the file extension doesn't look right, confirm with the
                // user.
                if (!hasValidExtension(file.name)) {
                    if (!confirm(flicks.trans('uploadBadExtension'))) {
                        return;
                    }
                }

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
            submittingForm = true;
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

        $(window).on('beforeunload', function(e) {
            if (!submittingForm) {
                return flicks.trans('uploadExit');
            }
        });
    });

    var EXTENSION_BLACKLIST = ['jpg', 'gif', 'png', 'exe', 'ppt', 'pptx',
                               'doc', 'docx', 'pdf'];
    function hasValidExtension(filename) {
        for (var k = 0; k < EXTENSION_BLACKLIST.length; k++) {
            var extension = EXTENSION_BLACKLIST[k];
            if (endsWith(filename, extension)) {
                return false;
            }
        }

        return true;
    }

    // Courtesy of chakrit on StackOverflow
    // http://stackoverflow.com/questions/280634/endswith-in-javascript
    function endsWith(str, suffix) {
        return str.indexOf(suffix, str.length - suffix.length) !== -1;
    }
})(jQuery, window.flicks);
