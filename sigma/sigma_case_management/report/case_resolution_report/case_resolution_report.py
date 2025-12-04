# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import date_diff, getdate


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "name", "label": _("Case ID"), "fieldtype": "Link", "options": "Case", "width": 140},
        {"fieldname": "case_title", "label": _("Title"), "fieldtype": "Data", "width": 200},
        {"fieldname": "case_type", "label": _("Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "severity", "label": _("Severity"), "fieldtype": "Link", "options": "Case Severity Matrix", "width": 100},
        {"fieldname": "status", "label": _("Status"), "fieldtype": "Data", "width": 100},
        {"fieldname": "resolution_type", "label": _("Resolution Type"), "fieldtype": "Data", "width": 120},
        {"fieldname": "date_reported", "label": _("Reported"), "fieldtype": "Date", "width": 100},
        {"fieldname": "actual_closure_date", "label": _("Closed"), "fieldtype": "Date", "width": 100},
        {"fieldname": "resolution_days", "label": _("Days to Resolve"), "fieldtype": "Int", "width": 100},
        {"fieldname": "assigned_case_manager", "label": _("Case Manager"), "fieldtype": "Link", "options": "User", "width": 150},
        {"fieldname": "outcome_notes", "label": _("Outcome"), "fieldtype": "Data", "width": 200},
    ]


def get_data(filters):
    conditions = get_conditions(filters)
    
    data = frappe.db.sql(f"""
        SELECT
            c.name,
            c.case_title,
            c.case_type,
            c.severity,
            c.status,
            c.date_reported,
            c.actual_closure_date,
            c.assigned_case_manager,
            c.resolution_type,
            c.outcome_notes
        FROM `tabCase` c
        WHERE c.docstatus < 2
        AND c.status IN ('Closed', 'Resolved', 'Rejected')
        {conditions}
        ORDER BY c.actual_closure_date DESC
    """, filters, as_dict=1)
    
    for row in data:
        if row.get("date_reported") and row.get("actual_closure_date"):
            row["resolution_days"] = date_diff(row["actual_closure_date"], row["date_reported"])
        else:
            row["resolution_days"] = 0
    
    return data


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("c.actual_closure_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("c.actual_closure_date <= %(to_date)s")
    if filters.get("case_type"):
        conditions.append("c.case_type = %(case_type)s")
    if filters.get("severity"):
        conditions.append("c.severity = %(severity)s")
    if filters.get("assigned_to"):
        conditions.append("c.assigned_case_manager = %(assigned_to)s")
    return " AND " + " AND ".join(conditions) if conditions else ""


def get_chart_data(data):
    if not data:
        return None
    resolution_counts = {}
    for row in data:
        res_type = row.get("resolution_type") or row.get("status") or "Unknown"
        resolution_counts[res_type] = resolution_counts.get(res_type, 0) + 1
    
    return {
        "data": {"labels": list(resolution_counts.keys()), "datasets": [{"name": "Cases by Resolution", "values": list(resolution_counts.values())}]},
        "type": "pie",
        "colors": ["#4CAF50", "#2196F3", "#FFC107", "#F44336", "#9C27B0", "#607D8B"]
    }


def get_summary(data):
    if not data:
        return []
    total = len(data)
    resolved_cases = [d for d in data if d.get("resolution_days")]
    avg_days = sum(d["resolution_days"] for d in resolved_cases) / len(resolved_cases) if resolved_cases else 0
    
    return [
        {"value": total, "indicator": "Blue", "label": "Total Resolved Cases", "datatype": "Int"},
        {"value": round(avg_days, 1), "indicator": "Green", "label": "Avg Days to Resolve", "datatype": "Float"},
    ]

