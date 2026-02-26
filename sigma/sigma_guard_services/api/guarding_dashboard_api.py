"""
Guarding Services Dashboard API - Enterprise-grade dashboard data
Aligned with ISO 18788, ASIS PAP.1, and modern corporate security operations
"""
import frappe
from frappe import _
from frappe.utils import now, today, getdate, add_days, add_months, get_first_day, get_last_day
from datetime import datetime, timedelta


# ============================================================================
# 1. EXECUTIVE SECURITY DASHBOARD (Board / HOD Level)
# ============================================================================

@frappe.whitelist()
def get_executive_security_dashboard():
    """
    Get executive security dashboard data for board/HOD level
    Quick strategic view of guarding performance, risk exposure, and compliance
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)
        
        # Overall Security Risk Index (site weighted score)
        risk_index = frappe.db.sql("""
            SELECT AVG(COALESCE(vulnerability_score, 50)) as avg_risk
            FROM `tabLocation Security Assessment`
            WHERE status = 'Completed'
        """)[0][0] or 50
        
        # Total Guards Deployed vs Approved Strength
        deployed_guards = frappe.db.count("Security Resource", filters={
            "resource_type": ["in", ["Security Guard", "Security Supervisor"]],
            "status": "Deployed"
        })
        
        approved_strength = frappe.db.count("Security Resource", filters={
            "resource_type": ["in", ["Security Guard", "Security Supervisor"]],
            "status": ["!=", "Retired"]
        })
        
        # High-Risk Sites Needing Urgent Action
        high_risk_sites = frappe.db.count("Location Security Assessment", filters={
            "overall_risk_level": ["in", ["High", "Critical"]],
            "status": ["!=", "Resolved"]
        })
        
        # Monthly guarding expenditure
        monthly_cost = frappe.db.sql("""
            SELECT COALESCE(SUM(surcharge_amount), 0) as total
            FROM `tabSurcharge Record`
            WHERE surcharge_date >= %s AND docstatus = 1
        """, [month_start])[0][0] or 0
        
        # Incident Summary
        incidents_by_type = frappe.db.sql("""
            SELECT category, COUNT(*) as count
            FROM `tabGuard Incident`
            GROUP BY category
            ORDER BY count DESC
        """, as_dict=True)
        
        # Top 5 incident-prone sites
        incident_prone_sites = frappe.db.sql("""
            SELECT l.name as site, COUNT(gi.name) as incident_count
            FROM `tabGuard Incident` gi
            INNER JOIN `tabLocation` l ON gi.location = l.name
            GROUP BY gi.location
            ORDER BY incident_count DESC
            LIMIT 5
        """, as_dict=True)
        
        # Guarding SLA Compliance
        sla_stats = frappe.db.sql("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) as compliant
            FROM `tabSLA Compliance Record`
            WHERE compliance_date >= %s
        """, [month_start], as_dict=True)
        
        sla_compliance = 0
        if sla_stats and sla_stats[0].get("total", 0) > 0:
            sla_compliance = (sla_stats[0].get("compliant", 0) / sla_stats[0]["total"]) * 100
        
        # Patrol completion rate
        patrol_stats = frappe.db.sql("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabPatrol Schedule`
            WHERE patrol_date >= %s
        """, [month_start], as_dict=True)
        
        patrol_completion = 0
        if patrol_stats and patrol_stats[0].get("total", 0) > 0:
            patrol_completion = (patrol_stats[0].get("completed", 0) / patrol_stats[0]["total"]) * 100
        
        # Vendor Scorecard
        vendor_scores = frappe.db.sql("""
            SELECT
                s.supplier_name,
                AVG(CASE WHEN scr.compliance_status = 'Compliant' THEN 100 WHEN scr.compliance_status = 'Partial' THEN 50 ELSE 0 END) as avg_score,
                COUNT(CASE WHEN scr.compliance_status = 'Compliant' THEN 1 END) as compliant_count,
                COUNT(*) as total_records
            FROM `tabSLA Compliance Record` scr
            INNER JOIN `tabContract` c ON scr.service_contract = c.name
            INNER JOIN `tabSupplier` s ON c.supplier = s.name
            GROUP BY s.supplier_name
            ORDER BY avg_score DESC
        """, as_dict=True)
        
        return {
            "security_risk_index": round(risk_index, 1),
            "deployed_guards": deployed_guards,
            "approved_strength": approved_strength,
            "deployment_rate": round((deployed_guards / approved_strength * 100) if approved_strength > 0 else 0, 1),
            "high_risk_sites": high_risk_sites,
            "monthly_cost": monthly_cost,
            "incidents_by_type": incidents_by_type,
            "incident_prone_sites": incident_prone_sites,
            "sla_compliance_rate": round(sla_compliance, 1),
            "patrol_completion_rate": round(patrol_completion, 1),
            "vendor_scores": vendor_scores
        }
    except Exception as e:
        frappe.log_error(f"Executive security dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 2. SECURITY OPERATIONS CENTER (SOC) DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_soc_dashboard():
    """
    Get SOC dashboard data for real-time monitoring
    Guards on duty, patrol status, live incidents, emergency alerts
    """
    try:
        today_date = getdate(today())
        now_time = now()
        
        # Guards on Duty Now
        guards_on_duty = frappe.db.count("Guard Shift", filters={
            "status": "Active"
        })
        
        # Posts Not Manned (Exceptions)
        # Sites with required guards but no active shifts
        unmanned_posts = frappe.db.sql("""
            SELECT COUNT(DISTINCT sa.name) as count
            FROM `tabSite Allocation` sa
            LEFT JOIN `tabGuard Shift` gs ON gs.site_allocation = sa.location AND gs.status = 'Active'
            WHERE sa.status = 'Active' AND gs.name IS NULL
        """)[0][0] or 0
        
        # Real-Time Patrol Status
        patrol_status = frappe.db.sql("""
            SELECT
                status,
                COUNT(*) as count
            FROM `tabPatrol Schedule`
            WHERE patrol_date = %s
            GROUP BY status
        """, [today_date], as_dict=True)

        # Missed checkpoints today
        missed_checkpoints = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabPatrol Verification Record` pvr
            WHERE pvr.patrol_date = %s AND pvr.discrepancies_found = 1
        """, [today_date])[0][0] or 0

        # Live Incident Feed
        live_incidents = frappe.get_all(
            "Guard Incident",
            filters={"incident_status": ["in", ["Open", "Under Investigation"]]},
            fields=["name", "location", "category", "reported_on", "incident_status"],
            order_by="reported_on desc",
            limit=10
        )

        # Shift Change Monitoring - Late check-ins
        late_checkins = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabGuard Shift`
            WHERE DATE(check_in_time) = %s
            AND TIME(check_in_time) > '08:15:00'
        """, [today_date])[0][0] or 0

        # Patrol compliance last 24h
        patrol_24h = frappe.db.sql("""
            SELECT
                HOUR(pvr.verification_time) as hour,
                COUNT(*) as verifications,
                SUM(CASE WHEN pvr.discrepancies_found = 1 THEN 1 ELSE 0 END) as with_discrepancies
            FROM `tabPatrol Verification Record` pvr
            WHERE pvr.verification_time >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
            GROUP BY HOUR(pvr.verification_time)
            ORDER BY hour
        """, as_dict=True)

        # Site status matrix
        site_status = frappe.db.sql("""
            SELECT
                lsa.overall_risk_level,
                COUNT(*) as count
            FROM `tabLocation Security Assessment` lsa
            WHERE lsa.status = 'Completed'
            GROUP BY lsa.overall_risk_level
        """, as_dict=True)

        return {
            "guards_on_duty": guards_on_duty,
            "unmanned_posts": unmanned_posts,
            "patrol_status": patrol_status,
            "missed_checkpoints": missed_checkpoints,
            "live_incidents": live_incidents,
            "late_checkins": late_checkins,
            "patrol_24h": patrol_24h,
            "site_status": site_status
        }
    except Exception as e:
        frappe.log_error(f"SOC dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 3. GUARD SUPERVISOR DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_guard_supervisor_dashboard():
    """
    Get guard supervisor dashboard data
    Daily assignments, shift discipline, equipment, OB summary
    """
    try:
        today_date = getdate(today())

        # Today's Roster - Guards per shift
        roster_by_shift = frappe.db.sql("""
            SELECT
                CASE
                    WHEN HOUR(check_in_time) < 14 THEN 'Day Shift'
                    ELSE 'Night Shift'
                END as shift_type,
                COUNT(*) as count
            FROM `tabGuard Shift`
            WHERE DATE(check_in_time) = %s
            GROUP BY shift_type
        """, [today_date], as_dict=True)

        # Vacant posts
        vacant_posts = frappe.db.sql("""
            SELECT sa.location, sa.name
            FROM `tabSite Allocation` sa
            LEFT JOIN `tabGuard Shift` gs ON gs.site_allocation = sa.location AND gs.status = 'Active'
            WHERE sa.status = 'Active' AND gs.name IS NULL
            LIMIT 10
        """, as_dict=True)

        # Attendance Exceptions - Late arrivals
        late_arrivals = frappe.db.sql("""
            SELECT gs.guard_name, gs.site_allocation, gs.check_in_time
            FROM `tabGuard Shift` gs
            WHERE DATE(gs.check_in_time) = %s
            AND TIME(gs.check_in_time) > '08:15:00'
            LIMIT 10
        """, [today_date], as_dict=True)

        # No-shows (expected but not checked in)
        no_shows = frappe.db.sql("""
            SELECT COUNT(*) as count
            FROM `tabGuard Deployment Schedule` gds
            WHERE gds.deployment_date = %s
            AND gds.status = 'Scheduled'
            AND NOT EXISTS (
                SELECT 1 FROM `tabGuard Shift` gs
                WHERE DATE(gs.check_in_time) = %s
            )
        """, [today_date, today_date])[0][0] or 0

        # Equipment Issued summary
        equipment_issued = frappe.db.sql("""
            SELECT
                sr.resource_type,
                sr.status,
                COUNT(*) as count
            FROM `tabSecurity Resource` sr
            WHERE sr.resource_type = 'Security Equipment'
            GROUP BY sr.resource_type, sr.status
        """, as_dict=True)

        # Guard Activity summary (OB entries)
        ob_entries = frappe.get_all(
            "Guard Activity",
            filters={"creation": [">=", today_date]},
            fields=["name", "description", "creation"],
            order_by="creation desc",
            limit=10
        )

        # Post Inspection Status
        post_inspections = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN discrepancies_found = 0 THEN 1 ELSE 0 END) as passed
            FROM `tabPatrol Verification Record`
            WHERE patrol_date >= DATE_SUB(%s, INTERVAL 7 DAY)
        """, [today_date], as_dict=True)

        return {
            "roster_by_shift": roster_by_shift,
            "vacant_posts": vacant_posts,
            "late_arrivals": late_arrivals,
            "no_shows": no_shows,
            "equipment_issued": equipment_issued,
            "ob_entries": ob_entries,
            "post_inspections": post_inspections
        }
    except Exception as e:
        frappe.log_error(f"Guard supervisor dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 4. GUARD FORCE PERFORMANCE DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_guard_performance_dashboard():
    """
    Get guard force performance dashboard data
    Patrol completion, response time, attendance, training compliance
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Patrol Completion Rate
        patrol_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabPatrol Schedule`
            WHERE patrol_date >= %s
        """, [month_start], as_dict=True)

        patrol_completion = 0
        if patrol_stats and patrol_stats[0].get("total", 0) > 0:
            patrol_completion = (patrol_stats[0].get("completed", 0) / patrol_stats[0]["total"]) * 100

        # Missed Checkpoints Rate
        checkpoint_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN discrepancies_found = 1 THEN 1 ELSE 0 END) as missed
            FROM `tabPatrol Verification Record`
            WHERE patrol_date >= %s
        """, [month_start], as_dict=True)

        missed_rate = 0
        if checkpoint_stats and checkpoint_stats[0].get("total", 0) > 0:
            missed_rate = (checkpoint_stats[0].get("missed", 0) / checkpoint_stats[0]["total"]) * 100

        # Attendance Scorecard
        attendance_stats = frappe.db.sql("""
            SELECT
                COUNT(DISTINCT guard_name) as total_guards,
                COUNT(*) as total_shifts,
                SUM(CASE WHEN TIME(check_in_time) <= '08:15:00' THEN 1 ELSE 0 END) as on_time
            FROM `tabGuard Shift`
            WHERE DATE(check_in_time) >= %s
        """, [month_start], as_dict=True)

        # Training Compliance by certification type
        training_compliance = frappe.db.sql("""
            SELECT
                rc.certification_type,
                COUNT(*) as total,
                SUM(CASE WHEN rc.expiry_date > %s OR rc.expiry_date IS NULL THEN 1 ELSE 0 END) as valid
            FROM `tabResource Certification` rc
            GROUP BY rc.certification_type
        """, [today_date], as_dict=True)

        # Top Performing Guards (by patrol completion)
        top_guards = frappe.db.sql("""
            SELECT
                ps.patrol_officer,
                COUNT(*) as total_patrols,
                SUM(CASE WHEN ps.status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabPatrol Schedule` ps
            WHERE ps.patrol_date >= %s
            GROUP BY ps.patrol_officer
            HAVING total_patrols > 5
            ORDER BY (completed / total_patrols) DESC
            LIMIT 10
        """, [month_start], as_dict=True)

        # Guards needing retraining (expired certifications)
        needs_retraining = frappe.db.sql("""
            SELECT DISTINCT sr.resource_name, rc.certification_type, rc.expiry_date
            FROM `tabSecurity Resource` sr
            INNER JOIN `tabResource Certification` rc ON rc.parent = sr.name
            WHERE rc.expiry_date < %s
            LIMIT 10
        """, [today_date], as_dict=True)

        # Internal vs Outsourced comparison
        guard_comparison = frappe.db.sql("""
            SELECT
                s.supplier_name,
                COUNT(*) as guard_count,
                AVG(CASE WHEN scr.compliance_status = 'Compliant' THEN 100 WHEN scr.compliance_status = 'Partial' THEN 50 ELSE 80 END) as avg_score
            FROM `tabSecurity Resource` sr
            INNER JOIN `tabSupplier` s ON sr.supplier = s.name
            LEFT JOIN `tabSLA Compliance Record` scr ON scr.service_contract IN (
                SELECT c.name FROM `tabContract` c WHERE c.supplier = s.name
            )
            WHERE sr.resource_type IN ('Security Guard', 'Security Supervisor')
            GROUP BY s.supplier_name
        """, as_dict=True)

        return {
            "patrol_completion_rate": round(patrol_completion, 1),
            "missed_checkpoint_rate": round(missed_rate, 1),
            "attendance_stats": attendance_stats[0] if attendance_stats else {},
            "training_compliance": training_compliance,
            "top_guards": top_guards,
            "needs_retraining": needs_retraining,
            "guard_comparison": guard_comparison
        }
    except Exception as e:
        frappe.log_error(f"Guard performance dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 5. GUARD TOUR (PATROL MONITORING) DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_patrol_monitoring_dashboard():
    """
    Get patrol monitoring dashboard data
    Visual & data-driven patrol compliance tracking
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Patrols scheduled vs completed
        patrol_comparison = frappe.db.sql("""
            SELECT
                DATE(patrol_date) as date,
                COUNT(*) as scheduled,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabPatrol Schedule`
            WHERE patrol_date >= %s
            GROUP BY DATE(patrol_date)
            ORDER BY date
        """, [month_start], as_dict=True)

        # Patrol anomalies
        patrol_anomalies = frappe.db.sql("""
            SELECT
                pvr.patrol_schedule,
                pvr.checkpoint,
                pvr.discrepancy_report
            FROM `tabPatrol Verification Record` pvr
            WHERE pvr.discrepancies_found = 1
            AND pvr.patrol_date >= %s
            ORDER BY pvr.verification_time DESC
            LIMIT 20
        """, [add_days(today_date, -7)], as_dict=True)

        # Most problematic patrol routes
        problematic_routes = frappe.db.sql("""
            SELECT
                ps.name as patrol_route,
                ps.location,
                COUNT(pvr.name) as verification_count,
                SUM(CASE WHEN pvr.discrepancies_found = 1 THEN 1 ELSE 0 END) as discrepancy_count
            FROM `tabPatrol Schedule` ps
            LEFT JOIN `tabPatrol Verification Record` pvr ON pvr.patrol_schedule = ps.name
            GROUP BY ps.name, ps.location
            HAVING discrepancy_count > 0
            ORDER BY discrepancy_count DESC
            LIMIT 10
        """, as_dict=True)

        # Hour-of-day patrol heatmap
        hourly_heatmap = frappe.db.sql("""
            SELECT
                HOUR(verification_time) as hour,
                DAYOFWEEK(patrol_date) as day_of_week,
                COUNT(*) as verification_count
            FROM `tabPatrol Verification Record`
            WHERE patrol_date >= %s
            GROUP BY HOUR(verification_time), DAYOFWEEK(patrol_date)
        """, [month_start], as_dict=True)

        # Checkpoint performance
        checkpoint_stats = frappe.db.sql("""
            SELECT
                pc.checkpoint_name,
                COUNT(pvr.name) as visit_count,
                SUM(CASE WHEN pvr.discrepancies_found = 1 THEN 1 ELSE 0 END) as issues
            FROM `tabPatrol Checkpoint` pc
            LEFT JOIN `tabPatrol Verification Record` pvr ON pvr.checkpoint = pc.name
            WHERE pvr.patrol_date >= %s OR pvr.patrol_date IS NULL
            GROUP BY pc.checkpoint_name
            ORDER BY visit_count DESC
            LIMIT 20
        """, [month_start], as_dict=True)

        return {
            "patrol_comparison": patrol_comparison,
            "patrol_anomalies": patrol_anomalies,
            "problematic_routes": problematic_routes,
            "hourly_heatmap": hourly_heatmap,
            "checkpoint_stats": checkpoint_stats
        }
    except Exception as e:
        frappe.log_error(f"Patrol monitoring dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 6. GUARDING CONTRACT & VENDOR MANAGEMENT DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_vendor_management_dashboard():
    """
    Get vendor management dashboard data
    Monitor outsourced provider performance
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Contracted guards vs actual deployed
        guard_deployment = frappe.db.sql("""
            SELECT
                s.supplier_name,
                COUNT(sr.name) as contracted,
                SUM(CASE WHEN sr.status = 'Deployed' THEN 1 ELSE 0 END) as deployed
            FROM `tabSecurity Resource` sr
            INNER JOIN `tabSupplier` s ON sr.supplier = s.name
            WHERE sr.resource_type IN ('Security Guard', 'Security Supervisor')
            GROUP BY s.supplier_name
        """, as_dict=True)

        # Vendor SLA performance
        vendor_sla = frappe.db.sql("""
            SELECT
                s.supplier_name,
                AVG(CASE WHEN scr.compliance_status = 'Compliant' THEN 100 WHEN scr.compliance_status = 'Partial' THEN 50 ELSE 0 END) as avg_score,
                SUM(CASE WHEN scr.compliance_status = 'Compliant' THEN 1 ELSE 0 END) as compliant,
                COUNT(*) as total
            FROM `tabSLA Compliance Record` scr
            INNER JOIN `tabContract` c ON scr.service_contract = c.name
            INNER JOIN `tabSupplier` s ON c.supplier = s.name
            GROUP BY s.supplier_name
            ORDER BY avg_score DESC
        """, as_dict=True)

        # Cost per site vs performance
        cost_performance = frappe.db.sql("""
            SELECT
                c.supplier,
                l.name as location,
                COALESCE(SUM(sur.surcharge_amount), 0) as total_surcharges,
                AVG(CASE WHEN scr.compliance_status = 'Compliant' THEN 100 WHEN scr.compliance_status = 'Partial' THEN 50 ELSE 0 END) as avg_score
            FROM `tabContract` c
            LEFT JOIN `tabLocation` l ON c.location = l.name
            LEFT JOIN `tabSurcharge Record` sur ON sur.service_contract = c.name
            LEFT JOIN `tabSLA Compliance Record` scr ON scr.service_contract = c.name
            GROUP BY c.supplier, l.name
        """, as_dict=True)

        # Contract renewal alerts (expiring in 30 days)
        expiring_contracts = frappe.get_all(
            "Contract",
            filters={
                "status": "Active",
                "end_date": ["between", [today_date, add_days(today_date, 30)]]
            },
            fields=["name", "supplier", "end_date"],
            order_by="end_date"
        )

        # Expiring licenses & certifications
        expiring_certs = frappe.db.sql("""
            SELECT
                sr.resource_name,
                sr.supplier,
                rc.certification_type,
                rc.expiry_date
            FROM `tabResource Certification` rc
            INNER JOIN `tabSecurity Resource` sr ON rc.parent = sr.name
            WHERE rc.expiry_date BETWEEN %s AND %s
            ORDER BY rc.expiry_date
            LIMIT 20
        """, [today_date, add_days(today_date, 30)], as_dict=True)

        return {
            "guard_deployment": guard_deployment,
            "vendor_sla": vendor_sla,
            "cost_performance": cost_performance,
            "expiring_contracts": expiring_contracts,
            "expiring_certifications": expiring_certs
        }
    except Exception as e:
        frappe.log_error(f"Vendor management dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 7. POST ORDERS & COMPLIANCE DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_post_compliance_dashboard():
    """
    Get post orders and compliance dashboard data
    Ensure guards follow required SOPs
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Post Order Compliance Score
        compliance_score = frappe.db.sql("""
            SELECT AVG(CASE WHEN compliance_status = 'Compliant' THEN 100 WHEN compliance_status = 'Partial' THEN 50 ELSE 0 END) as avg_score
            FROM `tabSLA Compliance Record`
            WHERE compliance_date >= %s
        """, [month_start])[0][0] or 0

        # Supervisor inspections completed
        inspections = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN discrepancies_found = 0 THEN 1 ELSE 0 END) as passed
            FROM `tabPatrol Verification Record`
            WHERE patrol_date >= %s
        """, [month_start], as_dict=True)

        # Non-compliance findings
        non_compliance = frappe.get_all(
            "Discrepancy Report",
            filters={"creation": [">=", month_start]},
            fields=["name", "severity", "status", "description"],
            order_by="creation desc",
            limit=20
        )

        # Repeat violations per site
        repeat_violations = frappe.db.sql("""
            SELECT
                pvr.checkpoint,
                COUNT(*) as violation_count
            FROM `tabPatrol Verification Record` pvr
            WHERE pvr.discrepancies_found = 1
            AND pvr.patrol_date >= %s
            GROUP BY pvr.checkpoint
            HAVING violation_count > 1
            ORDER BY violation_count DESC
            LIMIT 10
        """, [month_start], as_dict=True)

        # Common non-compliance areas
        common_issues = frappe.db.sql("""
            SELECT
                dr.severity,
                COUNT(*) as count
            FROM `tabDiscrepancy Report` dr
            WHERE dr.creation >= %s
            GROUP BY dr.severity
            ORDER BY count DESC
        """, [month_start], as_dict=True)

        # Weekly inspection pass rate
        weekly_rate = frappe.db.sql("""
            SELECT
                WEEK(patrol_date) as week_num,
                COUNT(*) as total,
                SUM(CASE WHEN discrepancies_found = 0 THEN 1 ELSE 0 END) as passed
            FROM `tabPatrol Verification Record`
            WHERE patrol_date >= %s
            GROUP BY WEEK(patrol_date)
            ORDER BY week_num
        """, [add_days(today_date, -30)], as_dict=True)

        return {
            "post_compliance_score": round(compliance_score, 1),
            "inspections": inspections[0] if inspections else {},
            "non_compliance_findings": non_compliance,
            "repeat_violations": repeat_violations,
            "common_issues": common_issues,
            "weekly_rate": weekly_rate
        }
    except Exception as e:
        frappe.log_error(f"Post compliance dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 8. INCIDENT MANAGEMENT & ESCALATION DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_incident_escalation_dashboard():
    """
    Get incident management and escalation dashboard data
    Track incidents linked to guarding operations
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Active incidents by severity
        active_by_severity = frappe.db.sql("""
            SELECT
                category,
                COUNT(*) as count
            FROM `tabGuard Incident`
            WHERE incident_status IN ('Open', 'Under Investigation')
            GROUP BY category
        """, as_dict=True)

        # Total incidents by status
        by_status = frappe.db.sql("""
            SELECT
                incident_status,
                COUNT(*) as count
            FROM `tabGuard Incident`
            GROUP BY incident_status
        """, as_dict=True)

        # Sites with recurring incidents
        recurring_sites = frappe.db.sql("""
            SELECT
                location,
                COUNT(*) as incident_count
            FROM `tabGuard Incident`
            GROUP BY location
            HAVING incident_count > 1
            ORDER BY incident_count DESC
            LIMIT 10
        """, as_dict=True)

        # Incidents over time
        incidents_trend = frappe.db.sql("""
            SELECT
                DATE_FORMAT(reported_on, '%%Y-%%m') as month,
                COUNT(*) as count
            FROM `tabGuard Incident`
            WHERE reported_on >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """, as_dict=True)

        # Incident category breakdown
        category_breakdown = frappe.db.sql("""
            SELECT
                category,
                COUNT(*) as count,
                SUM(CASE WHEN incident_status = 'Resolved' THEN 1 ELSE 0 END) as resolved
            FROM `tabGuard Incident`
            GROUP BY category
            ORDER BY count DESC
        """, as_dict=True)

        # Guard involvement statistics
        guard_incidents = frappe.db.sql("""
            SELECT
                reported_by,
                COUNT(*) as incident_count
            FROM `tabGuard Incident`
            WHERE reported_by IS NOT NULL
            GROUP BY reported_by
            ORDER BY incident_count DESC
            LIMIT 10
        """, as_dict=True)

        return {
            "active_by_severity": active_by_severity,
            "by_status": by_status,
            "recurring_sites": recurring_sites,
            "incidents_trend": incidents_trend,
            "category_breakdown": category_breakdown,
            "guard_incidents": guard_incidents
        }
    except Exception as e:
        frappe.log_error(f"Incident escalation dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 9. GATEHOUSE / ACCESS CONTROL DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_gatehouse_dashboard():
    """
    Get gatehouse / access control dashboard data
    Integrated into guarding if guards operate gates
    """
    try:
        today_date = getdate(today())

        # Try to get visitor data if sigma_visitor_management module exists
        visitors_today = 0
        vehicles_today = 0
        unauthorized_attempts = 0

        try:
            visitors_today = frappe.db.count("Visitor", filters={
                "check_in_time": [">=", today_date]
            })
        except:
            pass

        try:
            vehicles_today = frappe.db.count("Visitor Vehicle", filters={
                "creation": [">=", today_date]
            })
        except:
            pass

        # Guard assignments at gates
        gate_guards = frappe.db.sql("""
            SELECT
                sa.location,
                COUNT(gs.name) as guard_count
            FROM `tabSite Allocation` sa
            LEFT JOIN `tabGuard Shift` gs ON gs.site_allocation = sa.location AND gs.status = 'Active'
            WHERE sa.location LIKE '%%Gate%%' OR sa.location LIKE '%%Entrance%%'
            GROUP BY sa.location
        """, as_dict=True)

        # Visitor Guard Assignments
        vga_stats = frappe.db.sql("""
            SELECT
                status,
                COUNT(*) as count
            FROM `tabVisitor Guard Assignment`
            GROUP BY status
        """, as_dict=True)

        # Emergency evacuations
        evacuations = frappe.get_all(
            "Emergency Evacuation Tracking",
            filters={"status": ["in", ["In Progress", "Initiated"]]},
            fields=["name", "status", "total_visitors", "total_evacuated"],
            order_by="creation desc",
            limit=5
        )

        return {
            "visitors_today": visitors_today,
            "vehicles_today": vehicles_today,
            "gate_guards": gate_guards,
            "vga_stats": vga_stats,
            "active_evacuations": evacuations
        }
    except Exception as e:
        frappe.log_error(f"Gatehouse dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 10. K9 UNIT DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_k9_dashboard():
    """
    Get K9 unit dashboard data
    For high-risk sites with guard dogs
    """
    try:
        today_date = getdate(today())

        # K9 resources
        k9_stats = frappe.db.sql("""
            SELECT
                status,
                COUNT(*) as count
            FROM `tabSecurity Resource`
            WHERE resource_type = 'Guard Dog'
            GROUP BY status
        """, as_dict=True)

        # K9 deployments
        k9_deployed = frappe.db.count("Security Resource", filters={
            "resource_type": "Guard Dog",
            "status": "Deployed"
        })

        # Handler assignments
        handlers = frappe.db.sql("""
            SELECT
                sr.handler,
                COUNT(*) as dog_count
            FROM `tabSecurity Resource` sr
            WHERE sr.resource_type = 'Guard Dog'
            AND sr.handler IS NOT NULL
            GROUP BY sr.handler
        """, as_dict=True)

        # Vet checks due (using certification expiry as proxy)
        vet_checks_due = frappe.db.sql("""
            SELECT
                sr.resource_name,
                rc.certification_type,
                rc.expiry_date
            FROM `tabSecurity Resource` sr
            INNER JOIN `tabResource Certification` rc ON rc.parent = sr.name
            WHERE sr.resource_type = 'Guard Dog'
            AND rc.expiry_date BETWEEN %s AND %s
            ORDER BY rc.expiry_date
        """, [today_date, add_days(today_date, 30)], as_dict=True)

        return {
            "k9_stats": k9_stats,
            "k9_deployed": k9_deployed,
            "handlers": handlers,
            "vet_checks_due": vet_checks_due
        }
    except Exception as e:
        frappe.log_error(f"K9 dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 11. COMBINED SECURITY & RISK DASHBOARD (Strategic)
# ============================================================================

@frappe.whitelist()
def get_combined_security_risk_dashboard():
    """
    Get combined security and risk dashboard data
    Strategic view of security posture
    """
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Sites sorted by risk score
        sites_by_risk = frappe.db.sql("""
            SELECT
                lsa.location,
                lsa.overall_risk_level,
                lsa.vulnerability_score,
                COUNT(gi.name) as incident_count
            FROM `tabLocation Security Assessment` lsa
            LEFT JOIN `tabGuard Incident` gi ON gi.location = lsa.location
            WHERE lsa.status = 'Completed'
            GROUP BY lsa.location, lsa.overall_risk_level, lsa.vulnerability_score
            ORDER BY lsa.vulnerability_score DESC
            LIMIT 20
        """, as_dict=True)

        # Guarding adequacy vs risk
        guarding_adequacy = frappe.db.sql("""
            SELECT
                lsa.location,
                lsa.overall_risk_level,
                COUNT(gs.name) as active_guards
            FROM `tabLocation Security Assessment` lsa
            LEFT JOIN `tabGuard Shift` gs ON gs.site_allocation = lsa.location AND gs.status = 'Active'
            WHERE lsa.status = 'Completed'
            GROUP BY lsa.location, lsa.overall_risk_level
        """, as_dict=True)

        # Risk Level vs Incidents correlation
        risk_incidents = frappe.db.sql("""
            SELECT
                lsa.overall_risk_level,
                COUNT(DISTINCT lsa.location) as site_count,
                COUNT(gi.name) as incident_count
            FROM `tabLocation Security Assessment` lsa
            LEFT JOIN `tabGuard Incident` gi ON gi.location = lsa.location
            WHERE lsa.status = 'Completed'
            GROUP BY lsa.overall_risk_level
            ORDER BY FIELD(lsa.overall_risk_level, 'Critical', 'High', 'Medium', 'Low')
        """, as_dict=True)

        # Cost vs Risk Mitigation Effectiveness
        cost_effectiveness = frappe.db.sql("""
            SELECT
                s.supplier_name,
                COUNT(sr.name) as resources,
                COALESCE(SUM(sur.surcharge_amount), 0) as total_cost,
                AVG(CASE WHEN scr.compliance_status = 'Compliant' THEN 100 WHEN scr.compliance_status = 'Partial' THEN 50 ELSE 0 END) as avg_compliance
            FROM `tabSupplier` s
            LEFT JOIN `tabSecurity Resource` sr ON sr.supplier = s.name
            LEFT JOIN `tabContract` c ON c.supplier = s.name
            LEFT JOIN `tabSurcharge Record` sur ON sur.service_contract = c.name
            LEFT JOIN `tabSLA Compliance Record` scr ON scr.service_contract = c.name
            GROUP BY s.supplier_name
        """, as_dict=True)

        # Overall security index
        security_index = frappe.db.sql("""
            SELECT
                AVG(100 - COALESCE(vulnerability_score, 50)) as security_score
            FROM `tabLocation Security Assessment`
            WHERE status = 'Completed'
        """)[0][0] or 50

        return {
            "sites_by_risk": sites_by_risk,
            "guarding_adequacy": guarding_adequacy,
            "risk_incidents": risk_incidents,
            "cost_effectiveness": cost_effectiveness,
            "security_index": round(security_index, 1)
        }
    except Exception as e:
        frappe.log_error(f"Combined security risk dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# NUMBER CARD METHODS
# ============================================================================

@frappe.whitelist()
def get_guards_on_duty_count():
    """Get count of guards currently on duty"""
    try:
        count = frappe.db.count("Guard Shift", filters={"status": "Active"})
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Guards on duty count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_unmanned_posts_count():
    """Get count of posts that should be manned but aren't"""
    try:
        count = frappe.db.sql("""
            SELECT COUNT(DISTINCT sa.name)
            FROM `tabSite Allocation` sa
            LEFT JOIN `tabGuard Shift` gs ON gs.site_allocation = sa.location AND gs.status = 'Active'
            WHERE sa.status = 'Active' AND gs.name IS NULL
        """)[0][0] or 0
        return {"value": count, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Unmanned posts count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_patrol_completion_rate():
    """Get patrol completion rate for current month"""
    try:
        month_start = get_first_day(getdate(today()))
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabPatrol Schedule`
            WHERE patrol_date >= %s
        """, [month_start], as_dict=True)

        rate = 0
        if stats and stats[0].get("total", 0) > 0:
            rate = (stats[0].get("completed", 0) / stats[0]["total"]) * 100

        return {"value": round(rate, 1), "fieldtype": "Percent"}
    except Exception as e:
        frappe.log_error(f"Patrol completion rate error: {str(e)}")
        return {"value": 0, "fieldtype": "Percent"}


@frappe.whitelist()
def get_sla_compliance_rate():
    """Get SLA compliance rate for current month"""
    try:
        month_start = get_first_day(getdate(today()))
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN compliance_status = 'Compliant' THEN 1 ELSE 0 END) as compliant
            FROM `tabSLA Compliance Record`
            WHERE compliance_date >= %s
        """, [month_start], as_dict=True)

        rate = 0
        if stats and stats[0].get("total", 0) > 0:
            rate = (stats[0].get("compliant", 0) / stats[0]["total"]) * 100

        return {"value": round(rate, 1), "fieldtype": "Percent"}
    except Exception as e:
        frappe.log_error(f"SLA compliance rate error: {str(e)}")
        return {"value": 0, "fieldtype": "Percent"}


@frappe.whitelist()
def get_open_incidents_count():
    """Get count of open guard incidents"""
    try:
        count = frappe.db.count("Guard Incident", filters={
            "incident_status": ["in", ["Open", "Under Investigation"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Open incidents count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_high_risk_sites_count():
    """Get count of high risk sites"""
    try:
        count = frappe.db.count("Location Security Assessment", filters={
            "overall_risk_level": ["in", ["High", "Critical"]],
            "status": "Completed"
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"High risk sites count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_total_guards_deployed():
    """Get total guards currently deployed"""
    try:
        count = frappe.db.count("Security Resource", filters={
            "resource_type": ["in", ["Security Guard", "Security Supervisor"]],
            "status": "Deployed"
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Total guards deployed error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_k9_units_deployed():
    """Get count of K9 units deployed"""
    try:
        count = frappe.db.count("Security Resource", filters={
            "resource_type": "Guard Dog",
            "status": "Deployed"
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"K9 units deployed error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_active_vendors_count():
    """Get count of active security vendors"""
    try:
        count = frappe.db.sql("""
            SELECT COUNT(DISTINCT c.supplier)
            FROM `tabContract` c
            WHERE c.status = 'Active'
        """)[0][0] or 0
        return {"value": count, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Active vendors count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_security_risk_index():
    """Get overall security risk index"""
    try:
        risk_index = frappe.db.sql("""
            SELECT AVG(100 - COALESCE(vulnerability_score, 50)) as security_score
            FROM `tabLocation Security Assessment`
            WHERE status = 'Completed'
        """)[0][0] or 50
        return {"value": round(risk_index, 1), "fieldtype": "Percent"}
    except Exception as e:
        frappe.log_error(f"Security risk index error: {str(e)}")
        return {"value": 50, "fieldtype": "Percent"}

