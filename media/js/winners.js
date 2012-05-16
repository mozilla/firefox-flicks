(function ($) {

    $("body").addClass("js");

    var $window = $(window);
    var $nav = $('#nav-sections');
    var $head = $('.winners-head');
    var navTop = $nav.offset();
    var fixed = false;
    var didScroll = false;

    $window.scroll(function() {
        didScroll = true;
    });

    function adjustScrollbar() {
        if (didScroll) {
            didScroll = false;
            var scrollTop = $window.scrollTop();

            if( scrollTop >= navTop.top ) {
                if(!fixed) {
                    fixed = true;
                    $nav.addClass("fixed");
                    $head.css({ "padding-bottom" : "96px" });
                }
            } else {
                if(fixed) {
                    fixed = false;
                    $nav.removeClass("fixed");
                    $head.css({ "padding-bottom" : "0" });
                }
            }
        }
    };

    // Check for an adjusted scrollbar every 250ms.
    setInterval(adjustScrollbar, 250);

    // Bind scrolling to linked element.
    $window.on('click', '#nav-sections a', function(e) {
        e.preventDefault();

        // Extract the target element's ID from the link's href.
        var elem = $(this).attr("href").replace( /.*?(#.*)/g, "$1" );
        $('html, body').animate({
            scrollTop: $(elem).offset().top - 80
        }, 1000);

        if ( $window.width() < 760 ) {
            $("#nav-sections ul:visible").slideUp(100).attr("aria-hidden", "true");
            $("#nav-sections h2").removeClass("open");
        }

    });

    // Set up nav dropdown  
    $("#nav-sections h2").click(function() {
        if ( $window.width() < 760 ) {
            $(this).siblings("ul").slideToggle(150).removeAttr("aria-hidden");
            $(this).toggleClass("open");
            return false;
        }
    });

    // Hide dropdowns when anything else is clicked
    $(document).bind('click', function(e) {
      var $clicked = $(e.target);
      if ( ( $window.width() < 760 ) && ( !$clicked.parents().hasClass("menu") ) ) {
        $("#nav-sections ul:visible").hide().attr("aria-hidden", "true");
        $("#nav-sections h2").removeClass("open");
      }
    });

    // or gets focus
    $("a, input, textarea, button, :focus").bind('focus', function(e) {
      var $focused = $(e.target);
      if ( ( $window.width() < 760 ) && ( !$focused.parents().hasClass("menu") ) ) {
        $("#nav-sections ul").hide().attr("aria-hidden", "true");
        $("#nav-sections h2").removeClass("open");
      }
    });

    $window.resize(function() {
        if ( $window.width() > 760 ) {
            $("#nav-sections ul:hidden").show();
        }
        else if ( $window.width() < 760 ) {
            $("#nav-sections ul:visible").hide();
            $("#nav-sections h2").removeClass("open");
        }
    });

})(jQuery);
