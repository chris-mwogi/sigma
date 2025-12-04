# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import nowdate, add_days, date_diff, getdate


def execute(filters=None):
    """Execute Maintenance Due Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "schedule_name",
            "label": _("Schedule"),
            "fieldtype": "Link",
            "options": "Asset Maintenance Schedule",
            "width": 180
        },
        {
            "fieldname": "asset",
            "label": _("Asset"),
            "fieldtype": "Link",
            "options": "Asset",
            "width": 150
        },
        {
            "fieldname": "asset_name",
            "label": _("Asset Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "asset_category_sigma",
            "label": _("Category"),
            "fieldtype": "Link",
            "options": "Asset Category Sigma",
            "width": 150
        },
        {
            "fieldname": "asset_location",
            "label": _("Location"),
            "fieldtype": "Link",
            "options": "Asset Location",
            "width": 150
        },
        {
            "fieldname": "criticality_rating",
            "label": _("Criticality"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "maintenance_type",
            "label": _("Maintenance Type"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "next_due_date",
            "label": _("Next Due Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "days_until_due",
            "label": _("Days Until Due"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "estimated_duration_hours",
            "label": _("Est. Duration (Hrs)"),
            "fieldtype": "Float",
            "width": 130
        }
    ]


def get_data(filters):
    """Get report data"""
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            ams.name as schedule_name,
            ams.asset,
            ams.asset_name,
            ams.asset_category_sigma,
            ams.asset_location,
            ams.criticality_rating,
            ams.maintenance_type,
            ams.next_due_date,
            DATEDIFF(ams.next_due_date, CURDATE()) as days_until_due,
            ams.status,
            ams.estimated_duration_hours
        FROM
            `tabAsset Maintenance Schedule` ams
        WHERE
            ams.docstatus = 1
            AND ams.status IN ('Scheduled', 'Due', 'Overdue')
            AND ams.is_active = 1
            {conditions}
        ORDER BY
            ams.next_due_date ASC,
            ams.criticality_rating DESC
    """, filters, as_dict=1)
    
    return data


def get_conditions(filters):
    """Build filter conditions"""
    conditions = []
    
    if filters.get("asset"):
        conditions.append("AND ams.asset = %(asset)s")
    
    if filters.get("asset_category_sigma"):
        conditions.append("AND ams.asset_category_sigma = %(asset_category_sigma)s")
    
    if filters.get("asset_location"):
        conditions.append("AND ams.asset_location = %(asset_location)s")
    
    if filters.get("criticality_rating"):
        conditions.append("AND ams.criticality_rating = %(criticality_rating)s")
    
    if filters.get("maintenance_type"):
        conditions.append("AND ams.maintenance_type = %(maintenance_type)s")
    
    if filters.get("days_ahead"):
        conditions.append("AND ams.next_due_date <= DATE_ADD(CURDATE(), INTERVAL %(days_ahead)s DAY)")
    
    return " ".join(conditions)


def get_chart_data(data):
    """Generate chart data"""
    # Count by status
    status_counts = {}
    for row in data:
        status = row.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [
                {
                    "name": "Maintenance Schedules",
                    "values": list(status_counts.values())
                }
            ]
        },
        "type": "donut",
        "colors": ["#28a745", "#ffc107", "#dc3545"]
    }


def get_summary(data):
    """Generate summary statistics"""
    total_schedules = len(data)
    overdue = len([d for d in data if d.get("days_until_due", 0) < 0])
    due_this_week = len([d for d in data if 0 <= d.get("days_until_due", 0) <= 7])
    due_this_month = len([d for d in data if 0 <= d.get("days_until_due", 0) <= 30])
    total_cost = sum([d.get("estimated_cost", 0) for d in data])
    
    return [
        {
            "value": total_schedules,
            "label": "Total Schedules",
            "datatype": "Int",
            "indicator": "blue"
        },
        {
            "value": overdue,
            "label": "Overdue",
            "datatype": "Int",
            "indicator": "red"
        },
        {
            "value": due_this_week,
            "label": "Due This Week",
            "datatype": "Int",
            "indicator": "orange"
        },
        {
            "value": due_this_month,
            "label": "Due This Month",
            "datatype": "Int",
            "indicator": "yellow"
        },
        {
            "value": total_cost,
            "label": "Total Estimated Cost",
            "datatype": "Currency",
            "indicator": "blue"
        }
    ]

