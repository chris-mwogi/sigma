import frappe

@frappe.whitelist()
def get_case_summary():
    open_cases = frappe.db.count("Case", {"status": "Open"})
    resolved = frappe.db.count("Case", {"status": "Resolved"})
    awaiting_legal = frappe.db.count("Case", {"status": "Awaiting Legal"})
    return {"open": open_cases, "resolved": resolved, "awaiting_legal": awaiting_legal}