(function ($) {
    var $window = $(window);
    var $content = $('.content-wrapper');
    var $nav = $('#nav-sections');
    var navTop = $nav.offset();
    var navHeight = $nav.height() + 24;
    var fixed = false;
    var didScroll = false;

    $window.scroll(function() {
        didScroll = true;
    });

    function adjustScrollbar() {
        if (didScroll) {
            didScroll = false;
            var scrollTop = $window.scrollTop();

            if(scrollTop >= navTop.top) {
                if(!fixed) {
                    fixed = true;
                    $nav.addClass("fixed");
                    $content.css({ paddingTop: navHeight+24 });
                }
            } else {
                if(fixed) {
                    fixed = false;
                    $nav.removeClass("fixed");
                    $content.css({ paddingTop: "0" });
                }
            }
        }
    };

    // Check for an adjusted scrollbar every 300ms.
    setInterval(adjustScrollbar, 300);

    // Bind scrolling to linked element.
    $window.on('click', '#nav-sections a', function(e){
        e.preventDefault();

        // Extract the target element's ID from the link's href.
        var target = $(this).attr("href").replace( /.*?(#.*)/g, "$1" );
        $('html, body').animate({
            scrollTop: $(target).offset().top-navHeight
        }, 1000);
    });
})(jQuery);
