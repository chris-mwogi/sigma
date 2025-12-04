# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, add_months, add_years, getdate, nowdate, date_diff


class AssetMaintenanceSchedule(Document):
    """Asset Maintenance Schedule - ISO 55000 compliant maintenance scheduling"""
    
    def validate(self):
        """Validate maintenance schedule configuration"""
        self.validate_dates()
        self.validate_frequency()
        self.validate_condition_based()
        self.validate_predictive()
        self.calculate_next_due_date()
        self.update_status()
        self.calculate_compliance()
    
    def validate_dates(self):
        """Validate date logic"""
        if self.end_date and getdate(self.end_date) < getdate(self.start_date):
            frappe.throw(frappe._("End Date cannot be before Start Date"))
        
        if self.next_due_date and getdate(self.next_due_date) < getdate(self.start_date):
            frappe.throw(frappe._("Next Due Date cannot be before Start Date"))
    
    def validate_frequency(self):
        """Validate frequency configuration for recurring schedules"""
        if self.schedule_type == "Recurring":
            if not self.frequency or self.frequency <= 0:
                frappe.throw(frappe._("Frequency must be greater than 0 for recurring schedules"))
            
            if not self.frequency_unit:
                frappe.throw(frappe._("Frequency Unit is required for recurring schedules"))
    
    def validate_condition_based(self):
        """Validate condition-based triggering configuration"""
        if self.enable_condition_based:
            if not self.condition_metric:
                frappe.throw(frappe._("Condition Metric Name is required when condition-based triggering is enabled"))
            
            if self.condition_threshold is None:
                frappe.throw(frappe._("Threshold Value is required when condition-based triggering is enabled"))
            
            if not self.condition_operator:
                frappe.throw(frappe._("Operator is required when condition-based triggering is enabled"))
    
    def validate_predictive(self):
        """Validate predictive maintenance configuration"""
        if self.enable_predictive:
            if not self.mtbf_hours or self.mtbf_hours <= 0:
                frappe.throw(frappe._("MTBF (Hours) must be greater than 0 for predictive maintenance"))
            
            if self.failure_probability_threshold and (self.failure_probability_threshold < 0 or self.failure_probability_threshold > 100):
                frappe.throw(frappe._("Failure Probability Threshold must be between 0 and 100"))
    
    def calculate_next_due_date(self):
        """Calculate next due date based on schedule type and frequency"""
        if self.schedule_type == "One-Time":
            # For one-time schedules, next due date is the start date
            if not self.next_due_date:
                self.next_due_date = self.start_date
        
        elif self.schedule_type == "Recurring":
            # Calculate next due date based on frequency
            if not self.next_due_date or (self.last_completed_date and getdate(self.last_completed_date) >= getdate(self.next_due_date)):
                base_date = self.last_completed_date if self.last_completed_date else self.start_date
                
                if self.frequency_unit == "Days":
                    self.next_due_date = add_days(base_date, self.frequency)
                elif self.frequency_unit == "Weeks":
                    self.next_due_date = add_days(base_date, self.frequency * 7)
                elif self.frequency_unit == "Months":
                    self.next_due_date = add_months(base_date, self.frequency)
                elif self.frequency_unit == "Years":
                    self.next_due_date = add_years(base_date, self.frequency)
                # For Operating Hours and Cycles, next due date needs to be calculated based on telemetry
    
    def update_status(self):
        """Update status based on next due date and current date"""
        if not self.is_active:
            self.status = "Suspended"
            return
        
        if self.status == "Cancelled":
            return
        
        if self.status == "In Progress":
            return
        
        if self.next_due_date:
            today = getdate(nowdate())
            due_date = getdate(self.next_due_date)
            days_until_due = date_diff(due_date, today)
            
            if days_until_due < 0:
                self.status = "Overdue"
            elif days_until_due <= 7:  # Due within 7 days
                self.status = "Due"
            else:
                self.status = "Scheduled"
    
    def calculate_compliance(self):
        """Calculate compliance percentage"""
        total = self.total_completions + self.missed_schedules
        if total > 0:
            self.compliance_percentage = (self.total_completions / total) * 100
        else:
            self.compliance_percentage = 100.0
    
    def mark_completed(self, completion_date=None):
        """Mark schedule as completed and calculate next due date"""
        if not completion_date:
            completion_date = nowdate()
        
        self.last_completed_date = completion_date
        self.total_completions = (self.total_completions or 0) + 1
        
        # Recalculate next due date
        self.calculate_next_due_date()
        self.update_status()
        self.calculate_compliance()
        
        self.save(ignore_permissions=True)
        
        frappe.msgprint(
            frappe._("Maintenance schedule marked as completed. Next due date: {0}").format(self.next_due_date),
            indicator="green",
            alert=True
        )
    
    def mark_missed(self):
        """Mark schedule as missed"""
        self.missed_schedules = (self.missed_schedules or 0) + 1
        
        # Recalculate next due date
        self.calculate_next_due_date()
        self.update_status()
        self.calculate_compliance()
        
        self.save(ignore_permissions=True)
        
        frappe.msgprint(
            frappe._("Maintenance schedule marked as missed. Next due date: {0}").format(self.next_due_date),
            indicator="orange",
            alert=True
        )


@frappe.whitelist()
def get_due_schedules(asset=None, days_ahead=30):
    """Get maintenance schedules due within specified days"""
    filters = {
        "is_active": 1,
        "status": ["in", ["Scheduled", "Due", "Overdue"]],
        "next_due_date": ["<=", add_days(nowdate(), int(days_ahead))]
    }
    
    if asset:
        filters["asset"] = asset
    
    schedules = frappe.get_all(
        "Asset Maintenance Schedule",
        filters=filters,
        fields=[
            "name", "asset", "asset_name", "asset_category_sigma", "criticality_rating",
            "maintenance_type", "next_due_date", "status", "estimated_duration_hours"
        ],
        order_by="next_due_date asc"
    )
    
    return schedules


@frappe.whitelist()
def check_condition_triggers():
    """Check condition-based triggers and update schedules"""
    # Get all active condition-based schedules
    schedules = frappe.get_all(
        "Asset Maintenance Schedule",
        filters={
            "is_active": 1,
            "enable_condition_based": 1,
            "schedule_type": "Condition-Based"
        },
        fields=["name", "asset", "monitored_device", "condition_metric", "condition_threshold", "condition_operator"]
    )
    
    triggered_schedules = []
    
    for schedule in schedules:
        if not schedule.monitored_device:
            continue
        
        # Get latest telemetry for the condition metric
        telemetry = frappe.get_all(
            "Telemetry Event",
            filters={
                "device": schedule.monitored_device,
                "metric_name": schedule.condition_metric
            },
            fields=["metric_value"],
            order_by="timestamp desc",
            limit=1
        )
        
        if telemetry:
            metric_value = float(telemetry[0].metric_value)
            threshold = float(schedule.condition_threshold)
            
            # Check if condition is met
            condition_met = False
            if schedule.condition_operator == "Greater Than" and metric_value > threshold:
                condition_met = True
            elif schedule.condition_operator == "Less Than" and metric_value < threshold:
                condition_met = True
            elif schedule.condition_operator == "Equals" and metric_value == threshold:
                condition_met = True
            elif schedule.condition_operator == "Greater Than or Equal" and metric_value >= threshold:
                condition_met = True
            elif schedule.condition_operator == "Less Than or Equal" and metric_value <= threshold:
                condition_met = True
            
            if condition_met:
                triggered_schedules.append({
                    "schedule": schedule.name,
                    "asset": schedule.asset,
                    "metric": schedule.condition_metric,
                    "value": metric_value,
                    "threshold": threshold
                })
    
    return triggered_schedules

