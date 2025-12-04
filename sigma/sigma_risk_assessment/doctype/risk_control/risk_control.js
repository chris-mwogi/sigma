// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Risk Control', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Linked Assessments'), function() {
				frappe.set_route('List', 'Risk Assessment', {
					'existing_controls': ['like', '%' + frm.doc.name + '%']
				});
			});
			
			frm.add_custom_button(__('Effectiveness Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.risk_control.risk_control.get_control_effectiveness_summary',
					args: {
						control_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>Control Effectiveness Summary</h4>
								<table class="table table-bordered">
									<tr><th>Control Name</th><td>${r.message.control_name}</td></tr>
									<tr><th>Effectiveness Rating</th><td>${r.message.effectiveness_rating || 'Not Assessed'}</td></tr>
									<tr><th>Implementation Status</th><td>${r.message.implementation_status}</td></tr>
									<tr><th>Linked Assessments</th><td>${r.message.linked_assessments}</td></tr>
									<tr><th>Cost of Control</th><td>${format_currency(r.message.cost_of_control || 0)}</td></tr>
									<tr><th>Automation Level</th><td>${r.message.automation_level || 0}%</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('Effectiveness Summary'));
						}
					}
				});
			});
		}
		
		// Set indicator based on effectiveness rating
		if (frm.doc.effectiveness_rating) {
			let color = get_effectiveness_color(frm.doc.effectiveness_rating);
			frm.dashboard.add_indicator(__('Effectiveness: {0}', [frm.doc.effectiveness_rating]), color);
		}
		
		// Set indicator for implementation status
		if (frm.doc.implementation_status) {
			let color = get_implementation_color(frm.doc.implementation_status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.implementation_status]), color);
		}
		
		// Alert if review is overdue
		if (frm.doc.next_review_date && frappe.datetime.get_diff(frm.doc.next_review_date, frappe.datetime.nowdate()) < 0) {
			frm.dashboard.add_indicator(__('Review Overdue'), 'red');
		}
	},
	
	review_frequency_days: function(frm) {
		// Auto-calculate next review date when frequency changes
		if (frm.doc.review_frequency_days) {
			let base_date = frm.doc.last_review_date || frm.doc.implementation_date || frappe.datetime.nowdate();
			let next_date = frappe.datetime.add_days(base_date, frm.doc.review_frequency_days);
			frm.set_value('next_review_date', next_date);
		}
	},
	
	implementation_date: function(frm) {
		// Set next review date when implementation date is set
		if (frm.doc.implementation_date && frm.doc.review_frequency_days && !frm.doc.next_review_date) {
			let next_date = frappe.datetime.add_days(frm.doc.implementation_date, frm.doc.review_frequency_days);
			frm.set_value('next_review_date', next_date);
		}
	}
});

function get_effectiveness_color(rating) {
	const color_map = {
		'Not Assessed': 'grey',
		'Not Effective': 'red',
		'Partially Effective': 'orange',
		'Effective': 'green',
		'Highly Effective': 'blue'
	};
	return color_map[rating] || 'grey';
}

function get_implementation_color(status) {
	const color_map = {
		'Planned': 'grey',
		'In Progress': 'orange',
		'Implemented': 'green',
		'Under Review': 'blue',
		'Retired': 'red'
	};
	return color_map[status] || 'grey';
}

