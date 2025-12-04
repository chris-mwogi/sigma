# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """Execute Asset Criticality Matrix Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {"fieldname": "asset", "label": _("Asset"), "fieldtype": "Link", "options": "Asset", "width": 150},
        {"fieldname": "asset_name", "label": _("Asset Name"), "fieldtype": "Data", "width": 180},
        {"fieldname": "asset_category_sigma", "label": _("Category"), "fieldtype": "Link", "options": "Asset Category Sigma", "width": 150},
        {"fieldname": "criticality_rating", "label": _("Criticality"), "fieldtype": "Data", "width": 100},
        {"fieldname": "risk_score", "label": _("Risk Score"), "fieldtype": "Float", "width": 100},
        {"fieldname": "risk_classification", "label": _("Risk Classification"), "fieldtype": "Data", "width": 130},
        {"fieldname": "failure_probability", "label": _("Failure Probability"), "fieldtype": "Percent", "width": 140},
        {"fieldname": "condition_index", "label": _("Condition Index"), "fieldtype": "Percent", "width": 120},
        {"fieldname": "lifecycle_status", "label": _("Lifecycle Status"), "fieldtype": "Data", "width": 130}
    ]


def get_data(filters):
    """Get report data"""
    conditions = []
    if filters.get("criticality_rating"):
        conditions.append("AND a.criticality_rating = %(criticality_rating)s")
    if filters.get("risk_classification"):
        conditions.append("AND a.risk_classification = %(risk_classification)s")
    
    conditions_str = " ".join(conditions)
    
    data = frappe.db.sql(f"""
        SELECT
            a.name as asset,
            a.asset_name,
            a.asset_category_sigma,
            a.criticality_rating,
            a.risk_score,
            a.risk_classification,
            a.failure_probability,
            a.condition_index,
            a.lifecycle_status
        FROM
            `tabAsset` a
        WHERE
            a.docstatus = 1
            {conditions_str}
        ORDER BY
            a.criticality_rating DESC,
            a.risk_score DESC
    """, filters, as_dict=1)
    
    return data


def get_chart_data(data):
    """Generate chart data"""
    criticality_counts = {}
    for row in data:
        crit = row.get("criticality_rating", "Unknown")
        criticality_counts[crit] = criticality_counts.get(crit, 0) + 1
    
    return {
        "data": {
            "labels": list(criticality_counts.keys()),
            "datasets": [{"name": "Assets", "values": list(criticality_counts.values())}]
        },
        "type": "pie",
        "colors": ["#dc3545", "#ffc107", "#17a2b8", "#28a745"]
    }


def get_summary(data):
    """Generate summary statistics"""
    total = len(data)
    critical = len([d for d in data if d.get("criticality_rating") == "Critical"])
    high = len([d for d in data if d.get("criticality_rating") == "High"])
    very_high_risk = len([d for d in data if d.get("risk_classification") == "Very High Risk"])
    
    return [
        {"value": total, "label": "Total Assets", "datatype": "Int", "indicator": "blue"},
        {"value": critical, "label": "Critical Assets", "datatype": "Int", "indicator": "red"},
        {"value": high, "label": "High Criticality", "datatype": "Int", "indicator": "orange"},
        {"value": very_high_risk, "label": "Very High Risk", "datatype": "Int", "indicator": "red"}
    ]

