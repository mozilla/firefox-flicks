/**
 * Social Share Buttons Embed
 *
 * Provides a jQuery function, showShare, that allows us to dynamically load
 * the JS for social buttons and injects the necessary HTML into the page.
 * This allows us to use share buttons without violating the user's privacy.
 *
 * Example:
 *   $('#share').showShare(['facebook'], ['twitter'])
 *
 * You can also pass an options object as a second argument. Options are
 * organized by service name, e.g. options['facebook']['appId']. See the
 * individual service functions for more information.
 */
(function($) {

// Assuming a standard mozilla-style URL with locale at the beginning, e.g.
// http://mozilla.org/fr/honey/badger
var locale = window.location.pathname.split('/')[1];

$.fn.showShare = function (services, options) {
    var self = this,
        scripts = [],
        settings = $.extend({}, options);

    if (this.data('share-shown') === true) {
        return this;
    } else {
        this.data('share-shown', true);
    }

    // Each service is available as a property on $.fn.showShare
    // that returns the script it needs to load and HTML code
    // for the widget.
    for (var k = 0; k < services.length; k++) {
        var service = services[k];
        if (service in $.fn.showShare) {
            var result = $.fn.showShare[service](settings),
                widget = $('<div class="share-widget ' + service + '"></div>')
                    .append(result.output);
            this.append(widget);
            scripts.push(result.script);
        }
    }

    // Load scripts asynchronusly, and then show the widgets when they are
    // finished loading.
    $script(scripts, function() {
        self.show();
    });

    return this;
};


// Maps Mozilla-style locales to Facebook-style locales.
var fbLocaleMap = {'de': 'de_DE', 'en-US': 'en_US', 'es': 'es_LA',
                   'fr': 'fr_FR', 'it': 'it_IT', 'ja': 'ja_JP',
                   'nl': 'nl_NL', 'pl': 'pl_PL', 'pt-BR': 'pt_BR',
                   'ru': 'ru_RU', 'sq': 'sq_AL', 'zh-CN': 'zh_CN',
                   'zh-TW': 'zh_TW'};

// Facebook Like Button
$.fn.showShare.facebook = function(options) {
    var settings = $.extend({
        appId: '0',
        send: 'false',
        layout: 'box_count',
        width: '450',
        show_faces: 'false'
    }, ('facebook' in options ? options.facebook : {}));

    // Fallback to en-US if locale is unsupported by Facebook.
    var fbLocale = (locale in fbLocaleMap ? fbLocaleMap[locale] : 'en_US');

    // Build output.
    var output =
            '<div id="fb-root"></div>'
            + '<div class="fb-like" '
            + '  data-send="' + settings.send + '" '
            + '  data-layout="' + settings.layout + '" '
            + '  data-width="' + settings.width + '" '
            + '  data-show-faces="' + settings.show_faces + '">'
            + '</div>';

    return {
        script: 'https://connect.facebook.net/' + fbLocale +
            '/all.js#xfbml=1&appId=' + settings.appId,
        output: output
    };
};

// Twitter Tweet Button
$.fn.showShare.twitter = function(options) {
    var settings = $.extend({
        count: 'vertical',
        lang: locale,
        text: '',
        url: window.location
    }, ('twitter' in options ? options.twitter : {}));

    var output =
            '<a href="https://twitter.com/share" '
            + 'class="twitter-share-button" '
            + 'data-count="' + settings.count + '" '
            + 'data-lang="' + settings.lang + '" '
            + 'data-text="' + settings.text + '" '
            + 'data-url="' + settings.url + '"></a>';

    return {
        script: 'https://platform.twitter.com/widgets.js',
        output: output
    };
};

// Flicks-specific init code.
$('body').on('click', '.share', function() {
    var share = $(this);
    share.next('.share-links').showShare(['twitter', 'facebook'], {
        facebook: {appId: '198137183603911'},
        twitter: {text: share.data('tweet-text'),
                  url: share.data('video-share-link')}
    });
});

})(jQuery);
