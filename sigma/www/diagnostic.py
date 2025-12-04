import frappe

def get_context(context):
    """
    Context for diagnostic page
    """
    context.no_cache = 1
    context.show_sidebar = False
    
    # Check if user is logged in
    if frappe.session.user == "Guest":
        frappe.throw("Please login to access this page", frappe.PermissionError)
    
    return context

