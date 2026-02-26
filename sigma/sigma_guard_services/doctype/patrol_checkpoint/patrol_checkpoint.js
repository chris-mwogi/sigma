// Copyright (c) 2025, Prismod Technologies Limited and contributors
// For license information, please see license.txt

frappe.ui.form.on('Patrol Checkpoint', {
	refresh: function(frm) {
		// Setup zone filtering based on location
		frm.set_query('zone', function() {
			return {
				filters: {
					'location': frm.doc.location || '',
					'is_active': 1
				}
			};
		});
	},

	location: function(frm) {
		// Clear zone when location changes
		if (frm.doc.zone) {
			frm.set_value('zone', '');
		}
		// Refresh zone field to apply new filter
		frm.refresh_field('zone');
	}
});

