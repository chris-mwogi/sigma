// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Business Process Register', {
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
			
			if (frm.doc.is_group) {
				frm.add_custom_button(__('View Child Processes'), function() {
					frappe.set_route('List', 'Business Process Register', {
						'parent_process': frm.doc.name
					});
				});
			}
			
			frm.add_custom_button(__('Process Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.business_process_register.business_process_register.get_process_summary',
					args: {
						process_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>Business Process Summary</h4>
								<table class="table table-bordered">
									<tr><th>Process Name</th><td>${r.message.process_name}</td></tr>
									<tr><th>Category</th><td>${r.message.process_category}</td></tr>
									<tr><th>Status</th><td>${r.message.status}</td></tr>
									<tr><th>Criticality</th><td>${r.message.criticality}</td></tr>
									<tr><th>Risk Exposure</th><td>${r.message.risk_exposure_level || 'N/A'}</td></tr>
									<tr><th>Linked Risks</th><td>${r.message.linked_risks_count}</td></tr>
									<tr><th>Linked Controls</th><td>${r.message.linked_controls_count}</td></tr>
									<tr><th>Child Processes</th><td>${r.message.child_processes_count}</td></tr>
									<tr><th>Business Impact</th><td>${r.message.business_impact || 'N/A'}</td></tr>
									<tr><th>Customer Impact</th><td>${r.message.customer_impact || 'N/A'}</td></tr>
									<tr><th>Regulatory Impact</th><td>${r.message.regulatory_impact || 'N/A'}</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('Process Summary'));
						}
					}
				});
			});
		}
		
		// Set indicator based on status
		if (frm.doc.status) {
			let color = get_status_color(frm.doc.status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.status]), color);
		}
		
		// Set indicator for criticality
		if (frm.doc.criticality) {
			let color = get_criticality_color(frm.doc.criticality);
			frm.dashboard.add_indicator(__('Criticality: {0}', [frm.doc.criticality]), color);
		}
		
		// Set indicator for risk exposure
		if (frm.doc.risk_exposure_level) {
			let color = get_criticality_color(frm.doc.risk_exposure_level);
			frm.dashboard.add_indicator(__('Risk Exposure: {0}', [frm.doc.risk_exposure_level]), color);
		}
	}
});

function get_status_color(status) {
	const color_map = {
		'Active': 'green',
		'Under Review': 'orange',
		'Inactive': 'grey',
		'Retired': 'red'
	};
	return color_map[status] || 'grey';
}

function get_criticality_color(criticality) {
	const color_map = {
		'Low': 'green',
		'Medium': 'blue',
		'High': 'orange',
		'Critical': 'red'
	};
	return color_map[criticality] || 'grey';
}

