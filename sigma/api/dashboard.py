# Copyright (c) 2025
# Prismod Technologies Limited
# Sigma Unified Portal Dashboard API

import frappe
from frappe.utils import now_datetime, getdate


def safe_count(doctype: str, filters=None) -> int:
    """
    Safely count records for a Doctype.
    Returns 0 if the Doctype or table does not exist.
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            return 0
        return frappe.db.count(doctype, filters or {})
    except Exception:
        frappe.log_error(f"Failed to count records for {doctype}", "Sigma Home")
        return 0


def safe_grouped_data(doctype: str, group_field: str, label_field: str = None):
    """
    Returns grouped counts for a given Doctype and field.
    Example: group_by="status" or "risk_level"
    Returns empty list if Doctype missing or query fails.
    """
    try:
        if not frappe.db.exists("DocType", doctype):
            return []
        records = frappe.db.get_all(
            doctype,
            fields=[f"{group_field} as label", "count(name) as count"],
            group_by=group_field
        )
        return [{"label": r.label or "Unspecified", "count": r.count} for r in records]
    except Exception:
        frappe.log_error(f"Failed to group data for {doctype}", "Sigma Home")
        return []


@frappe.whitelist(allow_guest=True)
def get_dashboard_data():
    """Fetch Sigma KPIs and chart data for the unified portal dashboard."""

    # --- KPI Summary
    data = {
        # Legacy fields
        "open_calls": safe_count("Call Log", {"status": "Open"}),
        "open_tickets": safe_count("Issue", {"status": "Open"}),
        "active_guards": safe_count("Guard Shift", {"status": "Active"}),
        "pending_cases": safe_count("Case", {"status": "Open"}),
        "access_events_today": safe_count("Access Event", {"creation": [">", getdate(now_datetime())]}),
        "open_risks": safe_count("Risk Assessment", {"status": "Pending"}),

        # Enhanced dashboard fields
        "open_cases": safe_count("Case Record", {"status": "Open"}),
        "total_cases": safe_count("Case Record"),
        "denied_access_today": safe_count("Access Event", {
            "creation": [">", getdate(now_datetime())],
            "result": "Denied"
        }),
        "active_visitors": safe_count("Visitor", {"status": "Checked In"}),
        "vehicles_in_premises": safe_count("Vehicle Log", {"status": "In Premises"}),
    }

    # --- Chart: Call Volume (Last 7 Days) using Query Builder for cross-DB compatibility
    try:
        from frappe.query_builder import DocType
        from pypika.functions import Count
        from frappe.query_builder.functions import Date
        from frappe.utils import add_days
        CallLog = DocType("Call Log")
        seven_days_ago = add_days(getdate(now_datetime()), -7)
        q = (
            frappe.qb.from_(CallLog)
            .select(Date(CallLog.creation).as_("day"), Count("*").as_("count"))
            .where(CallLog.creation >= seven_days_ago)
            .groupby(Date(CallLog.creation))
            .orderby(Date(CallLog.creation))
        )
        call_data = q.run(as_dict=True)
        # Ensure day is date object/string
        labels = []
        values = []
        for d in call_data:
            day = d.get("day")
            try:
                label = day.strftime("%d %b")
            except Exception:
                label = str(day)
            labels.append(label)
            values.append(d.get("count", 0))
        data["call_chart"] = {"labels": labels, "values": values}
    except Exception:
        frappe.log_error("Failed to build call_chart", "Sigma Home")
        data["call_chart"] = {"labels": [], "values": []}

    # --- Chart: Case Status Distribution
    case_counts = safe_grouped_data("Case", "status")
    data["case_chart"] = {
        "labels": [d["label"] for d in case_counts],
        "values": [d["count"] for d in case_counts]
    }

    # --- Chart: Guard Activity
    guard_counts = safe_grouped_data("Guard Shift", "status")
    data["guard_chart"] = {
        "labels": [d["label"] for d in guard_counts],
        "values": [d["count"] for d in guard_counts]
    }

    # --- Chart: Risk Levels
    risk_levels = safe_grouped_data("Risk Assessment", "risk_level")
    data["risk_chart"] = {
        "labels": [d["label"] for d in risk_levels],
        "values": [d["count"] for d in risk_levels]
    }

    # --- Recent Activities
    data["activities"] = get_recent_activities()

    return {"data": data, "activities": data.get("activities", [])}


@frappe.whitelist()
def get_recent_activities(limit=10):
    """Get recent system activities for dashboard"""
    activities = []

    try:
        # Recent access events
        access_events = frappe.db.get_all(
            "Access Event",
            fields=["name", "creation", "result", "access_point"],
            order_by="creation desc",
            limit=limit // 2
        )

        for event in access_events:
            activities.append({
                "id": event.name,
                "type": "success" if event.result == "Granted" else "warning",
                "icon": "ti ti-lock-open" if event.result == "Granted" else "ti ti-lock",
                "text": f"Access {event.result} at {event.access_point}",
                "timestamp": event.creation
            })

        # Recent case updates
        cases = frappe.db.get_all(
            "Case Record",
            fields=["name", "creation", "title", "status"],
            order_by="creation desc",
            limit=limit // 2
        )

        for case in cases:
            activities.append({
                "id": case.name,
                "type": "info",
                "icon": "ti ti-file-text",
                "text": f"Case {case.name}: {case.title}",
                "timestamp": case.creation
            })

        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)

    except Exception as e:
        frappe.log_error(f"Failed to get recent activities: {str(e)}", "Dashboard API")

    return activities[:limit]


@frappe.whitelist()
def get_top_locations(limit=5):
    """Get top locations by access events"""
    try:
        locations = frappe.db.sql("""
            SELECT
                access_point as name,
                COUNT(*) as events
            FROM `tabAccess Event`
            WHERE creation >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY access_point
            ORDER BY events DESC
            LIMIT %s
        """, (limit,), as_dict=True)

        # Calculate percentages
        if locations:
            max_events = locations[0].events
            for loc in locations:
                loc["percentage"] = int((loc.events / max_events) * 100)

        return locations
    except Exception as e:
        frappe.log_error(f"Failed to get top locations: {str(e)}", "Dashboard API")
        return []


@frappe.whitelist()
def get_guard_performance(limit=5):
    """Get top performing guards"""
    try:
        guards = frappe.db.sql("""
            SELECT
                g.name,
                g.guard_name as name,
                g.user_image as avatar,
                COUNT(DISTINCT gs.name) as completed,
                SUM(TIMESTAMPDIFF(HOUR, gs.start_time, gs.end_time)) as hours,
                AVG(gs.performance_score) as score
            FROM `tabGuard` g
            LEFT JOIN `tabGuard Shift` gs ON gs.guard = g.name
            WHERE gs.creation >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY g.name
            ORDER BY score DESC
            LIMIT %s
        """, (limit,), as_dict=True)

        for guard in guards:
            guard["score"] = int(guard.get("score") or 85)
            guard["hours"] = int(guard.get("hours") or 0)
            guard["avatar"] = guard.get("avatar") or "/assets/frappe/images/default-avatar.png"

        return guards
    except Exception as e:
        frappe.log_error(f"Failed to get guard performance: {str(e)}", "Dashboard API")
        return []


@frappe.whitelist()
def get_recent_cases(limit=5):
    """Get recent cases for dashboard widget"""
    try:
        cases = frappe.db.get_all(
            "Case Record",
            fields=["name", "title", "priority", "status", "creation"],
            order_by="creation desc",
            limit=limit
        )

        return [{
            "id": case.name,
            "title": case.title,
            "priority": case.priority,
            "status": case.status,
            "created": case.creation
        } for case in cases]
    except Exception as e:
        frappe.log_error(f"Failed to get recent cases: {str(e)}", "Dashboard API")
        return []
