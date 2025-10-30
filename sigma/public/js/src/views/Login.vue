<template>
  <div class="login-container">
    <div class="login-background">
      <div class="pattern-overlay"></div>
    </div>

    <div class="login-content">
      <!-- Left Side: Brand Section -->
      <div class="login-left">
        <div class="login-brand">
          <div class="brand-icon">⚡</div>
          <h1 class="brand-title">Kenya Power</h1>
          <p class="brand-subtitle">Security Management System</p>

          <div class="brand-features">
            <div class="feature">
              <span class="feature-icon">🔐</span>
              <span class="feature-text">Secure Access</span>
            </div>
            <div class="feature">
              <span class="feature-icon">📊</span>
              <span class="feature-text">Real-time Monitoring</span>
            </div>
            <div class="feature">
              <span class="feature-icon">⚡</span>
              <span class="feature-text">Instant Alerts</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side: Login Form -->
      <div class="login-right">
        <div class="login-card">
          <div class="card-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your account</p>
          </div>

          <el-form
            ref="loginForm"
            :model="loginData"
            :rules="loginRules"
            class="login-form"
            @submit.prevent="handleLogin"
          >
            <el-form-item prop="email">
              <el-input
                v-model="loginData.email"
                placeholder="Email Address"
                size="large"
                :prefix-icon="User"
                class="form-input"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginData.password"
                type="password"
                placeholder="Enter your password"
                size="large"
                :prefix-icon="Lock"
                show-password
                class="form-input"
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="isLoading"
                @click="handleLogin"
                class="login-button"
              >
                <span v-if="!isLoading">Sign In</span>
                <span v-else>Signing In...</span>
              </el-button>
            </el-form-item>
          </el-form>

          <div class="card-footer">
            <p>© 2025 Kenya Power. All rights reserved.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginForm = ref()
const isLoading = ref(false)

const loginData = reactive({
  email: '',
  password: ''
})

const loginRules = {
  email: [
    { required: true, message: 'Please enter your username or email', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter your password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginForm.value) return
  
  try {
    const valid = await loginForm.value.validate()
    if (!valid) return
    
    isLoading.value = true
    
    const success = await authStore.login(loginData.email, loginData.password)
    
    if (success) {
      ElMessage.success('Login successful!')
      router.push('/')
    } else {
      ElMessage.error('Invalid email or password')
    }
  } catch (error) {
    ElMessage.error(error.message || 'Login failed')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  position: relative;
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  overflow: hidden;
}

.login-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, #003d7a 0%, #0052a3 50%, #003d7a 100%);
  z-index: 1;
}

.pattern-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.05) 0%, transparent 50%),
    radial-gradient(circle at 75% 75%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
  background-size: 100px 100px;
  animation: float 20s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

.login-content {
  position: relative;
  z-index: 2;
  display: flex;
  width: 100%;
  height: 100%;
  align-items: stretch;
}

.login-left {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
}

.login-brand {
  text-align: center;
  color: white;
  max-width: 400px;
}

.brand-icon {
  font-size: 80px;
  margin-bottom: 20px;
  display: block;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  margin: 0 0 12px 0;
  letter-spacing: -1px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.brand-subtitle {
  font-size: 18px;
  margin: 0 0 40px 0;
  opacity: 0.9;
  font-weight: 300;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-top: 40px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 16px;
  opacity: 0.95;
}

.feature-icon {
  font-size: 24px;
}

.feature-text {
  font-weight: 500;
}

.login-right {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.95);
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 48px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.card-header {
  text-align: center;
  margin-bottom: 32px;
}

.card-header h2 {
  color: #003d7a;
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
  letter-spacing: -0.5px;
}

.card-header p {
  color: #6c757d;
  margin: 0;
  font-size: 15px;
  font-weight: 400;
}

.login-form {
  width: 100%;
}

.login-form .el-form-item {
  margin-bottom: 24px;
}

.form-input .el-input__wrapper {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e4e7ed;
  background: rgba(255, 255, 255, 0.9);
  transition: all 0.3s ease;
}

.form-input .el-input__wrapper:hover {
  box-shadow: 0 0 0 1px #c0c4cc;
  background: rgba(255, 255, 255, 1);
}

.form-input .el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px #003d7a;
  background: rgba(255, 255, 255, 1);
}

.login-button {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background: linear-gradient(135deg, #003d7a 0%, #0052a3 100%);
  border: none;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 61, 122, 0.3);
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 61, 122, 0.4);
  background: linear-gradient(135deg, #002d5f 0%, #003d7a 100%);
}

.login-button:active {
  transform: translateY(0);
}

.card-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.card-footer p {
  color: #6c757d;
  font-size: 13px;
  margin: 0;
  opacity: 0.8;
}

@media (max-width: 1024px) {
  .login-left {
    padding: 40px 30px;
  }

  .login-right {
    padding: 40px 30px;
  }

  .brand-title {
    font-size: 40px;
  }

  .login-card {
    padding: 40px;
  }
}

@media (max-width: 768px) {
  .login-content {
    flex-direction: column;
  }

  .login-left {
    padding: 40px 20px;
    flex: 0;
  }

  .login-right {
    padding: 40px 20px;
    flex: 1;
  }

  .brand-title {
    font-size: 36px;
  }

  .brand-subtitle {
    font-size: 16px;
  }

  .brand-features {
    gap: 15px;
  }

  .feature {
    font-size: 14px;
  }

  .login-card {
    padding: 32px 24px;
  }
}

@media (max-width: 480px) {
  .login-left {
    padding: 30px 20px;
  }

  .login-right {
    padding: 30px 20px;
  }

  .brand-icon {
    font-size: 60px;
    margin-bottom: 15px;
  }

  .brand-title {
    font-size: 28px;
  }

  .brand-subtitle {
    font-size: 14px;
    margin-bottom: 30px;
  }

  .brand-features {
    gap: 12px;
  }

  .feature {
    font-size: 13px;
  }

  .login-card {
    padding: 24px 20px;
  }

  .card-header h2 {
    font-size: 24px;
  }
}
</style>
