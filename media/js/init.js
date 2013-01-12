$(function() {

    // Add a class to use as a style hook when JavaScript is available
    $('body').addClass('js');

    var wideMode = $(window).width() >= 768;
    var $pageNav = $('#page-nav');
    $(window).resize(function() {
        clearTimeout(this.id);
        this.id = setTimeout(doneResizing, 500);
    });

    function doneResizing() {
        if ($(window).width() >= 768) {
            wideMode = true;
        } else {
            wideMode = false;
        }
    }

    // Show/hide the navigation in small viewports
    if (!wideMode) {
        $pageNav.click(function(){
            $pageNav.animate({ top: "0" }, 'fast'); // Slide down
            $pageNav.mouseleave(function(){
              $pageNav.css({ top: "auto" });
            });
            $("body").bind('click', function(){
                $pageNav.css({ top: "auto" });
            });
        });
    }

    // Dummy console for IE7
    if (window.console === undefined) window.console = {log: function() {}};

    var cookie_name = $('body').attr('data-mobile-cookie');
    $(".desktop-link").attr("href", window.location).click(function() {
        $.cookie(cookie_name, "off", {expires:30});
    });
    $(".mobile-link").attr("href", window.location).click(function() {
        $.cookie(cookie_name, "on", {expires:30});
    });

    $('#browserid').click(function(e) {
        e.preventDefault();
        navigator.id.getVerifiedEmail(function(assertion) {
            if (assertion) {
                var $e = $('#id_assertion');
                $e.val(assertion.toString());
                $e.parent().submit();
            }
        });
    });

    // Submit on locale selector choice
    $('form.languages select').change(function(){
        this.form.submit();
    });

    // Load external links in new tab/window
    $("a[rel='external']").click( function(e) {
        e.preventDefault();
        window.open(this.href);
    });
});
