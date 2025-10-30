"""
Sigma Asset Integrations Module
Handles webhook ingestion, telemetry normalization, and outbound notifications
"""

import frappe
import json
import hmac
import hashlib
from frappe import _
from frappe.utils import now

class WebhookHandler:
    """Handle incoming webhooks from external systems"""
    
    @staticmethod
    def verify_signature(payload, signature, secret):
        """Verify HMAC-SHA256 signature"""
        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def process_access_event_webhook(payload):
        """Process access control event webhook"""
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            
            # Create Access Event
            event = frappe.new_doc("Access Event")
            event.event_time = data.get("timestamp", now())
            event.door = data.get("door_id")
            event.user_id = data.get("user_id")
            event.result = data.get("result", "Unknown")  # Granted, Denied, Timeout
            event.device_id = data.get("device_id")
            event.severity = "High" if event.result == "Denied" else "Low"
            event.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # Log webhook
            WebhookHandler.log_webhook("Access Event", payload, "Success")
            return {"status": "success", "event_id": event.name}
        except Exception as e:
            WebhookHandler.log_webhook("Access Event", payload, f"Failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def process_telemetry_webhook(payload):
        """Process telemetry/sensor data webhook"""
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            
            # Create Telemetry Data
            telemetry = frappe.new_doc("Telemetry Data")
            telemetry.device_id = data.get("device_id")
            telemetry.data_type = data.get("data_type", "Other")
            telemetry.value = data.get("value")
            telemetry.unit = data.get("unit")
            telemetry.timestamp = data.get("timestamp", now())
            telemetry.source = data.get("source", "Webhook")
            telemetry.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # Log webhook
            WebhookHandler.log_webhook("Telemetry Data", payload, "Success")
            return {"status": "success", "telemetry_id": telemetry.name}
        except Exception as e:
            WebhookHandler.log_webhook("Telemetry Data", payload, f"Failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def process_guard_activity_webhook(payload):
        """Process guard activity webhook (GPS, check-in, etc.)"""
        try:
            data = json.loads(payload) if isinstance(payload, str) else payload
            
            # Create Guard Activity
            activity = frappe.new_doc("Guard Activity")
            activity.guard_id = data.get("guard_id")
            activity.activity_type = data.get("activity_type", "Other")
            activity.timestamp = data.get("timestamp", now())
            activity.location = data.get("location")
            activity.gps_latitude = data.get("latitude")
            activity.gps_longitude = data.get("longitude")
            activity.notes = data.get("notes")
            activity.insert(ignore_permissions=True)
            frappe.db.commit()
            
            # Log webhook
            WebhookHandler.log_webhook("Guard Activity", payload, "Success")
            return {"status": "success", "activity_id": activity.name}
        except Exception as e:
            WebhookHandler.log_webhook("Guard Activity", payload, f"Failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def log_webhook(webhook_type, payload, status):
        """Log webhook for audit trail"""
        try:
            log = frappe.new_doc("Webhook Log")
            log.webhook_id = f"{webhook_type}-{now()}"
            log.integration_name = webhook_type
            log.payload = payload if isinstance(payload, str) else json.dumps(payload)
            log.status = "Success" if "Success" in status else "Failed"
            log.response = status
            log.timestamp = now()
            log.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.logger().error(f"Failed to log webhook: {str(e)}")

class TelemetryNormalizer:
    """Normalize telemetry data from different vendors"""
    
    @staticmethod
    def normalize_opmanager_data(vendor_payload):
        """Normalize OpManager telemetry"""
        return {
            "device_id": vendor_payload.get("deviceId"),
            "data_type": vendor_payload.get("metricType"),
            "value": vendor_payload.get("metricValue"),
            "unit": vendor_payload.get("unit"),
            "timestamp": vendor_payload.get("timestamp"),
            "source": "OpManager"
        }
    
    @staticmethod
    def normalize_jimiiot_data(vendor_payload):
        """Normalize JimiIOT telemetry"""
        return {
            "device_id": vendor_payload.get("imei"),
            "data_type": "GPS" if "latitude" in vendor_payload else "Sensor",
            "value": vendor_payload.get("value") or f"{vendor_payload.get('latitude')},{vendor_payload.get('longitude')}",
            "unit": vendor_payload.get("unit"),
            "timestamp": vendor_payload.get("time"),
            "source": "JimiIOT"
        }
    
    @staticmethod
    def normalize_holykell_data(vendor_payload):
        """Normalize Holykell telemetry"""
        return {
            "device_id": vendor_payload.get("deviceCode"),
            "data_type": vendor_payload.get("sensorType"),
            "value": vendor_payload.get("sensorValue"),
            "unit": vendor_payload.get("unit"),
            "timestamp": vendor_payload.get("recordTime"),
            "source": "Holykell"
        }

class NotificationService:
    """Handle outbound notifications"""
    
    @staticmethod
    def send_email_notification(recipient, subject, message):
        """Send email notification"""
        try:
            frappe.sendmail(
                recipients=[recipient],
                subject=subject,
                message=message,
                delayed=False
            )
            return True
        except Exception as e:
            frappe.logger().error(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_notification(phone, message):
        """Send SMS notification (requires SMS gateway integration)"""
        try:
            # This would integrate with SMS gateway like Twilio, AWS SNS, etc.
            frappe.logger().info(f"SMS to {phone}: {message}")
            return True
        except Exception as e:
            frappe.logger().error(f"Failed to send SMS: {str(e)}")
            return False
    
    @staticmethod
    def send_push_notification(user, title, message):
        """Send push notification"""
        try:
            # This would integrate with push notification service
            frappe.logger().info(f"Push to {user}: {title} - {message}")
            return True
        except Exception as e:
            frappe.logger().error(f"Failed to send push: {str(e)}")
            return False
    
    @staticmethod
    def send_webhook_notification(webhook_url, payload):
        """Send outbound webhook notification"""
        try:
            import requests
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            frappe.logger().error(f"Failed to send webhook: {str(e)}")
            return False

class ScheduledJobs:
    """Scheduled background jobs for integrations"""

    @staticmethod
    def poll_vendor_apis():
        """Poll external vendor APIs for data"""
        try:
            # Get all active integration settings
            integrations = frappe.get_list(
                "Integration Settings",
                filters={"status": "Active", "integration_type": "Scheduled Poll"}
            )

            for integration in integrations:
                frappe.logger().info(f"Polling {integration.integration_name}")
                # Implementation would depend on specific vendor API
        except Exception as e:
            frappe.logger().error(f"Failed to poll APIs: {str(e)}")

    @staticmethod
    def generate_reports():
        """Generate scheduled reports"""
        try:
            # Generate access reports
            from frappe.utils import getdate, add_days
            today = getdate()

            report = frappe.new_doc("Access Report")
            report.report_date = today
            report.total_events = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", today]}
            )
            report.granted_count = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", today], "result": "Granted"}
            )
            report.denied_count = frappe.db.count(
                "Access Event",
                filters={"event_time": [">=", today], "result": "Denied"}
            )
            report.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.logger().error(f"Failed to generate reports: {str(e)}")

    @staticmethod
    def refresh_dashboard_cache():
        """Refresh dashboard cache"""
        try:
            frappe.cache().delete_key("sigma_dashboard_data")
            frappe.logger().info("Dashboard cache refreshed")
        except Exception as e:
            frappe.logger().error(f"Failed to refresh cache: {str(e)}")


# Module-level wrapper functions for Frappe scheduler
# These are required because Frappe's scheduler expects module-level functions, not class methods

def poll_vendor_apis():
    """Wrapper function for scheduled job"""
    return ScheduledJobs.poll_vendor_apis()

def generate_reports():
    """Wrapper function for scheduled job"""
    return ScheduledJobs.generate_reports()

def refresh_dashboard_cache():
    """Wrapper function for scheduled job"""
    return ScheduledJobs.refresh_dashboard_cache()

