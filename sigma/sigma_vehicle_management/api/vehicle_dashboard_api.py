"""
Vehicle Dashboard API
Provides data for all 8 vehicle management dashboards
"""
import frappe
from frappe import _
from datetime import datetime, timedelta
import random

@frappe.whitelist()
def get_gate_traffic_dashboard(gate="all"):
    """Unified Gate & Traffic Dashboard - Live monitoring"""
    # Mock data for demonstration - replace with actual queries
    return {
        "companyVehiclesOnsite": random.randint(45, 65),
        "staffVehiclesOnsite": random.randint(120, 180),
        "visitorVehiclesOnsite": random.randint(15, 35),
        "entriesToday": random.randint(200, 350),
        "exitsToday": random.randint(180, 320),
        "unauthorizedAttempts": random.randint(0, 5),
        "awaitingApproval": random.randint(2, 10),
        "liveFeed": _get_live_feed(),
        "hourlyTraffic": _get_hourly_traffic(),
        "gateTraffic": _get_gate_traffic()
    }

@frappe.whitelist()
def get_fleet_operations_dashboard(department="all"):
    """Company Fleet Operations Dashboard"""
    return {
        "activeOnRoad": random.randint(25, 45),
        "parkedAtYards": random.randint(60, 90),
        "inMaintenance": random.randint(5, 15),
        "unavailable": random.randint(2, 8),
        "activeDrivers": random.randint(30, 50),
        "engineHours": [{"vehicle": f"KBZ {100+i}A", "hours": random.randint(50, 200)} for i in range(8)],
        "fuelUsage": [{"date": f"Dec {i+1}", "liters": random.randint(800, 1500)} for i in range(14)],
        "routeDeviations": [{"vehicle": f"KBZ {100+i}A", "count": random.randint(0, 5)} for i in range(6)],
        "workOrders": _get_work_orders(),
        "driverBehavior": {"speed": 85, "braking": 78, "acceleration": 82, "idling": 70, "fuel_efficiency": 88},
        "fleetInventory": _get_fleet_inventory()
    }

@frappe.whitelist()
def get_staff_vehicle_dashboard(location="all"):
    """Staff Vehicle Dashboard"""
    return {
        "parkingOccupancy": random.randint(65, 95),
        "vehiclesInside": random.randint(100, 180),
        "pastAllowedTime": random.randint(3, 12),
        "gateUsagePerHour": random.randint(15, 35),
        "departmentEntries": [
            {"department": "Engineering", "count": random.randint(30, 50)},
            {"department": "Operations", "count": random.randint(25, 45)},
            {"department": "Finance", "count": random.randint(15, 30)},
            {"department": "HR", "count": random.randint(10, 25)},
            {"department": "IT", "count": random.randint(20, 35)}
        ],
        "gateLoadHourly": [{"hour": f"{6+i}:00", "count": random.randint(5, 40)} for i in range(12)],
        "zoneOccupancy": [
            {"zone": "Zone A", "occupied": random.randint(30, 45), "available": random.randint(5, 20)},
            {"zone": "Zone B", "occupied": random.randint(25, 40), "available": random.randint(10, 25)},
            {"zone": "Zone C", "occupied": random.randint(20, 35), "available": random.randint(15, 30)},
            {"zone": "Zone D", "occupied": random.randint(15, 30), "available": random.randint(20, 35)}
        ],
        "registeredVehicles": _get_staff_vehicles()
    }

@frappe.whitelist()
def get_visitor_vehicle_dashboard(date_range="today"):
    """Visitor Vehicle Management Dashboard"""
    return {
        "expectedToday": random.randint(20, 40),
        "approved": random.randint(15, 35),
        "pendingApproval": random.randint(2, 8),
        "parkedOnsite": random.randint(10, 25),
        "overstayVehicles": random.randint(1, 5),
        "byPurpose": [
            {"purpose": "Meeting", "count": random.randint(8, 15)},
            {"purpose": "Delivery", "count": random.randint(5, 12)},
            {"purpose": "Maintenance", "count": random.randint(3, 8)},
            {"purpose": "Interview", "count": random.randint(2, 6)},
            {"purpose": "Other", "count": random.randint(1, 5)}
        ],
        "byVendor": [{"vendor": f"Vendor {chr(65+i)}", "count": random.randint(3, 12)} for i in range(6)],
        "byDepartment": [
            {"department": "Procurement", "count": random.randint(5, 15)},
            {"department": "Engineering", "count": random.randint(4, 12)},
            {"department": "HR", "count": random.randint(3, 10)},
            {"department": "IT", "count": random.randint(2, 8)}
        ],
        "activeVehicles": _get_visitor_vehicles(),
        "preRegistered": _get_preregistered_vehicles(),
        "anprHits": _get_anpr_hits()
    }

@frappe.whitelist()
def get_vehicle_access_control_dashboard(vehicle_type="all", date_range="today"):
    """Vehicle Access Control Dashboard - ISO Compliant"""
    return {
        "successfulEntries": random.randint(200, 350),
        "deniedEntries": random.randint(5, 20),
        "suspiciousAttempts": random.randint(1, 8),
        "anprMismatches": random.randint(2, 10),
        "expiredPasses": random.randint(3, 12),
        "companyAccess": {"allowed": random.randint(50, 80), "denied": random.randint(0, 3)},
        "staffAccess": {"allowed": random.randint(120, 180), "denied": random.randint(2, 8)},
        "visitorAccess": {"allowed": random.randint(25, 45), "denied": random.randint(3, 10)},
        "accessTrends": [{"hour": f"{6+i}:00", "company": random.randint(3, 10), "staff": random.randint(8, 25), "visitor": random.randint(1, 8)} for i in range(12)],
        "denialReasons": [
            {"reason": "Expired Pass", "count": random.randint(3, 8)},
            {"reason": "Not Registered", "count": random.randint(2, 6)},
            {"reason": "No Approval", "count": random.randint(2, 5)},
            {"reason": "ANPR Mismatch", "count": random.randint(1, 4)},
            {"reason": "Blacklisted", "count": random.randint(0, 2)}
        ],
        "accessEvents": _get_access_events(),
        "securityAlerts": _get_security_alerts()
    }

@frappe.whitelist()
def get_vehicle_maintenance_dashboard(department="all"):
    """Vehicle Maintenance & Health Dashboard"""
    return {
        "dueForService": random.randint(8, 18),
        "fuelCostPerVehicle": random.randint(15000, 35000),
        "maintenanceCost": random.randint(250000, 500000),
        "faultCodeAlerts": random.randint(2, 8),
        "batteryIssues": random.randint(1, 5),
        "serviceDue": _get_service_due(),
        "departmentCosts": [
            {"department": "Operations", "cost": random.randint(80000, 150000)},
            {"department": "Engineering", "cost": random.randint(60000, 120000)},
            {"department": "Corporate", "cost": random.randint(40000, 80000)},
            {"department": "Regional", "cost": random.randint(50000, 100000)}
        ],
        "fuelTrend": [{"month": f"Week {i+1}", "liters": random.randint(3000, 6000)} for i in range(4)],
        "vehicleFuel": [{"vehicle": f"KBZ {100+i}A", "cost": random.randint(8000, 25000)} for i in range(8)],
        "faultCodes": _get_fault_codes(),
        "batteryReport": _get_battery_report(),
        "maintenanceHistory": _get_maintenance_history()
    }

@frappe.whitelist()
def get_vehicle_security_dashboard(date_range="today"):
    """Vehicle Security & Incident Dashboard"""
    return {
        "restrictedZoneEntries": random.randint(2, 10),
        "nightEntries": random.randint(5, 20),
        "humanVehicleIncidents": random.randint(0, 5),
        "stolenPlates": random.randint(0, 3),
        "routeViolations": random.randint(3, 12),
        "totalAlerts": random.randint(10, 30),
        "specialAlerts": _get_special_alerts(),
        "restrictedByType": [
            {"type": "Company", "count": random.randint(1, 4)},
            {"type": "Staff", "count": random.randint(0, 3)},
            {"type": "Visitor", "count": random.randint(1, 5)}
        ],
        "nightByType": [
            {"type": "Company", "count": random.randint(3, 10)},
            {"type": "Staff", "count": random.randint(2, 8)},
            {"type": "Visitor", "count": random.randint(0, 4)}
        ],
        "routeViolationsList": _get_route_violations(),
        "tailgatingIncidents": _get_tailgating_incidents(),
        "incidentCorrelation": _get_incident_correlation(),
        "stolenDetections": _get_stolen_detections()
    }

@frappe.whitelist()
def get_parking_management_dashboard(location="all"):
    """Parking Management Dashboard"""
    total_capacity = random.randint(300, 400)
    company_occ = random.randint(40, 60)
    staff_occ = random.randint(100, 150)
    visitor_occ = random.randint(15, 30)
    total_occupied = company_occ + staff_occ + visitor_occ

    return {
        "totalCapacity": total_capacity,
        "companyOccupancy": company_occ,
        "staffOccupancy": staff_occ,
        "visitorOccupancy": visitor_occ,
        "violations": random.randint(3, 12),
        "totalOccupied": total_occupied,
        "totalAvailable": total_capacity - total_occupied,
        "zoneOccupancy": [
            {"zone": "Zone A - Executive", "occupied": random.randint(20, 35), "available": random.randint(5, 15)},
            {"zone": "Zone B - Staff", "occupied": random.randint(50, 80), "available": random.randint(10, 30)},
            {"zone": "Zone C - Visitor", "occupied": random.randint(15, 25), "available": random.randint(15, 25)},
            {"zone": "Zone D - Overflow", "occupied": random.randint(10, 25), "available": random.randint(25, 50)}
        ],
        "reservedUtilization": [
            {"category": "Executive", "used": random.randint(8, 15), "unused": random.randint(2, 7)},
            {"category": "Disabled", "used": random.randint(2, 5), "unused": random.randint(3, 8)},
            {"category": "Visitor VIP", "used": random.randint(3, 8), "unused": random.randint(2, 7)}
        ],
        "parkingSlots": _get_parking_slots(),
        "overstaying": _get_overstaying_vehicles(),
        "wrongZone": _get_wrong_zone_violations(),
        "unidentified": _get_unidentified_vehicles()
    }

# Helper functions for mock data
def _get_live_feed():
    categories = ["Company", "Staff", "Visitor"]
    gates = ["Main Gate", "Staff Gate", "Service Gate"]
    zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
    alerts = ["None", "None", "None", "Warning", "Danger"]
    return [
        {
            "plate_number": f"K{chr(65+i%3)}{chr(65+i%2)} {100+i*11}{chr(65+i%4)}",
            "category": categories[i % 3],
            "driver": f"{'Driver' if i%3==0 else 'Employee' if i%3==1 else 'Visitor'} {i+1}",
            "gate": gates[i % 3],
            "timestamp": f"{8+i//4}:{(i*7)%60:02d}",
            "zone": zones[i % 4],
            "alert": alerts[i % 5]
        } for i in range(15)
    ]

def _get_hourly_traffic():
    return [{"hour": f"{6+i}:00", "entries": random.randint(10, 50), "exits": random.randint(8, 45)} for i in range(14)]

def _get_gate_traffic():
    return [
        {"gate": "Main Gate", "company": random.randint(20, 40), "staff": random.randint(50, 80), "visitor": random.randint(15, 30)},
        {"gate": "Staff Gate", "company": random.randint(10, 25), "staff": random.randint(60, 100), "visitor": random.randint(5, 15)},
        {"gate": "Service Gate", "company": random.randint(15, 30), "staff": random.randint(10, 25), "visitor": random.randint(8, 20)},
        {"gate": "Emergency Gate", "company": random.randint(2, 8), "staff": random.randint(3, 10), "visitor": random.randint(0, 5)}
    ]

def _get_work_orders():
    statuses = ["In Progress", "Pending", "Completed"]
    return [
        {"vehicle": f"KBZ {100+i}A", "driver": f"Driver {i+1}", "task": f"Task {i+1}", "location": f"Site {chr(65+i)}", "status": statuses[i % 3]}
        for i in range(8)
    ]

def _get_fleet_inventory():
    statuses = ["Active", "In Maintenance", "Parked", "On Route"]
    return [
        {"plate": f"KBZ {100+i}A", "make_model": ["Toyota Hilux", "Isuzu D-Max", "Nissan Navara", "Ford Ranger"][i%4],
         "department": ["Operations", "Engineering", "Corporate", "Regional"][i%4], "assigned_driver": f"Driver {i+1}",
         "status": statuses[i % 4], "last_location": f"Location {chr(65+i)}"}
        for i in range(12)
    ]

def _get_staff_vehicles():
    levels = ["Full Access", "Limited", "Restricted", "Temporary"]
    statuses = ["Active", "Active", "Active", "Expired"]
    return [
        {"plate_number": f"KD{chr(65+i)} {200+i*11}{chr(65+i%3)}", "employee_name": f"Employee {i+1}",
         "department": ["Engineering", "Operations", "Finance", "HR", "IT"][i%5], "employee_id": f"EMP{1000+i}",
         "access_level": levels[i % 4], "last_entry": f"{8+i//3}:{(i*12)%60:02d}", "status": statuses[i % 4]}
        for i in range(15)
    ]

def _get_visitor_vehicles():
    statuses = ["Checked In", "Checked In", "Overstay", "Pending Exit"]
    return [
        {"plate_number": f"KE{chr(65+i)} {300+i*7}{chr(66+i%2)}", "visitor_name": f"Visitor {i+1}",
         "company": f"Company {chr(65+i)}", "purpose": ["Meeting", "Delivery", "Maintenance", "Interview"][i%4],
         "host": f"Host Employee {i+1}", "entry_time": f"{9+i//2}:{(i*15)%60:02d}", "status": statuses[i % 4]}
        for i in range(10)
    ]

def _get_preregistered_vehicles():
    statuses = ["Approved", "Pending", "Approved", "Rejected"]
    return [
        {"plate_number": f"KF{chr(65+i)} {400+i*9}{chr(65+i%3)}", "visitor_name": f"Pre-Visitor {i+1}",
         "company": f"Vendor {chr(65+i)}", "expected_date": f"Dec {14+i}", "host": f"Host {i+1}", "approval_status": statuses[i % 4]}
        for i in range(8)
    ]

def _get_anpr_hits():
    matches = ["Matched", "Matched", "Unmatched", "Partial"]
    return [
        {"plate_number": f"KG{chr(65+i)} {500+i*11}{chr(65+i%2)}", "camera": f"CAM-{chr(65+i)}",
         "timestamp": f"{10+i//2}:{(i*8)%60:02d}", "match_status": matches[i % 4], "host_responsible": f"Host {i+1}" if i%4 != 2 else "Unknown"}
        for i in range(10)
    ]

def _get_access_events():
    types = ["Company", "Staff", "Visitor"]
    actions = ["Entry Allowed", "Entry Allowed", "Entry Denied", "Exit"]
    return [
        {"timestamp": f"{8+i//3}:{(i*7)%60:02d}", "plate_number": f"K{chr(65+i%3)}{chr(66+i%2)} {100+i*8}{chr(65+i%4)}",
         "vehicle_type": types[i % 3], "gate": ["Main Gate", "Staff Gate", "Service Gate"][i%3],
         "action": actions[i % 4], "reason": "Authorized" if i%4 != 2 else "Pass Expired", "operator": f"Guard {i%3+1}"}
        for i in range(15)
    ]

def _get_security_alerts():
    severities = ["high", "medium", "low", "high"]
    return [
        {"id": i+1, "message": ["Unauthorized entry attempt", "ANPR mismatch detected", "Vehicle overstay alert", "Restricted zone breach"][i%4],
         "severity": severities[i % 4], "timestamp": f"{9+i}:{(i*12)%60:02d}", "acknowledged": i % 3 == 0}
        for i in range(6)
    ]

def _get_service_due():
    priorities = ["High", "Medium", "Low", "High"]
    return [
        {"vehicle": f"KBZ {100+i}A", "last_service": f"Nov {1+i*3}", "next_due": f"Dec {15+i*2}",
         "mileage": f"{45000+i*5000:,} km", "service_type": ["Oil Change", "Full Service", "Brake Check", "Tire Rotation"][i%4],
         "priority": priorities[i % 4]}
        for i in range(10)
    ]

def _get_fault_codes():
    severities = ["Critical", "Warning", "Info", "Critical"]
    return [
        {"vehicle": f"KBZ {100+i}A", "code": f"P0{300+i*10}", "description": ["Engine Misfire", "O2 Sensor", "Coolant Temp", "Battery Low"][i%4],
         "severity": severities[i % 4], "detected": f"Dec {10+i}"}
        for i in range(6)
    ]

def _get_battery_report():
    statuses = ["Good", "Good", "Warning", "Critical"]
    return [
        {"vehicle": f"KBZ {100+i}A", "voltage": f"{12.2+random.random():.1f}V", "health": random.randint(40, 100),
         "age_months": random.randint(6, 48), "status": statuses[i % 4]}
        for i in range(8)
    ]

def _get_maintenance_history():
    statuses = ["Completed", "Completed", "In Progress", "Scheduled"]
    return [
        {"vehicle": f"KBZ {100+i}A", "date": f"Dec {1+i*2}", "service_type": ["Oil Change", "Brake Service", "Tire Replacement", "Full Service"][i%4],
         "cost": random.randint(5000, 50000), "vendor": f"Garage {chr(65+i%3)}", "status": statuses[i % 4]}
        for i in range(12)
    ]

def _get_special_alerts():
    severities = ["high", "high", "medium", "high"]
    return [
        {"id": i+1, "message": ["Company vehicle out-of-route detected", "Visitor vehicle near restricted substation",
                               "Staff vehicle tailgating behavior", "Unauthorized night entry attempt"][i%4],
         "severity": severities[i % 4], "timestamp": f"{8+i*2}:{(i*15)%60:02d}", "acknowledged": False}
        for i in range(4)
    ]

def _get_route_violations():
    types = ["Visitor", "Contractor", "Visitor", "Staff"]
    return [
        {"plate": f"KH{chr(65+i)} {600+i*7}{chr(65+i%3)}", "type": types[i % 4], "driver": f"{'Visitor' if i%2==0 else 'Contractor'} {i+1}",
         "violation": ["Entered restricted area", "Deviated from route", "Unauthorized stop", "Wrong exit used"][i%4],
         "location": f"Zone {chr(65+i)}", "timestamp": f"{10+i}:{(i*10)%60:02d}"}
        for i in range(8)
    ]

def _get_tailgating_incidents():
    statuses = ["Confirmed", "Under Review", "Confirmed", "False Alarm"]
    return [
        {"lead_vehicle": f"KI{chr(65+i)} {700+i*5}A", "follow_vehicle": f"KJ{chr(65+i)} {800+i*3}B",
         "gate": ["Main Gate", "Staff Gate", "Service Gate"][i%3], "timestamp": f"{9+i}:{(i*12)%60:02d}", "status": statuses[i % 4]}
        for i in range(6)
    ]

def _get_incident_correlation():
    severities = ["High", "Medium", "Low", "Critical"]
    return [
        {"incident_id": f"INC-{1000+i}", "vehicle": f"KK{chr(65+i)} {900+i*6}{chr(65+i%2)}",
         "person": f"Person {i+1}", "type": ["Unauthorized Access", "Safety Violation", "Security Breach", "Policy Violation"][i%4],
         "description": f"Incident description {i+1}", "timestamp": f"{8+i*2}:{(i*8)%60:02d}", "severity": severities[i % 4]}
        for i in range(8)
    ]

def _get_stolen_detections():
    types = ["Stolen Plate", "Cloned Plate", "Mismatched", "Stolen Plate"]
    statuses = ["Escalated", "Under Investigation", "Resolved", "Escalated"]
    return [
        {"plate": f"KL{chr(65+i)} {950+i*4}{chr(65+i%3)}", "detection_time": f"{11+i}:{(i*7)%60:02d}",
         "camera": f"ANPR-{chr(65+i)}", "match_type": types[i % 4], "action_taken": ["Security notified", "Police alerted", "Vehicle detained", "Under monitoring"][i%4],
         "status": statuses[i % 4]}
        for i in range(5)
    ]

def _get_parking_slots():
    statuses = ["empty", "company", "staff", "visitor", "violation"]
    return [{"zone": f"Z{i//10+1}", "status": statuses[random.randint(0, 4)], "plate": None if random.random() > 0.7 else f"K{chr(65+i%5)} {i*11}"} for i in range(40)]

def _get_overstaying_vehicles():
    types = ["Staff", "Visitor", "Staff", "Visitor"]
    return [
        {"plate": f"KM{chr(65+i)} {100+i*9}{chr(65+i%2)}", "type": types[i % 4], "zone": f"Zone {chr(65+i%4)}",
         "entry_time": f"{7+i}:00", "duration": f"{4+i*2}h {(i*15)%60}m", "allowed": "8h" if i%2==0 else "4h"}
        for i in range(6)
    ]

def _get_wrong_zone_violations():
    types = ["Staff", "Visitor", "Company", "Visitor"]
    return [
        {"plate": f"KN{chr(65+i)} {200+i*7}{chr(65+i%3)}", "type": types[i % 4],
         "assigned_zone": f"Zone {chr(65+i%4)}", "actual_zone": f"Zone {chr(66+i%3)}", "timestamp": f"{9+i}:{(i*8)%60:02d}"}
        for i in range(5)
    ]

def _get_unidentified_vehicles():
    statuses = ["Under Review", "Flagged", "Cleared", "Under Review"]
    return [
        {"plate": f"KO{chr(65+i)} {300+i*6}{chr(65+i%2)}", "zone": f"Zone {chr(65+i%4)}",
         "entry_time": f"{10+i}:{(i*10)%60:02d}", "camera": f"CAM-{i+1}", "status": statuses[i % 4]}
        for i in range(6)
    ]

