# Copyright (c) 2025, Augment Code and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart_data(data, filters)
	return columns, data, None, chart


def get_columns():
	"""Return columns for the report"""
	return [
		{
			"fieldname": "risk_id",
			"label": _("Risk ID"),
			"fieldtype": "Link",
			"options": "Risk Register",
			"width": 120
		},
		{
			"fieldname": "risk_title",
			"label": _("Risk Title"),
			"fieldtype": "Data",
			"width": 200
		},
		{
			"fieldname": "risk_category",
			"label": _("Category"),
			"fieldtype": "Link",
			"options": "Risk Category",
			"width": 120
		},
		{
			"fieldname": "assessment_type",
			"label": _("Assessment Type"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "impact_level",
			"label": _("Impact"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "impact_score",
			"label": _("Impact Score"),
			"fieldtype": "Int",
			"width": 90
		},
		{
			"fieldname": "likelihood_level",
			"label": _("Likelihood"),
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "likelihood_score",
			"label": _("Likelihood Score"),
			"fieldtype": "Int",
			"width": 90
		},
		{
			"fieldname": "risk_score",
			"label": _("Risk Score"),
			"fieldtype": "Int",
			"width": 90
		},
		{
			"fieldname": "risk_rating",
			"label": _("Risk Rating"),
			"fieldtype": "Data",
			"width": 100
		}
	]


def get_data(filters):
	"""Get data for the report"""
	risk_type = filters.get("risk_type", "Residual")
	conditions = get_conditions(filters)
	
	# Determine which fields to use based on risk type
	if risk_type == "Inherent":
		impact_field = "inherent_impact"
		impact_score_field = "inherent_impact_score"
		likelihood_field = "inherent_likelihood"
		likelihood_score_field = "inherent_likelihood_score"
		risk_score_field = "inherent_risk_score"
		risk_rating_field = "inherent_risk_rating"
	else:  # Residual
		impact_field = "residual_impact"
		impact_score_field = "residual_impact_score"
		likelihood_field = "residual_likelihood"
		likelihood_score_field = "residual_likelihood_score"
		risk_score_field = "residual_risk_score"
		risk_rating_field = "residual_risk_rating"
	
	data = frappe.db.sql(f"""
		SELECT
			ra.linked_risk as risk_id,
			rr.risk_title,
			rr.risk_category,
			ra.assessment_type,
			ra.{impact_field} as impact_level,
			ra.{impact_score_field} as impact_score,
			ra.{likelihood_field} as likelihood_level,
			ra.{likelihood_score_field} as likelihood_score,
			ra.{risk_score_field} as risk_score,
			ra.{risk_rating_field} as risk_rating
		FROM
			`tabRisk Assessment` ra
		INNER JOIN
			`tabRisk Register` rr ON ra.linked_risk = rr.name
		WHERE
			ra.docstatus = 1
			{conditions}
		ORDER BY
			ra.{risk_score_field} DESC
	""", filters, as_dict=1)
	
	return data


def get_conditions(filters):
	"""Build WHERE conditions from filters"""
	conditions = []
	
	if filters.get("risk_category"):
		conditions.append("AND rr.risk_category = %(risk_category)s")
	
	if filters.get("assessment_type"):
		conditions.append("AND ra.assessment_type = %(assessment_type)s")
	
	if filters.get("from_date"):
		conditions.append("AND ra.assessment_date >= %(from_date)s")
	
	if filters.get("to_date"):
		conditions.append("AND ra.assessment_date <= %(to_date)s")
	
	return " ".join(conditions)


def get_chart_data(data, filters):
	"""Generate chart data for heat map visualization"""
	risk_type = filters.get("risk_type", "Residual")
	
	# Count risks by rating
	rating_counts = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
	for row in data:
		rating = row.get("risk_rating")
		if rating in rating_counts:
			rating_counts[rating] += 1
	
	chart = {
		"data": {
			"labels": ["Low", "Medium", "High", "Critical"],
			"datasets": [
				{
					"name": f"{risk_type} Risk Distribution",
					"values": [
						rating_counts["Low"],
						rating_counts["Medium"],
						rating_counts["High"],
						rating_counts["Critical"]
					]
				}
			]
		},
		"type": "bar",
		"colors": ["#28a745", "#ffc107", "#fd7e14", "#dc3545"]
	}
	
	return chart

