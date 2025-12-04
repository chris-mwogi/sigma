# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, now_datetime


def execute(filters=None):
    """
    Vehicle Movement Report
    Tracks all vehicle check-ins and check-outs with movement analysis
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "name",
            "label": _("ID"),
            "fieldtype": "Link",
            "options": "Vehicle Checkin Checkout",
            "width": 120
        },
        {
            "fieldname": "license_plate",
            "label": _("License Plate"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "visitor_type",
            "label": _("Visitor Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "driver_name",
            "label": _("Driver"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "check_in_time",
            "label": _("Check In"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "check_out_time",
            "label": _("Check Out"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "duration_hours",
            "label": _("Duration (hrs)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 100
        },
        {
            "fieldname": "parking_zone",
            "label": _("Parking Zone"),
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
        }
    ]


def get_data(filters):
    """Get vehicle movement data"""
    conditions = {}

    if filters:
        if filters.get("from_date"):
            conditions["check_in_time"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            conditions["check_in_time"] = ["<=", add_days(filters.get("to_date"), 1)]
        if filters.get("visitor_type"):
            conditions["visitor_type"] = filters.get("visitor_type")

    checkins = frappe.get_all("Vehicle Checkin Checkout",
        filters=conditions,
        fields=["name", "license_plate", "visitor_type", "driver_name",
                "check_in_time", "check_out_time", "parking_zone",
                "purpose", "status"],
        order_by="check_in_time desc",
        limit=500
    )

    data = []
    for checkin in checkins:
        duration = 0
        if checkin.check_in_time:
            end_time = checkin.check_out_time or now_datetime()
            duration = (end_time - checkin.check_in_time).total_seconds() / 3600

        data.append({
            "name": checkin.name,
            "license_plate": checkin.license_plate,
            "visitor_type": checkin.visitor_type,
            "driver_name": checkin.driver_name,
            "check_in_time": checkin.check_in_time,
            "check_out_time": checkin.check_out_time,
            "duration_hours": round(duration, 2),
            "parking_zone": checkin.parking_zone,
            "purpose": checkin.purpose,
            "status": checkin.status or "Active"
        })

    return data


def get_chart_data(data, filters):
    """Generate chart showing vehicle movements by visitor type"""
    type_counts = {}
    for d in data:
        vtype = d.get("visitor_type") or "Unknown"
        type_counts[vtype] = type_counts.get(vtype, 0) + 1

    return {
        "data": {
            "labels": list(type_counts.keys()),
            "datasets": [{"name": "Vehicles", "values": list(type_counts.values())}]
        },
        "type": "pie",
        "colors": ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#F44336"]
    }

