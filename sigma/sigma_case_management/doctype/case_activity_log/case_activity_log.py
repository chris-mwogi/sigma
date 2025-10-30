import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta


class CaseActivityLog(Document):
    """Case Activity Log DocType - Logs all activities on a case"""
    
    def before_insert(self):
        """Initialize activity log on creation"""
        if not self.activity_date:
            self.activity_date = frappe.utils.now()
        if not self.performed_by:
            self.performed_by = frappe.session.user
    
    def validate(self):
        """Validate activity log data"""
        # Validate activity type
        valid_types = ["Case Created", "Status Changed", "Assignment", "Evidence Added",
                      "Comment Added", "Milestone Recorded", "Escalation", "Reassignment",
                      "Closure", "Reopening", "Other"]
        if self.activity_type not in valid_types:
            frappe.throw(f"Invalid activity type: {self.activity_type}")
        
        # Validate SLA status if provided
        if self.sla_status:
            valid_sla_statuses = ["On Track", "At Risk", "Overdue"]
            if self.sla_status not in valid_sla_statuses:
                frappe.throw(f"Invalid SLA status: {self.sla_status}")
    
    def on_insert(self):
        """Process activity log on creation"""
        self._check_sla_status()
        self._create_sla_alert_if_needed()
    
    def _check_sla_status(self):
        """Check and update SLA status"""
        if not self.sla_deadline:
            return
        
        try:
            deadline = datetime.fromisoformat(str(self.sla_deadline))
            now = datetime.now()
            time_remaining = (deadline - now).total_seconds() / 3600  # hours
            
            if time_remaining < 0:
                self.sla_status = "Overdue"
                self.days_remaining = 0
            elif time_remaining < 24:  # Less than 24 hours
                self.sla_status = "At Risk"
                self.days_remaining = 0
            else:
                self.sla_status = "On Track"
                self.days_remaining = int(time_remaining / 24)
        except Exception as e:
            frappe.log_error(f"Failed to check SLA status: {str(e)}")
    
    def _create_sla_alert_if_needed(self):
        """Create alert if SLA is at risk or overdue"""
        if self.sla_status in ["At Risk", "Overdue"]:
            case = frappe.get_doc("Case", self.case)
            
            alert_message = f"SLA Alert for Case {self.case}: {self.sla_status}"
            if self.sla_status == "Overdue":
                alert_message += " - IMMEDIATE ACTION REQUIRED"
            
            frappe.msgprint(alert_message, alert=True)
            
            # Create notification for case lead investigator
            if case.lead_investigator:
                frappe.share.add(
                    "Case Activity Log",
                    self.name,
                    user=case.lead_investigator,
                    perm_level=1,
                    notify=1
                )
    
    def record_milestone(self, milestone_name, milestone_date=None):
        """Record a milestone in the case"""
        if not milestone_date:
            milestone_date = frappe.utils.today()
        
        self.activity_type = "Milestone Recorded"
        self.milestone_name = milestone_name
        self.milestone_date = milestone_date
        self.activity_description = f"Milestone recorded: {milestone_name}"
        self.save()
    
    def log_status_change(self, old_status, new_status):
        """Log status change activity"""
        self.activity_type = "Status Changed"
        self.old_value = old_status
        self.new_value = new_status
        self.activity_description = f"Status changed from {old_status} to {new_status}"
        self.save()
    
    def log_assignment(self, investigator, role):
        """Log case assignment"""
        self.activity_type = "Assignment"
        self.activity_description = f"Case assigned to {investigator} as {role}"
        self.save()
    
    def log_escalation(self, reason):
        """Log case escalation"""
        self.activity_type = "Escalation"
        self.activity_description = f"Case escalated: {reason}"
        self.save()
    
    def get_activity_timeline(self):
        """Get activity timeline for case"""
        activities = frappe.db.get_list(
            "Case Activity Log",
            filters={"case": self.case},
            fields=["name", "activity_type", "activity_date", "performed_by", "activity_description"],
            order_by="activity_date asc"
        )
        return activities
    
    def get_activity_summary(self):
        """Get summary of activities"""
        return {
            "activity_id": self.name,
            "case": self.case,
            "activity_type": self.activity_type,
            "performed_by": self.performed_by,
            "activity_date": self.activity_date,
            "sla_status": self.sla_status,
            "days_remaining": self.days_remaining
        }

