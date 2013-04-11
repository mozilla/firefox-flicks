/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($, flicks) {
    'use strict';

    $(function() {
        var $window = $(window);
        var $document = $(document);
        var $html = $('html');
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

        // Change the navbar color and current item to match the section
        // waypoint
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

        // Fire the waypoints for each section, passing classes for the current
        // and previous sections.
        // Uses jQuery Waypoints http://imakewebthings.com/jquery-waypoints/
        $('#intro').waypoint(waypointCallback('',''), {offset: headOffset});
        $('#about').waypoint(waypointCallback('nav-about', ''), {offset: headOffset});
        $('#flicks2013').waypoint(waypointCallback('nav-flicks', 'nav-about'), {offset: headOffset});
        $('#judges').waypoint(waypointCallback('nav-judges', 'nav-flicks'), {offset: headOffset});
        $('#prizes').waypoint(waypointCallback('nav-prizes', 'nav-judges'), {offset: headOffset});
        $('#rules').waypoint(waypointCallback('nav-rules', 'nav-prizes'), {offset: headOffset});

        // Scroll to the linked section
        $window.on('click', '#page-nav a[href*="#"], a.scroll', function(e) {
            e.preventDefault();
            // Extract the target element's ID from the link's href.
            var elem = $(this).attr('href').replace(/.*?(#.*)/g, '$1');
            // Determine how far we have to scroll
            var scrollDistance = Math.abs($(elem).offset().top -
                                          $document.scrollTop());
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

        // Judge quotes
        var $quote = $('#judge-quote .quote');
        $('.judge').each(function() {
            var $judge = $(this);
            var quote = $judge.children('.quote').html();
            $judge.hover(function() {
                if (quote) {
                    $quote.fadeOut(200, function() {
                        $quote.html(quote).fadeIn(200);
                    });
                }
            }, function() {
                if (quote) {
                    $quote.delay(200).fadeOut(200);
                }
            });
        });

        // Open judge bios in a modal
        $('.judge a.bio').click(function(e){
            e.preventDefault();
            flicks.createModal(this, $(this).data('bio'));
        });


        // Load director videos on stage
        var $directorVideoFrame = $('#video-frame');
        $('.videos-list a').click(function(e) {
            var vimeoId = $(this).data('vimeoId');
            if (vimeoId !== undefined) {
                e.preventDefault();
                var url = 'https://player.vimeo.com/video/' + vimeoId;
                var frameSrc = (url + '?title=0&byline=0&portrait=0&' +
                                'color=ffffff&autoplay=1&api=1');
                $directorVideoFrame.attr('src', frameSrc);

                // Auto-play video.
                var cmd = JSON.stringify({method: 'play'});
                $directorVideoFrame[0].contentWindow.postMessage(cmd, url);
            }
        });

    });

})(jQuery, window.flicks);

