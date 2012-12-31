/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function() {
    "use strict";

    var $window = $(window);
    var $nav = $('#page-nav');
    var $head = $('#masthead');

    // Sticky navigation
    var fixed = false;
    var didScroll = false;

    $window.scroll(function() {
        didScroll = true;
    });

    $(document).ready(function() {
        var scrollTop = $window.scrollTop();
        if ( scrollTop > 0 ) {
            didScroll = true;
        }
    });

    function adjustScrollbar() {
        if (didScroll) {
            didScroll = false;
            var scrollTop = $window.scrollTop();
            if( scrollTop > 0 ) {
                if(!fixed) {
                    fixed = true;
                    $head.addClass("fixed");
                }
            } else {
                if(fixed) {
                    fixed = false;
                    $head.removeAttr("class");
                }
            }
        }
    }

    // Check for an adjusted scrollbar every 100ms.
    setInterval(adjustScrollbar, 100);

    // Scroll to the linked section
    $window.on('click', '#page-nav a[href*="#"], a.scroll', function(e) {
        e.preventDefault();
        // Extract the target element's ID from the link's href.
        var elem = $(this).attr("href").replace( /.*?(#.*)/g, "$1" );
        $('html, body').animate({
            scrollTop: $(elem).offset().top
        }, 1000, function() {
            $(elem).attr('tabindex','100').focus().removeAttr('tabindex');
        });
    });
    
})();

