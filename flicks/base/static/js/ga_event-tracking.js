// All click based event tracking should go here 

$(function() {
    'use strict';

    // Tracks Creative Brief PDF Download 
    $('.ga_brief-dl').click(function() {
        _gaq.push(['_trackEvent', 'Downloads', 'PDF', 'Creative Brief']);        
        return true;
    });    
});
