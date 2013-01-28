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
        this.resizeTimeoutId = setTimeout(doneResizing, 500);
    });

    function doneResizing() {
        if ($window.width() < 768) {
            $body.addClass('thin-mode');
            $navList.attr('aria-hidden', 'true');
        } else {
            $body.removeClass('thin-mode');
            $navList.removeAttr('aria-hidden').css({ display: 'block' });
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
        window.open(this.href);
    });

    // Create text translation function using #strings element.
    var $strings = $('#strings');
    window.trans = function trans(stringId){
        return $strings.data(stringId);
    };
})(jQuery);
