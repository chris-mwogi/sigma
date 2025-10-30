import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = computed(() => !!user.value)

  const checkAuth = async () => {
    try {
      const response = await api.get('/api/method/frappe.auth.get_logged_user')
      if (response.data.message) {
        const userEmail = response.data.message
        const userResponse = await api.get(`/api/resource/User/${userEmail}`)
        user.value = userResponse.data.data
      }
    } catch (error) {
      user.value = null
      throw error
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post('/api/method/frappe.client.login', {
        usr: email,
        pwd: password
      })
      
      if (response.data.message === 'Logged In') {
        await checkAuth()
        return true
      }
      return false
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = async () => {
    try {
      await api.post('/api/method/frappe.client.logout')
      user.value = null
    } catch (error) {
      console.error('Logout failed:', error)
      throw error
    }
  }

  return {
    user,
    isAuthenticated,
    checkAuth,
    login,
    logout
  }
})

