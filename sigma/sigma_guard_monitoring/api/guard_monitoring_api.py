import frappe
from frappe.utils import now_datetime

@frappe.whitelist()
def create_guard_shift(site_allocation, guard_name, check_in_time=None):
    """Create a new guard shift record."""
    doc = frappe.get_doc({
        "doctype": "Guard Shift",
        "site_allocation": site_allocation,
        "guard_name": guard_name,
        "check_in_time": check_in_time or now_datetime(),
        "status": "Active"
    })
    doc.insert(ignore_permissions=True)
    return doc.name

@frappe.whitelist()
def report_incident(location, category, description, asset=None):
    """Create a guard incident record."""
    incident = frappe.get_doc({
        "doctype": "Guard Incident",
        "location": location,
        "category": category,
        "description": description,
        "asset": asset,
        "reported_on": now_datetime()
    })
    incident.insert(ignore_permissions=True)
    return incident.name
