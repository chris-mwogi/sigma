<template>
  <div id="app" class="sigma-app">
    <!-- Header -->
    <header class="sigma-header">
      <button class="sigma-toggle-btn" @click="toggleSidebar" title="Toggle Sidebar" :aria-expanded="!sidebarCollapsed" aria-controls="sigma-sidebar">
        <span v-if="!sidebarCollapsed">☰</span>
        <span v-else>✕</span>
      </button>

      <div class="sigma-header-logo" @click="toggleSidebar" title="Toggle Sidebar">
        <span class="logo-icon">⚡</span>
        <span class="logo-text">Sigma</span>
      </div>

      <div class="sigma-header-spacer"></div>

      <div class="sigma-header-user">
        <span class="user-name">{{ currentUser }}</span>
        <button @click="logout" class="btn-logout">Logout</button>
      </div>
    </header>

    <!-- Sidebar -->
    <aside id="sigma-sidebar" class="sigma-sidebar" :class="{ collapsed: sidebarCollapsed }" aria-label="Primary">
      <ul class="sigma-sidebar-menu">
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">📊</span>
            <span>Dashboard</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/cases"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">📋</span>
            <span>Cases</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/incidents"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">⚠️</span>
            <span>Incidents</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/access-control"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">🔐</span>
            <span>Access Control</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/guard-monitoring"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">👮</span>
            <span>Guard Monitoring</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/assets"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">🏢</span>
            <span>Assets</span>
          </router-link>
        </li>
        <li class="sigma-sidebar-menu-item">
          <router-link
            to="/risk-assessment"
            class="sigma-sidebar-menu-link"
            active-class="active"
            @click="closeSidebarOnMobile"
          >
            <span class="sigma-sidebar-menu-icon">⚡</span>
            <span>Risk Assessment</span>
          </router-link>
        </li>
      </ul>
    </aside>

    <!-- Mobile overlay -->
    <div v-if="!sidebarCollapsed" class="sigma-overlay" @click="toggleSidebar" aria-hidden="true"></div>

    <!-- Main Content -->
    <main class="sigma-main" :class="{ expanded: sidebarCollapsed }">
      <div class="sigma-content">
        <router-view />
      </div>
    </main>

    <!-- Loading Overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const loading = ref(false)
    const sidebarCollapsed = ref(false)

    const currentUser = computed(() => authStore.user?.full_name || 'User')

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value
      try {
        localStorage.setItem('sigma.sidebar.collapsed', sidebarCollapsed.value ? '1' : '0')
      } catch (e) {}
    }

    const closeSidebarOnMobile = () => {
      // Close sidebar on mobile when a link is clicked
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true
      }
    }

    const logout = async () => {
      await authStore.logout()
      router.push('/login')
    }

    onMounted(async () => {
      // restore persisted sidebar state
      try {
        const persisted = localStorage.getItem('sigma.sidebar.collapsed')
        if (persisted !== null) sidebarCollapsed.value = persisted === '1'
      } catch (e) {}

      loading.value = true
      try {
        await authStore.checkAuth()
      } catch (error) {
        console.error('Auth check failed:', error)
        router.push('/login')
      } finally {
        loading.value = false
      }
    })

    return {
      loading,
      currentUser,
      logout,
      sidebarCollapsed,
      toggleSidebar,
      closeSidebarOnMobile,
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.sigma-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--kp-bg);
}

/* Header Styles */
.sigma-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: linear-gradient(135deg, var(--kp-primary) 0%, var(--kp-primary-dark) 100%);
  color: white;
  display: flex;
  align-items: center;
  padding: 0 20px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 51, 127, 0.2);
}

.sigma-header-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 24px;
  font-weight: bold;
  user-select: none;
  transition: opacity 0.3s ease;
}

.sigma-header-logo:hover {
  opacity: 0.9;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.sigma-toggle-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
  padding: 5px 10px;
  margin-right: 10px;
  display: none;
  transition: opacity 0.3s ease;
}

.sigma-toggle-btn:hover {
  opacity: 0.8;
}

.sigma-header-spacer {
  flex: 1;
}

.sigma-header-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.btn-logout {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.btn-logout:hover {
  background-color: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

/* Sidebar Styles */
.sigma-sidebar {
  position: fixed;
  left: 0;
  top: 60px;
  width: 250px;
  height: calc(100vh - 60px);
  background: var(--kp-surface);
  color: var(--kp-text);
  overflow-y: auto;
  transition: transform 0.3s ease;
  z-index: 999;
  border-right: 1px solid var(--kp-border);
}

.sigma-sidebar.collapsed {
  transform: translateX(-100%);
}

.sigma-sidebar-menu {
  list-style: none;
  padding: 20px 0;
}

.sigma-sidebar-menu-item {
  padding: 0;
  margin: 0;
}

.sigma-sidebar-menu-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  color: #666;
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.sigma-sidebar-menu-link:hover {
  background-color: var(--kp-hover);
  border-left-color: var(--kp-primary);
  color: var(--kp-primary);
  padding-left: 17px;
}

.sigma-sidebar-menu-link.active {
  background-color: var(--kp-hover);
  border-left-color: var(--kp-primary);
  color: var(--kp-primary);
  font-weight: 600;
}

.sigma-sidebar-menu-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

/* Main Content Styles */
.sigma-main {
  margin-left: 250px;
  margin-top: 60px;
  flex: 1;
  overflow-y: auto;
  background-color: var(--kp-bg);
  transition: margin-left 0.3s ease;
}

.sigma-main.expanded {
  margin-left: 0;
}

.sigma-content {
  padding: 30px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Loading Overlay */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top: 4px solid white;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Overlay (mobile) */
.sigma-overlay {
  position: fixed;
  inset: 60px 0 0 0;
  background: rgba(0,0,0,0.35);
  z-index: 900;
  display: none;
}

/* Mobile Responsive */
@media (max-width: 768px) {
  .sigma-toggle-btn { display: block; }

  .sigma-sidebar { width: 100%; box-shadow: -2px 0 8px rgba(0, 0, 0, 0.2); }

  .sigma-overlay { display: block; }

  .sigma-main { margin-left: 0; }

  .sigma-content { padding: 20px; }

  .logo-text { display: none; }
}

@media (max-width: 480px) {
  .sigma-header {
    padding: 0 10px;
  }

  .sigma-content {
    padding: 15px;
  }

  .sigma-sidebar-menu-link {
    padding: 10px 15px;
  }

  .user-name {
    display: none;
  }
}
</style>

