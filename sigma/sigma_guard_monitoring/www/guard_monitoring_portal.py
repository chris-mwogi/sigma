import frappe

def get_context(context):
    # This function provides data to your portal page template
    context.locations = frappe.get_all("Location", fields=["name", "location_name"])
    context.incidents = frappe.get_all("Case Incident", fields=["name", "category", "location", "reported_on"])
    return context
