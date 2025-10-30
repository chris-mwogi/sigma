import axios from 'axios'

function getCookie(name) {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1))
        break
      }
    }
  }
  return cookieValue
}

function getCSRFToken() {
  // Try to get from cookie first
  let token = getCookie('frappe_csrf_token') || getCookie('csrf_token')

  // If not in cookie, try to get from meta tag
  if (!token) {
    const metaTag = document.querySelector('meta[name="csrf-token"]')
    if (metaTag) {
      token = metaTag.getAttribute('content')
    }
  }

  return token
}

const api = axios.create({
  baseURL: window.location.origin,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor
api.interceptors.request.use(
  config => {
    // Get CSRF token from cookie or meta tag
    const token = getCSRFToken()
    if (token) {
      config.headers['X-Frappe-CSRF-Token'] = token
    }
    return config
  },
  error => Promise.reject(error)
)

// Add response interceptor
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/app/login'
    }
    return Promise.reject(error)
  }
)

export default api
export { getCSRFToken }

