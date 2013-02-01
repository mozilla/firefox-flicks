/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($, trans) {
    'use strict';

    var $document = $(document);

    // Load videos in a full-page modal
    $("a.video-play").click(function(e) {
        e.preventDefault();
        createVimeoModal(this, $(this).data('vimeoId'));
    });

    function createVimeoModal(origin, videoId) {
        var content = '<iframe id="video" src="https://player.vimeo.com/video/'+ videoId +'?title=0&amp;byline=0&amp;portrait=0&amp;color=ffffff&amp;autoplay=1" width="600" height="338" frameborder="0"></iframe>';
        return createModal(origin, content);
    }

    // Create a full-page overlay and append the content
    function createModal(origin, content) {
        // Clear existing modal, if necessary,
        $('#modal').remove();
        $('.modalOrigin').removeClass('modalOrigin');

        // Create new modal
        var html = (
            '<div id="modal">' +
            '  <div class="inner">' +
            '    <button type="button" class="close">' +
            '      ' + trans('close') +
            '    </button>' +
            '  </div>' +
            '</div>'
        );

        // Add it to the page.
        $('body').addClass("noscroll").append(html);
        $("#modal .inner").append(content);
        $(origin).addClass('modalOrigin');
    }

    function closeModal() {
        $('#modal').remove();
        $('body').removeClass('noscroll');
        $('.modalOrigin').focus().remove('modalOrigin');
    }

    // Close modal on clicking close button or background.
    $document.on('click', '#modal .close', closeModal);
    $document.on('click', "#modal, #modal .inner", closeModal);

    // Close on escape
    $document.on('keyup', function(e) {
        if (e.keyCode === 27) { // esc
            closeModal();
        }
    });

})(jQuery, trans);
