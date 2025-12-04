# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Intelligent Work Order Assignment System
"""

import frappe
from frappe.utils import nowdate, getdate, get_datetime, time_diff_in_hours
import json


def calculate_technician_score(technician, work_order):
    """
    Calculate technician suitability score based on:
    - Skills match
    - Current workload
    - Location proximity
    - Performance history
    
    Returns: score (0-100)
    """
    score = 0
    
    # Factor 1: Skills match (40% weight)
    required_skills = work_order.get("required_skills", "").split(",") if work_order.get("required_skills") else []
    required_skills = [s.strip() for s in required_skills if s.strip()]
    
    if required_skills:
        # Get technician skills (assuming User has a custom field for skills)
        tech_skills = frappe.db.get_value("User", technician, "skills") or ""
        tech_skills = [s.strip() for s in tech_skills.split(",") if s.strip()]
        
        if tech_skills:
            matched_skills = len(set(required_skills) & set(tech_skills))
            skills_score = (matched_skills / len(required_skills)) * 100
        else:
            skills_score = 0
    else:
        skills_score = 50  # Neutral if no skills required
    
    score += skills_score * 0.40
    
    # Factor 2: Current workload (30% weight)
    active_work_orders = frappe.db.count("Asset Work Order", {
        "assigned_to": technician,
        "workflow_state": ["in", ["Assigned", "In Progress"]],
        "docstatus": ["<", 2]
    })
    
    # Lower workload = higher score
    workload_score = max(100 - (active_work_orders * 20), 0)
    score += workload_score * 0.30
    
    # Factor 3: Location proximity (20% weight)
    # Get technician's default location
    tech_location = frappe.db.get_value("User", technician, "location")
    work_order_location = work_order.get("asset_location")
    
    if tech_location and work_order_location:
        # Check if same location or parent location
        if tech_location == work_order_location:
            location_score = 100
        else:
            # Check if parent location matches
            asset_loc = frappe.get_doc("Asset Location", work_order_location)
            if asset_loc.parent_location == tech_location:
                location_score = 75
            else:
                location_score = 25
    else:
        location_score = 50  # Neutral if location not specified
    
    score += location_score * 0.20
    
    # Factor 4: Performance history (10% weight)
    # Get average completion time vs estimated time
    completed_orders = frappe.db.sql("""
        SELECT 
            AVG(actual_duration_hours / NULLIF(estimated_duration_hours, 0)) as avg_ratio
        FROM 
            `tabAsset Work Order`
        WHERE 
            assigned_to = %(technician)s
            AND workflow_state = 'Completed'
            AND actual_duration_hours IS NOT NULL
            AND estimated_duration_hours IS NOT NULL
            AND estimated_duration_hours > 0
    """, {"technician": technician}, as_dict=1)
    
    if completed_orders and completed_orders[0].avg_ratio:
        avg_ratio = completed_orders[0].avg_ratio
        # Lower ratio = better performance (completed faster than estimated)
        if avg_ratio <= 1.0:
            performance_score = 100
        elif avg_ratio <= 1.2:
            performance_score = 80
        elif avg_ratio <= 1.5:
            performance_score = 60
        else:
            performance_score = 40
    else:
        performance_score = 50  # Neutral if no history
    
    score += performance_score * 0.10
    
    return round(score, 2)


def auto_assign_work_orders():
    """
    Auto-assign unassigned work orders to best-suited technicians
    Runs every hour
    """
    frappe.logger().info("Starting auto-assignment of work orders...")
    
    # Get unassigned work orders
    work_orders = frappe.db.sql("""
        SELECT 
            name,
            asset,
            asset_location,
            work_order_type,
            priority,
            required_skills,
            estimated_duration_hours,
            scheduled_start_date
        FROM 
            `tabAsset Work Order`
        WHERE 
            workflow_state = 'Scheduled'
            AND assigned_to IS NULL
            AND docstatus < 2
        ORDER BY 
            FIELD(priority, 'Emergency', 'Critical', 'High', 'Medium', 'Low'),
            scheduled_start_date
        LIMIT 50
    """, as_dict=1)
    
    # Get available technicians (users with role "Maintenance Technician")
    technicians = frappe.db.sql("""
        SELECT DISTINCT
            u.name,
            u.full_name,
            u.location
        FROM 
            `tabUser` u
        INNER JOIN 
            `tabHas Role` hr ON u.name = hr.parent
        WHERE 
            hr.role = 'Maintenance Technician'
            AND u.enabled = 1
    """, as_dict=1)
    
    if not technicians:
        frappe.logger().warning("No maintenance technicians found for auto-assignment")
        return 0
    
    assigned_count = 0
    
    for wo in work_orders:
        try:
            # Calculate scores for all technicians
            technician_scores = []
            
            for tech in technicians:
                score = calculate_technician_score(tech.name, wo)
                technician_scores.append({
                    "technician": tech.name,
                    "full_name": tech.full_name,
                    "score": score
                })
            
            # Sort by score (highest first)
            technician_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Assign to best-suited technician
            if technician_scores and technician_scores[0]["score"] >= 50:  # Minimum threshold
                best_tech = technician_scores[0]
                
                work_order = frappe.get_doc("Asset Work Order", wo.name)
                work_order.assigned_to = best_tech["technician"]
                work_order.workflow_state = "Assigned"
                work_order.save(ignore_permissions=True)
                
                assigned_count += 1
                
                frappe.logger().info(
                    f"Assigned work order {wo.name} to {best_tech['full_name']} (score: {best_tech['score']})"
                )
        
        except Exception as e:
            frappe.logger().error(f"Error assigning work order {wo.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Auto-assigned {assigned_count} work orders")
    
    return assigned_count

