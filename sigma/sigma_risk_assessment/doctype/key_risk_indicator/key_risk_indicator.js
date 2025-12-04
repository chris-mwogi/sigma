// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Key Risk Indicator', {
	refresh: function(frm) {
		// Add custom buttons
		if (!frm.is_new()) {
			if (frm.doc.linked_risk) {
				frm.add_custom_button(__('View Linked Risk'), function() {
					frappe.set_route('Form', 'Risk Register', frm.doc.linked_risk);
				});
			}
			
			frm.add_custom_button(__('KRI Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.key_risk_indicator.key_risk_indicator.get_kri_summary',
					args: {
						kri_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>KRI Summary</h4>
								<table class="table table-bordered">
									<tr><th>KRI Name</th><td>${r.message.kri_name}</td></tr>
									<tr><th>Current Status</th><td>${r.message.current_status || 'N/A'}</td></tr>
									<tr><th>Current Value</th><td>${r.message.current_value || 'N/A'} ${r.message.unit_of_measurement}</td></tr>
									<tr><th>Target Value</th><td>${r.message.target_value || 'N/A'} ${r.message.unit_of_measurement}</td></tr>
									<tr><th>Trend</th><td>${r.message.trend || 'N/A'}</td></tr>
									<tr><th>Total Readings</th><td>${r.message.total_readings}</td></tr>
									<tr><th>Normal Readings</th><td>${r.message.normal_count}</td></tr>
									<tr><th>Warning Readings</th><td>${r.message.warning_count}</td></tr>
									<tr><th>Critical Readings</th><td>${r.message.critical_count}</td></tr>
									<tr><th>Last Reading Date</th><td>${r.message.last_reading_date || 'N/A'}</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('KRI Summary'));
						}
					}
				});
			});
			
			frm.add_custom_button(__('Add Reading'), function() {
				let d = new frappe.ui.Dialog({
					title: __('Add KRI Reading'),
					fields: [
						{
							fieldname: 'reading_date',
							fieldtype: 'Date',
							label: __('Reading Date'),
							reqd: 1,
							default: frappe.datetime.nowdate()
						},
						{
							fieldname: 'actual_value',
							fieldtype: 'Float',
							label: __('Actual Value'),
							reqd: 1
						},
						{
							fieldname: 'notes',
							fieldtype: 'Text',
							label: __('Notes')
						}
					],
					primary_action_label: __('Add Reading'),
					primary_action: function(values) {
						let new_row = frm.add_child('kri_readings');
						new_row.reading_date = values.reading_date;
						new_row.actual_value = values.actual_value;
						new_row.notes = values.notes;
						frm.refresh_field('kri_readings');
						frm.save();
						d.hide();
					}
				});
				d.show();
			});
		}
		
		// Set indicator based on current status
		if (frm.doc.current_status) {
			let color = get_status_color(frm.doc.current_status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.current_status]), color);
		}
		
		// Set indicator for trend
		if (frm.doc.trend) {
			let color = get_trend_color(frm.doc.trend);
			frm.dashboard.add_indicator(__('Trend: {0}', [frm.doc.trend]), color);
		}
		
		// Show current value vs target
		if (frm.doc.current_value && frm.doc.target_value) {
			let variance = ((frm.doc.current_value - frm.doc.target_value) / frm.doc.target_value * 100).toFixed(2);
			let color = Math.abs(variance) < 10 ? 'green' : 'orange';
			frm.dashboard.add_indicator(__('Variance: {0}%', [variance]), color);
		}
	},
	
	kri_readings: function(frm) {
		// Refresh form when readings change to update status
		frm.save();
	}
});

// Child table events
frappe.ui.form.on('KRI Reading', {
	actual_value: function(frm, cdt, cdn) {
		// Auto-save when value is entered
		setTimeout(function() {
			frm.save();
		}, 500);
	}
});

function get_status_color(status) {
	const color_map = {
		'Normal': 'green',
		'Warning': 'orange',
		'Critical': 'red'
	};
	return color_map[status] || 'grey';
}

function get_trend_color(trend) {
	const color_map = {
		'Improving': 'green',
		'Stable': 'blue',
		'Deteriorating': 'red'
	};
	return color_map[trend] || 'grey';
}

