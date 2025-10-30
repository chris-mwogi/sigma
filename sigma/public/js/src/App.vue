<template>
  <div id="app">
    <!-- Authenticated Layout -->
    <el-container v-if="!isLoginPage" class="app-container">
      <!-- Header -->
      <el-header class="app-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="sigma-logo" @click="toggleSidebar">Σ</div>
            <h1 class="app-title">Sigma Security Management</h1>
          </div>
          <div class="user-section">
            <el-dropdown>
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ currentUser?.full_name || 'User' }}
                <el-icon class="el-icon--right"><arrow-down /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="logout">
                    <el-icon><SwitchButton /></el-icon>
                    Logout
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-container class="app-body">
        <!-- Sidebar Navigation -->
        <el-aside :width="sidebarWidth" :class="['app-sidebar', { collapsed: !showSidebar }]">
          <div class="sidebar-content">
            <el-menu
              :default-active="$route.path"
              router
              class="sidebar-menu"
              :collapse="!showSidebar"
              background-color="#1a3a52"
              text-color="#ecf0f1"
              active-text-color="#4a9eff"
            >
              <el-menu-item index="/">
                <el-icon><House /></el-icon>
                <span>Dashboard</span>
              </el-menu-item>
              <el-menu-item index="/cases">
                <el-icon><Document /></el-icon>
                <span>Cases</span>
              </el-menu-item>
              <el-menu-item index="/incidents">
                <el-icon><Warning /></el-icon>
                <span>Incidents</span>
              </el-menu-item>
              <el-menu-item index="/access-control">
                <el-icon><Lock /></el-icon>
                <span>Access Control</span>
              </el-menu-item>
              <el-menu-item index="/guard-monitoring">
                <el-icon><View /></el-icon>
                <span>Guard Monitoring</span>
              </el-menu-item>
              <el-menu-item index="/assets">
                <el-icon><Box /></el-icon>
                <span>Assets</span>
              </el-menu-item>
              <el-menu-item index="/risk-assessment">
                <el-icon><DataAnalysis /></el-icon>
                <span>Risk Assessment</span>
              </el-menu-item>
              <el-menu-item index="/vehicle-management">
                <el-icon><Van /></el-icon>
                <span>Vehicle Management</span>
              </el-menu-item>
              <el-menu-item index="/visitor-management">
                <el-icon><User /></el-icon>
                <span>Visitor Management</span>
              </el-menu-item>
              <el-menu-item index="/helpdesk">
                <el-icon><Service /></el-icon>
                <span>Helpdesk</span>
              </el-menu-item>
              <el-menu-item index="/support">
                <el-icon><ChatDotRound /></el-icon>
                <span>Support</span>
              </el-menu-item>
              <el-menu-item index="/telephony">
                <el-icon><Phone /></el-icon>
                <span>Telephony</span>
              </el-menu-item>
              <el-menu-item index="/projects">
                <el-icon><Folder /></el-icon>
                <span>Projects</span>
              </el-menu-item>
              <el-menu-item index="/crm">
                <el-icon><Briefcase /></el-icon>
                <span>CRM</span>
              </el-menu-item>
            </el-menu>

            <!-- Version Display -->
            <div class="version-display" v-if="!showSidebar">
              <span class="version-text">v1.0</span>
            </div>
            <div class="version-display-expanded" v-else>
              <span class="version-text">Version 1.0.0</span>
            </div>
          </div>
        </el-aside>

        <!-- Main Content Area -->
        <el-main class="app-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>

    <!-- Login Page (No Layout) -->
    <router-view v-else />

    <!-- Mobile Overlay -->
    <div v-if="showSidebar && isMobile" class="mobile-overlay" @click="toggleSidebar"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import {
  User,
  ArrowDown,
  SwitchButton,
  House,
  Document,
  Warning,
  Lock,
  View,
  Box,
  DataAnalysis,
  Van,
  Service,
  ChatDotRound,
  Phone,
  Folder,
  Briefcase
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const showSidebar = ref(true)
const isMobile = ref(false)
const currentUser = ref(null)

// Computed
const isLoginPage = computed(() => route.path === '/login')
const sidebarWidth = computed(() => {
  if (isMobile.value) {
    return showSidebar.value ? '250px' : '0px'
  }
  return showSidebar.value ? '250px' : '64px'
})

// Methods
const toggleSidebar = () => {
  showSidebar.value = !showSidebar.value
  localStorage.setItem('sigma-sidebar-collapsed', !showSidebar.value)
}

const logout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Logout failed:', error)
  }
}

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
  if (isMobile.value) {
    showSidebar.value = false
  }
}

const loadCurrentUser = async () => {
  try {
    const response = await fetch('/api/method/frappe.auth.get_logged_user', {
      headers: {
        'X-Frappe-CSRF-Token': frappe.csrf_token
      }
    })
    const data = await response.json()
    if (data.message) {
      currentUser.value = {
        name: data.message,
        full_name: data.message
      }
    }
  } catch (error) {
    console.error('Failed to load user:', error)
  }
}

// Lifecycle
onMounted(() => {
  // Check mobile
  checkMobile()
  window.addEventListener('resize', checkMobile)

  // Restore sidebar state
  const collapsed = localStorage.getItem('sigma-sidebar-collapsed')
  if (collapsed !== null && !isMobile.value) {
    showSidebar.value = collapsed === 'false'
  }

  // Load current user
  if (!isLoginPage.value) {
    loadCurrentUser()
  }
})

// Watch route changes
watch(() => route.path, () => {
  if (isMobile.value) {
    showSidebar.value = false
  }
})
</script>

<style>
:root {
  --el-color-primary: #003d7a;
  --el-color-success: #0052a3;
  --el-color-info: #0052a3;
  --el-color-warning: #FFF9AF;
}

/* Ensure full width usage */
html, body {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  width: 100%;
  height: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: inherit;
}

/* Override Bootstrap container width limitations */
@media (min-width: 576px) {
  .container-sm, .container {
    max-width: none !important;
  }
}

@media (min-width: 768px) {
  .container-md, .container-sm, .container {
    max-width: none !important;
  }
}

@media (min-width: 992px) {
  .container-lg, .container-md, .container-sm, .container {
    max-width: none !important;
  }
}

@media (min-width: 1200px) {
  .container-xl, .container-lg, .container-md, .container-sm, .container {
    max-width: none !important;
  }
}

@media (min-width: 1400px) {
  .container-xxl, .container-xl, .container-lg, .container-md, .container-sm, .container {
    max-width: none !important;
  }
}

/* Override Bootstrap container padding */
@media (min-width: 992px) {
  .container {
    padding-left: 0 !important;
    padding-right: 0 !important;
  }
}

/* Override Bootstrap margin utilities */
.mb-4, .my-4 {
  margin-bottom: 0 !important;
}

.mt-4, .my-4 {
  margin-top: 0 !important;
}

/* Table header theme */
.el-table th, .el-table__header th {
  background-color: #154D71 !important;
  color: #FFF9AF !important;
}
.el-table thead .cell {
  color: #FFF9AF !important;
}
</style>

<style scoped>
.app-container {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #003d7a 0%, #0052a3 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  flex-shrink: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  height: 60px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sigma-logo {
  font-size: 32px;
  font-weight: bold;
  cursor: pointer;
  user-select: none;
  transition: transform 0.3s ease;
  opacity: 0.95;
}

.sigma-logo:hover {
  transform: scale(1.1);
}

.app-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #FFF9AF;
  letter-spacing: 0.3px;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.app-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  height: calc(100vh - 60px);
}

.app-sidebar {
  background-color: #1a3a52;
  transition: width .2s ease;
  overflow-y: auto;
  overflow-x: hidden;
  flex-shrink: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.app-sidebar.collapsed {
  width: 64px !important;
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-menu {
  border: none;
  flex: 1;
}

.version-display {
  background-color: #0f2a3d;
  padding: 12px 0;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.version-display-expanded {
  background-color: #0f2a3d;
  padding: 12px 20px;
  text-align: center;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  flex-shrink: 0;
}

.version-text {
  color: #95a5a6;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.app-main {
  background-color: #f5f7fa;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  height: 100%;
}

.mobile-overlay {
  position: fixed;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .app-header {
    height: 56px;
    padding: 0 12px;
  }

  .app-title {
    font-size: 16px;
  }

  .app-body {
    height: calc(100vh - 56px);
  }

  .app-sidebar {
    position: fixed;
    top: 56px;
    left: 0;
    height: calc(100vh - 56px);
    z-index: 1000;
  }
}
</style>

