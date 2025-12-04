// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Risk Register', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Create Assessment'), function() {
				frappe.new_doc('Risk Assessment', {
					linked_risk: frm.doc.name,
					risk_title: frm.doc.risk_title
				});
			});
			
			frm.add_custom_button(__('View Assessments'), function() {
				frappe.set_route('List', 'Risk Assessment', {
					linked_risk: frm.doc.name
				});
			});
		}
		
		// Set indicator based on status
		if (frm.doc.status === 'Active') {
			frm.dashboard.set_headline_alert('This risk is currently active and requires monitoring');
		}
	},
	
	review_frequency_days: function(frm) {
		// Recalculate next review date when frequency changes
		if (frm.doc.review_frequency_days) {
			let base_date = frm.doc.last_review_date || frm.doc.date_identified || frappe.datetime.get_today();
			let next_date = frappe.datetime.add_days(base_date, frm.doc.review_frequency_days);
			frm.set_value('next_review_date', next_date);
		}
	}
});

