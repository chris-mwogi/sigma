import frappe
from frappe.model.document import Document
import hashlib
import os


class CaseEvidence(Document):
    """Case Evidence DocType - Manages evidence for cases"""
    
    def before_insert(self):
        """Initialize evidence on creation"""
        if not self.captured_by:
            self.captured_by = frappe.session.user
        if not self.collection_date:
            self.collection_date = frappe.utils.today()
    
    def validate(self):
        """Validate evidence data"""
        # Validate evidence type
        valid_types = ["Photo", "Video", "Document", "Audio", "IoT Log", 
                      "Witness Statement", "Other"]
        if self.evidence_type not in valid_types:
            frappe.throw(f"Invalid evidence type: {self.evidence_type}")
        
        # Validate file size if attachment exists
        if self.file_attachment:
            self._validate_file_size()
        
        # Validate evidence category
        valid_categories = ["Physical", "Digital", "Documentary", "Testimonial", "Other"]
        if self.evidence_category not in valid_categories:
            frappe.throw(f"Invalid evidence category: {self.evidence_category}")
    
    def _validate_file_size(self):
        """Validate file size (max 50 MB)"""
        max_size_mb = 50
        max_size_bytes = max_size_mb * 1024 * 1024
        
        # Get file size from attachment
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
            if file_doc.file_size > max_size_bytes:
                frappe.throw(f"File size exceeds maximum limit of {max_size_mb} MB")
        except:
            pass  # File might not exist yet
    
    def on_insert(self):
        """Process evidence on creation"""
        self._generate_file_hash()
        self._initialize_chain_of_custody()
    
    def _generate_file_hash(self):
        """Generate SHA256 hash of file for integrity verification"""
        if self.file_attachment:
            try:
                file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
                file_path = file_doc.get_full_path()
                
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                
                self.file_hash = sha256_hash.hexdigest()
                self.integrity_verified = 1
                frappe.msgprint(f"File hash generated: {self.file_hash[:16]}...")
            except Exception as e:
                frappe.log_error(f"Failed to generate file hash: {str(e)}")
    
    def _initialize_chain_of_custody(self):
        """Initialize chain of custody log"""
        if not self.custody_log:
            self.append("custody_log", {
                "collected_by": self.captured_by,
                "collection_date": self.collection_date,
                "action": "Evidence Collected",
                "notes": "Initial collection"
            })
    
    def verify_integrity(self):
        """Verify file integrity using stored hash"""
        if not self.file_hash or not self.file_attachment:
            frappe.throw("Cannot verify integrity: hash or file missing")
        
        try:
            file_doc = frappe.get_doc("File", {"file_url": self.file_attachment})
            file_path = file_doc.get_full_path()
            
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            
            current_hash = sha256_hash.hexdigest()
            if current_hash == self.file_hash:
                self.integrity_verified = 1
                frappe.msgprint("File integrity verified successfully")
                return True
            else:
                self.integrity_verified = 0
                frappe.throw("File integrity check failed - file may have been modified")
                return False
        except Exception as e:
            frappe.throw(f"Failed to verify integrity: {str(e)}")
    
    def add_custody_entry(self, action, notes=""):
        """Add entry to chain of custody"""
        self.append("custody_log", {
            "collected_by": frappe.session.user,
            "collection_date": frappe.utils.today(),
            "action": action,
            "notes": notes
        })
        self.save()
    
    def get_evidence_details(self):
        """Get evidence details"""
        return {
            "evidence_id": self.name,
            "case": self.case,
            "evidence_type": self.evidence_type,
            "category": self.evidence_category,
            "captured_by": self.captured_by,
            "capture_date": self.capture_date,
            "file_hash": self.file_hash[:16] + "..." if self.file_hash else None,
            "integrity_verified": self.integrity_verified,
            "custody_entries": len(self.custody_log or [])
        }

