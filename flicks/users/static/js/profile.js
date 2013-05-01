;(function($, flicks) {
    $(function() {
        var $region = $('#region');
        var $country = $('#id_country');
        var $mailingCountry = $('#id_mailing_country');
        var regionMap = $('body').data('regionMap');

        var mailingCountryCustom = false;

        $country.change(function(e) {
            // Update region string when country changes.
            var regionId = regionMap[$country.val()];
            $region.text(flicks.trans('region-' + regionId));

            // If the user hasn't set their mailing country manually, update it
            // to the same country as this input.
            if (!mailingCountryCustom) {
                $mailingCountry.val($country.val());
            }
        }).change();

        $mailingCountry.change(function(e) {
            mailingCountryCustom = true;
        });
    });
})(jQuery, flicks);
