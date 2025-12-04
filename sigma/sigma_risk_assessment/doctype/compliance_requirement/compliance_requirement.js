// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Compliance Requirement', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Linked Risks'), function() {
				frappe.set_route('List', 'Risk Register', {
					'notes': ['like', '%' + frm.doc.name + '%']
				});
			});
			
			frm.add_custom_button(__('View Linked Controls'), function() {
				frappe.set_route('List', 'Risk Control', {
					'notes': ['like', '%' + frm.doc.name + '%']
				});
			});
			
			frm.add_custom_button(__('Compliance Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.compliance_requirement.compliance_requirement.get_compliance_summary',
					args: {
						requirement_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>Compliance Summary</h4>
								<table class="table table-bordered">
									<tr><th>Requirement</th><td>${r.message.requirement_title}</td></tr>
									<tr><th>Status</th><td>${r.message.compliance_status}</td></tr>
									<tr><th>Compliance Level</th><td>${r.message.current_compliance_level || 0}%</td></tr>
									<tr><th>Priority</th><td>${r.message.priority || 'N/A'}</td></tr>
									<tr><th>Framework</th><td>${r.message.regulatory_framework || 'N/A'}</td></tr>
									<tr><th>Linked Risks</th><td>${r.message.linked_risks_count}</td></tr>
									<tr><th>Linked Controls</th><td>${r.message.linked_controls_count}</td></tr>
									<tr><th>Target Date</th><td>${r.message.target_compliance_date || 'N/A'}</td></tr>
									<tr><th>Next Review</th><td>${r.message.next_review_date || 'N/A'}</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('Compliance Summary'));
						}
					}
				});
			});
		}
		
		// Set indicator based on compliance status
		if (frm.doc.compliance_status) {
			let color = get_compliance_color(frm.doc.compliance_status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.compliance_status]), color);
		}
		
		// Set indicator for compliance level
		if (frm.doc.current_compliance_level) {
			let color = frm.doc.current_compliance_level >= 90 ? 'green' :
			            frm.doc.current_compliance_level >= 70 ? 'blue' :
			            frm.doc.current_compliance_level >= 50 ? 'orange' : 'red';
			frm.dashboard.add_indicator(__('Compliance: {0}%', [frm.doc.current_compliance_level]), color);
		}
		
		// Alert if review is overdue
		if (frm.doc.next_review_date && frappe.datetime.get_diff(frm.doc.next_review_date, frappe.datetime.nowdate()) < 0) {
			frm.dashboard.add_indicator(__('Review Overdue'), 'red');
		}
		
		// Alert if target compliance date is approaching or overdue
		if (frm.doc.target_compliance_date && frm.doc.compliance_status !== 'Compliant') {
			let days_diff = frappe.datetime.get_diff(frm.doc.target_compliance_date, frappe.datetime.nowdate());
			if (days_diff < 0) {
				frm.dashboard.add_indicator(__('Overdue by {0} days', [Math.abs(days_diff)]), 'red');
			} else if (days_diff <= 30) {
				frm.dashboard.add_indicator(__('Due in {0} days', [days_diff]), 'orange');
			}
		}
	},
	
	review_frequency_days: function(frm) {
		// Auto-calculate next review date when frequency changes
		if (frm.doc.review_frequency_days) {
			let base_date = frm.doc.last_review_date || frm.doc.effective_date || frappe.datetime.nowdate();
			let next_date = frappe.datetime.add_days(base_date, frm.doc.review_frequency_days);
			frm.set_value('next_review_date', next_date);
		}
	},
	
	effective_date: function(frm) {
		// Set next review date when effective date is set
		if (frm.doc.effective_date && frm.doc.review_frequency_days && !frm.doc.next_review_date) {
			let next_date = frappe.datetime.add_days(frm.doc.effective_date, frm.doc.review_frequency_days);
			frm.set_value('next_review_date', next_date);
		}
	}
});

function get_compliance_color(status) {
	const color_map = {
		'Not Started': 'grey',
		'In Progress': 'orange',
		'Compliant': 'green',
		'Partially Compliant': 'blue',
		'Non-Compliant': 'red',
		'Under Review': 'yellow'
	};
	return color_map[status] || 'grey';
}

