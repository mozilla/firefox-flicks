$(function() {
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
});
