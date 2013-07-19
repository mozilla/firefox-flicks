(function($, django_browserid) {
    'use strict';
    var $window = $(window);
    var $document = $(document);
    var $body = $('body');
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

    function expandPageNav() {
        $navList.slideDown('fast').removeAttr('aria-hidden').attr('aria-expanded', 'true');
        $("#page-nav .toggle").addClass("open");
    }

    function collapsePageNav() {
        $navList.slideUp('fast').attr('aria-hidden', 'true').removeAttr('aria-expanded');
        $("#page-nav .toggle").removeClass("open");
    }


    // Dummy console for IE7
    if (window.console === undefined) {
        window.console = {log: function() {}};
    }


    // Submit on locale selector choice
    $('form.languages select').change(function(){
        this.form.submit();
    });


    // Load external links in new tab/window
    $document.on('click', 'a[rel="external"]', function(e){
        e.preventDefault();
        var opts = $(this).data('windowOpts');
        if (opts) {
            window.open(this.href, '_blank', $(this).data('windowOpts'));
        } else {
            window.open(this.href);
        }
    });


    // Store common functions on flicks global.
    var $strings = $('#strings');
    var flicks = {
        trans: function(stringId){
            return $strings.data(stringId);
        },

        createModal: function(origin, content, bg_close) {
            // Clear existing modal, if necessary,
            $('#modal').remove();
            $('.modalOrigin').removeClass('modalOrigin');

            // If bg_close is false, we disable being able to close the modal
            // just by clicking the background.
            var modal_class = 'bg_close';
            if (!bg_close && bg_close !== undefined) {
                modal_class = '';
            }

            // Create new modal
            var html = (
                '<div id="modal" class="' + modal_class + '">' +
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
            if (typeof cycle === 'function') {
                $('.cycle-slideshow').cycle('pause');
            }
        },

        closeModal: function() {
            $('#modal').fadeOut(100, function(){
                $(this).remove();
            });
            $('body').removeClass('noscroll');
            $('.modalOrigin').focus().remove('modalOrigin');
            if (typeof cycle === 'function') {
                $('.cycle-slideshow').cycle('resume');
            }
        }
    };
    window.flicks = flicks;

    // Close modal on clicking close button or background.
    $document.on('click', '#modal .close', flicks.closeModal);
    $document.on('click', '#modal.bg_close, #modal > .inner', function(e) {
        if (e.target === this) {
            flicks.closeModal();
        }
    });

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

    // Load video details in a modal
    $('a.detail-play').click(function(e){
        e.preventDefault();
        var sourcedoc = this.href;
        $.ajax({
            url: sourcedoc,
            success: function(data){
                var content = $(data).find('article.wrap');
                return flicks.createModal(this, content);
            },
            dataType: 'html'
        });
    });

    // Trigger a Persona login prompt on links that require auth if the user
    // isn't currently authed.
    $document.on('click', 'a.requires-auth', function(e) {
        // If django-browserid isn't loaded, do nothing.
        if (django_browserid) {
            e.preventDefault();

            var href = $(this).attr('href');
            if (!django_browserid.isUserAuthenticated()) {
                django_browserid.login(href);
            } else {
                window.location = href;
            }
        }
    });

    // Open share widget on click, close on hover off.
    $document.on('click', '.share .trigger-share-dialog', function(e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).siblings('.popup').fadeIn(200);
    });

    $document.on('mouseleave', '.share', function() {
        $(this).find('.popup').delay(200).fadeOut(200);
    });

    // JS Shim for HTML5 form `requires` attribute.
    var testInput = document.createElement('input');
    if (!('required' in testInput)) {
        $document.on('submit', 'form', validateForm);
    }

    /* jshint validthis:true */
    function validateForm(e) {
        var $inputs = $(this).find('input');
        for (var k = 0, len = $inputs.length; k < len; k++) {
            var input = $inputs[k];
            var $input = $(input);
            var $label = $('label[for="' + input.id + '"]');

            $input.removeClass('error');
            $label.find('strong.err').remove();
            if (!isInputValid(input)) {
                e.preventDefault();

                var errorMsg = document.createElement('strong');
                errorMsg.className = 'err';
                errorMsg.innerHTML = flicks.trans('inputRequired');
                $label.append(errorMsg);
                $input.addClass('error');
            }
        }
    }

    function isInputValid(input) {
        var isFilled = null;
        if ((input.type === 'checkbox' || input.type === 'radio')) {
            isFilled = input.checked;
        } else {
            isFilled = input.value !== '';
        }

        return input.getAttribute('required') === null || isFilled;
    }
})(jQuery, window.django_browserid);
