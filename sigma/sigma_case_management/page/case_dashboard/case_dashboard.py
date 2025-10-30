import frappe

@frappe.whitelist()
def get_case_summary():
    return {
        "open": frappe.db.count("Case", {"status": "Open"}),
        "resolved": frappe.db.count("Case", {"status": "Resolved"}),
        "awaiting_legal": frappe.db.count("Case", {"status": "Awaiting Legal"})
    }
