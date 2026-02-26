"""
Dashboard API - Comprehensive dashboard data for Case Management
Provides data for all 13 specialized dashboards as per KPLC requirements
"""
import frappe
from frappe import _
from frappe.utils import now, today, getdate, add_days, add_months, get_first_day, get_last_day
from datetime import datetime, timedelta


# ============================================================================
# 1. EXECUTIVE CASE OVERVIEW DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_executive_overview():
    """
    Get executive overview data for board-level dashboard
    KPIs: Total Cases (YTD/MTD), Open Cases, Closed Cases, High Severity, SLA Breach
    """
    try:
        today_date = getdate(today())
        year_start = today_date.replace(month=1, day=1)
        month_start = get_first_day(today_date)
        
        # Total cases YTD
        total_cases_ytd = frappe.db.count("Case", filters={
            "date_reported": [">=", year_start]
        })
        
        # Total cases MTD
        total_cases_mtd = frappe.db.count("Case", filters={
            "date_reported": [">=", month_start]
        })
        
        # Open cases
        open_cases = frappe.db.count("Case", filters={
            "status": ["in", ["Open", "Under Investigation", "Waiting for Information"]]
        })
        
        # Closed cases
        closed_cases = frappe.db.count("Case", filters={
            "status": "Closed"
        })
        
        # High severity cases (Critical and High)
        high_severity = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
            WHERE sm.severity_level IN ('Critical', 'High')
            AND c.status NOT IN ('Closed', 'Rejected')
        """)[0][0] or 0
        
        # Cases breaching SLA
        sla_breached = frappe.db.count("Case", filters={
            "status": ["not in", ["Closed", "Rejected"]],
            "sla_due_date": ["<", today_date]
        })
        
        # Average time to close (days)
        avg_close_time = frappe.db.sql("""
            SELECT AVG(DATEDIFF(actual_closure_date, date_reported))
            FROM `tabCase`
            WHERE status = 'Closed' AND actual_closure_date IS NOT NULL
            AND date_reported >= %s
        """, [year_start])[0][0] or 0
        
        # Top 5 risk areas by case count
        top_risk_areas = frappe.db.sql("""
            SELECT case_category, COUNT(*) as count
            FROM `tabCase`
            WHERE status NOT IN ('Closed', 'Rejected')
            GROUP BY case_category
            ORDER BY count DESC
            LIMIT 5
        """, as_dict=True)
        
        return {
            "total_cases_ytd": total_cases_ytd,
            "total_cases_mtd": total_cases_mtd,
            "open_cases": open_cases,
            "closed_cases": closed_cases,
            "high_severity_cases": high_severity,
            "sla_breached_cases": sla_breached,
            "avg_days_to_close": round(avg_close_time, 1),
            "top_risk_areas": top_risk_areas
        }
    except Exception as e:
        frappe.log_error(f"Executive overview error: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_case_distribution_by_type():
    """Get case distribution by type for pie chart"""
    return frappe.db.sql("""
        SELECT case_type as label, COUNT(*) as value
        FROM `tabCase`
        GROUP BY case_type
        ORDER BY value DESC
    """, as_dict=True)


@frappe.whitelist()
def get_case_severity_heatmap():
    """Get severity distribution for heatmap"""
    return frappe.db.sql("""
        SELECT 
            c.severity,
            sm.severity_level,
            c.status,
            COUNT(*) as count
        FROM `tabCase` c
        LEFT JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
        GROUP BY c.severity, sm.severity_level, c.status
        ORDER BY sm.severity_level, c.status
    """, as_dict=True)


@frappe.whitelist()
def get_cases_over_time(period="monthly"):
    """Get cases trend over time"""
    if period == "daily":
        date_format = "%Y-%m-%d"
        group_by = "DATE(date_reported)"
    elif period == "weekly":
        date_format = "%Y-W%u"
        group_by = "DATE_FORMAT(date_reported, '%Y-W%u')"
    elif period == "quarterly":
        date_format = "%Y-Q"
        group_by = "CONCAT(YEAR(date_reported), '-Q', QUARTER(date_reported))"
    else:  # monthly
        date_format = "%Y-%m"
        group_by = "DATE_FORMAT(date_reported, '%Y-%m')"
    
    return frappe.db.sql(f"""
        SELECT 
            {group_by} as period,
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) as closed,
            SUM(CASE WHEN status IN ('Open', 'Under Investigation') THEN 1 ELSE 0 END) as open
        FROM `tabCase`
        WHERE date_reported >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY {group_by}
        ORDER BY period
    """, as_dict=True)


@frappe.whitelist()
def get_cases_by_business_unit():
    """Get cases by business unit/region"""
    return frappe.db.sql("""
        SELECT
            COALESCE(business_unit, 'Unassigned') as business_unit,
            COALESCE(region, 'Unassigned') as region,
            COUNT(*) as count,
            SUM(CASE WHEN status NOT IN ('Closed', 'Rejected') THEN 1 ELSE 0 END) as open_count
        FROM `tabCase`
        GROUP BY business_unit, region
        ORDER BY count DESC
    """, as_dict=True)


@frappe.whitelist()
def get_case_outcomes():
    """Get case outcome distribution"""
    return frappe.db.sql("""
        SELECT
            CASE
                WHEN status = 'Closed' AND case_type IN ('HR Misconduct', 'Fraud') THEN 'Disciplinary Action'
                WHEN status = 'Closed' AND case_type = 'Complaint' THEN 'Policy Change'
                WHEN status = 'Closed' THEN 'Resolved'
                WHEN status = 'Rejected' THEN 'No Action'
                ELSE 'In Progress'
            END as outcome,
            COUNT(*) as count
        FROM `tabCase`
        GROUP BY outcome
        ORDER BY count DESC
    """, as_dict=True)


# ============================================================================
# 2. INVESTIGATION MANAGEMENT DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_investigation_overview():
    """Get investigation management overview"""
    try:
        # Investigations by status
        by_status = frappe.db.sql("""
            SELECT status, COUNT(*) as count
            FROM `tabCase Investigation`
            GROUP BY status
        """, as_dict=True)

        # Investigations per investigator
        per_investigator = frappe.db.sql("""
            SELECT
                lead_investigator,
                COUNT(*) as total,
                SUM(CASE WHEN status = 'In Progress' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabCase Investigation`
            GROUP BY lead_investigator
            ORDER BY total DESC
            LIMIT 10
        """, as_dict=True)

        # Pending evidence submissions
        pending_evidence = frappe.db.count("Case Evidence", filters={
            "docstatus": 0
        })

        # Cases awaiting interview (activity type)
        awaiting_interview = frappe.db.sql("""
            SELECT COUNT(DISTINCT linked_case) as count
            FROM `tabCase Activity`
            WHERE activity_type = 'Interview'
            AND status IN ('Planned', 'Pending')
        """)[0][0] or 0

        return {
            "by_status": by_status,
            "per_investigator": per_investigator,
            "pending_evidence": pending_evidence,
            "awaiting_interview": awaiting_interview
        }
    except Exception as e:
        frappe.log_error(f"Investigation overview error: {str(e)}")
        return {"error": str(e)}


@frappe.whitelist()
def get_evidence_by_type():
    """Get evidence distribution by type"""
    return frappe.db.sql("""
        SELECT evidence_type as label, COUNT(*) as value
        FROM `tabCase Evidence`
        GROUP BY evidence_type
        ORDER BY value DESC
    """, as_dict=True)


@frappe.whitelist()
def get_investigation_duration():
    """Get investigation duration stats"""
    return frappe.db.sql("""
        SELECT
            CASE
                WHEN DATEDIFF(COALESCE(actual_completion_date, CURDATE()), start_date) <= 7 THEN '0-7 days'
                WHEN DATEDIFF(COALESCE(actual_completion_date, CURDATE()), start_date) <= 30 THEN '8-30 days'
                WHEN DATEDIFF(COALESCE(actual_completion_date, CURDATE()), start_date) <= 90 THEN '31-90 days'
                ELSE '90+ days'
            END as duration_bucket,
            COUNT(*) as count
        FROM `tabCase Investigation`
        WHERE start_date IS NOT NULL
        GROUP BY duration_bucket
        ORDER BY FIELD(duration_bucket, '0-7 days', '8-30 days', '31-90 days', '90+ days')
    """, as_dict=True)


# ============================================================================
# 3. RISK & COMPLIANCE DASHBOARD (ISO 31000 / ISO 37001)
# ============================================================================

@frappe.whitelist()
def get_risk_compliance_overview():
    """Get risk and compliance overview"""
    try:
        # Risk score distribution
        risk_distribution = frappe.db.sql("""
            SELECT
                CASE
                    WHEN risk_score >= 12 THEN 'Critical'
                    WHEN risk_score >= 8 THEN 'High'
                    WHEN risk_score >= 4 THEN 'Medium'
                    ELSE 'Low'
                END as risk_level,
                COUNT(*) as count
            FROM `tabCase`
            WHERE status NOT IN ('Closed', 'Rejected')
            GROUP BY risk_level
            ORDER BY FIELD(risk_level, 'Critical', 'High', 'Medium', 'Low')
        """, as_dict=True)

        # High impact/high likelihood cases
        high_risk_cases = frappe.db.count("Case", filters={
            "risk_score": [">=", 12],
            "status": ["not in", ["Closed", "Rejected"]]
        })

        # Cases linked to policy violations
        policy_violations = frappe.db.count("Case", filters={
            "case_type": ["in", ["Complaint", "HR Misconduct", "Fraud", "Corruption"]]
        })

        return {
            "risk_distribution": risk_distribution,
            "high_risk_cases": high_risk_cases,
            "policy_violations": policy_violations
        }
    except Exception as e:
        frappe.log_error(f"Risk compliance overview error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 4. FRAUD & ETHICS DASHBOARD (ACFE Standards)
# ============================================================================

@frappe.whitelist()
def get_fraud_dashboard():
    """Get fraud and ethics dashboard data"""
    try:
        # Total fraud cases
        total_fraud = frappe.db.count("Case", filters={
            "case_type": "Fraud"
        })

        # Confirmed fraud cases (closed with confirmed status)
        confirmed_fraud = frappe.db.count("Case", filters={
            "case_type": "Fraud",
            "status": "Closed"
        })

        # Fraud by department/region
        fraud_by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unassigned') as region,
                COUNT(*) as count
            FROM `tabCase`
            WHERE case_type = 'Fraud'
            GROUP BY region
            ORDER BY count DESC
        """, as_dict=True)

        # Fraud schemes breakdown (using case_category)
        fraud_schemes = frappe.db.sql("""
            SELECT
                COALESCE(cc.category_name, 'Unknown') as scheme,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabCase Category` cc ON c.case_category = cc.name
            WHERE c.case_type = 'Fraud'
            GROUP BY cc.category_name
            ORDER BY count DESC
        """, as_dict=True)

        # Whistleblower reports
        whistleblower_reports = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            WHERE cs.source_name LIKE '%Whistleblower%'
            OR cs.source_name LIKE '%Anonymous%'
            OR cs.source_name LIKE '%Hotline%'
        """)[0][0] or 0

        return {
            "total_fraud_cases": total_fraud,
            "confirmed_fraud": confirmed_fraud,
            "fraud_by_region": fraud_by_region,
            "fraud_schemes": fraud_schemes,
            "whistleblower_reports": whistleblower_reports
        }
    except Exception as e:
        frappe.log_error(f"Fraud dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 5. HR MISCONDUCT & DISCIPLINARY DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_hr_misconduct_dashboard():
    """Get HR misconduct and disciplinary dashboard data"""
    try:
        # Employee-related cases
        employee_cases = frappe.db.count("Case", filters={
            "case_type": "HR Misconduct"
        })

        # Cases pending HR decision
        pending_hr = frappe.db.count("Case", filters={
            "case_type": "HR Misconduct",
            "status": ["in", ["Open", "Under Investigation", "Waiting for Information"]]
        })

        # Cases by department
        by_department = frappe.db.sql("""
            SELECT
                COALESCE(d.department_name, 'Unassigned') as department,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabDepartment` d ON c.assigned_department = d.name
            WHERE c.case_type = 'HR Misconduct'
            GROUP BY d.department_name
            ORDER BY count DESC
            LIMIT 10
        """, as_dict=True)

        # Misconduct categories
        misconduct_types = frappe.db.sql("""
            SELECT
                COALESCE(cc.category_name, 'Other') as category,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabCase Category` cc ON c.case_category = cc.name
            WHERE c.case_type = 'HR Misconduct'
            GROUP BY cc.category_name
            ORDER BY count DESC
        """, as_dict=True)

        # Repeat offenders (employees with multiple cases)
        repeat_offenders = frappe.db.sql("""
            SELECT linked_employee, COUNT(*) as case_count
            FROM `tabCase`
            WHERE linked_employee IS NOT NULL
            AND case_type = 'HR Misconduct'
            GROUP BY linked_employee
            HAVING case_count > 1
            ORDER BY case_count DESC
            LIMIT 10
        """, as_dict=True)

        return {
            "employee_cases": employee_cases,
            "pending_hr_decision": pending_hr,
            "by_department": by_department,
            "misconduct_types": misconduct_types,
            "repeat_offenders": len(repeat_offenders)
        }
    except Exception as e:
        frappe.log_error(f"HR misconduct dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 6. SAFETY & INCIDENT DASHBOARD (HSE / OSHA / ISO 45001)
# ============================================================================

@frappe.whitelist()
def get_safety_dashboard():
    """Get safety and incident dashboard data"""
    try:
        # Safety incidents
        safety_incidents = frappe.db.count("Case", filters={
            "case_type": "Safety"
        })

        # Open safety cases
        open_safety = frappe.db.count("Case", filters={
            "case_type": "Safety",
            "status": ["not in", ["Closed", "Rejected"]]
        })

        # Safety cases by region/site
        by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unassigned') as region,
                COUNT(*) as count,
                SUM(CASE WHEN status NOT IN ('Closed', 'Rejected') THEN 1 ELSE 0 END) as open_count
            FROM `tabCase`
            WHERE case_type = 'Safety'
            GROUP BY region
            ORDER BY count DESC
        """, as_dict=True)

        # Severity pyramid
        severity_pyramid = frappe.db.sql("""
            SELECT
                COALESCE(sm.severity_level, 'Unknown') as severity,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
            WHERE c.case_type = 'Safety'
            GROUP BY sm.severity_level
            ORDER BY FIELD(sm.severity_level, 'Critical', 'High', 'Medium', 'Low')
        """, as_dict=True)

        # Corrective action completion rate
        action_stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN completion_status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabCase Action Plan` cap
            INNER JOIN `tabCase` c ON cap.linked_case = c.name
            WHERE c.case_type = 'Safety'
        """, as_dict=True)

        completion_rate = 0
        if action_stats and action_stats[0].get("total", 0) > 0:
            completion_rate = (action_stats[0].get("completed", 0) / action_stats[0]["total"]) * 100

        return {
            "safety_incidents": safety_incidents,
            "open_safety_cases": open_safety,
            "by_region": by_region,
            "severity_pyramid": severity_pyramid,
            "corrective_action_completion": round(completion_rate, 1)
        }
    except Exception as e:
        frappe.log_error(f"Safety dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 7. CUSTOMER COMPLAINT RESOLUTION DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_customer_complaint_dashboard():
    """Get customer complaint resolution dashboard data"""
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Complaints received this month
        complaints_received = frappe.db.count("Case", filters={
            "case_type": "Customer",
            "date_reported": [">=", month_start]
        })

        # Complaints resolved this month
        complaints_resolved = frappe.db.count("Case", filters={
            "case_type": "Customer",
            "status": "Closed",
            "actual_closure_date": [">=", month_start]
        })

        # Complaint SLA compliance
        sla_compliance = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN actual_closure_date <= sla_due_date THEN 1 ELSE 0 END) as on_time
            FROM `tabCase`
            WHERE case_type = 'Customer'
            AND status = 'Closed'
            AND actual_closure_date IS NOT NULL
            AND sla_due_date IS NOT NULL
        """, as_dict=True)

        compliance_rate = 0
        if sla_compliance and sla_compliance[0].get("total", 0) > 0:
            compliance_rate = (sla_compliance[0].get("on_time", 0) / sla_compliance[0]["total"]) * 100

        # Escalated complaints
        escalated = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
            WHERE c.case_type = 'Customer'
            AND sm.severity_level IN ('Critical', 'High')
        """)[0][0] or 0

        # Complaints by region
        by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unassigned') as region,
                COUNT(*) as count
            FROM `tabCase`
            WHERE case_type = 'Customer'
            GROUP BY region
            ORDER BY count DESC
        """, as_dict=True)

        # Top recurring issues
        recurring_issues = frappe.db.sql("""
            SELECT
                COALESCE(cc.category_name, 'Other') as issue,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabCase Category` cc ON c.case_category = cc.name
            WHERE c.case_type = 'Customer'
            GROUP BY cc.category_name
            ORDER BY count DESC
            LIMIT 10
        """, as_dict=True)

        return {
            "complaints_received": complaints_received,
            "complaints_resolved": complaints_resolved,
            "sla_compliance_rate": round(compliance_rate, 1),
            "escalated_complaints": escalated,
            "by_region": by_region,
            "recurring_issues": recurring_issues
        }
    except Exception as e:
        frappe.log_error(f"Customer complaint dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 8. LEGAL & REGULATORY CASE DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_legal_dashboard():
    """Get legal and regulatory case dashboard data"""
    try:
        # Cases with legal exposure (linked to Legal Case)
        legal_cases = frappe.db.count("Legal Case")

        # Active legal cases
        active_legal = frappe.db.count("Legal Case", filters={
            "case_status": ["not in", ["Closed", "Withdrawn"]]
        })

        # Cases by court type
        by_court = frappe.db.sql("""
            SELECT
                COALESCE(court_type, 'Unknown') as court_type,
                COUNT(*) as count
            FROM `tabLegal Case`
            GROUP BY court_type
            ORDER BY count DESC
        """, as_dict=True)

        # Cases requiring legal opinion (pending)
        pending_legal = frappe.db.count("Legal Case", filters={
            "case_status": "Pending"
        })

        # Prosecution cases
        prosecution_cases = frappe.db.count("Prosecution Case")

        return {
            "total_legal_cases": legal_cases,
            "active_legal_cases": active_legal,
            "by_court_type": by_court,
            "pending_legal_opinion": pending_legal,
            "prosecution_cases": prosecution_cases
        }
    except Exception as e:
        frappe.log_error(f"Legal dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 9. CASE SLA PERFORMANCE DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_sla_performance_dashboard():
    """Get SLA performance dashboard data"""
    try:
        today_date = getdate(today())

        # Closed cases within SLA
        sla_met = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase`
            WHERE status = 'Closed'
            AND actual_closure_date <= sla_due_date
        """)[0][0] or 0

        # Total closed cases with SLA
        total_with_sla = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase`
            WHERE status = 'Closed'
            AND sla_due_date IS NOT NULL
        """)[0][0] or 0

        sla_compliance = (sla_met / total_with_sla * 100) if total_with_sla > 0 else 0

        # Cases nearing SLA breach (within 2 days)
        nearing_breach = frappe.db.count("Case", filters={
            "status": ["not in", ["Closed", "Rejected"]],
            "sla_due_date": ["between", [today_date, add_days(today_date, 2)]]
        })

        # Overdue cases
        overdue = frappe.db.count("Case", filters={
            "status": ["not in", ["Closed", "Rejected"]],
            "sla_due_date": ["<", today_date]
        })

        # SLA by department
        by_department = frappe.db.sql("""
            SELECT
                COALESCE(d.department_name, 'Unassigned') as department,
                COUNT(*) as total,
                SUM(CASE WHEN c.actual_closure_date <= c.sla_due_date THEN 1 ELSE 0 END) as on_time
            FROM `tabCase` c
            LEFT JOIN `tabDepartment` d ON c.assigned_department = d.name
            WHERE c.status = 'Closed'
            AND c.sla_due_date IS NOT NULL
            GROUP BY d.department_name
            ORDER BY total DESC
        """, as_dict=True)

        # SLA by case type
        by_type = frappe.db.sql("""
            SELECT
                case_type,
                COUNT(*) as total,
                SUM(CASE WHEN actual_closure_date <= sla_due_date THEN 1 ELSE 0 END) as on_time
            FROM `tabCase`
            WHERE status = 'Closed'
            AND sla_due_date IS NOT NULL
            GROUP BY case_type
            ORDER BY total DESC
        """, as_dict=True)

        return {
            "sla_compliance_rate": round(sla_compliance, 1),
            "cases_nearing_breach": nearing_breach,
            "overdue_cases": overdue,
            "by_department": by_department,
            "by_case_type": by_type
        }
    except Exception as e:
        frappe.log_error(f"SLA performance dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 10. CASE HEATMAP & GIS DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_geo_dashboard():
    """Get geographic/heatmap dashboard data"""
    try:
        # Cases by region
        by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unassigned') as region,
                COUNT(*) as total,
                SUM(CASE WHEN status NOT IN ('Closed', 'Rejected') THEN 1 ELSE 0 END) as open_count
            FROM `tabCase`
            GROUP BY region
            ORDER BY total DESC
        """, as_dict=True)

        # Cases by business unit
        by_business_unit = frappe.db.sql("""
            SELECT
                COALESCE(business_unit, 'Unassigned') as business_unit,
                COUNT(*) as total,
                SUM(CASE WHEN status NOT IN ('Closed', 'Rejected') THEN 1 ELSE 0 END) as open_count
            FROM `tabCase`
            GROUP BY business_unit
            ORDER BY total DESC
        """, as_dict=True)

        # Asset-linked cases
        asset_cases = frappe.db.sql("""
            SELECT
                case_type,
                COUNT(*) as count
            FROM `tabCase`
            WHERE case_type IN ('Theft', 'Vandalism', 'Technical')
            GROUP BY case_type
        """, as_dict=True)

        # Hotspot analysis (regions with most critical cases)
        hotspots = frappe.db.sql("""
            SELECT
                COALESCE(c.region, 'Unknown') as region,
                COUNT(*) as critical_count
            FROM `tabCase` c
            INNER JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
            WHERE sm.severity_level = 'Critical'
            AND c.status NOT IN ('Closed', 'Rejected')
            GROUP BY c.region
            ORDER BY critical_count DESC
            LIMIT 5
        """, as_dict=True)

        return {
            "by_region": by_region,
            "by_business_unit": by_business_unit,
            "asset_cases": asset_cases,
            "hotspots": hotspots
        }
    except Exception as e:
        frappe.log_error(f"Geo dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 11. INTERNAL AUDIT DASHBOARD (IIA Standards)
# ============================================================================

@frappe.whitelist()
def get_audit_dashboard():
    """Get internal audit dashboard data"""
    try:
        # Audit-triggered cases
        audit_cases = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            WHERE cs.source_name LIKE '%Audit%'
            OR cs.source_name LIKE '%Internal Audit%'
        """)[0][0] or 0

        # Cases pending control gap assessment
        pending_assessment = frappe.db.count("Case", filters={
            "case_type": "Audit Finding",
            "status": ["in", ["Open", "Under Investigation"]]
        })

        # Cases referred to management
        referred_to_mgmt = frappe.db.sql("""
            SELECT COUNT(DISTINCT c.name)
            FROM `tabCase` c
            INNER JOIN `tabCase Activity` ca ON ca.linked_case = c.name
            WHERE ca.activity_type IN ('Management Referral', 'Escalation')
        """)[0][0] or 0

        # Follow-up actions due
        actions_due = frappe.db.count("Case Action Plan", filters={
            "completion_status": ["in", ["Not Started", "In Progress"]],
            "expected_completion_date": ["<", today()]
        })

        # Audit vs Non-audit case ratio
        audit_ratio = frappe.db.sql("""
            SELECT
                CASE WHEN cs.source_name LIKE '%Audit%' THEN 'Audit' ELSE 'Non-Audit' END as source_type,
                COUNT(*) as count
            FROM `tabCase` c
            LEFT JOIN `tabCase Source` cs ON c.case_source = cs.name
            GROUP BY source_type
        """, as_dict=True)

        return {
            "audit_triggered_cases": audit_cases,
            "pending_assessment": pending_assessment,
            "referred_to_management": referred_to_mgmt,
            "actions_due": actions_due,
            "audit_ratio": audit_ratio
        }
    except Exception as e:
        frappe.log_error(f"Audit dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 12. WHISTLEBLOWER & ETHICS HOTLINE DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_whistleblower_dashboard():
    """Get whistleblower and ethics hotline dashboard data"""
    try:
        # Anonymous reports
        anonymous_reports = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            WHERE cs.source_name LIKE '%Anonymous%'
            OR cs.source_name LIKE '%Whistleblower%'
            OR cs.source_name LIKE '%Hotline%'
        """)[0][0] or 0

        # High severity anonymous cases
        high_severity_anonymous = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            INNER JOIN `tabCase Severity Matrix` sm ON c.severity = sm.name
            WHERE (cs.source_name LIKE '%Anonymous%'
                OR cs.source_name LIKE '%Whistleblower%'
                OR cs.source_name LIKE '%Hotline%')
            AND sm.severity_level IN ('Critical', 'High')
        """)[0][0] or 0

        # Reports by channel
        by_channel = frappe.db.sql("""
            SELECT
                cs.source_name as channel,
                COUNT(*) as count
            FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            GROUP BY cs.source_name
            ORDER BY count DESC
        """, as_dict=True)

        # Reports trend
        reports_trend = frappe.db.sql("""
            SELECT
                DATE_FORMAT(date_reported, '%Y-%m') as month,
                COUNT(*) as count
            FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            WHERE cs.source_name LIKE '%Anonymous%'
                OR cs.source_name LIKE '%Whistleblower%'
                OR cs.source_name LIKE '%Hotline%'
            AND date_reported >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """, as_dict=True)

        # Average response time
        avg_response = frappe.db.sql("""
            SELECT AVG(DATEDIFF(
                (SELECT MIN(activity_date) FROM `tabCase Activity Log`
                 WHERE `case` = c.name),
                c.date_reported
            )) as avg_days
            FROM `tabCase` c
            INNER JOIN `tabCase Source` cs ON c.case_source = cs.name
            WHERE cs.source_name LIKE '%Anonymous%'
                OR cs.source_name LIKE '%Whistleblower%'
        """)[0][0] or 0

        return {
            "anonymous_reports": anonymous_reports,
            "high_severity_anonymous": high_severity_anonymous,
            "by_channel": by_channel,
            "reports_trend": reports_trend,
            "avg_response_days": round(avg_response, 1) if avg_response else 0
        }
    except Exception as e:
        frappe.log_error(f"Whistleblower dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# 13. CASE CLOSURE & POST-INCIDENT REVIEW DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_closure_dashboard():
    """Get case closure and post-incident review dashboard data"""
    try:
        today_date = getdate(today())
        month_start = get_first_day(today_date)

        # Closed cases this month
        closed_this_month = frappe.db.count("Case", filters={
            "status": "Closed",
            "actual_closure_date": [">=", month_start]
        })

        # Cases with completed action plans
        with_completed_actions = frappe.db.sql("""
            SELECT COUNT(DISTINCT c.name)
            FROM `tabCase` c
            INNER JOIN `tabCase Action Plan` cap ON cap.linked_case = c.name
            WHERE c.status = 'Closed'
            AND cap.completion_status = 'Completed'
        """)[0][0] or 0

        # Cases awaiting lessons learned
        awaiting_lessons = frappe.db.sql("""
            SELECT COUNT(*) FROM `tabCase` c
            WHERE c.status = 'Closed'
            AND NOT EXISTS (
                SELECT 1 FROM `tabCase Action Plan` cap
                WHERE cap.linked_case = c.name
                AND cap.action_type IN ('Lessons Learned', 'Process Improvement')
            )
        """)[0][0] or 0

        # Cases reopened
        reopened = frappe.db.sql("""
            SELECT COUNT(DISTINCT c.name)
            FROM `tabCase` c
            INNER JOIN `tabCase Activity Log` cal ON cal.`case` = c.name
            WHERE cal.activity_type = 'Status Change'
            AND cal.old_value = 'Closed'
            AND cal.new_value != 'Closed'
        """)[0][0] or 0

        # Action categories
        action_categories = frappe.db.sql("""
            SELECT
                action_type,
                COUNT(*) as count
            FROM `tabCase Action Plan`
            GROUP BY action_type
            ORDER BY count DESC
        """, as_dict=True)

        # Preventive vs corrective actions
        action_types = frappe.db.sql("""
            SELECT
                CASE
                    WHEN action_type = 'Preventive' THEN 'Preventive'
                    WHEN action_type = 'Corrective' THEN 'Corrective'
                    ELSE 'Other'
                END as type,
                COUNT(*) as count
            FROM `tabCase Action Plan`
            GROUP BY type
        """, as_dict=True)

        return {
            "closed_this_month": closed_this_month,
            "with_completed_actions": with_completed_actions,
            "awaiting_lessons_learned": awaiting_lessons,
            "cases_reopened": reopened,
            "action_categories": action_categories,
            "preventive_vs_corrective": action_types
        }
    except Exception as e:
        frappe.log_error(f"Closure dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# ASSET THEFT DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_asset_theft_dashboard():
    """Get asset theft dashboard data"""
    try:
        # Total theft cases
        total_thefts = frappe.db.count("Asset Theft")

        # Open theft cases
        open_thefts = frappe.db.count("Asset Theft", filters={
            "status": ["not in", ["Closed", "Recovered"]]
        })

        # Total value stolen
        total_value = frappe.db.sql("""
            SELECT COALESCE(SUM(asset_value), 0) as total
            FROM `tabAsset Theft`
        """)[0][0] or 0

        # Recovered value
        recovered_value = frappe.db.sql("""
            SELECT COALESCE(SUM(asset_value), 0) as total
            FROM `tabAsset Theft`
            WHERE recovery_status = 'Fully Recovered'
        """)[0][0] or 0

        # By asset type
        by_asset_type = frappe.db.sql("""
            SELECT
                COALESCE(asset_type, 'Unknown') as asset_type,
                COUNT(*) as count,
                SUM(asset_value) as value
            FROM `tabAsset Theft`
            GROUP BY asset_type
            ORDER BY count DESC
        """, as_dict=True)

        # By region
        by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unknown') as region,
                COUNT(*) as count
            FROM `tabAsset Theft`
            GROUP BY region
            ORDER BY count DESC
        """, as_dict=True)

        return {
            "total_thefts": total_thefts,
            "open_thefts": open_thefts,
            "total_value_stolen": total_value,
            "recovered_value": recovered_value,
            "recovery_rate": round((recovered_value / total_value * 100) if total_value > 0 else 0, 1),
            "by_asset_type": by_asset_type,
            "by_region": by_region
        }
    except Exception as e:
        frappe.log_error(f"Asset theft dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# ILLEGAL CONNECTION DASHBOARD
# ============================================================================

@frappe.whitelist()
def get_illegal_connection_dashboard():
    """Get illegal connection dashboard data"""
    try:
        # Total illegal connections
        total_connections = frappe.db.count("Illegal Connection")

        # Open cases
        open_cases = frappe.db.count("Illegal Connection", filters={
            "status": ["not in", ["Closed", "Resolved"]]
        })

        # Revenue loss
        revenue_loss = frappe.db.sql("""
            SELECT COALESCE(SUM(estimated_revenue_loss), 0) as total
            FROM `tabIllegal Connection`
        """)[0][0] or 0

        # Recovered revenue
        recovered_revenue = frappe.db.sql("""
            SELECT COALESCE(SUM(recovered_amount), 0) as total
            FROM `tabIllegal Connection`
        """)[0][0] or 0

        # By connection type
        by_type = frappe.db.sql("""
            SELECT
                COALESCE(connection_type, 'Unknown') as connection_type,
                COUNT(*) as count
            FROM `tabIllegal Connection`
            GROUP BY connection_type
            ORDER BY count DESC
        """, as_dict=True)

        # By region
        by_region = frappe.db.sql("""
            SELECT
                COALESCE(region, 'Unknown') as region,
                COUNT(*) as count
            FROM `tabIllegal Connection`
            GROUP BY region
            ORDER BY count DESC
        """, as_dict=True)

        # Trend over time
        trend = frappe.db.sql("""
            SELECT
                DATE_FORMAT(creation, '%Y-%m') as month,
                COUNT(*) as count
            FROM `tabIllegal Connection`
            WHERE creation >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
            GROUP BY month
            ORDER BY month
        """, as_dict=True)

        return {
            "total_connections": total_connections,
            "open_cases": open_cases,
            "revenue_loss": revenue_loss,
            "recovered_revenue": recovered_revenue,
            "recovery_rate": round((recovered_revenue / revenue_loss * 100) if revenue_loss > 0 else 0, 1),
            "by_type": by_type,
            "by_region": by_region,
            "trend": trend
        }
    except Exception as e:
        frappe.log_error(f"Illegal connection dashboard error: {str(e)}")
        return {"error": str(e)}


# ============================================================================
# NUMBER CARD METHODS
# ============================================================================

@frappe.whitelist()
def get_sla_breached_cases_count():
    """
    Get count of SLA breached cases - cases where SLA due date has passed
    and status is not Closed or Rejected
    """
    try:
        today_date = now()
        count = frappe.db.count("Case", filters={
            "status": ["not in", ["Closed", "Rejected"]],
            "sla_due_date": ["<", today_date],
            "docstatus": ["!=", 2]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"SLA breached cases count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}
