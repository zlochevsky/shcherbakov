jQuery.noConflict();

function toggleChords() {
    jQuery("span.ch").each(function(i, el) {
        jQuery(el).toggle();
        jQuery(".transpose-keys").toggle();
    });
}

jQuery(document).ready(function() {
    jQuery("pre").transpose();
    jQuery('#toggleChords').bind('click', function(){
        var e = jQuery(this);
        e.toggleClass('note1').toggleClass('note2');
        toggleChords();
    });
});

