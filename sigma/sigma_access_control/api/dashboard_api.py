import frappe
from frappe import _
from frappe.utils import nowdate, add_days, getdate


@frappe.whitelist()
def get_command_center_kpis():
    """Get KPI data for the Command Center dashboard"""
    today = nowdate()
    
    # Employees onsite (entry events today)
    employees_onsite = frappe.db.count("Access Event", filters={
        "event_time": [">=", today],
        "result": "Granted",
        "direction": "Entry",
        "holder_type": "Employee"
    })
    
    # Visitors onsite
    visitors_onsite = frappe.db.count("Access Event", filters={
        "event_time": [">=", today],
        "result": "Granted",
        "direction": "Entry",
        "holder_type": "Visitor"
    })
    
    # Contractors onsite
    contractors_onsite = frappe.db.count("Access Event", filters={
        "event_time": [">=", today],
        "result": "Granted",
        "direction": "Entry",
        "holder_type": "Contractor"
    })
    
    # Vehicles in parking
    vehicles_in_parking = frappe.db.count("ANPR Event Log", filters={
        "event_time": [">=", today],
        "gate_action": "Opened",
        "direction": "Entry"
    })
    
    # Active alarms
    active_alarms = frappe.db.count("Door Alarm", filters={"status": "Active"})
    
    # Open incidents
    open_incidents = frappe.db.count("Access Incident", filters={
        "status": ["in", ["Open", "Investigating"]]
    })
    
    # Events today
    events_today = frappe.db.count("Access Event", filters={
        "event_time": [">=", today]
    })
    
    # Denied today
    denied_today = frappe.db.count("Access Event", filters={
        "event_time": [">=", today],
        "result": "Denied"
    })
    
    return {
        "employees_onsite": employees_onsite,
        "visitors_onsite": visitors_onsite,
        "contractors_onsite": contractors_onsite,
        "vehicles_in_parking": vehicles_in_parking,
        "active_alarms": active_alarms,
        "open_incidents": open_incidents,
        "events_today": events_today,
        "denied_today": denied_today
    }


@frappe.whitelist()
def get_events_trend():
    """Get access events trend for the last 7 days"""
    labels = []
    values = []
    
    for i in range(6, -1, -1):
        date = add_days(nowdate(), -i)
        labels.append(frappe.utils.formatdate(date, "d MMM"))
        
        count = frappe.db.count("Access Event", filters={
            "event_time": ["between", [date, add_days(date, 1)]]
        })
        values.append(count)
    
    return {
        "labels": labels,
        "datasets": [{"values": values}]
    }


@frappe.whitelist()
def get_access_by_result():
    """Get access events grouped by result"""
    data = frappe.db.sql("""
        SELECT result, COUNT(*) as count
        FROM `tabAccess Event`
        WHERE event_time >= %s
        GROUP BY result
        ORDER BY count DESC
    """, nowdate(), as_dict=True)
    
    labels = [d.result for d in data]
    values = [d.count for d in data]
    
    return {
        "labels": labels,
        "datasets": [{"values": values}]
    }


@frappe.whitelist()
def get_access_by_zone():
    """Get access events grouped by zone"""
    data = frappe.db.sql("""
        SELECT COALESCE(zone, 'Unknown') as zone, COUNT(*) as count
        FROM `tabAccess Event`
        WHERE event_time >= %s
        GROUP BY zone
        ORDER BY count DESC
        LIMIT 10
    """, nowdate(), as_dict=True)
    
    labels = [d.zone for d in data]
    values = [d.count for d in data]
    
    return {
        "labels": labels,
        "datasets": [{"values": values}]
    }


@frappe.whitelist()
def get_device_health():
    """Get device health status distribution"""
    data = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabDevice Health Log`
        WHERE log_time >= %s
        GROUP BY status
        ORDER BY FIELD(status, 'Online', 'Degraded', 'Offline')
    """, nowdate(), as_dict=True)

    labels = [d.status for d in data]
    values = [d.count for d in data]

    return {
        "labels": labels,
        "datasets": [{"values": values}]
    }


@frappe.whitelist()
def get_recent_events(limit=20):
    """Get recent access events for the live feed"""
    events = frappe.db.sql("""
        SELECT
            ae.name,
            ae.event_type,
            ae.event_time,
            ae.result,
            ae.access_point,
            ap.access_point_name,
            ae.zone,
            ae.anomaly_detected,
            ae.holder_type,
            CASE
                WHEN ae.holder_type = 'Employee' THEN hp.full_name
                WHEN ae.holder_type = 'Visitor' THEN CONCAT(v.first_name, ' ', COALESCE(v.last_name, ''))
                ELSE NULL
            END as person_name
        FROM `tabAccess Event` ae
        LEFT JOIN `tabAccess Point` ap ON ae.access_point = ap.name
        LEFT JOIN `tabHuman Profile` hp ON ae.human_profile = hp.name
        LEFT JOIN `tabVisitor` v ON ae.visitor = v.name
        ORDER BY ae.event_time DESC
        LIMIT %s
    """, (int(limit),), as_dict=True)

    return events


@frappe.whitelist()
def get_management_kpis():
    """Get KPI data for the Management dashboard"""
    today = nowdate()
    first_of_month = getdate(today).replace(day=1)

    # Events this month
    events_this_month = frappe.db.count("Access Event", filters={
        "event_time": [">=", first_of_month]
    })

    # Active credentials
    active_credentials = frappe.db.count("Access Credential", filters={
        "status": "Active"
    })

    # Credentials expiring in 30 days
    expiring_soon = frappe.db.count("Access Credential", filters={
        "status": "Active",
        "valid_until": ["between", [today, add_days(today, 30)]]
    })

    # High risk events today
    high_risk_events = frappe.db.count("Access Event", filters={
        "event_time": [">=", today],
        "risk_score": [">=", 70]
    })

    # Device health issues
    device_issues = frappe.db.count("Device Health Log", filters={
        "log_time": [">=", today],
        "status": ["in", ["Degraded", "Offline"]]
    })

    # Total access points
    total_access_points = frappe.db.count("Access Point")

    # Active emergency rules
    active_emergency = frappe.db.count("Emergency Access Rule", filters={
        "status": "Triggered"
    })

    return {
        "events_this_month": events_this_month,
        "active_credentials": active_credentials,
        "expiring_soon": expiring_soon,
        "high_risk_events": high_risk_events,
        "device_issues": device_issues,
        "total_access_points": total_access_points,
        "active_emergency": active_emergency
    }

