"""
Sigma API Endpoints
Webhook receivers and integration endpoints
"""

import frappe
import json
from frappe import _
from frappe.utils import now
from frappe import whitelist
from sigma.api.integrations import WebhookHandler, TelemetryNormalizer, NotificationService
from sigma.fix_workspace_content import fix_workspace_content, fix_vehicle_management_workspace

@whitelist(allow_guest=True)
def receive_access_event_webhook():
    """
    Receive access control event webhook
    POST /api/method/sigma.sigma.api.receive_access_event_webhook
    """
    try:
        # Get request data
        data = frappe.request.get_json()
        signature = frappe.request.headers.get("X-Signature")

        # Verify signature if provided
        if signature:
            integration = frappe.get_doc("Integration Settings", "Access Control Webhook")
            payload = frappe.request.get_data(as_text=True)
            if not WebhookHandler.verify_signature(payload, signature, integration.api_secret):
                return {"status": "error", "message": "Invalid signature"}

        # Process webhook
        result = WebhookHandler.process_access_event_webhook(data)
        return result
    except Exception as e:
        frappe.logger().error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist(allow_guest=True)
def receive_telemetry_webhook():
    """
    Receive telemetry/sensor data webhook
    POST /api/method/sigma.sigma.api.receive_telemetry_webhook
    """
    try:
        data = frappe.request.get_json()
        signature = frappe.request.headers.get("X-Signature")

        if signature:
            integration = frappe.get_doc("Integration Settings", "Telemetry Webhook")
            payload = frappe.request.get_data(as_text=True)
            if not WebhookHandler.verify_signature(payload, signature, integration.api_secret):
                return {"status": "error", "message": "Invalid signature"}

        result = WebhookHandler.process_telemetry_webhook(data)
        return result
    except Exception as e:
        frappe.logger().error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist(allow_guest=True)
def receive_guard_activity_webhook():
    """
    Receive guard activity webhook (GPS, check-in, etc.)
    POST /api/method/sigma.sigma.api.receive_guard_activity_webhook
    """
    try:
        data = frappe.request.get_json()
        signature = frappe.request.headers.get("X-Signature")

        if signature:
            integration = frappe.get_doc("Integration Settings", "Guard Activity Webhook")
            payload = frappe.request.get_data(as_text=True)
            if not WebhookHandler.verify_signature(payload, signature, integration.api_secret):
                return {"status": "error", "message": "Invalid signature"}

        result = WebhookHandler.process_guard_activity_webhook(data)
        return result
    except Exception as e:
        frappe.logger().error(f"Webhook error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist()
def get_dashboard_data():
    """
    Get dashboard data with KPIs and metrics
    GET /api/method/sigma.api.api.get_dashboard_data
    """
    try:
        from frappe.utils import getdate
        today = getdate()

        # Get metrics (align with existing DocTypes/fields)
        total_cases = frappe.db.count("Case Record")
        open_cases = frappe.db.count("Case Record", filters={"status": "Open"})
        access_events_today = frappe.db.count(
            "Access Event",
            filters={"timestamp": [">=", today]}
        )
        denied_access_today = frappe.db.count(
            "Access Event",
            filters={"timestamp": [">=", today], "result": "Denied"}
        )
        # Use Guard Shift (status Active) as proxy for active guards
        active_guards = frappe.db.count("Guard Shift", filters={"status": "Active"}) if frappe.db.exists("DocType", "Guard Shift") else 0

        return {
            "status": "success",
            "data": {
                "total_cases": total_cases,
                "open_cases": open_cases,
                "access_events_today": access_events_today,
                "denied_access_today": denied_access_today,
                "active_guards": active_guards,
                "timestamp": now()
            }
        }
    except Exception as e:
        frappe.logger().error(f"Dashboard error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist()
def get_case_details(case_id):
    """
    Get detailed case information
    GET /api/method/sigma.sigma.api.get_case_details?case_id=CASE-001
    """
    try:
        case = frappe.get_doc("Case Record", case_id)

        # Get timeline
        timeline = frappe.get_list(
            "Case Timeline",
            filters={"case_id": case_id},
            order_by="timestamp desc"
        )

        # Get evidence
        evidence = frappe.get_list(
            "Case Evidence",
            filters={"case_id": case_id}
        )

        return {
            "status": "success",
            "case": case.as_dict(),
            "timeline": timeline,
            "evidence": evidence
        }
    except Exception as e:
        frappe.logger().error(f"Case details error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist()
def get_guard_tracking(guard_id):
    """
    Get guard real-time tracking data
    GET /api/method/sigma.sigma.api.get_guard_tracking?guard_id=GUARD-001
    """
    try:
        # Get latest activity
        latest_activity = frappe.get_list(
            "Guard Activity",
            filters={"guard_id": guard_id},
            order_by="timestamp desc",
            limit=1
        )

        # Get current shift
        from frappe.utils import getdate
        today = getdate()
        current_shift = frappe.get_list(
            "Guard Shift",
            filters={"guard_id": guard_id, "shift_date": today},
            limit=1
        )

        return {
            "status": "success",
            "guard_id": guard_id,
            "latest_activity": latest_activity[0] if latest_activity else None,
            "current_shift": current_shift[0] if current_shift else None
        }
    except Exception as e:
        frappe.logger().error(f"Guard tracking error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist()
def get_access_report(report_date=None):
    """
    Get access control report
    GET /api/method/sigma.sigma.api.get_access_report?report_date=2024-10-19
    """
    try:
        from frappe.utils import getdate
        if not report_date:
            report_date = getdate()

        report = frappe.get_list(
            "Access Report",
            filters={"report_date": report_date},
            limit=1
        )

        if report:
            return {"status": "success", "report": report[0]}
        else:
            return {"status": "not_found", "message": "No report for this date"}
    except Exception as e:
        frappe.logger().error(f"Report error: {str(e)}")
        return {"status": "error", "message": str(e)}

@whitelist()
def get_risk_heatmap():
    """
    Get risk assessment heatmap data
    GET /api/method/sigma.sigma.api.get_risk_heatmap
    """
    try:
        risks = frappe.get_list(
            "Risk Assessment",
            fields=["name", "title", "likelihood_score", "impact_score", "risk_score", "status"],
            order_by="risk_score desc"
        )

        return {
            "status": "success",
            "risks": risks,
            "total_risks": len(risks),
            "critical_risks": len([r for r in risks if r.get("risk_score", 0) >= 20])
        }
    except Exception as e:
        frappe.logger().error(f"Heatmap error: {str(e)}")
        return {"status": "error", "message": str(e)}


@whitelist()
def create_helpdesk_ticket_from_call_log(call_log_name: str):
    """Create an HD Ticket from a Call Log and link both ways if custom fields exist."""
    try:
        cl = frappe.get_doc("Call Log", call_log_name)
        subject = f"Call from {getattr(cl, 'caller_id', '') or 'Unknown'}"
        description = getattr(cl, 'description', None) or f"Auto-created from Call Log {cl.name}"

        # Create Helpdesk Ticket
        ticket = frappe.new_doc("HD Ticket")
        meta = frappe.get_meta("HD Ticket")
        if meta.has_field("subject"):
            ticket.subject = subject
        if meta.has_field("description"):
            ticket.description = description
        ticket.insert(ignore_permissions=True)

        # Link back to Call Log if field exists
        if frappe.db.has_column("Call Log", "helpdesk_ticket"):
            frappe.db.set_value("Call Log", cl.name, "helpdesk_ticket", ticket.name)
        # Optional reverse links on HD Ticket if custom fields exist
        if frappe.db.has_column("HD Ticket", "sigma_case") and getattr(cl, 'linked_case', None):
            frappe.db.set_value("HD Ticket", ticket.name, "sigma_case", cl.linked_case)
        if frappe.db.has_column("HD Ticket", "call_log"):
            frappe.db.set_value("HD Ticket", ticket.name, "call_log", cl.name)

        frappe.db.commit()
        return {"ticket": ticket.name}
    except Exception as e:
        frappe.logger().error(f"Create HD Ticket failed: {e}")
        return {"error": str(e)}


@whitelist()
def fix_all_workspaces():
    """
    Fix all Sigma workspaces by rebuilding their content fields
    GET /api/method/sigma.api.api.fix_all_workspaces
    """
    try:
        results = []

        # Standard workspaces with shortcuts
        workspaces_to_fix = [
            'Sigma',
            'Risk Assessment',
            'Assets & Inventory',
            'Acquisition (Buying)',
            'Disposal (Selling)'
        ]

        for workspace_name in workspaces_to_fix:
            if frappe.db.exists('Workspace', workspace_name):
                try:
                    success = fix_workspace_content(workspace_name)
                    results.append({
                        "workspace": workspace_name,
                        "status": "success" if success else "failed",
                        "message": "Content field updated" if success else "Update failed"
                    })
                except Exception as e:
                    results.append({
                        "workspace": workspace_name,
                        "status": "error",
                        "message": str(e)
                    })
            else:
                results.append({
                    "workspace": workspace_name,
                    "status": "skipped",
                    "message": "Workspace does not exist"
                })

        # Fix Vehicle Management separately (has links instead of shortcuts)
        if frappe.db.exists('Workspace', 'Vehicle Management'):
            try:
                success = fix_vehicle_management_workspace()
                results.append({
                    "workspace": "Vehicle Management",
                    "status": "success" if success else "failed",
                    "message": "Content field updated" if success else "Update failed"
                })
            except Exception as e:
                results.append({
                    "workspace": "Vehicle Management",
                    "status": "error",
                    "message": str(e)
                })

        frappe.db.commit()

        return {
            "status": "completed",
            "results": results,
            "total": len(results),
            "successful": len([r for r in results if r["status"] == "success"])
        }
    except Exception as e:
        frappe.logger().error(f"Fix workspaces failed: {e}")
        return {"status": "error", "message": str(e)}


@whitelist()
def get_workspace_status():
    """
    Get status of all Sigma workspaces
    GET /api/method/sigma.api.api.get_workspace_status
    """
    try:
        workspaces = [
            'Sigma',
            'Risk Assessment',
            'Assets & Inventory',
            'Acquisition (Buying)',
            'Disposal (Selling)',
            'Vehicle Management'
        ]

        status_list = []
        for workspace_name in workspaces:
            if frappe.db.exists('Workspace', workspace_name):
                ws = frappe.get_doc('Workspace', workspace_name)
                content_length = len(ws.content) if ws.content else 0

                status_list.append({
                    "name": workspace_name,
                    "exists": True,
                    "shortcuts_count": len(ws.shortcuts) if ws.shortcuts else 0,
                    "links_count": len(ws.links) if ws.links else 0,
                    "number_cards_count": len(ws.number_cards) if ws.number_cards else 0,
                    "content_length": content_length,
                    "has_content": content_length > 0,
                    "needs_fix": content_length < 100 or (len(ws.shortcuts) > 0 and content_length < 500) or (len(ws.links) > 0 and content_length < 500)
                })
            else:
                status_list.append({
                    "name": workspace_name,
                    "exists": False,
                    "needs_fix": False
                })

        return {
            "status": "success",
            "workspaces": status_list,
            "total": len(status_list),
            "needs_fix": len([w for w in status_list if w.get("needs_fix", False)])
        }
    except Exception as e:
        frappe.logger().error(f"Get workspace status failed: {e}")
        return {"status": "error", "message": str(e)}
