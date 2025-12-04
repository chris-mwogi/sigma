# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime, get_datetime, time_diff_in_hours


class AssetWorkOrder(Document):
    """Asset Work Order - ISO 55000 compliant work order management"""
    
    def validate(self):
        """Validate work order configuration"""
        self.validate_dates()
        self.validate_priority()
        self.calculate_actual_duration()
        self.calculate_actual_cost()
        self.check_sla_compliance()
    
    def validate_dates(self):
        """Validate date logic"""
        if self.scheduled_end_date and self.scheduled_start_date:
            if get_datetime(self.scheduled_end_date) < get_datetime(self.scheduled_start_date):
                frappe.throw(frappe._("Scheduled End Date cannot be before Scheduled Start Date"))
        
        if self.actual_end_date and self.actual_start_date:
            if get_datetime(self.actual_end_date) < get_datetime(self.actual_start_date):
                frappe.throw(frappe._("Actual End Date cannot be before Actual Start Date"))
    
    def validate_priority(self):
        """Auto-set priority based on criticality and emergency flag"""
        if self.is_emergency:
            self.priority = "Emergency"
        elif self.criticality_rating == "Critical" and self.priority not in ["Critical", "Emergency"]:
            self.priority = "Critical"
            frappe.msgprint(
                frappe._("Priority automatically set to Critical based on asset criticality"),
                indicator="orange",
                alert=True
            )
    
    def calculate_actual_duration(self):
        """Calculate actual duration from start and end dates"""
        if self.actual_start_date and self.actual_end_date:
            self.actual_duration_hours = time_diff_in_hours(
                get_datetime(self.actual_end_date),
                get_datetime(self.actual_start_date)
            )
    
    def calculate_actual_cost(self):
        """Calculate total actual cost from parts and materials"""
        total_cost = 0.0
        
        if self.spare_parts_cost:
            total_cost += self.spare_parts_cost
        
        if self.materials_cost:
            total_cost += self.materials_cost
        
        self.actual_cost = total_cost
    
    def check_sla_compliance(self):
        """Check if work order is SLA compliant"""
        if self.workflow_state == "Completed" and self.actual_end_date:
            if self.scheduled_end_date:
                # Check if completed within scheduled time
                self.sla_compliance = get_datetime(self.actual_end_date) <= get_datetime(self.scheduled_end_date)
            else:
                # If no scheduled end date, consider compliant
                self.sla_compliance = True
    
    def on_submit(self):
        """Actions on work order submission"""
        # Update maintenance schedule if linked
        if self.maintenance_schedule:
            self.update_maintenance_schedule()
        
        # Update asset last maintenance date
        if self.asset and self.workflow_state == "Completed":
            self.update_asset_maintenance_date()
    
    def update_maintenance_schedule(self):
        """Update linked maintenance schedule as completed"""
        try:
            schedule = frappe.get_doc("Asset Maintenance Schedule", self.maintenance_schedule)
            schedule.mark_completed(self.actual_end_date or now_datetime())
        except Exception as e:
            frappe.log_error(f"Failed to update maintenance schedule: {str(e)}")
    
    def update_asset_maintenance_date(self):
        """Update asset's last maintenance date"""
        try:
            asset = frappe.get_doc("Asset", self.asset)
            asset.last_maintenance_date = self.actual_end_date or now_datetime()
            asset.save(ignore_permissions=True)
        except Exception as e:
            frappe.log_error(f"Failed to update asset maintenance date: {str(e)}")


@frappe.whitelist()
def start_work_order(work_order_name):
    """Start a work order"""
    work_order = frappe.get_doc("Asset Work Order", work_order_name)
    
    if work_order.workflow_state not in ["Scheduled", "Assigned"]:
        frappe.throw(frappe._("Work order must be in Scheduled or Assigned state to start"))
    
    work_order.workflow_state = "In Progress"
    work_order.actual_start_date = now_datetime()
    work_order.save(ignore_permissions=True)
    
    frappe.msgprint(
        frappe._("Work order started at {0}").format(work_order.actual_start_date),
        indicator="blue",
        alert=True
    )
    
    return work_order


@frappe.whitelist()
def complete_work_order(work_order_name, work_performed=None, findings=None, recommendations=None):
    """Complete a work order"""
    work_order = frappe.get_doc("Asset Work Order", work_order_name)
    
    if work_order.workflow_state != "In Progress":
        frappe.throw(frappe._("Work order must be in In Progress state to complete"))
    
    work_order.workflow_state = "Completed"
    work_order.actual_end_date = now_datetime()
    work_order.completion_percentage = 100
    
    if work_performed:
        work_order.work_performed = work_performed
    if findings:
        work_order.findings = findings
    if recommendations:
        work_order.recommendations = recommendations
    
    work_order.save(ignore_permissions=True)
    
    frappe.msgprint(
        frappe._("Work order completed at {0}").format(work_order.actual_end_date),
        indicator="green",
        alert=True
    )
    
    return work_order


@frappe.whitelist()
def create_work_order_from_schedule(schedule_name):
    """Create work order from maintenance schedule"""
    schedule = frappe.get_doc("Asset Maintenance Schedule", schedule_name)
    
    work_order = frappe.new_doc("Asset Work Order")
    work_order.asset = schedule.asset
    work_order.maintenance_schedule = schedule.name
    work_order.work_order_type = "Preventive Maintenance"
    work_order.priority = "Medium" if schedule.criticality_rating in ["Low", "Medium"] else "High"
    work_order.work_description = schedule.task_description or f"Scheduled maintenance for {schedule.asset_name}"
    work_order.estimated_duration_hours = schedule.estimated_duration_hours
    work_order.required_skills = schedule.required_skills
    work_order.required_tools = schedule.required_tools
    work_order.safety_requirements = schedule.safety_requirements
    work_order.scheduled_start_date = schedule.next_due_date
    
    work_order.insert(ignore_permissions=True)
    
    frappe.msgprint(
        frappe._("Work order {0} created from maintenance schedule").format(work_order.name),
        indicator="green",
        alert=True
    )
    
    return work_order


@frappe.whitelist()
def create_work_order_from_alert(alert_name):
    """Create work order from monitoring alert"""
    alert = frappe.get_doc("Monitoring Alert", alert_name)
    
    if not alert.asset:
        frappe.throw(frappe._("Alert must be linked to an asset to create work order"))
    
    work_order = frappe.new_doc("Asset Work Order")
    work_order.asset = alert.asset
    work_order.monitoring_alert = alert.name
    work_order.work_order_type = "Corrective Maintenance"
    
    # Set priority based on alert severity
    severity_priority_map = {
        "Critical": "Critical",
        "High": "High",
        "Medium": "Medium",
        "Low": "Low",
        "Info": "Low"
    }
    work_order.priority = severity_priority_map.get(alert.severity, "Medium")
    
    work_order.work_description = f"Alert: {alert.alert_type}<br><br>{alert.message}"
    work_order.is_emergency = alert.severity == "Critical"
    
    work_order.insert(ignore_permissions=True)
    
    # Update alert workflow state
    alert.workflow_state = "In Progress"
    alert.save(ignore_permissions=True)
    
    frappe.msgprint(
        frappe._("Work order {0} created from monitoring alert").format(work_order.name),
        indicator="green",
        alert=True
    )
    
    return work_order


@frappe.whitelist()
def get_overdue_work_orders():
    """Get all overdue work orders"""
    work_orders = frappe.get_all(
        "Asset Work Order",
        filters={
            "workflow_state": ["in", ["Scheduled", "Assigned", "In Progress"]],
            "scheduled_end_date": ["<", now_datetime()]
        },
        fields=[
            "name", "asset", "asset_name", "work_order_type", "priority",
            "scheduled_start_date", "scheduled_end_date", "workflow_state"
        ],
        order_by="priority desc, scheduled_end_date asc"
    )
    
    return work_orders

