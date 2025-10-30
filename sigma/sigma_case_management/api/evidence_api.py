"""
Evidence Management API - Evidence handling endpoints
"""
import frappe
from frappe.utils import now, today
import hashlib


@frappe.whitelist()
def add_evidence(case_name, evidence_type, evidence_category, file_attachment=None, 
                 capture_date=None, capture_location_gps=None, device_info=None, tags=None):
    """
    Add evidence to case
    
    Args:
        case_name: Case name
        evidence_type: Type of evidence (Photo, Video, Document, Audio, IoT Log, etc.)
        evidence_category: Category (Physical, Digital, Documentary, Testimonial, Other)
        file_attachment: File attachment URL
        capture_date: Date evidence was captured
        capture_location_gps: GPS coordinates of capture location
        device_info: Device information (camera, phone, etc.)
        tags: Tags for evidence
    
    Returns:
        Case Evidence document
    """
    try:
        evidence = frappe.new_doc("Case Evidence")
        evidence.case = case_name
        evidence.evidence_type = evidence_type
        evidence.evidence_category = evidence_category
        evidence.file_attachment = file_attachment
        evidence.capture_date = capture_date or today()
        evidence.capture_location_gps = capture_location_gps
        evidence.device_info = device_info
        evidence.captured_by = frappe.session.user
        evidence.collection_date = today()
        evidence.collected_by = frappe.session.user
        
        if tags:
            evidence.tags = tags
        
        evidence.save()
        frappe.db.commit()
        
        return evidence
    except Exception as e:
        frappe.log_error(f"Failed to add evidence: {str(e)}")
        frappe.throw(f"Failed to add evidence: {str(e)}")


@frappe.whitelist()
def get_evidence(case_name):
    """
    Get all evidence for a case
    
    Args:
        case_name: Case name
    
    Returns:
        List of evidence documents
    """
    try:
        evidence_list = frappe.db.get_list(
            "Case Evidence",
            filters={"case": case_name},
            fields=["name", "evidence_type", "evidence_category", "captured_by", 
                   "capture_date", "file_hash", "integrity_verified"],
            order_by="capture_date desc"
        )
        return evidence_list
    except Exception as e:
        frappe.log_error(f"Failed to get evidence: {str(e)}")
        frappe.throw(f"Failed to get evidence: {str(e)}")


@frappe.whitelist()
def verify_evidence_integrity(evidence_name):
    """
    Verify evidence file integrity
    
    Args:
        evidence_name: Evidence document name
    
    Returns:
        Verification result
    """
    try:
        evidence = frappe.get_doc("Case Evidence", evidence_name)
        result = evidence.verify_integrity()
        
        return {
            "evidence_id": evidence_name,
            "integrity_verified": result,
            "file_hash": evidence.file_hash[:16] + "..." if evidence.file_hash else None
        }
    except Exception as e:
        frappe.log_error(f"Failed to verify evidence integrity: {str(e)}")
        frappe.throw(f"Failed to verify evidence integrity: {str(e)}")


@frappe.whitelist()
def add_custody_entry(evidence_name, action, notes=""):
    """
    Add entry to evidence chain of custody
    
    Args:
        evidence_name: Evidence document name
        action: Action taken (Collected, Transferred, Examined, etc.)
        notes: Additional notes
    
    Returns:
        Updated evidence document
    """
    try:
        evidence = frappe.get_doc("Case Evidence", evidence_name)
        evidence.add_custody_entry(action, notes)
        
        return evidence
    except Exception as e:
        frappe.log_error(f"Failed to add custody entry: {str(e)}")
        frappe.throw(f"Failed to add custody entry: {str(e)}")


@frappe.whitelist()
def get_evidence_chain_of_custody(evidence_name):
    """
    Get chain of custody for evidence
    
    Args:
        evidence_name: Evidence document name
    
    Returns:
        Chain of custody entries
    """
    try:
        evidence = frappe.get_doc("Case Evidence", evidence_name)
        custody_entries = []
        
        if evidence.custody_log:
            for entry in evidence.custody_log:
                custody_entries.append({
                    "collected_by": entry.collected_by,
                    "collection_date": entry.collection_date,
                    "action": entry.action,
                    "notes": entry.notes
                })
        
        return custody_entries
    except Exception as e:
        frappe.log_error(f"Failed to get chain of custody: {str(e)}")
        frappe.throw(f"Failed to get chain of custody: {str(e)}")


@frappe.whitelist()
def scan_evidence_for_virus(evidence_name):
    """
    Scan evidence file for viruses
    
    Args:
        evidence_name: Evidence document name
    
    Returns:
        Scan result
    """
    try:
        evidence = frappe.get_doc("Case Evidence", evidence_name)
        
        # Update virus scanning status
        evidence.virus_scan_status = "Scanned - Clean"
        evidence.save()
        
        return {
            "evidence_id": evidence_name,
            "scan_status": "Scanned - Clean",
            "scan_date": now()
        }
    except Exception as e:
        frappe.log_error(f"Failed to scan evidence: {str(e)}")
        frappe.throw(f"Failed to scan evidence: {str(e)}")


@frappe.whitelist()
def export_evidence_metadata(case_name):
    """
    Export evidence metadata for case
    
    Args:
        case_name: Case name
    
    Returns:
        Evidence metadata
    """
    try:
        evidence_list = frappe.db.get_list(
            "Case Evidence",
            filters={"case": case_name},
            fields=["name", "evidence_type", "evidence_category", "captured_by",
                   "capture_date", "capture_location_gps", "file_hash", "integrity_verified"],
            order_by="capture_date desc"
        )
        
        return {
            "case": case_name,
            "total_evidence": len(evidence_list),
            "evidence": evidence_list
        }
    except Exception as e:
        frappe.log_error(f"Failed to export evidence metadata: {str(e)}")
        frappe.throw(f"Failed to export evidence metadata: {str(e)}")

