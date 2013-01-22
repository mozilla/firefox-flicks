/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($, trans) {
    'use strict';

    var $window = $(window);
    var $document = $(document);
    var $pageNav = $('#page-nav');
    var $head = $('#masthead');
    var headOffset = $head.height() + 10;

    // Sticky navigation
    var navFixed = false;
    var didScroll = false;
    var scrollTime = 1000;

    $window.scroll(function() {
        didScroll = true;
        if ($window.scrollTop() >= 1){
            $head.addClass('fixed');
        }
    });

    $document.ready(function() {
        didScroll = $window.scrollTop() > 0;
    });

    function adjustScrollbar() {
        if (didScroll) {
            didScroll = false;
            var scrollTop = $window.scrollTop();
            if (scrollTop > 0) {
                if (!navFixed) {
                    navFixed = true;
                    $head.addClass('fixed');
                }
            } else {
                if (navFixed) {
                    navFixed = false;
                    $head.removeClass('fixed');
                    $pageNav.find("li.current").removeClass('current');
                }
            }
        }
    }

    // Check for an adjusted scrollbar every 100ms.
    setInterval(adjustScrollbar, 100);

    // Change the navbar color and current item to match the section waypoint
    function waypointCallback(current, previous) {
        return function(event, direction) {
            if (navFixed) {
                if (direction === 'down') {
                    $pageNav.attr('class', 'fixed ' + current);
                    $pageNav.find("li.current").removeClass('current');
                    $("#" + current).addClass('current');
                } else {
                    $pageNav.attr('class', 'fixed ' + previous);
                    $pageNav.find("li.current").removeClass('current');
                    $("#" + previous).addClass('current');
                }
            }
        };
    }

    // Fire the waypoints for each section, passing classes for the current and previous sections
    // Uses jQuery Waypoints http://imakewebthings.com/jquery-waypoints/
    $('#intro').waypoint(waypointCallback('',''), {offset: headOffset});
    $('#about').waypoint(waypointCallback('nav-about', ''), {offset: headOffset});
    $('#winners2012').waypoint(waypointCallback('nav-winners', 'nav-about'), {offset: headOffset});
    $('#judges').waypoint(waypointCallback('nav-judges', 'nav-winners'), {offset: headOffset});
    $('#prizes').waypoint(waypointCallback('nav-prizes', 'nav-judges'), {offset: headOffset});
    $('#rules').waypoint(waypointCallback('nav-rules', 'nav-prizes'), {offset: headOffset});

    // Scroll to the linked section
    $window.on('click', '#page-nav a[href*="#"], a.scroll', function(e) {
        e.preventDefault();
        // Extract the target element's ID from the link's href.
        var elem = $(this).attr('href').replace(/.*?(#.*)/g, '$1');
        // Determine how far we have to scroll
        var scrollDistance = Math.abs($(elem).offset().top - $document.scrollTop());
        // Slower scrolling for further targets
        if (scrollDistance > 1200) {
            scrollTime = 2500;
        }
        else {
            scrollTime = 1000;
        }
        $('html, body').animate({
            scrollTop: $(elem).offset().top
        }, scrollTime, function() {
            $(elem).attr('tabindex','100').focus().removeAttr('tabindex');
        });
    });

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

