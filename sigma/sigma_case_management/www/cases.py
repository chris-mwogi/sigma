import frappe

def get_context(context):
    # Pull all cases visible to the logged-in user
    context.cases = frappe.get_all("Case", filters={"owner": frappe.session.user}, fields=["name", "status", "case_type"])
