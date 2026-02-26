# Risk Dashboard API
# Comprehensive API endpoints for Risk Management Dashboards
import frappe
from frappe import _
from frappe.utils import getdate, add_days, nowdate, flt, cint
from datetime import datetime, timedelta

# ============================================================================
# 1. ENTERPRISE RISK OVERVIEW DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_enterprise_risk_overview(filters=None):
    """Get high-level enterprise risk overview for Board/Executive dashboard"""
    if isinstance(filters, str):
        filters = frappe.parse_json(filters)
    filters = filters or {}
    
    department = filters.get('department')
    category = filters.get('category')
    period = filters.get('period', 'ytd')
    
    conditions = []
    if department:
        conditions.append(f"rr.department = '{frappe.db.escape(department)}'")
    if category:
        conditions.append(f"rr.risk_category = '{frappe.db.escape(category)}'")
    
    where_clause = " AND ".join(conditions) if conditions else "1=1"
    
    # Total Risks
    total_risks = frappe.db.sql(f"""
        SELECT COUNT(*) as count FROM `tabRisk Register` rr
        WHERE {where_clause}
    """, as_dict=True)[0].count
    
    # High & Critical Risks (from assessments)
    high_critical = frappe.db.sql("""
        SELECT COUNT(*) as count FROM `tabRisk Assessment`
        WHERE residual_risk_rating IN ('High', 'Critical', 'Extreme')
        AND docstatus = 1
    """, as_dict=True)[0].count
    
    # Risks by Priority
    by_priority = frappe.db.sql(f"""
        SELECT 
            COALESCE(ra.residual_risk_rating, 'Not Assessed') as priority,
            COUNT(DISTINCT rr.name) as count
        FROM `tabRisk Register` rr
        LEFT JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name AND ra.docstatus = 1
        WHERE {where_clause}
        GROUP BY priority
        ORDER BY FIELD(priority, 'Extreme', 'Critical', 'High', 'Medium', 'Low', 'Not Assessed')
    """, as_dict=True)
    
    # Risks by Category
    by_category = frappe.db.sql(f"""
        SELECT 
            COALESCE(rr.risk_category, 'Uncategorized') as category,
            COUNT(*) as count
        FROM `tabRisk Register` rr
        WHERE {where_clause}
        GROUP BY rr.risk_category
        ORDER BY count DESC
    """, as_dict=True)
    
    # Top 10 Risks by Inherent Score
    top_risks = frappe.db.sql("""
        SELECT 
            rr.name, rr.risk_title, rr.risk_category, rr.department, rr.risk_owner,
            ra.inherent_risk_score, ra.residual_risk_score, ra.inherent_risk_rating,
            ra.residual_risk_rating
        FROM `tabRisk Register` rr
        INNER JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name
        WHERE ra.docstatus = 1
        ORDER BY ra.inherent_risk_score DESC
        LIMIT 10
    """, as_dict=True)
    
    # Active Risks
    active_risks = frappe.db.sql(f"""
        SELECT COUNT(*) as count FROM `tabRisk Register` rr
        WHERE rr.status = 'Active' AND {where_clause}
    """, as_dict=True)[0].count
    
    # Mitigated Risks
    mitigated_risks = frappe.db.sql(f"""
        SELECT COUNT(*) as count FROM `tabRisk Register` rr
        WHERE rr.status = 'Mitigated' AND {where_clause}
    """, as_dict=True)[0].count
    
    return {
        'total_risks': total_risks,
        'high_critical_risks': high_critical,
        'active_risks': active_risks,
        'mitigated_risks': mitigated_risks,
        'by_priority': by_priority,
        'by_category': by_category,
        'top_risks': top_risks
    }

@frappe.whitelist()
def get_residual_risk_heatmap():
    """Get 5x5 risk heat map data for inherent and residual risks"""
    # Initialize 5x5 matrix
    heatmap = {
        'inherent': [[0]*5 for _ in range(5)],
        'residual': [[0]*5 for _ in range(5)]
    }
    
    assessments = frappe.db.sql("""
        SELECT 
            inherent_impact_score, inherent_likelihood_score,
            residual_impact_score, residual_likelihood_score
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
    """, as_dict=True)
    
    for a in assessments:
        # Map scores 1-5 to array indices 0-4
        if a.inherent_impact_score and a.inherent_likelihood_score:
            i_row = min(4, max(0, cint(a.inherent_likelihood_score) - 1))
            i_col = min(4, max(0, cint(a.inherent_impact_score) - 1))
            heatmap['inherent'][4-i_row][i_col] += 1  # Invert row for display
        
        if a.residual_impact_score and a.residual_likelihood_score:
            r_row = min(4, max(0, cint(a.residual_likelihood_score) - 1))
            r_col = min(4, max(0, cint(a.residual_impact_score) - 1))
            heatmap['residual'][4-r_row][r_col] += 1
    
    return heatmap

# ============================================================================
# 2. DEPARTMENTAL RISK DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_departmental_risk_summary(department=None):
    """Get risk summary for a specific department"""
    if not department:
        department = frappe.form_dict.get('department')
    
    dept_filter = f"AND rr.department = '{frappe.db.escape(department)}'" if department else ""
    
    # Risks by department
    by_department = frappe.db.sql(f"""
        SELECT 
            COALESCE(rr.department, 'Unassigned') as department,
            COUNT(*) as total,
            SUM(CASE WHEN rr.status = 'Active' THEN 1 ELSE 0 END) as active,
            SUM(CASE WHEN rr.status IN ('Mitigated', 'Closed') THEN 1 ELSE 0 END) as closed
        FROM `tabRisk Register` rr
        WHERE 1=1 {dept_filter}
        GROUP BY rr.department
        ORDER BY total DESC
    """, as_dict=True)
    
    return {'by_department': by_department}


@frappe.whitelist()
def get_risks_due_for_review(department=None, days_ahead=30):
    """Get risks due for review within specified days"""
    days_ahead = cint(days_ahead) or 30
    dept_filter = f"AND department = '{frappe.db.escape(department)}'" if department else ""

    due_date = add_days(nowdate(), days_ahead)

    risks = frappe.db.sql(f"""
        SELECT name, risk_title, risk_category, department, risk_owner,
               next_review_date, status
        FROM `tabRisk Register`
        WHERE next_review_date <= %(due_date)s
        AND status = 'Active'
        {dept_filter}
        ORDER BY next_review_date ASC
        LIMIT 20
    """, {'due_date': due_date}, as_dict=True)

    return risks


@frappe.whitelist()
def get_treatment_plans_status(department=None):
    """Get treatment plans status summary"""
    dept_filter = ""
    if department:
        dept_filter = f"""AND rtp.linked_risk IN (
            SELECT name FROM `tabRisk Register` WHERE department = '{frappe.db.escape(department)}'
        )"""

    # Status summary
    by_status = frappe.db.sql(f"""
        SELECT
            plan_status as status,
            COUNT(*) as count
        FROM `tabRisk Treatment Plan` rtp
        WHERE 1=1 {dept_filter}
        GROUP BY plan_status
    """, as_dict=True)

    # Overdue treatment plans
    overdue = frappe.db.sql(f"""
        SELECT
            rtp.name, rtp.plan_title, rtp.linked_risk, rtp.plan_owner,
            rtp.target_completion_date, rtp.plan_status, rtp.progress_percentage,
            rr.risk_title
        FROM `tabRisk Treatment Plan` rtp
        LEFT JOIN `tabRisk Register` rr ON rr.name = rtp.linked_risk
        WHERE rtp.target_completion_date < CURDATE()
        AND rtp.plan_status NOT IN ('Completed', 'Cancelled')
        {dept_filter}
        ORDER BY rtp.target_completion_date ASC
        LIMIT 20
    """, as_dict=True)

    # Avg residual risk score
    avg_score = frappe.db.sql("""
        SELECT AVG(residual_risk_score) as avg_score
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
    """, as_dict=True)[0].avg_score or 0

    return {
        'by_status': by_status,
        'overdue_plans': overdue,
        'overdue_count': len(overdue),
        'avg_residual_score': round(flt(avg_score), 2)
    }


# ============================================================================
# 3. RISK HEAT MAP DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_risk_movement_data():
    """Get risk movement data (inherent to residual)"""
    movements = frappe.db.sql("""
        SELECT
            rr.name as risk_id, rr.risk_title,
            ra.inherent_risk_score, ra.inherent_risk_rating,
            ra.residual_risk_score, ra.residual_risk_rating,
            (ra.inherent_risk_score - ra.residual_risk_score) as reduction
        FROM `tabRisk Register` rr
        INNER JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name
        WHERE ra.docstatus = 1
        ORDER BY reduction DESC
        LIMIT 20
    """, as_dict=True)

    return movements


# ============================================================================
# 4. RISK TREATMENT & MITIGATION DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_treatment_dashboard_data():
    """Get comprehensive treatment plan dashboard data"""
    # Treatment Plans by Status
    by_status = frappe.db.sql("""
        SELECT plan_status as status, COUNT(*) as count
        FROM `tabRisk Treatment Plan`
        GROUP BY plan_status
    """, as_dict=True)

    # Overdue Treatment Plans
    overdue = frappe.db.sql("""
        SELECT
            rtp.name, rtp.plan_title, rtp.linked_risk, rtp.plan_owner,
            rtp.target_completion_date, rtp.progress_percentage,
            DATEDIFF(CURDATE(), rtp.target_completion_date) as days_overdue,
            rr.risk_title, rr.risk_category
        FROM `tabRisk Treatment Plan` rtp
        LEFT JOIN `tabRisk Register` rr ON rr.name = rtp.linked_risk
        WHERE rtp.target_completion_date < CURDATE()
        AND rtp.plan_status NOT IN ('Completed', 'Cancelled')
        ORDER BY days_overdue DESC
        LIMIT 15
    """, as_dict=True)

    # Average Time to Close
    avg_close_time = frappe.db.sql("""
        SELECT AVG(DATEDIFF(actual_completion_date, start_date)) as avg_days
        FROM `tabRisk Treatment Plan`
        WHERE plan_status = 'Completed'
        AND actual_completion_date IS NOT NULL
        AND start_date IS NOT NULL
    """, as_dict=True)[0].avg_days or 0

    # Risks Without Treatment Plans
    risks_without_plans = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabRisk Register` rr
        WHERE rr.status = 'Active'
        AND NOT EXISTS (
            SELECT 1 FROM `tabRisk Treatment Plan` rtp
            WHERE rtp.linked_risk = rr.name
            AND rtp.plan_status NOT IN ('Cancelled')
        )
    """, as_dict=True)[0].count

    return {
        'by_status': by_status,
        'overdue_plans': overdue,
        'avg_close_time_days': round(flt(avg_close_time), 1),
        'risks_without_plans': risks_without_plans
    }


# ============================================================================
# 5. KEY RISK INDICATOR (KRI) DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_kri_dashboard_data():
    """Get KRI dashboard summary data"""
    # KRIs by Status
    by_status = frappe.db.sql("""
        SELECT current_status as status, COUNT(*) as count
        FROM `tabKey Risk Indicator`
        WHERE status = 'Active'
        GROUP BY current_status
    """, as_dict=True)

    # Status counts
    normal = sum(s['count'] for s in by_status if s['status'] == 'Normal')
    warning = sum(s['count'] for s in by_status if s['status'] == 'Warning')
    critical = sum(s['count'] for s in by_status if s['status'] == 'Critical')

    # Active KRI Alerts (Warning + Critical)
    active_alerts = frappe.db.sql("""
        SELECT
            name, kri_name, kri_category, linked_risk, kri_owner,
            current_value, target_value, current_status, trend,
            last_reading_date
        FROM `tabKey Risk Indicator`
        WHERE status = 'Active'
        AND current_status IN ('Warning', 'Critical')
        ORDER BY
            CASE current_status WHEN 'Critical' THEN 1 ELSE 2 END,
            last_reading_date DESC
        LIMIT 15
    """, as_dict=True)

    # Top 5 KRIs by Deviation
    top_deviation = frappe.db.sql("""
        SELECT
            name, kri_name, kri_category,
            current_value, target_value,
            ABS(current_value - target_value) as deviation,
            CASE
                WHEN target_value != 0 THEN
                    ROUND(ABS((current_value - target_value) / target_value) * 100, 1)
                ELSE 0
            END as deviation_pct,
            current_status
        FROM `tabKey Risk Indicator`
        WHERE status = 'Active'
        AND target_value IS NOT NULL
        ORDER BY deviation_pct DESC
        LIMIT 5
    """, as_dict=True)

    return {
        'normal_count': normal,
        'warning_count': warning,
        'critical_count': critical,
        'total_active': normal + warning + critical,
        'by_status': by_status,
        'active_alerts': active_alerts,
        'top_deviation': top_deviation
    }


@frappe.whitelist()
def get_kri_trends(kri_name=None, months=6):
    """Get KRI trend data over time"""
    months = cint(months) or 6

    if kri_name:
        # Get readings for specific KRI
        readings = frappe.db.sql("""
            SELECT kr.reading_date, kr.actual_value, kr.status
            FROM `tabKRI Reading` kr
            INNER JOIN `tabKey Risk Indicator` kri ON kr.parent = kri.name
            WHERE kri.name = %(kri_name)s
            ORDER BY kr.reading_date DESC
            LIMIT 12
        """, {'kri_name': kri_name}, as_dict=True)
        return readings

    # Get aggregate KRI status over time (monthly)
    trends = frappe.db.sql("""
        SELECT
            DATE_FORMAT(kr.reading_date, '%%Y-%%m') as period,
            SUM(CASE WHEN kr.status = 'Normal' THEN 1 ELSE 0 END) as normal,
            SUM(CASE WHEN kr.status = 'Warning' THEN 1 ELSE 0 END) as warning,
            SUM(CASE WHEN kr.status = 'Critical' THEN 1 ELSE 0 END) as critical
        FROM `tabKRI Reading` kr
        INNER JOIN `tabKey Risk Indicator` kri ON kr.parent = kri.name
        WHERE kr.reading_date >= DATE_SUB(CURDATE(), INTERVAL %(months)s MONTH)
        GROUP BY period
        ORDER BY period ASC
    """, {'months': months}, as_dict=True)

    return trends


# ============================================================================
# 6. INCIDENT & LOSS EVENTS DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_incident_dashboard_data():
    """Get incident and loss events dashboard data"""
    # Incidents by Severity
    by_severity = frappe.db.sql("""
        SELECT
            COALESCE(severity, 'Unknown') as severity,
            COUNT(*) as count
        FROM `tabRisk Incident`
        GROUP BY severity
        ORDER BY FIELD(severity, 'Critical', 'High', 'Medium', 'Low', 'Unknown')
    """, as_dict=True)

    # Incidents by Risk Category
    by_category = frappe.db.sql("""
        SELECT
            COALESCE(ri.risk_category, 'Uncategorized') as category,
            COUNT(*) as count
        FROM `tabRisk Incident` ri
        GROUP BY ri.risk_category
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True)

    # Incidents over time (last 12 months)
    over_time = frappe.db.sql("""
        SELECT
            DATE_FORMAT(incident_date, '%%Y-%%m') as period,
            COUNT(*) as count
        FROM `tabRisk Incident`
        WHERE incident_date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
        GROUP BY period
        ORDER BY period ASC
    """, as_dict=True)

    # Top Risks with Most Incidents
    top_risks = frappe.db.sql("""
        SELECT
            ri.linked_risk, rr.risk_title,
            COUNT(*) as incident_count
        FROM `tabRisk Incident` ri
        INNER JOIN `tabRisk Register` rr ON rr.name = ri.linked_risk
        GROUP BY ri.linked_risk
        ORDER BY incident_count DESC
        LIMIT 10
    """, as_dict=True)

    # Total incidents
    total = frappe.db.count('Risk Incident')

    return {
        'total_incidents': total,
        'by_severity': by_severity,
        'by_category': by_category,
        'over_time': over_time,
        'top_risks_by_incidents': top_risks
    }


# ============================================================================
# 7. COMPLIANCE & REGULATORY RISK DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_compliance_dashboard_data():
    """Get compliance and regulatory risk dashboard data"""
    # Risks Linked to Regulations
    linked_to_regulations = frappe.db.sql("""
        SELECT COUNT(DISTINCT cr.linked_risk) as count
        FROM `tabCompliance Requirement` cr
        WHERE cr.linked_risk IS NOT NULL
    """, as_dict=True)[0].count

    # Compliance Status
    compliance_status = frappe.db.sql("""
        SELECT
            COALESCE(compliance_status, 'Unknown') as status,
            COUNT(*) as count
        FROM `tabCompliance Requirement`
        GROUP BY compliance_status
    """, as_dict=True)

    # Overdue Compliance Actions
    overdue_actions = frappe.db.sql("""
        SELECT
            name, requirement_name, regulatory_body, compliance_status,
            next_review_date, linked_risk
        FROM `tabCompliance Requirement`
        WHERE next_review_date < CURDATE()
        AND compliance_status != 'Compliant'
        ORDER BY next_review_date ASC
        LIMIT 15
    """, as_dict=True)

    # Risks by Regulatory Framework
    by_framework = frappe.db.sql("""
        SELECT
            COALESCE(regulatory_body, 'Unspecified') as framework,
            COUNT(*) as count
        FROM `tabCompliance Requirement`
        GROUP BY regulatory_body
        ORDER BY count DESC
        LIMIT 10
    """, as_dict=True)

    return {
        'risks_linked_to_regulations': linked_to_regulations,
        'compliance_status': compliance_status,
        'overdue_actions': overdue_actions,
        'by_framework': by_framework
    }


# ============================================================================
# 8. AUDIT & ASSURANCE DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_audit_dashboard_data():
    """Get audit and assurance dashboard data"""
    # This would integrate with audit findings if available
    # For now, we'll use risk assessment data as a proxy

    # Risk Coverage by Audit (assessed vs total risks)
    total_risks = frappe.db.count('Risk Register', {'status': 'Active'})
    assessed_risks = frappe.db.sql("""
        SELECT COUNT(DISTINCT linked_risk) as count
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
    """, as_dict=True)[0].count

    coverage_pct = round((assessed_risks / total_risks * 100) if total_risks > 0 else 0, 1)

    # High-Risk Findings (high/critical residual risks)
    high_risk_findings = frappe.db.sql("""
        SELECT
            ra.name, ra.linked_risk, rr.risk_title,
            ra.residual_risk_rating, ra.residual_risk_score,
            ra.assessment_date, ra.control_gaps_identified
        FROM `tabRisk Assessment` ra
        INNER JOIN `tabRisk Register` rr ON rr.name = ra.linked_risk
        WHERE ra.docstatus = 1
        AND ra.residual_risk_rating IN ('High', 'Critical', 'Extreme')
        ORDER BY ra.residual_risk_score DESC
        LIMIT 15
    """, as_dict=True)

    # Repeat Findings (risks with multiple assessments showing same issues)
    repeat_findings = frappe.db.sql("""
        SELECT
            linked_risk, COUNT(*) as assessment_count
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
        AND residual_risk_rating IN ('High', 'Critical')
        GROUP BY linked_risk
        HAVING COUNT(*) > 1
        ORDER BY assessment_count DESC
        LIMIT 10
    """, as_dict=True)

    return {
        'total_risks': total_risks,
        'assessed_risks': assessed_risks,
        'coverage_percentage': coverage_pct,
        'high_risk_findings': high_risk_findings,
        'high_risk_count': len(high_risk_findings),
        'repeat_findings': repeat_findings
    }


# ============================================================================
# 9. ICT / CYBER RISK DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_ict_risk_dashboard_data():
    """Get ICT and cyber risk dashboard data"""
    # Filter by Technology-related categories
    ict_categories = ['Technology', 'Cyber', 'ICT', 'Information Security', 'IT']
    category_filter = "', '".join(ict_categories)

    # ICT Risks by Severity
    by_severity = frappe.db.sql(f"""
        SELECT
            COALESCE(ra.residual_risk_rating, 'Not Assessed') as severity,
            COUNT(*) as count
        FROM `tabRisk Register` rr
        LEFT JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name AND ra.docstatus = 1
        WHERE rr.risk_category IN ('{category_filter}')
        OR rr.impact_area = 'Technology'
        GROUP BY severity
        ORDER BY FIELD(severity, 'Extreme', 'Critical', 'High', 'Medium', 'Low', 'Not Assessed')
    """, as_dict=True)

    # ICT Risks List
    ict_risks = frappe.db.sql(f"""
        SELECT
            rr.name, rr.risk_title, rr.risk_category, rr.status, rr.risk_owner,
            ra.residual_risk_rating, ra.residual_risk_score
        FROM `tabRisk Register` rr
        LEFT JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name AND ra.docstatus = 1
        WHERE rr.risk_category IN ('{category_filter}')
        OR rr.impact_area = 'Technology'
        ORDER BY COALESCE(ra.residual_risk_score, 0) DESC
        LIMIT 20
    """, as_dict=True)

    # ICT KRIs
    ict_kris = frappe.db.sql("""
        SELECT
            name, kri_name, current_value, target_value, current_status, trend
        FROM `tabKey Risk Indicator`
        WHERE status = 'Active'
        AND (kri_category LIKE '%ICT%' OR kri_category LIKE '%Cyber%'
             OR kri_category LIKE '%Tech%' OR kri_category LIKE '%IT%')
        ORDER BY
            CASE current_status WHEN 'Critical' THEN 1 WHEN 'Warning' THEN 2 ELSE 3 END
        LIMIT 10
    """, as_dict=True)

    return {
        'by_severity': by_severity,
        'ict_risks': ict_risks,
        'ict_kris': ict_kris,
        'total_ict_risks': len(ict_risks)
    }


# ============================================================================
# 10. RISK PERFORMANCE & MATURITY DASHBOARD APIs
# ============================================================================

@frappe.whitelist()
def get_risk_performance_data():
    """Get risk performance and maturity metrics"""
    # Risk Closure Rate
    total_risks = frappe.db.count('Risk Register')
    closed_risks = frappe.db.count('Risk Register', {'status': ['in', ['Mitigated', 'Closed', 'Accepted']]})
    closure_rate = round((closed_risks / total_risks * 100) if total_risks > 0 else 0, 1)

    # Average Residual Risk Reduction
    reduction_data = frappe.db.sql("""
        SELECT
            AVG(inherent_risk_score - residual_risk_score) as avg_reduction,
            AVG(
                CASE WHEN inherent_risk_score > 0
                THEN ((inherent_risk_score - residual_risk_score) / inherent_risk_score) * 100
                ELSE 0 END
            ) as avg_reduction_pct
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
        AND inherent_risk_score IS NOT NULL
        AND residual_risk_score IS NOT NULL
    """, as_dict=True)[0]

    avg_reduction = round(flt(reduction_data.avg_reduction), 2)
    avg_reduction_pct = round(flt(reduction_data.avg_reduction_pct), 1)

    # Risk Review Compliance Rate
    total_active = frappe.db.count('Risk Register', {'status': 'Active'})
    reviewed_on_time = frappe.db.sql("""
        SELECT COUNT(*) as count
        FROM `tabRisk Register`
        WHERE status = 'Active'
        AND (next_review_date IS NULL OR next_review_date >= CURDATE())
    """, as_dict=True)[0].count
    review_compliance = round((reviewed_on_time / total_active * 100) if total_active > 0 else 0, 1)

    # Heat Map Trend (Quarterly)
    quarterly_trend = frappe.db.sql("""
        SELECT
            CONCAT(YEAR(assessment_date), '-Q', QUARTER(assessment_date)) as quarter,
            AVG(inherent_risk_score) as avg_inherent,
            AVG(residual_risk_score) as avg_residual,
            COUNT(*) as assessments
        FROM `tabRisk Assessment`
        WHERE docstatus = 1
        AND assessment_date >= DATE_SUB(CURDATE(), INTERVAL 8 QUARTER)
        GROUP BY quarter
        ORDER BY quarter ASC
    """, as_dict=True)

    # Treatment plan effectiveness
    treatment_effectiveness = frappe.db.sql("""
        SELECT
            COUNT(*) as total_plans,
            SUM(CASE WHEN plan_status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN target_completion_date >= actual_completion_date THEN 1 ELSE 0 END) as on_time
        FROM `tabRisk Treatment Plan`
        WHERE plan_status = 'Completed'
    """, as_dict=True)[0]

    return {
        'total_risks': total_risks,
        'closed_risks': closed_risks,
        'closure_rate': closure_rate,
        'avg_risk_reduction': avg_reduction,
        'avg_reduction_percentage': avg_reduction_pct,
        'review_compliance_rate': review_compliance,
        'quarterly_trend': quarterly_trend,
        'treatment_completed': treatment_effectiveness.completed or 0,
        'treatment_on_time': treatment_effectiveness.on_time or 0
    }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@frappe.whitelist()
def get_filter_options():
    """Get filter options for dashboards"""
    departments = frappe.db.sql("""
        SELECT DISTINCT department as value, department as label
        FROM `tabRisk Register`
        WHERE department IS NOT NULL AND department != ''
        ORDER BY department
    """, as_dict=True)

    categories = frappe.db.sql("""
        SELECT name as value, category_name as label
        FROM `tabRisk Category`
        ORDER BY category_name
    """, as_dict=True)

    owners = frappe.db.sql("""
        SELECT DISTINCT risk_owner as value, risk_owner as label
        FROM `tabRisk Register`
        WHERE risk_owner IS NOT NULL
        ORDER BY risk_owner
    """, as_dict=True)

    return {
        'departments': departments,
        'categories': categories,
        'owners': owners
    }


@frappe.whitelist()
def get_all_dashboard_summary():
    """Get a combined summary for all risk dashboards"""
    return {
        'enterprise': get_enterprise_risk_overview(),
        'treatment': get_treatment_dashboard_data(),
        'kri': get_kri_dashboard_data(),
        'performance': get_risk_performance_data()
    }


# ============================================================================
# NUMBER CARD METHODS
# ============================================================================

@frappe.whitelist()
def get_total_risks_count():
    """Get total count of risks in the register"""
    try:
        count = frappe.db.count("Risk Register")
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Total risks count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_high_risks_count():
    """Get count of high/critical risks"""
    try:
        count = frappe.db.sql("""
            SELECT COUNT(DISTINCT rr.name)
            FROM `tabRisk Register` rr
            INNER JOIN `tabRisk Assessment` ra ON ra.linked_risk = rr.name
            WHERE ra.docstatus = 1
            AND ra.residual_risk_rating IN ('High', 'Critical', 'Extreme')
        """)[0][0] or 0
        return {"value": count, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"High risks count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_active_risks_count():
    """Get count of active risks"""
    try:
        count = frappe.db.count("Risk Register", filters={"status": "Active"})
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Active risks count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_mitigated_risks_count():
    """Get count of mitigated/closed risks"""
    try:
        count = frappe.db.count("Risk Register", filters={
            "status": ["in", ["Mitigated", "Closed", "Accepted"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Mitigated risks count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_open_incidents_count():
    """Get count of open risk incidents"""
    try:
        count = frappe.db.count("Risk Incident", filters={
            "incident_status": ["in", ["Open", "Under Investigation", "Reported"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Open incidents count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_total_incidents_count():
    """Get total count of risk incidents"""
    try:
        count = frappe.db.count("Risk Incident")
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Total incidents count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_kri_alerts_count():
    """Get count of KRIs in warning/critical status"""
    try:
        count = frappe.db.count("Key Risk Indicator", filters={
            "status": "Active",
            "current_status": ["in", ["Warning", "Critical"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"KRI alerts count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_active_kris_count():
    """Get count of active KRIs"""
    try:
        count = frappe.db.count("Key Risk Indicator", filters={"status": "Active"})
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Active KRIs count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_overdue_treatments_count():
    """Get count of overdue treatment plans"""
    try:
        count = frappe.db.sql("""
            SELECT COUNT(*)
            FROM `tabRisk Treatment Plan`
            WHERE target_completion_date < CURDATE()
            AND plan_status NOT IN ('Completed', 'Cancelled')
        """)[0][0] or 0
        return {"value": count, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Overdue treatments count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_active_treatments_count():
    """Get count of active treatment plans"""
    try:
        count = frappe.db.count("Risk Treatment Plan", filters={
            "plan_status": ["in", ["Draft", "In Progress", "Pending Approval"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Active treatments count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_total_controls_count():
    """Get total count of risk controls"""
    try:
        count = frappe.db.count("Risk Control")
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Total controls count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_effective_controls_count():
    """Get count of effective controls"""
    try:
        count = frappe.db.count("Risk Control", filters={
            "effectiveness_rating": ["in", ["Effective", "Highly Effective"]]
        })
        return {"value": count or 0, "fieldtype": "Int"}
    except Exception as e:
        frappe.log_error(f"Effective controls count error: {str(e)}")
        return {"value": 0, "fieldtype": "Int"}


@frappe.whitelist()
def get_risk_score_average():
    """Get average residual risk score"""
    try:
        avg = frappe.db.sql("""
            SELECT AVG(residual_risk_score)
            FROM `tabRisk Assessment`
            WHERE docstatus = 1
            AND residual_risk_score IS NOT NULL
        """)[0][0] or 0
        return {"value": round(flt(avg), 1), "fieldtype": "Float"}
    except Exception as e:
        frappe.log_error(f"Risk score average error: {str(e)}")
        return {"value": 0, "fieldtype": "Float"}


@frappe.whitelist()
def get_treatment_completion_rate():
    """Get treatment plan completion rate"""
    try:
        stats = frappe.db.sql("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN plan_status = 'Completed' THEN 1 ELSE 0 END) as completed
            FROM `tabRisk Treatment Plan`
        """, as_dict=True)

        rate = 0
        if stats and stats[0].get("total", 0) > 0:
            rate = (stats[0].get("completed", 0) / stats[0]["total"]) * 100

        return {"value": round(rate, 1), "fieldtype": "Percent"}
    except Exception as e:
        frappe.log_error(f"Treatment completion rate error: {str(e)}")
        return {"value": 0, "fieldtype": "Percent"}
