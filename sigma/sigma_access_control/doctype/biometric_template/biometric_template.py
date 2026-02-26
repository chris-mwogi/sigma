# Copyright (c) 2025, Sigma and contributors
# For license information, please see license.txt

import frappe
import hashlib
from frappe.model.document import Document


class BiometricTemplate(Document):
    def validate(self):
        self.validate_consent()
        self.validate_quality_score()
        self.generate_template_hash()
    
    def validate_consent(self):
        """Ensure consent is obtained before saving biometric data"""
        if not self.consent_obtained:
            frappe.throw("Consent must be obtained before storing biometric data (GDPR/Kenya DPA compliance)")
    
    def validate_quality_score(self):
        """Validate quality score is within range"""
        if self.quality_score and (self.quality_score < 0 or self.quality_score > 100):
            frappe.throw("Quality score must be between 0 and 100")
    
    def generate_template_hash(self):
        """Generate SHA-256 hash of template data for integrity verification"""
        if self.template_data:
            self.template_hash = hashlib.sha256(self.template_data.encode()).hexdigest()
    
    def before_save(self):
        """Check for duplicate active templates of same type for same person"""
        if self.status == "Active":
            existing = frappe.db.exists("Biometric Template", {
                "human_profile": self.human_profile,
                "template_type": self.template_type,
                "status": "Active",
                "name": ("!=", self.name)
            })
            if existing:
                frappe.throw(f"An active {self.template_type} template already exists for this person. Please deactivate the existing template first.")
    
    def update_verification_stats(self, success=True):
        """Update verification statistics - called from access event processing"""
        self.verification_count = (self.verification_count or 0) + 1
        self.last_verification_date = frappe.utils.now_datetime()
        if not success:
            self.false_rejection_count = (self.false_rejection_count or 0) + 1
        self.save(ignore_permissions=True)

