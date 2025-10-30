# sigma_access_control_api.py
import frappe
from frappe.utils import now_datetime

# -------------------------------
# Webhook: Receive Access Device Events
# -------------------------------
@frappe.whitelist(allow_guest=True)
def access_event_webhook():
    """
    Receives device events from access control devices.
    
    Payload example:
    {
        "access_point": "Main Gate",
        "employee": "EMP001",
        "card_id": "12345",
        "timestamp": "2025-10-17 08:00:00",
        "result": "Granted",
        "notes": "Optional note"
    }
    """
    data = frappe.local.form_dict

    doc = frappe.get_doc({
        "doctype": "Access Event",
        "access_point": data.get("access_point"),
        "employee": data.get("employee"),
        "card_id": data.get("card_id"),
        "timestamp": data.get("timestamp") or now_datetime(),
        "result": data.get("result") or "Denied",
        "notes": data.get("notes")
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Real-time alert for denied access
    if doc.result == "Denied":
        frappe.publish_realtime(
            "access_event_alert",
            message=f"Access denied at {doc.access_point} for {doc.card_id}",
            user="All"
        )

    return {"status": "success", "event": doc.name}


# -------------------------------
# Doc Event: After Insert
# -------------------------------
def after_access_event_insert(doc, method):
    """
    Triggered via hooks.py after a new Access Event is inserted.
    """
    if doc.result == "Denied":
        frappe.publish_realtime(
            "access_event_alert",
            message=f"Access denied at {doc.access_point} for {doc.card_id}",
            user="All"
        )


# -------------------------------
# Doc Event: On Update
# -------------------------------
def on_access_event_update(doc, method):
    """
    Triggered when Access Event is updated.
    """
    frappe.enqueue(
        "sigma_access_control.sigma_access_control_api.update_daily_stats",
        doc=doc.name
    )


# -------------------------------
# Doc Event: On Delete
# -------------------------------
def on_access_event_delete(doc, method):
    """
    Triggered when Access Event is deleted.
    """
    # Optional cleanup of related logs
    frappe.db.sql(
        "DELETE FROM `tabAccessEventLog` WHERE parent=%s", doc.name
    )


# -------------------------------
# Helper: Update Daily Stats
# -------------------------------
@frappe.whitelist()
def update_daily_stats(doc):
    """
    Queued function to update daily access statistics.
    """
    # Placeholder logic for aggregation
    frappe.msgprint(f"Daily stats updated for {doc}")
