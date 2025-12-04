# Copyright (c) 2025
# Prismod Technologies Limited / Nevel Enterprises
# Sigma Unified Dashboard Controller (Desk Version)

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, getdate


# ---------- Utility Helpers ----------

def safe_count(doctype: str, filters=None) -> int:
    """Safely count records for a Doctype, returning 0 if it doesn't exist or fails."""
    try:
        if not frappe.db.exists("DocType", doctype):
            return 0
        return frappe.db.count(doctype, filters or {})
    except Exception:
        frappe.log_error(f"Count failed for {doctype}", "Sigma Dashboard")
        return 0


def safe_grouped_data(doctype: str, field: str):
    """Safely group records for a Doctype by a field."""
    try:
        if not frappe.db.exists("DocType", doctype):
            return []
        records = frappe.db.get_all(
            doctype,
            fields=[f"{field} as label", "count(name) as count"],
            group_by=field,
        )
        return [{"label": r.label or "Unspecified", "count": r.count} for r in records]
    except Exception:
        frappe.log_error(f"Group data failed for {doctype}", "Sigma Dashboard")
        return []


def build_dashboard_data():
    """Build fresh dashboard KPIs and charts."""
    data = {
        "open_calls": safe_count("Call Log", {"status": "Open"}),
        "open_tickets": safe_count("Issue", {"status": "Open"}),
        "active_guards": safe_count("Guard Shift", {"status": "Active"}),
        "pending_cases": safe_count("Case", {"status": "Open"}),
        "access_events_today": safe_count(
            "Access Event", {"creation": [">", getdate(now_datetime())]}
        ),
        "open_risks": safe_count("Risk Assessment", {"status": "Pending"}),
    }

    # --- Call Volume (last 7 days)
    try:
        call_data = frappe.db.sql(
            """
            SELECT DATE(creation) AS day, COUNT(*) AS count
            FROM `tabCall Log`
            WHERE creation >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(creation)
            ORDER BY DATE(creation)
            """,
            as_dict=True,
        )
        data["call_chart"] = {
            "labels": [d.day.strftime("%d %b") for d in call_data],
            "values": [d.count for d in call_data],
        }
    except Exception:
        data["call_chart"] = {"labels": [], "values": []}

    # --- Case Status
    case_counts = safe_grouped_data("Case", "status")
    data["case_chart"] = {
        "labels": [d["label"] for d in case_counts],
        "values": [d["count"] for d in case_counts],
    }

    # --- Guard Activity
    guards_active = safe_count("Guard Shift", {"status": "Active"})
    guards_inactive = safe_count("Guard Shift", {"status": ["!=", "Active"]})
    data["guard_chart"] = {
        "labels": ["Active", "Inactive"],
        "values": [guards_active, guards_inactive],
    }

    # --- Risk Levels
    risk_levels = safe_grouped_data("Risk Assessment", "risk_level")
    data["risk_chart"] = {
        "labels": [d["label"] for d in risk_levels],
        "values": [d["count"] for d in risk_levels],
    }

    return data


# ---------- Doctype Controller ----------

class SigmaDashboard(Document):
    @frappe.whitelist()
    def get_summary_data(self):
        """Return cached dashboard data for Desk form."""
        cache_key = "sigma_dashboard_cache"
        cached = frappe.cache().get_value(cache_key)
        if cached:
            return cached

        data = build_dashboard_data()
        frappe.cache().set_value(cache_key, data, expires_in_sec=60)
        return data


# ---------- Admin Utility ----------

@frappe.whitelist()
def refresh_cache():
    """Force-refresh the dashboard cache (admin use)."""
    data = build_dashboard_data()
    frappe.cache().set_value("sigma_dashboard_cache", data, expires_in_sec=60)
    frappe.msgprint("Dashboard data refreshed successfully.")
    return data
