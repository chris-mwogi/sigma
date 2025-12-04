# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, getdate, date_diff


class SLAContract(Document):
    """SLA Contract - Submittable DocType for SLA contract management"""
    
    def validate(self):
        """Validate SLA contract"""
        self.validate_dates()
        self.calculate_contract_duration()
        self.calculate_kpi_achievement()
        self.calculate_sla_compliance()
        self.check_contract_expiry()
        self.determine_next_review_date()
    
    def validate_dates(self):
        """Validate contract dates"""
        if self.start_date and self.end_date:
            if getdate(self.end_date) < getdate(self.start_date):
                frappe.throw("End Date cannot be before Start Date")
        
        if self.renewal_date:
            if getdate(self.renewal_date) < getdate(self.end_date):
                frappe.throw("Renewal Date should be on or after End Date")
    
    def calculate_contract_duration(self):
        """Calculate contract duration in days"""
        if self.start_date and self.end_date:
            self.contract_duration_days = date_diff(self.end_date, self.start_date)
    
    def calculate_kpi_achievement(self):
        """Calculate KPI achievement percentage for each KPI"""
        for kpi in self.sla_kpis:
            if kpi.target_value and kpi.actual_value:
                # Calculate achievement percentage
                kpi.achievement_percentage = (kpi.actual_value / kpi.target_value) * 100
                
                # Determine status
                if kpi.achievement_percentage >= 100:
                    kpi.status = "Met" if kpi.achievement_percentage == 100 else "Exceeded"
                elif kpi.achievement_percentage >= 80:
                    kpi.status = "Partially Met"
                else:
                    kpi.status = "Not Met"
            else:
                kpi.status = "Not Measured"
    
    def calculate_sla_compliance(self):
        """Calculate overall SLA compliance percentage"""
        if not self.sla_kpis:
            return
        
        total_kpis = len(self.sla_kpis)
        met_kpis = len([kpi for kpi in self.sla_kpis if kpi.status in ["Met", "Exceeded"]])
        
        if total_kpis > 0:
            self.sla_compliance_percentage = (met_kpis / total_kpis) * 100
    
    def check_contract_expiry(self):
        """Check contract expiry and update status"""
        if self.end_date:
            days_to_expiry = date_diff(self.end_date, nowdate())
            
            if days_to_expiry < 0:
                if self.contract_status == "Active":
                    self.contract_status = "Expired"
                    frappe.msgprint(
                        f"Contract expired on {self.end_date}",
                        indicator="red",
                        alert=True
                    )
            elif days_to_expiry <= 30:
                frappe.msgprint(
                    f"Warning: Contract expires in {days_to_expiry} days",
                    indicator="orange",
                    alert=True
                )
    
    def determine_next_review_date(self):
        """Determine next review date based on reporting frequency"""
        if not self.next_review_date and self.last_review_date and self.reporting_frequency:
            frequency_map = {
                "Weekly": 7,
                "Monthly": 30,
                "Quarterly": 90,
                "Annually": 365
            }
            
            days_to_add = frequency_map.get(self.reporting_frequency, 30)
            self.next_review_date = add_days(self.last_review_date, days_to_add)
        elif not self.next_review_date and self.start_date and self.reporting_frequency:
            frequency_map = {
                "Weekly": 7,
                "Monthly": 30,
                "Quarterly": 90,
                "Annually": 365
            }
            
            days_to_add = frequency_map.get(self.reporting_frequency, 30)
            self.next_review_date = add_days(self.start_date, days_to_add)
    
    def on_submit(self):
        """Actions on submission"""
        # Set contract status to Active if it's Draft
        if self.contract_status == "Draft":
            self.contract_status = "Active"
            self.save()
        
        # Update vendor contract count
        self.update_vendor_contracts()
    
    def on_cancel(self):
        """Actions on cancellation"""
        self.contract_status = "Terminated"
        self.save()
    
    def update_vendor_contracts(self):
        """Update vendor contract count"""
        if self.vendor:
            vendor = frappe.get_doc("Asset Vendor", self.vendor)
            vendor.update_contract_count()
    
    def update_performance_metrics(self):
        """Update performance metrics from work orders"""
        # Get work orders linked to this contract
        work_orders = frappe.get_all(
            "Asset Work Order",
            filters={"sla_contract": self.name},
            fields=["name", "work_order_status", "sla_status"]
        )
        
        self.total_incidents = len(work_orders)
        self.resolved_incidents = len([wo for wo in work_orders if wo.work_order_status == "Completed"])
        
        # Count SLA breaches
        self.breaches_count = len([wo for wo in work_orders if wo.sla_status == "Breached"])
        
        # Calculate SLA compliance
        if self.total_incidents > 0:
            compliant_incidents = self.total_incidents - self.breaches_count
            self.sla_compliance_percentage = (compliant_incidents / self.total_incidents) * 100
        
        self.save()


@frappe.whitelist()
def update_kpi_actual_value(contract, kpi_name, actual_value):
    """Update KPI actual value"""
    contract_doc = frappe.get_doc("SLA Contract", contract)
    
    for kpi in contract_doc.sla_kpis:
        if kpi.kpi_name == kpi_name:
            kpi.actual_value = actual_value
            break
    
    contract_doc.save()
    
    return {
        "success": True,
        "message": f"KPI '{kpi_name}' updated successfully"
    }


@frappe.whitelist()
def get_contract_performance(contract):
    """Get contract performance summary"""
    contract_doc = frappe.get_doc("SLA Contract", contract)
    
    # Update performance metrics
    contract_doc.update_performance_metrics()
    
    return {
        "contract_title": contract_doc.contract_title,
        "vendor": contract_doc.vendor_name,
        "contract_status": contract_doc.contract_status,
        "sla_compliance_percentage": contract_doc.sla_compliance_percentage,
        "total_incidents": contract_doc.total_incidents,
        "resolved_incidents": contract_doc.resolved_incidents,
        "breaches_count": contract_doc.breaches_count,
        "penalties_applied": contract_doc.penalties_applied,
        "bonuses_earned": contract_doc.bonuses_earned,
        "kpis": [
            {
                "kpi_name": kpi.kpi_name,
                "kpi_category": kpi.kpi_category,
                "target_value": kpi.target_value,
                "actual_value": kpi.actual_value,
                "achievement_percentage": kpi.achievement_percentage,
                "status": kpi.status
            }
            for kpi in contract_doc.sla_kpis
        ]
    }

