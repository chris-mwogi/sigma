# Copyright (c) 2025, Augment and contributors
# For license information, please see license.txt

"""
Scheduled jobs for Asset Management automation
"""

import frappe
from frappe.utils import nowdate, add_days, add_months, getdate, date_diff


def auto_generate_maintenance_schedules():
    """
    Auto-generate maintenance schedules based on MTBF and condition
    Runs daily
    """
    frappe.logger().info("Starting auto-generation of maintenance schedules...")
    
    # Get all operational assets without active maintenance schedules
    assets = frappe.db.sql("""
        SELECT 
            a.name, 
            a.asset_name,
            a.asset_category_sigma,
            a.asset_location,
            a.criticality_rating,
            ac.default_maintenance_strategy,
            ac.mtbf_hours,
            ac.expected_useful_life_years
        FROM 
            `tabAsset` a
        LEFT JOIN 
            `tabAsset Category Sigma` ac ON a.asset_category_sigma = ac.name
        WHERE 
            a.docstatus = 1
            AND a.lifecycle_status = 'Operational'
            AND ac.default_maintenance_strategy IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 
                FROM `tabAsset Maintenance Schedule` ams 
                WHERE ams.asset = a.name 
                AND ams.schedule_status = 'Active'
                AND ams.docstatus = 1
            )
    """, as_dict=1)
    
    created_count = 0
    for asset in assets:
        try:
            # Create maintenance schedule
            schedule = frappe.get_doc({
                "doctype": "Asset Maintenance Schedule",
                "asset": asset.name,
                "asset_name": asset.asset_name,
                "asset_category_sigma": asset.asset_category_sigma,
                "asset_location": asset.asset_location,
                "criticality_rating": asset.criticality_rating,
                "maintenance_type": asset.default_maintenance_strategy or "Preventive Maintenance",
                "frequency": "Monthly",
                "start_date": nowdate(),
                "schedule_status": "Active",
                "estimated_duration_hours": 4,
                "estimated_cost": 5000
            })
            schedule.insert(ignore_permissions=True)
            schedule.submit()
            created_count += 1
            
        except Exception as e:
            frappe.logger().error(f"Error creating maintenance schedule for {asset.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Auto-generated {created_count} maintenance schedules")


def auto_escalate_critical_alerts():
    """
    Auto-escalate critical monitoring alerts to work orders
    Runs hourly
    """
    frappe.logger().info("Starting auto-escalation of critical alerts...")
    
    # Get critical unresolved alerts
    alerts = frappe.db.sql("""
        SELECT 
            ma.name,
            ma.monitored_device,
            ma.alert_type,
            ma.severity,
            ma.alert_message,
            md.asset
        FROM 
            `tabMonitoring Alert` ma
        LEFT JOIN 
            `tabMonitored Device` md ON ma.monitored_device = md.name
        WHERE 
            ma.status = 'Open'
            AND ma.severity IN ('Critical', 'High')
            AND md.asset IS NOT NULL
            AND NOT EXISTS (
                SELECT 1 
                FROM `tabAsset Work Order` awo 
                WHERE awo.monitoring_alert = ma.name
            )
        LIMIT 50
    """, as_dict=1)
    
    escalated_count = 0
    for alert in alerts:
        try:
            # Create work order from alert
            work_order = frappe.get_doc({
                "doctype": "Asset Work Order",
                "asset": alert.asset,
                "work_order_type": "Corrective Maintenance",
                "priority": "Critical" if alert.severity == "Critical" else "High",
                "description": f"<p>Auto-escalated from monitoring alert: {alert.alert_message}</p>",
                "monitoring_alert": alert.name,
                "scheduled_start_date": nowdate(),
                "scheduled_end_date": add_days(nowdate(), 1),
                "work_order_status": "Open"
            })
            work_order.insert(ignore_permissions=True)
            escalated_count += 1
            
        except Exception as e:
            frappe.logger().error(f"Error escalating alert {alert.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Auto-escalated {escalated_count} critical alerts to work orders")


def auto_update_asset_health():
    """
    Auto-update asset health scores from telemetry data
    Runs hourly
    """
    frappe.logger().info("Starting auto-update of asset health scores...")
    
    # Get assets with monitored devices
    assets = frappe.db.sql("""
        SELECT DISTINCT
            a.name,
            a.health_score as current_health_score
        FROM 
            `tabAsset` a
        INNER JOIN 
            `tabMonitored Device` md ON md.asset = a.name
        WHERE 
            a.docstatus = 1
            AND a.lifecycle_status = 'Operational'
    """, as_dict=1)
    
    updated_count = 0
    for asset in assets:
        try:
            # Get recent telemetry events for this asset
            telemetry = frappe.db.sql("""
                SELECT 
                    AVG(CASE WHEN te.metric_name = 'health_score' THEN te.metric_value ELSE NULL END) as avg_health,
                    AVG(CASE WHEN te.metric_name = 'temperature' THEN te.metric_value ELSE NULL END) as avg_temp,
                    COUNT(*) as event_count
                FROM 
                    `tabTelemetry Event` te
                INNER JOIN 
                    `tabMonitored Device` md ON te.device_id = md.device_id
                WHERE 
                    md.asset = %(asset)s
                    AND te.timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            """, {"asset": asset.name}, as_dict=1)
            
            if telemetry and telemetry[0].event_count > 0:
                new_health_score = telemetry[0].avg_health or asset.current_health_score or 100
                
                # Update asset health score
                frappe.db.set_value("Asset", asset.name, "health_score", new_health_score, update_modified=False)
                updated_count += 1
                
        except Exception as e:
            frappe.logger().error(f"Error updating health for asset {asset.name}: {str(e)}")
            continue
    
    frappe.db.commit()
    frappe.logger().info(f"Auto-updated health scores for {updated_count} assets")

