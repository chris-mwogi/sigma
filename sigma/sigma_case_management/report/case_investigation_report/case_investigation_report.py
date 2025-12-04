# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate, nowdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "name", "label": _("Investigation ID"), "fieldtype": "Link", "options": "Case Investigation", "width": 150},
        {"fieldname": "investigation_title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "linked_case", "label": _("Case"), "fieldtype": "Link", "options": "Case", "width": 140},
        {"fieldname": "investigation_type", "label": _("Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "priority", "label": _("Priority"), "fieldtype": "Data", "width": 80},
        {"fieldname": "lead_investigator", "label": _("Lead Investigator"), "fieldtype": "Link", "options": "User", "width": 150},
        {"fieldname": "start_date", "label": _("Start Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "target_completion_date", "label": _("Target Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "actual_completion_date", "label": _("Actual Date"), "fieldtype": "Date", "width": 100},
        {"fieldname": "days_elapsed", "label": _("Days Elapsed"), "fieldtype": "Int", "width": 90},
        {"fieldname": "findings_summary", "label": _("Findings"), "fieldtype": "Data", "width": 200},
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            ci.name,
            ci.investigation_title,
            ci.linked_case,
            ci.investigation_type,
            ci.status,
            ci.priority,
            ci.lead_investigator,
            ci.start_date,
            ci.target_completion_date,
            ci.actual_completion_date,
            ci.findings_summary
        FROM `tabCase Investigation` ci
        WHERE ci.docstatus < 2
        {conditions}
        ORDER BY ci.start_date DESC
    """, filters, as_dict=1)
    
    today = getdate(nowdate())
    for row in data:
        if row.get("start_date"):
            end_date = row.get("actual_completion_date") or today
            row["days_elapsed"] = date_diff(end_date, row["start_date"])
        else:
            row["days_elapsed"] = 0
    
    return data


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("ci.start_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("ci.start_date <= %(to_date)s")
    if filters.get("status"):
        conditions.append("ci.status = %(status)s")
    if filters.get("investigation_type"):
        conditions.append("ci.investigation_type = %(investigation_type)s")
    if filters.get("lead_investigator"):
        conditions.append("ci.lead_investigator = %(lead_investigator)s")
    return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
    if not data:
        return None
    status_counts = {}
    for row in data:
        status = row.get("status") or "Unknown"
        status_counts[status] = status_counts.get(status, 0) + 1
    
    return {
        "data": {"labels": list(status_counts.keys()), "datasets": [{"name": "Investigations by Status", "values": list(status_counts.values())}]},
        "type": "donut",
        "colors": ["#4CAF50", "#2196F3", "#FFC107", "#F44336", "#9E9E9E"]
    }


def get_summary(data):
    if not data:
        return []
    total = len(data)
    completed = len([d for d in data if d.get("status") == "Completed"])
    in_progress = len([d for d in data if d.get("status") == "In Progress"])
    
    return [
        {"value": total, "indicator": "Blue", "label": "Total Investigations", "datatype": "Int"},
        {"value": completed, "indicator": "Green", "label": "Completed", "datatype": "Int"},
        {"value": in_progress, "indicator": "Orange", "label": "In Progress", "datatype": "Int"},
    ]

