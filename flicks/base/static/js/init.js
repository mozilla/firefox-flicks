(function($) {
    'use strict';
    var $window = $(window);
    var $document = $(document);
    var $body = $('body');
    var $nav = $('#page-nav');
    var $navList = $('#page-nav-list');

    // Add a class to use as a style hook when JavaScript is available
    $body.addClass('js');


    // Trigger the .thin-mode class on <body> when the screen is thinner than
    // 768 pixels.
    $window.resize(function() {
        clearTimeout(this.resizeTimeoutId);
        this.resizeTimeoutId = setTimeout(doneResizing, 200);
    });

    function doneResizing() {
        if ($window.width() < 768) {
            $body.addClass('thin-mode');
            $navList.attr('aria-hidden', 'true').hide();
        } else {
            $body.removeClass('thin-mode');
            $navList.removeAttr('aria-hidden').show();
        }
    }
    $(doneResizing);  // Call once when done loading the page to initialize.


    // Show/hide the navigation in small viewports
    $document.on('click', 'body.thin-mode #page-nav .toggle', expandPageNav);
    $document.on('click', 'body.thin-mode .toggle.open', collapsePageNav);
    $document.on('mouseleave', 'body.thin-mode #page-nav', collapsePageNav);

    function expandPageNav(){
        $navList.slideDown('fast').removeAttr('aria-hidden').attr('aria-expanded', 'true');
        $("#page-nav .toggle").addClass("open");
    }

    function collapsePageNav(){
        $navList.slideUp('fast').attr('aria-hidden', 'true').removeAttr('aria-expanded');
        $("#page-nav .toggle").removeClass("open");
    }


    // Dummy console for IE7
    if (window.console === undefined) window.console = {log: function() {}};


    // Submit on locale selector choice
    $('form.languages select').change(function(){
        this.form.submit();
    });


    // Load external links in new tab/window
    $('a[rel="external"]').click(function(e){
        e.preventDefault();
        window.open(this.href, '_blank', $(this).data('windowOpts'));
    });


    // Store common functions on flicks global.
    var $strings = $('#strings');
    var flicks = {
        'trans': function(stringId){
            return $strings.data(stringId);
        },
        'createModal': function(origin, content) {
            // Clear existing modal, if necessary,
            $('#modal').remove();
            $('.modalOrigin').removeClass('modalOrigin');

            // Create new modal
            var html = (
                '<div id="modal">' +
                '  <div class="inner">' +
                '    <button type="button" class="close">' +
                '      ' + flicks.trans('close') +
                '    </button>' +
                '  </div>' +
                '</div>'
            );

            // Add it to the page.
            $('body').addClass('noscroll').append(html);
            $('#modal .inner').append(content);
            $('#modal').fadeIn(100);
            $(origin).addClass('modalOrigin');
        },
        'closeModal': function() {
            $('#modal').fadeOut(100, function(){ $(this).remove() } );
            $('body').removeClass('noscroll');
            $('.modalOrigin').focus().remove('modalOrigin');
        },
        'notification': function(text) {
            // TODO: Implement notification popup here.
        },
        'isUserAuthenticated': function() {
            return !!$('#browserid-info').data('userEmail');
        }
    };
    window.flicks = flicks;

    // Close modal on clicking close button or background.
    $document.on('click', '#modal .close', flicks.closeModal);
    $document.on('click', '#modal', flicks.closeModal);

    // Close on escape
    $document.on('keyup', function(e) {
        if (e.keyCode === 27) { // esc
            flicks.closeModal();
        }
    });


    // Load videos in a full-page modal
    $('a.video-play').click(function(e) {
        var vimeoId = $(this).data('vimeoId');
        if (vimeoId !== undefined) {
            e.preventDefault();
            var content = '<iframe id="video" src="https://player.vimeo.com/video/'+ vimeoId +'?title=0&amp;byline=0&amp;portrait=0&amp;color=ffffff&amp;autoplay=1" width="600" height="338" frameborder="0"></iframe>';
            return flicks.createModal(this, content);
        }
    });

    $(function() {
        /* Share Widget *******/
        var $share = $('.share');
        var $popup = $share.find('.popup');

        // Toggle the popup when the button is clicked.
        $share.find('.toggle').click(function(e) {
            e.preventDefault();
            $(this).siblings('.popup').fadeIn(200);
        });

        // Hide the popup when the mouse moves away.
        $share.hover(null, function() {
            $(this).find('.popup').fadeOut(200);
        });
    });
})(jQuery);
