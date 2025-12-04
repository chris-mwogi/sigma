# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters=None):
    """Execute Vendor Performance Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    """Define report columns"""
    return [
        {"fieldname": "vendor", "label": _("Vendor"), "fieldtype": "Link", "options": "Asset Vendor", "width": 180},
        {"fieldname": "vendor_code", "label": _("Vendor Code"), "fieldtype": "Data", "width": 120},
        {"fieldname": "vendor_type", "label": _("Type"), "fieldtype": "Data", "width": 130},
        {"fieldname": "vendor_status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "vendor_rating", "label": _("Rating"), "fieldtype": "Float", "width": 80},
        {"fieldname": "total_contracts", "label": _("Contracts"), "fieldtype": "Int", "width": 90},
        {"fieldname": "on_time_delivery_rate", "label": _("On-Time Delivery"), "fieldtype": "Percent", "width": 130},
        {"fieldname": "quality_rating", "label": _("Quality"), "fieldtype": "Float", "width": 80},
        {"fieldname": "response_time_hours", "label": _("Response Time (Hrs)"), "fieldtype": "Float", "width": 140},
        {"fieldname": "defect_rate", "label": _("Defect Rate"), "fieldtype": "Percent", "width": 100}
    ]


def get_data(filters):
    """Get report data"""
    conditions = []
    if filters.get("vendor_status"):
        conditions.append("AND av.vendor_status = %(vendor_status)s")
    if filters.get("vendor_type"):
        conditions.append("AND av.vendor_type = %(vendor_type)s")
    
    conditions_str = " ".join(conditions)
    
    data = frappe.db.sql(f"""
        SELECT
            av.name as vendor,
            av.vendor_code,
            av.vendor_type,
            av.vendor_status,
            av.vendor_rating,
            av.total_contracts,
            av.on_time_delivery_rate,
            av.quality_rating,
            av.response_time_hours,
            av.defect_rate
        FROM
            `tabAsset Vendor` av
        WHERE
            1=1
            {conditions_str}
        ORDER BY
            av.vendor_rating DESC,
            av.on_time_delivery_rate DESC
    """, filters, as_dict=1)
    
    return data


def get_chart_data(data):
    """Generate chart data"""
    vendor_names = [d.get("vendor") for d in data[:10]]  # Top 10 vendors
    vendor_ratings = [d.get("vendor_rating", 0) for d in data[:10]]
    
    return {
        "data": {
            "labels": vendor_names,
            "datasets": [{"name": "Vendor Rating", "values": vendor_ratings}]
        },
        "type": "bar"
    }


def get_summary(data):
    """Generate summary statistics"""
    total_vendors = len(data)
    active_vendors = len([d for d in data if d.get("vendor_status") == "Active"])
    avg_rating = sum([d.get("vendor_rating", 0) for d in data]) / total_vendors if total_vendors > 0 else 0
    avg_on_time = sum([d.get("on_time_delivery_rate", 0) for d in data]) / total_vendors if total_vendors > 0 else 0
    
    return [
        {"value": total_vendors, "label": "Total Vendors", "datatype": "Int", "indicator": "blue"},
        {"value": active_vendors, "label": "Active Vendors", "datatype": "Int", "indicator": "green"},
        {"value": round(avg_rating, 2), "label": "Average Rating", "datatype": "Float", "indicator": "blue"},
        {"value": round(avg_on_time, 2), "label": "Avg On-Time Delivery %", "datatype": "Float", "indicator": "green"}
    ]

