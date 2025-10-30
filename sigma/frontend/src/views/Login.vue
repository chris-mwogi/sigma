<template>
  <div class="login-container">
    <div class="login-left">
      <div class="login-branding">
        <div class="logo-large">⚡</div>
        <h1>Kenya Power</h1>
        <p>Security Management System</p>
        <div class="features">
          <div class="feature-item">
            <span class="feature-icon">🔒</span>
            <span>Secure Access</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📊</span>
            <span>Real-time Monitoring</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">⚡</span>
            <span>Instant Alerts</span>
          </div>
        </div>
      </div>
    </div>

    <div class="login-right">
      <div class="login-box">
        <div class="login-header">
          <h2>Welcome Back</h2>
          <p>Sign in to your account</p>
        </div>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="you@example.com"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              required
            />
          </div>

          <div v-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg btn-block" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <div class="login-footer">
          <p>© 2025 Kenya Power. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const email = ref('')
    const password = ref('')
    const loading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      loading.value = true
      error.value = ''

      try {
        await authStore.login(email.value, password.value)
        router.push('/')
      } catch (err) {
        error.value = err.response?.data?.message || 'Login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      email,
      password,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  min-height: 100vh;
  background: white;
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #00337F 0%, #002555 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  min-height: 100vh;
}

.login-branding {
  text-align: center;
  max-width: 400px;
}

.logo-large {
  font-size: 80px;
  margin-bottom: 20px;
  display: block;
}

.login-branding h1 {
  font-size: 36px;
  margin: 0 0 10px 0;
  font-weight: 700;
}

.login-branding p {
  font-size: 16px;
  margin: 0 0 40px 0;
  opacity: 0.9;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 40px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
}

.feature-icon {
  font-size: 24px;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: #f8f9fa;
}

.login-box {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 51, 127, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 28px;
  margin: 0 0 8px 0;
  color: #00337F;
  font-weight: 700;
}

.login-header p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

label {
  font-weight: 600;
  margin-bottom: 8px;
  color: #333;
  font-size: 14px;
}

input {
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.3s ease;
}

input:focus {
  outline: none;
  border-color: #00337F;
  box-shadow: 0 0 0 3px rgba(0, 51, 127, 0.1);
}

.btn-lg {
  padding: 12px;
  font-size: 16px;
  margin-top: 10px;
  font-weight: 600;
  border-radius: 6px;
}

.btn-block {
  width: 100%;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border-left: 4px solid;
}

.alert-danger {
  background-color: #f8d7da;
  border-color: #dc3545;
  color: #721c24;
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  font-size: 12px;
  color: #999;
}

@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
  }

  .login-left {
    min-height: auto;
    padding: 30px 20px;
  }

  .login-branding h1 {
    font-size: 28px;
  }

  .logo-large {
    font-size: 60px;
  }

  .features {
    gap: 15px;
    margin-top: 30px;
  }

  .login-right {
    padding: 20px;
  }

  .login-box {
    padding: 30px 20px;
  }

  .login-header h2 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .login-box {
    padding: 20px;
  }

  .login-header h2 {
    font-size: 20px;
  }

  .login-left {
    padding: 20px;
  }

  .login-branding h1 {
    font-size: 24px;
  }

  .logo-large {
    font-size: 48px;
  }

  .features {
    gap: 12px;
    margin-top: 20px;
  }

  .feature-item {
    font-size: 12px;
  }

  .feature-icon {
    font-size: 20px;
  }
}
</style>

