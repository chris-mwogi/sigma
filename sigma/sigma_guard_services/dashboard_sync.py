import json
import os

import frappe


def _load_dashboard_from_file(dashboard_dir_name: str) -> dict:
    """Load dashboard JSON from the sigma_guard_services dashboard folder.

    dashboard_dir_name is something like "executive_security_dashboard" or "soc_dashboard".
    """
    # App root is apps/sigma, then "sigma_guard_services/dashboard/..."
    base_path = frappe.get_app_path("sigma", "sigma_guard_services", "dashboard")
    file_path = os.path.join(base_path, dashboard_dir_name, f"{dashboard_dir_name}.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def sync_executive_and_soc_dashboards() -> None:
    """Synchronise Executive Security & SOC dashboards in the DB with JSON definitions.

    Frappe's built-in dashboard sync only creates dashboards once; afterwards updates to the
    JSON files are not applied automatically. This helper reads our JSON fixtures and updates
    the existing Dashboard records' cards and charts so that what you see in the UI matches
    the current specification in the repo.
    """
    dashboards = [
        "executive_security_dashboard",
        "soc_dashboard",
    ]

    for dirname in dashboards:
        data = _load_dashboard_from_file(dirname)
        name = data.get("name") or data.get("dashboard_name")
        if not name:
            continue

        if not frappe.db.exists("Dashboard", name):
            # If the dashboard does not exist yet, create it directly from JSON
            doc = frappe.get_doc(data)
            doc.insert(ignore_if_duplicate=True)
            continue

        doc = frappe.get_doc("Dashboard", name)

        # Replace cards child table
        doc.cards = []
        for card in data.get("cards", []):
            if isinstance(card, dict) and card.get("card"):
                doc.append("cards", {"card": card["card"]})

        # Replace charts child table
        doc.charts = []
        for chart in data.get("charts", []):
            if isinstance(chart, dict) and chart.get("chart"):
                row = {"chart": chart["chart"]}
                if chart.get("width"):
                    row["width"] = chart["width"]
                doc.append("charts", row)

        # Keep meta fields (module, flags) in sync where provided
        if data.get("dashboard_name"):
            doc.dashboard_name = data["dashboard_name"]
        if data.get("module"):
            doc.module = data["module"]
        if "is_standard" in data:
            doc.is_standard = data["is_standard"]

        doc.save()

    frappe.db.commit()

