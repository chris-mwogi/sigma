import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// Views
import Dashboard from '../views/Dashboard.vue'
import CaseList from '../views/cases/CaseList.vue'
import CaseDetail from '../views/cases/CaseDetail.vue'
import CaseForm from '../views/cases/CaseForm.vue'
import IncidentList from '../views/incidents/IncidentList.vue'
import IncidentDetail from '../views/incidents/IncidentDetail.vue'
import AccessControl from '../views/access-control/AccessControl.vue'
import GuardMonitoring from '../views/guard-monitoring/GuardMonitoring.vue'
import AssetList from '../views/assets/AssetList.vue'
import AssetDetail from '../views/assets/AssetDetail.vue'
import RiskAssessment from '../views/risk-assessment/RiskAssessment.vue'
import Login from '../views/Login.vue'

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
    path: '/guard-monitoring',
    name: 'GuardMonitoring',
    component: GuardMonitoring,
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
    path: '/risk-assessment',
    name: 'RiskAssessment',
    component: RiskAssessment,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory('/app/sigma/'),
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

