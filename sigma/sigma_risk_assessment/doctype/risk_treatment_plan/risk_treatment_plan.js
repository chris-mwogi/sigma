// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Risk Treatment Plan', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('View Risk Register'), function() {
				frappe.set_route('Form', 'Risk Register', frm.doc.linked_risk);
			});
			
			if (frm.doc.risk_assessment) {
				frm.add_custom_button(__('View Risk Assessment'), function() {
					frappe.set_route('Form', 'Risk Assessment', frm.doc.risk_assessment);
				});
			}
			
			frm.add_custom_button(__('Treatment Summary'), function() {
				frappe.call({
					method: 'sigma.sigma_risk_assessment.doctype.risk_treatment_plan.risk_treatment_plan.get_treatment_plan_summary',
					args: {
						plan_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							let msg = `
								<h4>Treatment Plan Summary</h4>
								<table class="table table-bordered">
									<tr><th>Plan Title</th><td>${r.message.plan_title}</td></tr>
									<tr><th>Status</th><td>${r.message.plan_status}</td></tr>
									<tr><th>Progress</th><td>${r.message.progress_percentage}%</td></tr>
									<tr><th>Total Actions</th><td>${r.message.total_actions}</td></tr>
									<tr><th>Completed Actions</th><td>${r.message.completed_actions}</td></tr>
									<tr><th>Overdue Actions</th><td>${r.message.overdue_actions}</td></tr>
									<tr><th>Estimated Budget</th><td>${format_currency(r.message.estimated_budget || 0)}</td></tr>
									<tr><th>Actual Cost</th><td>${format_currency(r.message.actual_cost || 0)}</td></tr>
									<tr><th>Budget Variance</th><td>${format_currency(r.message.budget_variance || 0)}</td></tr>
									<tr><th>Effectiveness Rating</th><td>${r.message.effectiveness_rating || 'Not Assessed'}</td></tr>
								</table>
							`;
							frappe.msgprint(msg, __('Treatment Plan Summary'));
						}
					}
				});
			});
		}
		
		// Set indicators
		if (frm.doc.plan_status) {
			let color = get_status_color(frm.doc.plan_status);
			frm.dashboard.add_indicator(__('Status: {0}', [frm.doc.plan_status]), color);
		}
		
		if (frm.doc.progress_percentage) {
			let color = frm.doc.progress_percentage === 100 ? 'green' : 
			            frm.doc.progress_percentage >= 50 ? 'blue' : 'orange';
			frm.dashboard.add_indicator(__('Progress: {0}%', [frm.doc.progress_percentage]), color);
		}
		
		// Alert if overdue
		if (frm.doc.target_completion_date && !frm.doc.actual_completion_date) {
			let days_diff = frappe.datetime.get_diff(frm.doc.target_completion_date, frappe.datetime.nowdate());
			if (days_diff < 0) {
				frm.dashboard.add_indicator(__('Overdue by {0} days', [Math.abs(days_diff)]), 'red');
			}
		}
		
		// Budget variance indicator
		if (frm.doc.budget_variance && frm.doc.budget_variance !== 0) {
			let color = frm.doc.budget_variance > 0 ? 'red' : 'green';
			let label = frm.doc.budget_variance > 0 ? 'Over Budget' : 'Under Budget';
			frm.dashboard.add_indicator(__('{0}: {1}', [label, format_currency(Math.abs(frm.doc.budget_variance))]), color);
		}
	},
	
	linked_risk: function(frm) {
		// Fetch risk title when linked risk changes
		if (frm.doc.linked_risk) {
			frappe.db.get_value('Risk Register', frm.doc.linked_risk, 'risk_title', function(r) {
				if (r && r.risk_title) {
					frm.set_value('risk_title', r.risk_title);
				}
			});
		}
	},
	
	treatment_actions: function(frm) {
		// Recalculate progress when actions change
		calculate_progress(frm);
		calculate_actual_cost(frm);
	}
});

// Child table events
frappe.ui.form.on('Risk Treatment Action', {
	status: function(frm, cdt, cdn) {
		calculate_progress(frm);
	},
	
	actual_cost: function(frm, cdt, cdn) {
		calculate_actual_cost(frm);
	},
	
	treatment_actions_remove: function(frm, cdt, cdn) {
		calculate_progress(frm);
		calculate_actual_cost(frm);
	}
});

function calculate_progress(frm) {
	if (!frm.doc.treatment_actions || frm.doc.treatment_actions.length === 0) {
		frm.set_value('progress_percentage', 0);
		return;
	}
	
	let total = frm.doc.treatment_actions.length;
	let completed = frm.doc.treatment_actions.filter(a => a.status === 'Completed').length;
	let progress = (completed / total) * 100;
	
	frm.set_value('progress_percentage', progress);
}

function calculate_actual_cost(frm) {
	let total_cost = 0;
	if (frm.doc.treatment_actions) {
		frm.doc.treatment_actions.forEach(function(action) {
			if (action.actual_cost) {
				total_cost += action.actual_cost;
			}
		});
	}
	frm.set_value('actual_cost', total_cost);
	
	// Calculate variance
	if (frm.doc.estimated_budget) {
		let variance = total_cost - frm.doc.estimated_budget;
		frm.set_value('budget_variance', variance);
		
		if (frm.doc.estimated_budget > 0) {
			let variance_pct = (variance / frm.doc.estimated_budget) * 100;
			frm.set_value('budget_variance_percentage', variance_pct);
		}
	}
}

function get_status_color(status) {
	const color_map = {
		'Draft': 'grey',
		'Approved': 'blue',
		'In Progress': 'orange',
		'Completed': 'green',
		'On Hold': 'yellow',
		'Cancelled': 'red'
	};
	return color_map[status] || 'grey';
}

