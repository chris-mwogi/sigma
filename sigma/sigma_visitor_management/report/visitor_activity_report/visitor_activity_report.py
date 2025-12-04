# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, now_datetime


def execute(filters=None):
    """
    Visitor Activity Report
    Comprehensive visitor tracking and activity analysis
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "name",
            "label": _("Registration ID"),
            "fieldtype": "Link",
            "options": "Visitor Registration",
            "width": 120
        },
        {
            "fieldname": "visitor_name",
            "label": _("Visitor Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "visitor_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "expected_arrival_date",
            "label": _("Expected Arrival"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "registration_date",
            "label": _("Registration Date"),
            "fieldtype": "Date",
            "width": 120
        },
        {
            "fieldname": "host_employee",
            "label": _("Host"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 150
        },
        {
            "fieldname": "host_department",
            "label": _("Department"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "purpose",
            "label": _("Purpose"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "risk_band",
            "label": _("Risk"),
            "fieldtype": "Data",
            "width": 80
        }
    ]


def get_data(filters):
    """Get visitor activity data"""
    conditions = {}

    if filters:
        if filters.get("from_date"):
            conditions["expected_arrival_date"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            conditions["expected_arrival_date"] = ["<=", filters.get("to_date")]
        if filters.get("visitor_type"):
            conditions["visitor_type"] = filters.get("visitor_type")

    registrations = frappe.get_all("Visitor Registration",
        filters=conditions,
        fields=["name", "visitor", "visitor_type", "expected_arrival_date",
                "registration_date", "host_employee", "host_department",
                "purpose_of_visit", "status", "risk_band"],
        order_by="expected_arrival_date desc",
        limit=500
    )

    data = []
    for reg in registrations:
        # Get visitor name
        visitor_name = ""
        if reg.visitor:
            visitor_doc = frappe.db.get_value("Visitor", reg.visitor,
                ["first_name", "last_name"], as_dict=True)
            if visitor_doc:
                visitor_name = f"{visitor_doc.first_name or ''} {visitor_doc.last_name or ''}".strip()

        data.append({
            "name": reg.name,
            "visitor_name": visitor_name,
            "visitor_type": reg.visitor_type,
            "expected_arrival_date": reg.expected_arrival_date,
            "registration_date": reg.registration_date,
            "host_employee": reg.host_employee,
            "host_department": reg.host_department,
            "purpose": reg.purpose_of_visit,
            "status": reg.status,
            "risk_band": reg.risk_band or "Low"
        })

    return data


def get_chart_data(data):
    """Generate chart showing visitors by type"""
    type_counts = {}
    for d in data:
        vtype = d.get("visitor_type") or "Unknown"
        type_counts[vtype] = type_counts.get(vtype, 0) + 1
    
    return {
        "data": {
            "labels": list(type_counts.keys()),
            "datasets": [{"name": "Visitors", "values": list(type_counts.values())}]
        },
        "type": "donut",
        "colors": ["#2196F3", "#4CAF50", "#FF9800", "#9C27B0", "#F44336"]
    }

