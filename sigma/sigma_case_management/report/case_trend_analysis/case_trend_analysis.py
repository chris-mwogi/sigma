# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, add_months, get_first_day, get_last_day, nowdate
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart


def get_columns():
    return [
        {"fieldname": "period", "label": _("Period"), "fieldtype": "Data", "width": 120},
        {"fieldname": "cases_opened", "label": _("Cases Opened"), "fieldtype": "Int", "width": 120},
        {"fieldname": "cases_closed", "label": _("Cases Closed"), "fieldtype": "Int", "width": 120},
        {"fieldname": "net_change", "label": _("Net Change"), "fieldtype": "Int", "width": 100},
        {"fieldname": "high_severity", "label": _("High Severity"), "fieldtype": "Int", "width": 100},
        {"fieldname": "medium_severity", "label": _("Medium Severity"), "fieldtype": "Int", "width": 110},
        {"fieldname": "low_severity", "label": _("Low Severity"), "fieldtype": "Int", "width": 100},
        {"fieldname": "avg_resolution_days", "label": _("Avg Resolution Days"), "fieldtype": "Float", "width": 130},
    ]


def get_data(filters):
    # Default to last 12 months
    to_date = getdate(filters.get("to_date") or nowdate())
    from_date = getdate(filters.get("from_date") or add_months(to_date, -11))
    
    # Get all cases in date range
    cases = frappe.db.sql("""
        SELECT name, date_reported, actual_closure_date, severity, status
        FROM `tabCase`
        WHERE docstatus < 2
        AND (date_reported BETWEEN %s AND %s OR actual_closure_date BETWEEN %s AND %s)
    """, (from_date, to_date, from_date, to_date), as_dict=1)
    
    # Group by month
    monthly_data = defaultdict(lambda: {"opened": 0, "closed": 0, "high": 0, "medium": 0, "low": 0, "resolution_days": []})
    
    for case in cases:
        if case.get("date_reported"):
            month_key = case["date_reported"].strftime("%Y-%m")
            if from_date <= case["date_reported"] <= to_date:
                monthly_data[month_key]["opened"] += 1
                severity = (case.get("severity") or "").lower()
                if "high" in severity or "critical" in severity:
                    monthly_data[month_key]["high"] += 1
                elif "medium" in severity:
                    monthly_data[month_key]["medium"] += 1
                else:
                    monthly_data[month_key]["low"] += 1
        
        if case.get("actual_closure_date"):
            month_key = case["actual_closure_date"].strftime("%Y-%m")
            if from_date <= case["actual_closure_date"] <= to_date:
                monthly_data[month_key]["closed"] += 1
                if case.get("date_reported"):
                    days = (case["actual_closure_date"] - case["date_reported"]).days
                    monthly_data[month_key]["resolution_days"].append(days)
    
    # Convert to list sorted by month
    data = []
    for month_key in sorted(monthly_data.keys()):
        m = monthly_data[month_key]
        avg_days = sum(m["resolution_days"]) / len(m["resolution_days"]) if m["resolution_days"] else 0
        data.append({
            "period": month_key,
            "cases_opened": m["opened"],
            "cases_closed": m["closed"],
            "net_change": m["opened"] - m["closed"],
            "high_severity": m["high"],
            "medium_severity": m["medium"],
            "low_severity": m["low"],
            "avg_resolution_days": round(avg_days, 1)
        })
    
    return data


def get_chart_data(data):
    if not data:
        return None
    
    return {
        "data": {
            "labels": [d["period"] for d in data],
            "datasets": [
                {"name": "Cases Opened", "values": [d["cases_opened"] for d in data]},
                {"name": "Cases Closed", "values": [d["cases_closed"] for d in data]}
            ]
        },
        "type": "line",
        "colors": ["#2196F3", "#4CAF50"]
    }

