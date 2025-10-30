"""
Communication API - Case discussion and external communication
"""
import frappe
from frappe.utils import now, today


@frappe.whitelist()
def add_comment(case_name, content, discussion_type="Internal Note", is_private=False, mentions=None):
    """
    Add comment/discussion to case
    
    Args:
        case_name: Case name
        content: Comment content
        discussion_type: Type of discussion (Internal Note, Discussion Thread, etc.)
        is_private: Whether comment is private
        mentions: List of users to mention
    
    Returns:
        Case Discussion document
    """
    try:
        discussion = frappe.new_doc("Case Discussion")
        discussion.case = case_name
        discussion.content = content
        discussion.discussion_type = discussion_type
        discussion.is_private = is_private
        discussion.created_by = frappe.session.user
        discussion.created_date = now()
        
        # Add mentions
        if mentions:
            if isinstance(mentions, str):
                mentions = mentions.split(",")
            
            for user in mentions:
                discussion.append("mentions", {
                    "user": user.strip(),
                    "mention_type": "For Information"
                })
        
        discussion.save()
        frappe.db.commit()
        
        # Notify mentioned users
        if mentions:
            for user in mentions:
                frappe.share.add("Case Discussion", discussion.name, user=user.strip(), notify=1)
        
        return discussion
    except Exception as e:
        frappe.log_error(f"Failed to add comment: {str(e)}")
        frappe.throw(f"Failed to add comment: {str(e)}")


@frappe.whitelist()
def log_communication(case_name, stakeholder_type, stakeholder_name, communication_type, 
                     subject, message, follow_up_required=False, follow_up_date=None):
    """
    Log external communication
    
    Args:
        case_name: Case name
        stakeholder_type: Type of stakeholder (Police, Court, Legal Counsel, etc.)
        stakeholder_name: Name of stakeholder
        communication_type: Type of communication (Email, Phone Call, etc.)
        subject: Subject of communication
        message: Message content
        follow_up_required: Whether follow-up is required
        follow_up_date: Date for follow-up
    
    Returns:
        Case External Communication document
    """
    try:
        communication = frappe.new_doc("Case External Communication")
        communication.case = case_name
        communication.stakeholder_type = stakeholder_type
        communication.stakeholder_name = stakeholder_name
        communication.communication_type = communication_type
        communication.subject = subject
        communication.message = message
        communication.communication_date = now()
        communication.communicated_by = frappe.session.user
        communication.communication_status = "Sent"
        communication.follow_up_required = follow_up_required
        
        if follow_up_date:
            communication.follow_up_date = follow_up_date
        
        communication.save()
        frappe.db.commit()
        
        return communication
    except Exception as e:
        frappe.log_error(f"Failed to log communication: {str(e)}")
        frappe.throw(f"Failed to log communication: {str(e)}")


@frappe.whitelist()
def get_case_discussions(case_name):
    """
    Get all discussions for a case
    
    Args:
        case_name: Case name
    
    Returns:
        List of discussions
    """
    try:
        discussions = frappe.db.get_list(
            "Case Discussion",
            filters={"case": case_name},
            fields=["name", "discussion_type", "content", "created_by", "created_date", "is_pinned"],
            order_by="created_date desc"
        )
        return discussions
    except Exception as e:
        frappe.log_error(f"Failed to get discussions: {str(e)}")
        frappe.throw(f"Failed to get discussions: {str(e)}")


@frappe.whitelist()
def get_case_communications(case_name):
    """
    Get all external communications for a case
    
    Args:
        case_name: Case name
    
    Returns:
        List of communications
    """
    try:
        communications = frappe.db.get_list(
            "Case External Communication",
            filters={"case": case_name},
            fields=["name", "stakeholder_type", "stakeholder_name", "communication_type",
                   "subject", "communication_date", "communication_status"],
            order_by="communication_date desc"
        )
        return communications
    except Exception as e:
        frappe.log_error(f"Failed to get communications: {str(e)}")
        frappe.throw(f"Failed to get communications: {str(e)}")


@frappe.whitelist()
def pin_discussion(discussion_name):
    """
    Pin discussion to top
    
    Args:
        discussion_name: Discussion name
    
    Returns:
        Updated discussion
    """
    try:
        discussion = frappe.get_doc("Case Discussion", discussion_name)
        discussion.is_pinned = 1
        discussion.save()
        return discussion
    except Exception as e:
        frappe.log_error(f"Failed to pin discussion: {str(e)}")
        frappe.throw(f"Failed to pin discussion: {str(e)}")


@frappe.whitelist()
def mark_communication_resolved(communication_name, response_content=None):
    """
    Mark communication as resolved
    
    Args:
        communication_name: Communication name
        response_content: Response content
    
    Returns:
        Updated communication
    """
    try:
        communication = frappe.get_doc("Case External Communication", communication_name)
        communication.communication_status = "Resolved"
        communication.response_received = 1
        communication.response_date = now()
        
        if response_content:
            communication.response_content = response_content
        
        communication.save()
        return communication
    except Exception as e:
        frappe.log_error(f"Failed to mark communication resolved: {str(e)}")
        frappe.throw(f"Failed to mark communication resolved: {str(e)}")

