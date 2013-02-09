/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($) {

    var $shareOpts = $("#share-opts"),
    $shareToggle = $("#sharetoggle");

    // Toggle the dropdown when the button is clicked
    $shareToggle.click(function() {
        $shareOpts.fadeIn(200);
        return false;
    });

    $shareOpts.hover(
        function() {
            $(this).show();
        },
        function() {
            $(this).fadeOut(100);
        $shareToggle.blur();
        }
    );

    $(document).bind("click", function(e) {
        if (! $(e.target).parents().hasClass("share")) {
            $shareOpts.hide();
        }
    });

    $("a, input, textarea, button").bind("focus", function(e) {
        if (! $(e.target).parents().hasClass("share")) {
            $shareOpts.hide();
        }
    });

    $('#share-opts li a').click(function () {
        window.open($(this).attr('href'), 'sharer',
            'toolbar=0, status=0, resizable=1, width=626, height=436');
        return false;
    });

})(jQuery);