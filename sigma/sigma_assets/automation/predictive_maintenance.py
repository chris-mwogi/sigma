# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Predictive Maintenance Engine - Advanced ML-based maintenance prediction
"""

import frappe
from frappe.utils import nowdate, add_days, getdate, date_diff, flt
import json
from datetime import datetime, timedelta


def calculate_failure_probability(asset_name):
    """
    Calculate failure probability based on multiple factors:
    - Operating hours vs MTBF
    - Health score trend
    - Recent alert frequency
    - Maintenance history
    
    Returns: probability (0-100)
    """
    asset = frappe.get_doc("Asset", asset_name)
    
    # Get asset category for MTBF
    category = frappe.get_doc("Asset Category Sigma", asset.asset_category_sigma) if asset.asset_category_sigma else None
    
    if not category or not category.mtbf_hours:
        return 0
    
    # Factor 1: Operating hours vs MTBF (40% weight)
    operating_hours = flt(asset.total_operating_hours or 0)
    mtbf = flt(category.mtbf_hours)
    hours_factor = min((operating_hours / mtbf) * 100, 100) if mtbf > 0 else 0
    
    # Factor 2: Health score trend (30% weight)
    health_score = flt(asset.health_score or 100)
    health_factor = 100 - health_score
    
    # Factor 3: Recent alert frequency (20% weight)
    alert_count = frappe.db.count("Monitoring Alert", {
        "monitored_device": ["in", frappe.db.get_all("Monitored Device", {"asset": asset_name}, pluck="name")],
        "severity": ["in", ["Critical", "High"]],
        "timestamp": [">=", add_days(nowdate(), -30)],
        "status": ["!=", "Resolved"]
    })
    alert_factor = min(alert_count * 10, 100)
    
    # Factor 4: Maintenance overdue (10% weight)
    overdue_schedules = frappe.db.count("Asset Maintenance Schedule", {
        "asset": asset_name,
        "schedule_status": "Overdue",
        "docstatus": 1
    })
    maintenance_factor = min(overdue_schedules * 25, 100)
    
    # Calculate weighted probability
    probability = (
        (hours_factor * 0.40) +
        (health_factor * 0.30) +
        (alert_factor * 0.20) +
        (maintenance_factor * 0.10)
    )
    
    return round(probability, 2)


def generate_predictive_alerts():
    """
    Generate predictive maintenance alerts for assets with high failure probability
    Runs daily
    """
    frappe.logger().info("Starting predictive maintenance alert generation...")

    # Get all operational assets with predictive maintenance enabled
    assets = frappe.db.sql("""
        SELECT
            a.name,
            a.asset_name,
            a.asset_category_sigma,
            a.criticality_rating
        FROM
            `tabAsset` a
        INNER JOIN
            `tabAsset Category Sigma` ac ON a.asset_category_sigma = ac.name
        WHERE
            a.docstatus = 1
            AND a.lifecycle_status = 'Operational'
            AND ac.enable_predictive_maintenance = 1
            AND ac.mtbf_hours IS NOT NULL
    """, as_dict=1)
    
    alerts_created = 0
    
    for asset in assets:
        try:
            # Calculate failure probability
            probability = calculate_failure_probability(asset.name)

            # Use default threshold of 70% for predictive alerts
            threshold = 70.0

            if probability >= threshold:
                # Check if alert already exists
                existing_alert = frappe.db.exists("Monitoring Alert", {
                    "alert_type": "Predictive Maintenance",
                    "monitored_device": ["in", frappe.db.get_all("Monitored Device", {"asset": asset.name}, pluck="name")],
                    "status": ["!=", "Resolved"],
                    "timestamp": [">=", add_days(nowdate(), -7)]
                })
                
                if not existing_alert:
                    # Get monitored device
                    device = frappe.db.get_value("Monitored Device", {"asset": asset.name}, "name")
                    
                    if device:
                        # Create predictive alert
                        alert = frappe.get_doc({
                            "doctype": "Monitoring Alert",
                            "monitored_device": device,
                            "alert_type": "Predictive Maintenance",
                            "severity": "High" if probability >= 80 else "Medium",
                            "status": "Open",
                            "alert_message": f"Predictive maintenance required for {asset.asset_name}. Failure probability: {probability}%",
                            "timestamp": nowdate(),
                            "metric_name": "failure_probability",
                            "metric_value": probability
                        })
                        alert.insert(ignore_permissions=True)
                        alerts_created += 1
                        
                        frappe.logger().info(f"Created predictive alert for {asset.name} (probability: {probability}%)")
        
        except Exception as e:
            frappe.logger().error(f"Error generating predictive alert for {asset.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Generated {alerts_created} predictive maintenance alerts")
    
    return alerts_created

