import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import Dashboard from '../views/Dashboard.vue'
import CaseList from '../views/cases/CaseList.vue'
import CaseDetail from '../views/cases/CaseDetail.vue'
import CaseForm from '../views/cases/CaseForm.vue'
import IncidentList from '../views/incidents/IncidentList.vue'
import IncidentDetail from '../views/incidents/IncidentDetail.vue'
import AccessControl from '../views/dashboard-access/AccessControl.vue'
import AssetList from '../views/assets/AssetList.vue'
import AssetDetail from '../views/assets/AssetDetail.vue'
import AssetTransactions from '../views/assets/AssetTransactions.vue'
import HelpdeskDashboard from '../views/helpdesk/HelpdeskDashboard.vue'
import SupportDashboard from '../views/support/SupportDashboard.vue'
import TelephonyDashboard from '../views/telephony/TelephonyDashboard.vue'
import ProjectsDashboard from '../views/projects/ProjectsDashboard.vue'
import CRMDashboard from '../views/crm/CRMDashboard.vue'
import Login from '../views/Login.vue'

// Guarding Enterprise Dashboards
import ExecutiveSecurityDashboard from '../views/dashboard-guarding/ExecutiveSecurityDashboard.vue'
import SOCDashboard from '../views/dashboard-guarding/SOCDashboard.vue'
import GuardSupervisorDashboard from '../views/dashboard-guarding/GuardSupervisorDashboard.vue'
import GuardPerformanceDashboard from '../views/dashboard-guarding/GuardPerformanceDashboard.vue'
import PatrolMonitoringDashboard from '../views/dashboard-guarding/PatrolMonitoringDashboard.vue'
import VendorManagementDashboard from '../views/dashboard-guarding/VendorManagementDashboard.vue'
import PostComplianceDashboard from '../views/dashboard-guarding/PostComplianceDashboard.vue'
import IncidentEscalationDashboard from '../views/dashboard-guarding/IncidentEscalationDashboard.vue'
import GatehouseDashboard from '../views/dashboard-guarding/GatehouseDashboard.vue'
import K9UnitDashboard from '../views/dashboard-guarding/K9UnitDashboard.vue'
import CombinedSecurityRiskDashboard from '../views/dashboard-guarding/CombinedSecurityRiskDashboard.vue'

// Vehicle Management Dashboards
import GateTrafficDashboard from '../views/dashboard-vehicle/GateTrafficDashboard.vue'
import FleetOperationsDashboard from '../views/dashboard-vehicle/FleetOperationsDashboard.vue'
import StaffVehicleDashboard from '../views/dashboard-vehicle/StaffVehicleDashboard.vue'
import VisitorVehicleDashboard from '../views/dashboard-vehicle/VisitorVehicleDashboard.vue'
import VehicleAccessControlDashboard from '../views/dashboard-vehicle/VehicleAccessControlDashboard.vue'
import VehicleMaintenanceDashboard from '../views/dashboard-vehicle/VehicleMaintenanceDashboard.vue'
import VehicleSecurityDashboard from '../views/dashboard-vehicle/VehicleSecurityDashboard.vue'
import ParkingManagementDashboard from '../views/dashboard-vehicle/ParkingManagementDashboard.vue'

// Case Management Dashboards
import CaseExecutiveDashboard from '../views/dashboard-case/CaseExecutiveDashboard.vue'
import CaseInvestigationDashboard from '../views/dashboard-case/CaseInvestigationDashboard.vue'
import FraudEthicsDashboard from '../views/dashboard-case/FraudEthicsDashboard.vue'
import HRMisconductDashboard from '../views/dashboard-case/HRMisconductDashboard.vue'
import SafetyIncidentDashboard from '../views/dashboard-case/SafetyIncidentDashboard.vue'
import CustomerComplaintDashboard from '../views/dashboard-case/CustomerComplaintDashboard.vue'
import LegalCaseDashboard from '../views/dashboard-case/LegalCaseDashboard.vue'
import SLAPerformanceDashboard from '../views/dashboard-case/SLAPerformanceDashboard.vue'
import CaseGeographicDashboard from '../views/dashboard-case/CaseGeographicDashboard.vue'
import AuditCaseDashboard from '../views/dashboard-case/AuditCaseDashboard.vue'
import WhistleblowerDashboard from '../views/dashboard-case/WhistleblowerDashboard.vue'
import CaseClosureDashboard from '../views/dashboard-case/CaseClosureDashboard.vue'
import AssetTheftDashboard from '../views/dashboard-case/AssetTheftDashboard.vue'
import IllegalConnectionDashboard from '../views/dashboard-case/IllegalConnectionDashboard.vue'

// Access Control Dashboards
import AccessCommandCenterDashboard from '../views/dashboard-access/AccessCommandCenterDashboard.vue'
import AccessManagementDashboard from '../views/dashboard-access/AccessManagementDashboard.vue'

// Risk Management Dashboards
import EnterpriseRiskDashboard from '../views/dashboard-risk/EnterpriseRiskDashboard.vue'
import DepartmentalRiskDashboard from '../views/dashboard-risk/DepartmentalRiskDashboard.vue'
import RiskHeatMapDashboard from '../views/dashboard-risk/RiskHeatMapDashboard.vue'
import RiskTreatmentDashboard from '../views/dashboard-risk/RiskTreatmentDashboard.vue'
import KRIDashboard from '../views/dashboard-risk/KRIDashboard.vue'
import IncidentLossDashboard from '../views/dashboard-risk/IncidentLossDashboard.vue'
import ComplianceRiskDashboard from '../views/dashboard-risk/ComplianceRiskDashboard.vue'
import AuditAssuranceDashboard from '../views/dashboard-risk/AuditAssuranceDashboard.vue'
import ICTRiskDashboard from '../views/dashboard-risk/ICTRiskDashboard.vue'
import RiskPerformanceDashboard from '../views/dashboard-risk/RiskPerformanceDashboard.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/cases',
    name: 'CaseList',
    component: CaseList,
    meta: { requiresAuth: true }
  },
  {
    path: '/cases/:id',
    name: 'CaseDetail',
    component: CaseDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/cases/new',
    name: 'CaseForm',
    component: CaseForm,
    meta: { requiresAuth: true }
  },
  {
    path: '/incidents',
    name: 'IncidentList',
    component: IncidentList,
    meta: { requiresAuth: true }
  },
  {
    path: '/incidents/:id',
    name: 'IncidentDetail',
    component: IncidentDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/access-control',
    name: 'AccessControl',
    component: AccessControl,
    meta: { requiresAuth: true }
  },
  {
    path: '/assets',
    name: 'AssetList',
    component: AssetList,
    meta: { requiresAuth: true }
  },
  {
    path: '/assets/:id',
    name: 'AssetDetail',
    component: AssetDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/asset-transactions',
    name: 'AssetTransactions',
    component: AssetTransactions,
    meta: { requiresAuth: true }
  },
  {
    path: '/helpdesk',
    name: 'HelpdeskDashboard',
    component: HelpdeskDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/support',
    name: 'SupportDashboard',
    component: SupportDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/telephony',
    name: 'TelephonyDashboard',
    component: TelephonyDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/projects',
    name: 'ProjectsDashboard',
    component: ProjectsDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/crm',
    name: 'CRMDashboard',
    component: CRMDashboard,
    meta: { requiresAuth: true }
  },
  // Enterprise Guarding Dashboards
  {
    path: '/dashboards/executive-security',
    name: 'ExecutiveSecurityDashboard',
    component: ExecutiveSecurityDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/soc',
    name: 'SOCDashboard',
    component: SOCDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/guard-supervisor',
    name: 'GuardSupervisorDashboard',
    component: GuardSupervisorDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/guard-performance',
    name: 'GuardPerformanceDashboard',
    component: GuardPerformanceDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/patrol-monitoring',
    name: 'PatrolMonitoringDashboard',
    component: PatrolMonitoringDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/vendor-management',
    name: 'VendorManagementDashboard',
    component: VendorManagementDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/post-compliance',
    name: 'PostComplianceDashboard',
    component: PostComplianceDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/incident-escalation',
    name: 'IncidentEscalationDashboard',
    component: IncidentEscalationDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/gatehouse',
    name: 'GatehouseDashboard',
    component: GatehouseDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/k9-unit',
    name: 'K9UnitDashboard',
    component: K9UnitDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/security-risk',
    name: 'CombinedSecurityRiskDashboard',
    component: CombinedSecurityRiskDashboard,
    meta: { requiresAuth: true }
  },
  // Vehicle Management Dashboards
  {
    path: '/dashboards/gate-traffic',
    name: 'GateTrafficDashboard',
    component: GateTrafficDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/fleet-operations',
    name: 'FleetOperationsDashboard',
    component: FleetOperationsDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/staff-vehicle',
    name: 'StaffVehicleDashboard',
    component: StaffVehicleDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/visitor-vehicle',
    name: 'VisitorVehicleDashboard',
    component: VisitorVehicleDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/vehicle-access-control',
    name: 'VehicleAccessControlDashboard',
    component: VehicleAccessControlDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/vehicle-maintenance',
    name: 'VehicleMaintenanceDashboard',
    component: VehicleMaintenanceDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/vehicle-security',
    name: 'VehicleSecurityDashboard',
    component: VehicleSecurityDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/parking-management',
    name: 'ParkingManagementDashboard',
    component: ParkingManagementDashboard,
    meta: { requiresAuth: true }
  },
  // Case Management Dashboards
  {
    path: '/dashboards/case-executive',
    name: 'CaseExecutiveDashboard',
    component: CaseExecutiveDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/case-investigation',
    name: 'CaseInvestigationDashboard',
    component: CaseInvestigationDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/fraud-ethics',
    name: 'FraudEthicsDashboard',
    component: FraudEthicsDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/hr-misconduct',
    name: 'HRMisconductDashboard',
    component: HRMisconductDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/safety-incident',
    name: 'SafetyIncidentDashboard',
    component: SafetyIncidentDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/customer-complaint',
    name: 'CustomerComplaintDashboard',
    component: CustomerComplaintDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/legal-case',
    name: 'LegalCaseDashboard',
    component: LegalCaseDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/sla-performance',
    name: 'SLAPerformanceDashboard',
    component: SLAPerformanceDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/case-geographic',
    name: 'CaseGeographicDashboard',
    component: CaseGeographicDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/audit-case',
    name: 'AuditCaseDashboard',
    component: AuditCaseDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/whistleblower',
    name: 'WhistleblowerDashboard',
    component: WhistleblowerDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/case-closure',
    name: 'CaseClosureDashboard',
    component: CaseClosureDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/asset-theft',
    name: 'AssetTheftDashboard',
    component: AssetTheftDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/illegal-connection',
    name: 'IllegalConnectionDashboard',
    component: IllegalConnectionDashboard,
    meta: { requiresAuth: true }
  },
  // Access Control Dashboards
  {
    path: '/dashboards/access-command-center',
    name: 'AccessCommandCenterDashboard',
    component: AccessCommandCenterDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/access-management',
    name: 'AccessManagementDashboard',
    component: AccessManagementDashboard,
    meta: { requiresAuth: true }
  },
  // Risk Management Dashboards
  {
    path: '/dashboards/risk-enterprise',
    name: 'EnterpriseRiskDashboard',
    component: EnterpriseRiskDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-departmental',
    name: 'DepartmentalRiskDashboard',
    component: DepartmentalRiskDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-heatmap',
    name: 'RiskHeatMapDashboard',
    component: RiskHeatMapDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-treatment',
    name: 'RiskTreatmentDashboard',
    component: RiskTreatmentDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-kri',
    name: 'KRIDashboard',
    component: KRIDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-incidents',
    name: 'IncidentLossDashboard',
    component: IncidentLossDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-compliance',
    name: 'ComplianceRiskDashboard',
    component: ComplianceRiskDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-audit',
    name: 'AuditAssuranceDashboard',
    component: AuditAssuranceDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-ict',
    name: 'ICTRiskDashboard',
    component: ICTRiskDashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/dashboards/risk-performance',
    name: 'RiskPerformanceDashboard',
    component: RiskPerformanceDashboard,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/sigma-frontend/'),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router

