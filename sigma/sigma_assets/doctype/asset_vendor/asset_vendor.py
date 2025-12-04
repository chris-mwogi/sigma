# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import nowdate, add_days, getdate


class AssetVendor(Document):
    """Asset Vendor - Master DocType for vendor/supplier management"""
    
    def validate(self):
        """Validate vendor entry"""
        self.validate_contact_information()
        self.validate_certifications()
        self.validate_performance_metrics()
        self.check_insurance_expiry()
        self.calculate_vendor_rating()
    
    def validate_contact_information(self):
        """Validate contact information"""
        if not self.primary_contact_person and not self.primary_contact_email:
            frappe.throw("Either Primary Contact Person or Primary Contact Email is required")
    
    def validate_certifications(self):
        """Validate certifications"""
        if self.certification_expiry_date:
            if getdate(self.certification_expiry_date) < getdate(nowdate()):
                frappe.msgprint(
                    f"Warning: Certifications expired on {self.certification_expiry_date}",
                    indicator="orange",
                    alert=True
                )
    
    def validate_performance_metrics(self):
        """Validate performance metrics"""
        if self.vendor_rating and (self.vendor_rating < 0 or self.vendor_rating > 5):
            frappe.throw("Vendor Rating must be between 0 and 5")
        
        if self.quality_rating and (self.quality_rating < 0 or self.quality_rating > 5):
            frappe.throw("Quality Rating must be between 0 and 5")
        
        if self.on_time_delivery_rate and (self.on_time_delivery_rate < 0 or self.on_time_delivery_rate > 100):
            frappe.throw("On-Time Delivery Rate must be between 0 and 100")
        
        if self.defect_rate and (self.defect_rate < 0 or self.defect_rate > 100):
            frappe.throw("Defect Rate must be between 0 and 100")
    
    def check_insurance_expiry(self):
        """Check insurance expiry"""
        if self.insurance_expiry_date:
            days_to_expiry = (getdate(self.insurance_expiry_date) - getdate(nowdate())).days
            
            if days_to_expiry < 0:
                frappe.msgprint(
                    f"Warning: Insurance expired on {self.insurance_expiry_date}",
                    indicator="red",
                    alert=True
                )
            elif days_to_expiry <= 30:
                frappe.msgprint(
                    f"Warning: Insurance expires in {days_to_expiry} days",
                    indicator="orange",
                    alert=True
                )
    
    def calculate_vendor_rating(self):
        """Calculate overall vendor rating based on performance metrics"""
        if not self.vendor_rating and (self.on_time_delivery_rate or self.quality_rating or self.defect_rate):
            # Calculate weighted average
            total_weight = 0
            total_score = 0
            
            # On-time delivery (40% weight)
            if self.on_time_delivery_rate:
                total_score += (self.on_time_delivery_rate / 100) * 5 * 0.4
                total_weight += 0.4
            
            # Quality rating (40% weight)
            if self.quality_rating:
                total_score += self.quality_rating * 0.4
                total_weight += 0.4
            
            # Defect rate (20% weight, inverted)
            if self.defect_rate:
                total_score += ((100 - self.defect_rate) / 100) * 5 * 0.2
                total_weight += 0.2
            
            if total_weight > 0:
                self.vendor_rating = round(total_score / total_weight, 2)
    
    def on_update(self):
        """Actions on update"""
        self.update_contract_count()
    
    def update_contract_count(self):
        """Update total contracts count"""
        contract_count = frappe.db.count("SLA Contract", {"vendor": self.name})
        if contract_count != self.total_contracts:
            frappe.db.set_value("Asset Vendor", self.name, "total_contracts", contract_count, update_modified=False)


@frappe.whitelist()
def get_vendor_performance(vendor):
    """Get vendor performance metrics"""
    vendor_doc = frappe.get_doc("Asset Vendor", vendor)
    
    # Get contract performance
    contracts = frappe.get_all(
        "SLA Contract",
        filters={"vendor": vendor},
        fields=["name", "contract_status", "sla_compliance_percentage", "total_incidents", "resolved_incidents"]
    )
    
    # Calculate aggregate metrics
    total_contracts = len(contracts)
    active_contracts = len([c for c in contracts if c.contract_status == "Active"])
    avg_sla_compliance = sum([c.sla_compliance_percentage or 0 for c in contracts]) / total_contracts if total_contracts > 0 else 0
    total_incidents = sum([c.total_incidents or 0 for c in contracts])
    resolved_incidents = sum([c.resolved_incidents or 0 for c in contracts])
    resolution_rate = (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 0
    
    return {
        "vendor_name": vendor_doc.vendor_name,
        "vendor_rating": vendor_doc.vendor_rating,
        "vendor_status": vendor_doc.vendor_status,
        "total_contracts": total_contracts,
        "active_contracts": active_contracts,
        "avg_sla_compliance": round(avg_sla_compliance, 2),
        "on_time_delivery_rate": vendor_doc.on_time_delivery_rate,
        "quality_rating": vendor_doc.quality_rating,
        "defect_rate": vendor_doc.defect_rate,
        "response_time_hours": vendor_doc.response_time_hours,
        "total_incidents": total_incidents,
        "resolved_incidents": resolved_incidents,
        "resolution_rate": round(resolution_rate, 2)
    }


@frappe.whitelist()
def check_vendor_compliance(vendor):
    """Check vendor compliance status"""
    vendor_doc = frappe.get_doc("Asset Vendor", vendor)
    
    issues = []
    
    # Check certifications
    if vendor_doc.certification_expiry_date:
        if getdate(vendor_doc.certification_expiry_date) < getdate(nowdate()):
            issues.append(f"Certifications expired on {vendor_doc.certification_expiry_date}")
    
    # Check insurance
    if vendor_doc.insurance_expiry_date:
        if getdate(vendor_doc.insurance_expiry_date) < getdate(nowdate()):
            issues.append(f"Insurance expired on {vendor_doc.insurance_expiry_date}")
    
    # Check regulatory compliance
    if vendor_doc.regulatory_compliance_status == "Non-Compliant":
        issues.append("Vendor is non-compliant with regulatory requirements")
    
    # Check vendor status
    if vendor_doc.vendor_status in ["Suspended", "Blacklisted"]:
        issues.append(f"Vendor status is {vendor_doc.vendor_status}")
    
    return {
        "compliant": len(issues) == 0,
        "issues": issues
    }

