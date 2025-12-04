# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Scheduled jobs for SLA Contract automation
"""

import frappe
from frappe.utils import nowdate, add_days, date_diff, getdate


def check_contract_expiry():
    """
    Check for expiring SLA contracts and send notifications
    Runs daily
    """
    frappe.logger().info("Starting contract expiry check...")
    
    # Get contracts expiring in the next 30 days
    contracts = frappe.db.sql("""
        SELECT 
            name,
            contract_title,
            vendor,
            vendor_name,
            end_date,
            DATEDIFF(end_date, CURDATE()) as days_until_expiry,
            auto_renewal
        FROM 
            `tabSLA Contract`
        WHERE 
            docstatus = 1
            AND contract_status = 'Active'
            AND end_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY)
        ORDER BY 
            end_date ASC
    """, as_dict=1)
    
    notification_count = 0
    for contract in contracts:
        try:
            # Determine notification urgency
            if contract.days_until_expiry <= 7:
                urgency = "Critical"
            elif contract.days_until_expiry <= 14:
                urgency = "High"
            else:
                urgency = "Medium"
            
            # Create notification
            notification_message = f"""
                <p><strong>SLA Contract Expiring Soon</strong></p>
                <p>Contract: {contract.contract_title}</p>
                <p>Vendor: {contract.vendor_name}</p>
                <p>Expiry Date: {contract.end_date}</p>
                <p>Days Until Expiry: {contract.days_until_expiry}</p>
                <p>Auto-Renewal: {'Yes' if contract.auto_renewal else 'No'}</p>
            """
            
            # Send notification to System Managers
            users = frappe.get_all("User", filters={"enabled": 1}, fields=["name"])
            for user in users:
                if frappe.db.exists("Has Role", {"parent": user.name, "role": "System Manager"}):
                    frappe.get_doc({
                        "doctype": "Notification Log",
                        "subject": f"SLA Contract Expiring: {contract.contract_title}",
                        "email_content": notification_message,
                        "for_user": user.name,
                        "type": "Alert",
                        "document_type": "SLA Contract",
                        "document_name": contract.name
                    }).insert(ignore_permissions=True)
            
            notification_count += 1
            
        except Exception as e:
            frappe.logger().error(f"Error processing contract expiry for {contract.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Sent {notification_count} contract expiry notifications")


def update_contract_performance():
    """
    Update SLA contract performance metrics from work orders
    Runs daily
    """
    frappe.logger().info("Starting contract performance update...")
    
    # Get all active contracts
    contracts = frappe.db.sql("""
        SELECT 
            name,
            contract_title
        FROM 
            `tabSLA Contract`
        WHERE 
            docstatus = 1
            AND contract_status = 'Active'
    """, as_dict=1)
    
    updated_count = 0
    for contract in contracts:
        try:
            # Get work orders linked to this contract
            work_orders = frappe.db.sql("""
                SELECT 
                    name,
                    work_order_status,
                    scheduled_start_date,
                    actual_start_date,
                    scheduled_end_date,
                    actual_end_date,
                    sla_compliant
                FROM 
                    `tabAsset Work Order`
                WHERE 
                    sla_contract = %(contract)s
                    AND docstatus = 1
            """, {"contract": contract.name}, as_dict=1)
            
            if work_orders:
                total_incidents = len(work_orders)
                resolved_incidents = len([wo for wo in work_orders if wo.work_order_status == "Completed"])
                breaches = len([wo for wo in work_orders if wo.sla_compliant == 0])
                
                # Update contract metrics
                frappe.db.set_value("SLA Contract", contract.name, {
                    "total_incidents": total_incidents,
                    "resolved_incidents": resolved_incidents,
                    "breaches_count": breaches
                }, update_modified=False)
                
                updated_count += 1
                
        except Exception as e:
            frappe.logger().error(f"Error updating performance for contract {contract.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Updated performance metrics for {updated_count} contracts")


def check_vendor_compliance():
    """
    Check vendor compliance status (certifications, insurance)
    Runs daily
    """
    frappe.logger().info("Starting vendor compliance check...")
    
    # Get vendors with expiring certifications or insurance
    vendors = frappe.db.sql("""
        SELECT 
            name,
            vendor_name,
            certification_expiry_date,
            insurance_expiry_date,
            DATEDIFF(certification_expiry_date, CURDATE()) as cert_days_left,
            DATEDIFF(insurance_expiry_date, CURDATE()) as insurance_days_left
        FROM 
            `tabAsset Vendor`
        WHERE 
            vendor_status = 'Active'
            AND (
                (certification_expiry_date IS NOT NULL AND certification_expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY))
                OR
                (insurance_expiry_date IS NOT NULL AND insurance_expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY))
            )
    """, as_dict=1)
    
    notification_count = 0
    for vendor in vendors:
        try:
            issues = []
            
            if vendor.cert_days_left is not None and vendor.cert_days_left <= 30:
                if vendor.cert_days_left < 0:
                    issues.append(f"Certification EXPIRED {abs(vendor.cert_days_left)} days ago")
                else:
                    issues.append(f"Certification expiring in {vendor.cert_days_left} days")
            
            if vendor.insurance_days_left is not None and vendor.insurance_days_left <= 30:
                if vendor.insurance_days_left < 0:
                    issues.append(f"Insurance EXPIRED {abs(vendor.insurance_days_left)} days ago")
                else:
                    issues.append(f"Insurance expiring in {vendor.insurance_days_left} days")
            
            if issues:
                notification_message = f"""
                    <p><strong>Vendor Compliance Issue</strong></p>
                    <p>Vendor: {vendor.vendor_name}</p>
                    <p>Issues:</p>
                    <ul>
                        {''.join([f'<li>{issue}</li>' for issue in issues])}
                    </ul>
                """
                
                # Send notification to System Managers
                users = frappe.get_all("User", filters={"enabled": 1}, fields=["name"])
                for user in users:
                    if frappe.db.exists("Has Role", {"parent": user.name, "role": "System Manager"}):
                        frappe.get_doc({
                            "doctype": "Notification Log",
                            "subject": f"Vendor Compliance Issue: {vendor.vendor_name}",
                            "email_content": notification_message,
                            "for_user": user.name,
                            "type": "Alert",
                            "document_type": "Asset Vendor",
                            "document_name": vendor.name
                        }).insert(ignore_permissions=True)
                
                notification_count += 1
                
        except Exception as e:
            frappe.logger().error(f"Error checking compliance for vendor {vendor.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Sent {notification_count} vendor compliance notifications")

