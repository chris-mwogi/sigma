"""
Sigma Real-time Features
Socket.io event system for real-time updates
"""

import frappe
import json
from frappe import _
from frappe.utils import now

class RealtimeEvents:
    """Handle real-time Socket.io events"""
    
    @staticmethod
    def emit_call_log_event(call_log_doc):
        """Emit call log event to connected clients"""
        try:
            event_data = {
                "type": "call_log",
                "action": "new",
                "data": {
                    "id": call_log_doc.name,
                    "caller_name": call_log_doc.caller_name,
                    "caller_phone": call_log_doc.caller_phone,
                    "severity": call_log_doc.severity,
                    "summary": call_log_doc.summary,
                    "timestamp": str(call_log_doc.creation)
                }
            }
            frappe.publish_realtime("sigma:call_log", event_data)
        except Exception as e:
            frappe.logger().error(f"Failed to emit call log event: {str(e)}")
    
    @staticmethod
    def emit_case_update_event(case_doc):
        """Emit case update event to connected clients"""
        try:
            event_data = {
                "type": "case_record",
                "action": "update",
                "data": {
                    "id": case_doc.name,
                    "title": case_doc.title,
                    "status": case_doc.status,
                    "severity": case_doc.severity,
                    "assigned_to": case_doc.assigned_to,
                    "sla_due_date": str(case_doc.sla_due_date) if case_doc.sla_due_date else None,
                    "timestamp": str(case_doc.modified)
                }
            }
            frappe.publish_realtime("sigma:case_update", event_data)
        except Exception as e:
            frappe.logger().error(f"Failed to emit case update event: {str(e)}")
    
    @staticmethod
    def emit_access_event(access_event_doc):
        """Emit access control event to connected clients"""
        try:
            event_data = {
                "type": "access_event",
                "action": "new",
                "data": {
                    "id": access_event_doc.name,
                    "door": access_event_doc.door,
                    "user_id": access_event_doc.user_id,
                    "result": access_event_doc.result,
                    "severity": access_event_doc.severity,
                    "timestamp": str(access_event_doc.event_time)
                }
            }
            frappe.publish_realtime("sigma:access_event", event_data)
        except Exception as e:
            frappe.logger().error(f"Failed to emit access event: {str(e)}")
    
    @staticmethod
    def emit_guard_location_update(guard_activity_doc):
        """Emit guard location update for real-time tracking"""
        try:
            event_data = {
                "type": "guard_location",
                "action": "update",
                "data": {
                    "guard_id": guard_activity_doc.guard_id,
                    "latitude": guard_activity_doc.gps_latitude,
                    "longitude": guard_activity_doc.gps_longitude,
                    "location": guard_activity_doc.location,
                    "activity_type": guard_activity_doc.activity_type,
                    "timestamp": str(guard_activity_doc.timestamp)
                }
            }
            frappe.publish_realtime("sigma:guard_location", event_data)
        except Exception as e:
            frappe.logger().error(f"Failed to emit guard location: {str(e)}")
    
    @staticmethod
    def emit_alert_notification(alert_type, alert_data):
        """Emit alert notification to connected clients"""
        try:
            event_data = {
                "type": "alert",
                "alert_type": alert_type,
                "severity": alert_data.get("severity", "Medium"),
                "message": alert_data.get("message"),
                "data": alert_data.get("data", {}),
                "timestamp": now()
            }
            frappe.publish_realtime("sigma:alert", event_data)
        except Exception as e:
            frappe.logger().error(f"Failed to emit alert: {str(e)}")

class SLAManager:
    """Manage SLA timers and escalation"""
    
    @staticmethod
    def calculate_sla_due_date(case_doc):
        """Calculate SLA due date based on severity"""
        from frappe.utils import add_hours, getdate
        
        severity_sla_hours = {
            "Critical": 2,
            "High": 4,
            "Medium": 8,
            "Low": 24
        }
        
        sla_hours = severity_sla_hours.get(case_doc.severity, 24)
        case_doc.sla_due_date = add_hours(now(), sla_hours)
    
    @staticmethod
    def check_sla_breaches():
        """Check for SLA breaches and escalate"""
        try:
            from frappe.utils import getdate
            today = getdate()
            
            # Find cases with breached SLA
            breached_cases = frappe.get_list(
                "Case Record",
                filters={
                    "status": ["!=", "Closed"],
                    "sla_due_date": ["<", today]
                }
            )
            
            for case in breached_cases:
                case_doc = frappe.get_doc("Case Record", case.name)
                
                # Escalate
                case_doc.db_set("status", "Pending Review")
                
                # Send notification
                RealtimeEvents.emit_alert_notification(
                    "SLA_BREACH",
                    {
                        "severity": "High",
                        "message": f"SLA breached for case {case.name}",
                        "data": {"case_id": case.name}
                    }
                )
        except Exception as e:
            frappe.logger().error(f"Failed to check SLA breaches: {str(e)}")
    
    @staticmethod
    def send_escalation_notification(case_doc):
        """Send escalation notification"""
        try:
            from frappe.utils import add_hours, getdate
            
            # Check if escalation is needed
            if case_doc.sla_due_date:
                hours_remaining = (case_doc.sla_due_date - now()).total_seconds() / 3600
                
                if hours_remaining < 1:
                    # Critical - escalate to manager
                    RealtimeEvents.emit_alert_notification(
                        "ESCALATION_CRITICAL",
                        {
                            "severity": "Critical",
                            "message": f"Case {case_doc.name} requires immediate attention",
                            "data": {"case_id": case_doc.name}
                        }
                    )
                elif hours_remaining < 4:
                    # Warning - notify assigned user
                    RealtimeEvents.emit_alert_notification(
                        "ESCALATION_WARNING",
                        {
                            "severity": "High",
                            "message": f"Case {case_doc.name} SLA expiring soon",
                            "data": {"case_id": case_doc.name}
                        }
                    )
        except Exception as e:
            frappe.logger().error(f"Failed to send escalation notification: {str(e)}")

class TaskQueue:
    """Background task queue for async operations"""
    
    @staticmethod
    def enqueue_case_creation(call_log_id):
        """Enqueue case creation task"""
        try:
            frappe.enqueue(
                "sigma.sigma.realtime.TaskQueue.create_case_from_call",
                call_log_id=call_log_id,
                queue="default",
                timeout=300
            )
        except Exception as e:
            frappe.logger().error(f"Failed to enqueue task: {str(e)}")
    
    @staticmethod
    def create_case_from_call(call_log_id):
        """Create case from call log (async)"""
        try:
            call_log = frappe.get_doc("Call Log", call_log_id)
            
            case = frappe.new_doc("Case Record")
            case.case_number = f"CASE-{call_log_id}"
            case.title = f"Case from Call: {call_log.caller_name}"
            case.description = call_log.description
            case.severity = call_log.severity
            case.status = "Open"
            case.assigned_to = frappe.session.user
            case.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # Emit event
            RealtimeEvents.emit_case_update_event(case)
        except Exception as e:
            frappe.logger().error(f"Failed to create case: {str(e)}")
    
    @staticmethod
    def enqueue_report_generation(report_date):
        """Enqueue report generation task"""
        try:
            frappe.enqueue(
                "sigma.sigma.realtime.TaskQueue.generate_access_report",
                report_date=report_date,
                queue="default",
                timeout=600
            )
        except Exception as e:
            frappe.logger().error(f"Failed to enqueue report: {str(e)}")
    
    @staticmethod
    def generate_access_report(report_date):
        """Generate access report (async)"""
        try:
            from frappe.utils import getdate
            
            report = frappe.new_doc("Access Report")
            report.report_date = getdate(report_date)
            report.total_events = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", report_date]}
            )
            report.granted_count = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", report_date], "result": "Granted"}
            )
            report.denied_count = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", report_date], "result": "Denied"}
            )
            report.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.logger().error(f"Failed to generate report: {str(e)}")

