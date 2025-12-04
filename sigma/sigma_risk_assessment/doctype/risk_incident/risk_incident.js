// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Risk Incident', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1) {
			if (frm.doc.linked_risk) {
				frm.add_custom_button(__('View Linked Risk'), function() {
					frappe.set_route('Form', 'Risk Register', frm.doc.linked_risk);
				});
			}
			
			if (frm.doc.linked_control) {
				frm.add_custom_button(__('View Linked Control'), function() {
					frappe.set_route('Form', 'Risk Control', frm.doc.linked_control);
				});
			}
			
			if (frm.doc.linked_risk && frm.doc.impact_level in ['High', 'Critical']) {
				frm.add_custom_button(__('Create Risk Assessment'), function() {
					frappe.new_doc('Risk Assessment', {
						linked_risk: frm.doc.linked_risk,
						assessment_type: 'Incident-Triggered'
					});
				});
			}
			
			frm.add_custom_button(__('Incident Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.risk_incident.risk_incident.get_incident_summary',
					args: {
						incident_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>Incident Summary</h4>
								<table class="table table-bordered">
									<tr><th>Incident</th><td>${r.message.incident_title}</td></tr>
									<tr><th>Type</th><td>${r.message.incident_type}</td></tr>
									<tr><th>Status</th><td>${r.message.incident_status}</td></tr>
									<tr><th>Impact Level</th><td>${r.message.impact_level}</td></tr>
									<tr><th>Financial Impact</th><td>${format_currency(r.message.financial_impact || 0)}</td></tr>
									<tr><th>Incident Date</th><td>${r.message.incident_date}</td></tr>
									<tr><th>Investigation Status</th><td>${r.message.investigation_status || 'N/A'}</td></tr>
									<tr><th>Investigation Owner</th><td>${r.message.investigation_owner || 'N/A'}</td></tr>
									<tr><th>Linked Risk</th><td>${r.message.linked_risk || 'N/A'}</td></tr>
									<tr><th>Linked Control</th><td>${r.message.linked_control || 'N/A'}</td></tr>
									<tr><th>Closure Date</th><td>${r.message.closure_date || 'Not Closed'}</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('Incident Summary'));
						}
					}
				});
			});
		}
		
		// Set indicator based on incident status
		if (frm.doc.incident_status) {
			let color = get_incident_status_color(frm.doc.incident_status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.incident_status]), color);
		}
		
		// Set indicator for impact level
		if (frm.doc.impact_level) {
			let color = get_impact_color(frm.doc.impact_level);
			frm.dashboard.add_indicator(__('Impact: {0}', [frm.doc.impact_level]), color);
		}
		
		// Set indicator for investigation status
		if (frm.doc.investigation_status) {
			let color = get_investigation_color(frm.doc.investigation_status);
			frm.dashboard.add_indicator(__('Investigation: {0}', [frm.doc.investigation_status]), color);
		}
		
		// Alert if high/critical impact
		if (frm.doc.impact_level in ['High', 'Critical']) {
			frm.dashboard.add_indicator(__('High Priority Incident'), 'red');
		}
	},
	
	investigation_status: function(frm) {
		// Auto-update incident status when investigation is completed
		if (frm.doc.investigation_status === 'Completed' && frm.doc.incident_status === 'Under Investigation') {
			frm.set_value('incident_status', 'Contained');
		}
	},
	
	incident_status: function(frm) {
		// Auto-set closure date when status is closed
		if (frm.doc.incident_status === 'Closed' && !frm.doc.closure_date) {
			frm.set_value('closure_date', frappe.datetime.nowdate());
		}
	}
});

function get_incident_status_color(status) {
	const color_map = {
		'Reported': 'orange',
		'Under Investigation': 'blue',
		'Contained': 'yellow',
		'Resolved': 'green',
		'Closed': 'grey'
	};
	return color_map[status] || 'grey';
}

function get_impact_color(impact) {
	const color_map = {
		'Low': 'green',
		'Medium': 'blue',
		'High': 'orange',
		'Critical': 'red'
	};
	return color_map[impact] || 'grey';
}

function get_investigation_color(status) {
	const color_map = {
		'Not Started': 'grey',
		'In Progress': 'orange',
		'Completed': 'green'
	};
	return color_map[status] || 'grey';
}

