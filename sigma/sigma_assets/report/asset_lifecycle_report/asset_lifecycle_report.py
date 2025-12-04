# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, date_diff, getdate


def execute(filters=None):
    """Execute Asset Lifecycle Report"""
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
        {"fieldname": "asset_location", "label": _("Location"), "fieldtype": "Link", "options": "Asset Location", "width": 150},
        {"fieldname": "lifecycle_status", "label": _("Lifecycle Status"), "fieldtype": "Data", "width": 130},
        {"fieldname": "purchase_date", "label": _("Purchase Date"), "fieldtype": "Date", "width": 130},
        {"fieldname": "age_years", "label": _("Age (Years)"), "fieldtype": "Float", "width": 100},
        {"fieldname": "expected_useful_life_years", "label": _("Expected Life (Years)"), "fieldtype": "Float", "width": 150},
        {"fieldname": "remaining_life_years", "label": _("Remaining Life (Years)"), "fieldtype": "Float", "width": 150},
        {"fieldname": "condition_index", "label": _("Condition Index"), "fieldtype": "Percent", "width": 120},
        {"fieldname": "health_status", "label": _("Health Status"), "fieldtype": "Data", "width": 120}
    ]


def get_data(filters):
    """Get report data"""
    conditions = []
    if filters.get("asset_category_sigma"):
        conditions.append("AND a.asset_category_sigma = %(asset_category_sigma)s")
    if filters.get("asset_location"):
        conditions.append("AND a.asset_location = %(asset_location)s")
    if filters.get("lifecycle_status"):
        conditions.append("AND a.lifecycle_status = %(lifecycle_status)s")
    
    conditions_str = " ".join(conditions)
    
    data = frappe.db.sql(f"""
        SELECT
            a.name as asset,
            a.asset_name,
            a.asset_category_sigma,
            a.asset_location,
            a.lifecycle_status,
            a.purchase_date,
            ROUND(DATEDIFF(CURDATE(), a.purchase_date) / 365.25, 2) as age_years,
            a.expected_useful_life_years,
            ROUND(a.expected_useful_life_years - (DATEDIFF(CURDATE(), a.purchase_date) / 365.25), 2) as remaining_life_years,
            a.condition_index,
            a.health_status
        FROM
            `tabAsset` a
        WHERE
            a.docstatus = 1
            {conditions_str}
        ORDER BY
            remaining_life_years ASC
    """, filters, as_dict=1)
    
    return data


def get_chart_data(data):
    """Generate chart data"""
    lifecycle_counts = {}
    for row in data:
        status = row.get("lifecycle_status", "Unknown")
        lifecycle_counts[status] = lifecycle_counts.get(status, 0) + 1
    
    return {
        "data": {
            "labels": list(lifecycle_counts.keys()),
            "datasets": [{"name": "Assets", "values": list(lifecycle_counts.values())}]
        },
        "type": "bar"
    }


def get_summary(data):
    """Generate summary statistics"""
    total_assets = len(data)
    avg_age = sum([d.get("age_years", 0) for d in data]) / total_assets if total_assets > 0 else 0
    avg_remaining_life = sum([d.get("remaining_life_years", 0) for d in data]) / total_assets if total_assets > 0 else 0
    end_of_life_soon = len([d for d in data if 0 < d.get("remaining_life_years", 0) <= 2])
    
    return [
        {"value": total_assets, "label": "Total Assets", "datatype": "Int", "indicator": "blue"},
        {"value": round(avg_age, 2), "label": "Average Age (Years)", "datatype": "Float", "indicator": "blue"},
        {"value": round(avg_remaining_life, 2), "label": "Avg Remaining Life (Years)", "datatype": "Float", "indicator": "green"},
        {"value": end_of_life_soon, "label": "End of Life Soon (< 2 years)", "datatype": "Int", "indicator": "red"}
    ]

