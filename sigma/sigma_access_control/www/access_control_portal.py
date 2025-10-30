# sigma/sigma/sigma_access_control/www/access_control_portal.py
import frappe

def get_context(context):
    context.title = "Access Control Portal"
    context.access_events = frappe.get_all(
        "Access Event",
        order_by="timestamp desc",
        limit=50,
        fields=["employee", "access_point", "result", "timestamp", "card_id"]
    )
    return context