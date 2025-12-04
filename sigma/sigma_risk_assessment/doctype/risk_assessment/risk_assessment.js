// Copyright (c) 2025, Augment Code and contributors
// For license information, please see license.txt

frappe.ui.form.on('Risk Assessment', {
	refresh: function(frm) {
		// Add custom buttons
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('View Risk Register'), function() {
				frappe.set_route('Form', 'Risk Register', frm.doc.linked_risk);
			});

			frm.add_custom_button(__('Create Treatment Plan'), function() {
				frappe.new_doc('Risk Treatment Plan', {
					risk_assessment: frm.doc.name,
					linked_risk: frm.doc.linked_risk
				});
			});
		}

		// Set risk rating indicators
		if (frm.doc.inherent_risk_rating) {
			frm.dashboard.add_indicator(__('Inherent Risk: {0}', [frm.doc.inherent_risk_rating]),
				get_risk_color(frm.doc.inherent_risk_rating));
		}
		if (frm.doc.residual_risk_rating) {
			frm.dashboard.add_indicator(__('Residual Risk: {0}', [frm.doc.residual_risk_rating]),
				get_risk_color(frm.doc.residual_risk_rating));
		}
	},

	linked_risk: function(frm) {
		// Fetch risk title when risk register is selected
		if (frm.doc.linked_risk) {
			frappe.db.get_value('Risk Register', frm.doc.linked_risk, 'risk_title', (r) => {
				if (r && r.risk_title) {
					frm.set_value('risk_title', r.risk_title);
				}
			});
		}
	},

	inherent_impact: function(frm) {
		fetch_impact_score(frm, 'inherent_impact', 'inherent_impact_score');
		calculate_inherent_risk(frm);
	},

	inherent_likelihood: function(frm) {
		fetch_likelihood_score(frm, 'inherent_likelihood', 'inherent_likelihood_score');
		calculate_inherent_risk(frm);
	},

	residual_impact: function(frm) {
		fetch_impact_score(frm, 'residual_impact', 'residual_impact_score');
		calculate_residual_risk(frm);
	},

	residual_likelihood: function(frm) {
		fetch_likelihood_score(frm, 'residual_likelihood', 'residual_likelihood_score');
		calculate_residual_risk(frm);
	}
});

function fetch_impact_score(frm, impact_field, score_field) {
	if (frm.doc[impact_field]) {
		frappe.db.get_value('Risk Impact Matrix', frm.doc[impact_field], 'impact_score', (r) => {
			if (r && r.impact_score) {
				frm.set_value(score_field, r.impact_score);
			}
		});
	}
}

function fetch_likelihood_score(frm, likelihood_field, score_field) {
	if (frm.doc[likelihood_field]) {
		frappe.db.get_value('Risk Likelihood Matrix', frm.doc[likelihood_field], 'likelihood_score', (r) => {
			if (r && r.likelihood_score) {
				frm.set_value(score_field, r.likelihood_score);
			}
		});
	}
}

function calculate_inherent_risk(frm) {
	if (frm.doc.inherent_impact_score && frm.doc.inherent_likelihood_score) {
		let score = frm.doc.inherent_impact_score * frm.doc.inherent_likelihood_score;
		frm.set_value('inherent_risk_score', score);

		// Get risk rating from server
		frappe.call({
			method: 'sigma.sigma_risk_assessment.doctype.risk_dashboard_settings.risk_dashboard_settings.get_risk_rating',
			args: {
				risk_score: score
			},
			callback: function(r) {
				if (r.message) {
					frm.set_value('inherent_risk_rating', r.message);
				}
			}
		});
	}
}

function calculate_residual_risk(frm) {
	if (frm.doc.residual_impact_score && frm.doc.residual_likelihood_score) {
		let score = frm.doc.residual_impact_score * frm.doc.residual_likelihood_score;
		frm.set_value('residual_risk_score', score);

		// Get risk rating from server
		frappe.call({
			method: 'sigma.sigma_risk_assessment.doctype.risk_dashboard_settings.risk_dashboard_settings.get_risk_rating',
			args: {
				risk_score: score
			},
			callback: function(r) {
				if (r.message) {
					frm.set_value('residual_risk_rating', r.message);
				}
			}
		});
	}
}

function get_risk_color(rating) {
	const color_map = {
		'Low': 'green',
		'Medium': 'yellow',
		'High': 'orange',
		'Critical': 'red'
	};
	return color_map[rating] || 'gray';
}
