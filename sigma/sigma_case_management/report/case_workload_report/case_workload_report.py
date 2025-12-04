# Copyright (c) 2025, Mwogi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from collections import defaultdict


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_summary(data)
    
    return columns, data, None, chart, summary


def get_columns():
    return [
        {"fieldname": "case_manager", "label": _("Case Manager"), "fieldtype": "Link", "options": "User", "width": 200},
        {"fieldname": "full_name", "label": _("Name"), "fieldtype": "Data", "width": 150},
        {"fieldname": "active_cases", "label": _("Active Cases"), "fieldtype": "Int", "width": 100},
        {"fieldname": "high_priority", "label": _("High Priority"), "fieldtype": "Int", "width": 100},
        {"fieldname": "overdue_cases", "label": _("Overdue"), "fieldtype": "Int", "width": 80},
        {"fieldname": "cases_closed_month", "label": _("Closed This Month"), "fieldtype": "Int", "width": 120},
        {"fieldname": "total_cases", "label": _("Total Assigned"), "fieldtype": "Int", "width": 110},
        {"fieldname": "avg_resolution_days", "label": _("Avg Resolution Days"), "fieldtype": "Float", "width": 130},
        {"fieldname": "workload_status", "label": _("Workload Status"), "fieldtype": "Data", "width": 120},
    ]


def get_data(filters):
    from frappe.utils import nowdate, get_first_day, getdate, now_datetime
    
    today = getdate(nowdate())
    month_start = get_first_day(today)
    now = now_datetime()
    
    # Get all assigned cases
    cases = frappe.db.sql("""
        SELECT 
            c.assigned_case_manager,
            c.status,
            c.severity,
            c.sla_due_date,
            c.date_reported,
            c.actual_closure_date
        FROM `tabCase` c
        WHERE c.docstatus < 2
        AND c.assigned_case_manager IS NOT NULL
        AND c.assigned_case_manager != ''
    """, as_dict=1)
    
    # Group by case manager
    manager_data = defaultdict(lambda: {
        "active": 0, "high": 0, "overdue": 0, "closed_month": 0, "total": 0, "resolution_days": []
    })
    
    for case in cases:
        mgr = case.get("assigned_case_manager")
        if not mgr:
            continue
        
        manager_data[mgr]["total"] += 1
        
        status = case.get("status") or ""
        if status not in ("Closed", "Resolved", "Rejected"):
            manager_data[mgr]["active"] += 1
            
            severity = (case.get("severity") or "").lower()
            if "high" in severity or "critical" in severity:
                manager_data[mgr]["high"] += 1
            
            sla = case.get("sla_due_date")
            if sla and now > sla:
                manager_data[mgr]["overdue"] += 1
        else:
            closure = case.get("actual_closure_date")
            if closure and closure >= month_start:
                manager_data[mgr]["closed_month"] += 1
            
            if case.get("date_reported") and closure:
                days = (closure - case["date_reported"]).days
                manager_data[mgr]["resolution_days"].append(days)
    
    # Build result with user names
    data = []
    for mgr, stats in manager_data.items():
        user = frappe.db.get_value("User", mgr, "full_name") or mgr
        avg_days = sum(stats["resolution_days"]) / len(stats["resolution_days"]) if stats["resolution_days"] else 0
        
        # Determine workload status
        if stats["active"] > 15 or stats["overdue"] > 3:
            workload = "Overloaded"
        elif stats["active"] > 10:
            workload = "High"
        elif stats["active"] > 5:
            workload = "Normal"
        else:
            workload = "Light"
        
        data.append({
            "case_manager": mgr,
            "full_name": user,
            "active_cases": stats["active"],
            "high_priority": stats["high"],
            "overdue_cases": stats["overdue"],
            "cases_closed_month": stats["closed_month"],
            "total_cases": stats["total"],
            "avg_resolution_days": round(avg_days, 1),
            "workload_status": workload
        })
    
    return sorted(data, key=lambda x: x["active_cases"], reverse=True)


def get_chart_data(data):
    if not data:
        return None
    top_10 = data[:10]
    return {
        "data": {
            "labels": [d["full_name"] for d in top_10],
            "datasets": [
                {"name": "Active Cases", "values": [d["active_cases"] for d in top_10]},
                {"name": "Overdue", "values": [d["overdue_cases"] for d in top_10]}
            ]
        },
        "type": "bar",
        "colors": ["#2196F3", "#F44336"]
    }


def get_summary(data):
    if not data:
        return []
    total_active = sum(d["active_cases"] for d in data)
    total_overdue = sum(d["overdue_cases"] for d in data)
    overloaded = len([d for d in data if d["workload_status"] == "Overloaded"])
    
    return [
        {"value": len(data), "indicator": "Blue", "label": "Total Case Managers", "datatype": "Int"},
        {"value": total_active, "indicator": "Orange", "label": "Total Active Cases", "datatype": "Int"},
        {"value": total_overdue, "indicator": "Red", "label": "Total Overdue Cases", "datatype": "Int"},
        {"value": overloaded, "indicator": "Red" if overloaded else "Green", "label": "Overloaded Staff", "datatype": "Int"},
    ]

