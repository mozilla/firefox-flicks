;(function($, flicks) {
    $(function() {
        var $region = $('#region');
        var $country = $('#id_country');
        var regionMap = $('body').data('regionMap');

        $country.change(function(e) {
            var regionId = regionMap[$country.val()];
            $region.text(flicks.trans('region-' + regionId));
        }).change();
    });
})(jQuery, flicks);
