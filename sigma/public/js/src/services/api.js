import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: window.location.origin,
  timeout: 120000,  // 2 minutes - supports slow API calls
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add CSRF token if available (meta, window.frappe, window or cookie fallback)
    const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
    const winToken = (window.frappe && window.frappe.csrf_token) || window.csrf_token
    const cookieToken = (() => {
      const m = document.cookie.match(/(?:^|; )csrf_token=([^;]+)/)
      return m ? decodeURIComponent(m[1]) : null
    })()
    const csrfToken = metaToken || winToken || cookieToken
    if (csrfToken && csrfToken !== 'None') {
      config.headers['X-Frappe-CSRF-Token'] = csrfToken
    }

    // Add site name if available
    const siteName = window.frappe?.boot?.sitename
    if (siteName) {
      config.headers['X-Frappe-Site-Name'] = siteName
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 401:
          // Unauthorized - redirect to login
          window.location.href = '/login'
          break
        case 403:
          // Forbidden
          console.error('Access forbidden:', data.message || 'You do not have permission to perform this action')
          break
        case 404:
          // Not found
          console.error('Resource not found:', data.message || 'The requested resource was not found')
          break
        case 500:
          // Server error
          console.error('Server error:', data.message || 'An internal server error occurred')
          break
        default:
          console.error('API error:', data.message || error.message)
      }

      // Extract error message from Frappe response format
      if (data && data.message) {
        error.message = data.message
      } else if (data && data.exc) {
        error.message = data.exc
      }
    } else if (error.request) {
      // Network error
      error.message = 'Network error: Please check your internet connection'
    }

    return Promise.reject(error)
  }
)

// Helper methods
export const apiHelpers = {
  // Get CSRF token
  getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
  },

  // Format error message
  formatError(error) {
    if (error.response && error.response.data) {
      const data = error.response.data
      if (data.message) {
        return data.message
      } else if (data.exc) {
        return data.exc
      }
    }
    return error.message || 'An unexpected error occurred'
  }
}

// Add call method to api instance for calling Frappe whitelisted methods
api.call = async function(method, args = {}) {
  const response = await this.post('/api/method/' + method, args)
  return response.data
}

export default api

