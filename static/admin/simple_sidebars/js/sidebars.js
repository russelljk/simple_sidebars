django.jQuery(function() {
	django.jQuery('.field-version').hide();
	django.jQuery('a#add_new').click(function() {
		var loc = django.jQuery(this).attr('href');
		var kind = django.jQuery('#widget_kind').val();
		django.jQuery(this).attr('href', loc + '?kind=' + kind);
	});
});
