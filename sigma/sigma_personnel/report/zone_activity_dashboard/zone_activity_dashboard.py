# Copyright (c) 2025, Prismod Technologies Limited and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import now_datetime, getdate, add_days


def execute(filters=None):
    """
    Zone Activity Dashboard
    Real-time overview of zone activity, entries, exits, and alerts
    """
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    return columns, data, None, chart


def get_columns():
    """Define report columns"""
    return [
        {
            "fieldname": "zone",
            "label": _("Zone"),
            "fieldtype": "Link",
            "options": "Zone Configuration",
            "width": 150
        },
        {
            "fieldname": "zone_name",
            "label": _("Zone Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "zone_type",
            "label": _("Type"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "current_count",
            "label": _("Current Count"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "entries_today",
            "label": _("Entries Today"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "exits_today",
            "label": _("Exits Today"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "avg_dwell_time",
            "label": _("Avg Dwell (mins)"),
            "fieldtype": "Float",
            "precision": 1,
            "width": 120
        },
        {
            "fieldname": "alerts_today",
            "label": _("Alerts Today"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "hazard_level",
            "label": _("Hazard Level"),
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 100
        }
    ]


def get_data(filters):
    """Get zone activity data"""
    today = getdate()

    # Get all zones
    zones = frappe.get_all("Zone Configuration",
        filters={"is_active": 1},
        fields=["name", "zone_name", "zone_type", "hazard_level", "max_occupancy"]
    )
    
    data = []
    for zone in zones:
        # Current count (active presences)
        current_count = frappe.db.count("Zone Presence", {
            "zone": zone.name,
            "status": "Active"
        })
        
        # Entries today
        entries_today = frappe.db.count("Zone Presence", {
            "zone": zone.name,
            "time_entered": [">=", today]
        })
        
        # Exits today
        exits_today = frappe.db.count("Zone Presence", {
            "zone": zone.name,
            "time_exited": [">=", today],
            "status": "Exited"
        })
        
        # Average dwell time (in minutes)
        avg_dwell = frappe.db.sql("""
            SELECT AVG(TIMESTAMPDIFF(MINUTE, time_entered, COALESCE(time_exited, NOW())))
            FROM `tabZone Presence`
            WHERE zone = %s AND time_entered >= %s
        """, (zone.name, today))[0][0] or 0
        
        # Alerts today
        alerts_today = frappe.db.count("Zone Breach Alerts", {
            "zone": zone.name,
            "creation": [">=", today]
        })
        
        # Determine status
        status = "Normal"
        if zone.max_occupancy and current_count >= zone.max_occupancy:
            status = "At Capacity"
        elif alerts_today > 0:
            status = "Has Alerts"
        elif current_count == 0:
            status = "Empty"
        
        data.append({
            "zone": zone.name,
            "zone_name": zone.zone_name,
            "zone_type": zone.zone_type,
            "current_count": current_count,
            "entries_today": entries_today,
            "exits_today": exits_today,
            "avg_dwell_time": round(avg_dwell, 1) if avg_dwell else 0,
            "alerts_today": alerts_today,
            "hazard_level": zone.hazard_level,
            "status": status
        })
    
    return data


def get_chart_data(data):
    """Generate chart for zone activity"""
    labels = [d["zone_name"] for d in data[:10]]  # Top 10 zones
    entries = [d["entries_today"] for d in data[:10]]
    exits = [d["exits_today"] for d in data[:10]]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Entries", "values": entries},
                {"name": "Exits", "values": exits}
            ]
        },
        "type": "bar",
        "colors": ["#4CAF50", "#F44336"]
    }

