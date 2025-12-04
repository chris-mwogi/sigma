# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_days, now_datetime, time_diff_in_seconds


def execute(filters=None):
    """
    Lone Worker Monitoring Report
    Real-time monitoring of lone workers in hazardous zones (ISO 45001 compliance)
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    return columns, data, summary, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "alert_id",
            "label": _("Alert ID"),
            "fieldtype": "Link",
            "options": "Lone Worker Alert",
            "width": 120
        },
        {
            "fieldname": "human",
            "label": _("Personnel"),
            "fieldtype": "Link",
            "options": "Human Profile",
            "width": 150
        },
        {
            "fieldname": "human_name",
            "label": _("Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "zone",
            "label": _("Zone"),
            "fieldtype": "Link",
            "options": "Zone Configuration",
            "width": 150
        },
        {
            "fieldname": "zone_name",
            "label": _("Zone Name"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "alert_type",
            "label": _("Alert Type"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "raised_at",
            "label": _("Raised At"),
            "fieldtype": "Datetime",
            "width": 150
        },
        {
            "fieldname": "severity",
            "label": _("Severity"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "resolution_status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "responder",
            "label": _("Responder"),
            "fieldtype": "Link",
            "options": "User",
            "width": 120
        },
        {
            "fieldname": "escalation_level",
            "label": _("Escalation Level"),
            "fieldtype": "Int",
            "width": 100
        }
    ]


def get_data(filters):
    """Get lone worker alert data"""
    conditions = {}

    if filters:
        if filters.get("from_date"):
            conditions["raised_at"] = [">=", filters.get("from_date")]
        if filters.get("to_date"):
            conditions["raised_at"] = ["<=", add_days(filters.get("to_date"), 1)]
        if filters.get("resolution_status"):
            conditions["resolution_status"] = filters.get("resolution_status")
        if filters.get("severity"):
            conditions["severity"] = filters.get("severity")

    alerts = frappe.get_all("Lone Worker Alert",
        filters=conditions,
        fields=["name", "human", "zone", "alert_type", "raised_at",
                "severity", "resolution_status", "responder", "escalation_level"],
        order_by="raised_at desc",
        limit=500
    )

    data = []
    for alert in alerts:
        # Get human name
        human_name = frappe.db.get_value("Human Profile", alert.human, "full_name") or ""

        # Get zone details
        zone_data = frappe.db.get_value("Zone Configuration", alert.zone,
            ["zone_name", "hazard_level"], as_dict=True) or {}

        data.append({
            "alert_id": alert.name,
            "human": alert.human,
            "human_name": human_name,
            "zone": alert.zone,
            "zone_name": zone_data.get("zone_name", ""),
            "alert_type": alert.alert_type,
            "raised_at": alert.raised_at,
            "severity": alert.severity,
            "resolution_status": alert.resolution_status,
            "responder": alert.responder,
            "escalation_level": alert.escalation_level or 0
        })

    return data


def get_chart_data(data):
    """Generate chart showing alerts by status"""
    status_counts = {}
    for d in data:
        status = d.get("resolution_status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1

    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"name": "Alerts", "values": list(status_counts.values())}]
        },
        "type": "donut",
        "colors": ["#F44336", "#FF9800", "#4CAF50", "#2196F3"]
    }


def get_summary(data):
    """Generate summary message"""
    if not data:
        return "No lone worker alerts in the selected period."

    pending = sum(1 for d in data if d.get("resolution_status") == "Pending")
    resolved = sum(1 for d in data if d.get("resolution_status") == "Resolved")

    return f"Total Alerts: {len(data)} | Pending: {pending} | Resolved: {resolved}"

