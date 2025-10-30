import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  // State
  const currentUser = ref(null)
  const isAuthenticated = ref(false)
  const isInitialized = ref(false)

  // Actions
  const checkSession = async () => {
    try {
      // Check if user is logged in by calling get_logged_user
      const response = await api.get('/api/method/frappe.auth.get_logged_user')

      if (response.data && response.data.message && response.data.message !== 'Guest') {
        // User is logged in, get their details
        await getCurrentUser()
        return true
      } else {
        isAuthenticated.value = false
        currentUser.value = null
        return false
      }
    } catch (error) {
      console.error('Session check error:', error)
      isAuthenticated.value = false
      currentUser.value = null
      return false
    } finally {
      isInitialized.value = true
    }
  }

  const getCurrentUser = async () => {
    try {
      // Get current user from Frappe session
      const response = await api.get('/api/method/frappe.client.get_list', {
        params: {
          doctype: 'User',
          filters: [['User', 'email', '=', frappe.session.user]],
          fields: ['email', 'full_name', 'user_image', 'first_name', 'last_name']
        }
      })

      if (response.data && response.data.message && response.data.message.length > 0) {
        const userData = response.data.message[0]
        currentUser.value = {
          email: userData.email,
          full_name: userData.full_name,
          user_image: userData.user_image,
          first_name: userData.first_name,
          last_name: userData.last_name,
          roles: (window.frappe && window.frappe.user_roles) || []
        }
        isAuthenticated.value = true
      }
      return currentUser.value
    } catch (error) {
      currentUser.value = null
      isAuthenticated.value = false
      throw error
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/method/login', {
        usr: email,
        pwd: password
      })

      if (response.data && response.data.message === 'Logged In') {
        await getCurrentUser()
        return true
      }
      return false
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/method/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      currentUser.value = null
      isAuthenticated.value = false
    }
  }

  return {
    // State
    currentUser,
    isAuthenticated,
    isInitialized,

    // Actions
    checkSession,
    getCurrentUser,
    login,
    logout
  }
})

