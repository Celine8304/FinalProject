<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">等保测评辅助系统</div>

      <el-form :model="loginForm" label-width="0">
        <div class="login-label">用户名</div>
        <el-form-item>
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <div class="login-label">密码</div>
        <el-form-item>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <div class="login-label">验证码</div>
        <el-form-item>
          <div class="captcha-row">
            <el-input v-model="loginForm.captcha" placeholder="请输入验证码" />
            <div class="captcha-box" @click="generateCaptcha" title="点击刷新验证码">
              <span
                v-for="(char, index) in captchaChars"
                :key="index"
                class="captcha-char"
                :style="getCaptchaCharStyle(index)"
              >
                {{ char }}
              </span>
            </div>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" class="login-btn" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>

        <div class="login-footer">
          <span>还没有账号？</span>
          <el-button link type="primary" @click="registerDialogVisible = true">注册用户</el-button>
        </div>
      </el-form>
    </div>

    <el-dialog v-model="registerDialogVisible" title="注册用户" width="420px">
      <el-form :model="registerForm" label-width="90px">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input v-model="registerForm.password" type="password" show-password />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="registerDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">注册</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

const loading = ref(false)
const registerLoading = ref(false)
const registerDialogVisible = ref(false)

const loginForm = ref({
  username: '',
  password: '',
  captcha: ''
})

const registerForm = ref({
  username: '',
  password: ''
})

const captchaText = ref('')
const captchaChars = ref([])

const generateCaptcha = () => {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'
  let result = ''
  for (let i = 0; i < 4; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  captchaText.value = result
  captchaChars.value = result.split('')
}

generateCaptcha()

const getCaptchaCharStyle = (index) => {
  const rotateList = [-12, 8, -6, 10]
  const translateYList = [-2, 3, -3, 2]
  const colorList = ['#3f7fe8', '#5b8ff9', '#2f54eb', '#6a5acd']

  return {
    transform: `rotate(${rotateList[index % rotateList.length]}deg) translateY(${translateYList[index % translateYList.length]}px)`,
    color: colorList[index % colorList.length]
  }
}

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  if (!loginForm.value.captcha) {
    ElMessage.warning('请输入验证码')
    return
  }

  if (loginForm.value.captcha.trim().toUpperCase() !== captchaText.value) {
    ElMessage.error('验证码错误')
    loginForm.value.captcha = ''
    generateCaptcha()
    return
  }

  loading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/users/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    localStorage.setItem('currentUser', JSON.stringify(res.data))
    ElMessage.success('登录成功')
    router.push('/projects')
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
    generateCaptcha()
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  registerLoading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/users/register', registerForm.value)
    ElMessage.success('注册成功，请登录')
    registerDialogVisible.value = false
    loginForm.value.username = registerForm.value.username
    loginForm.value.password = ''
    registerForm.value = {
      username: '',
      password: ''
    }
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '注册失败'
    ElMessage.error(msg)
  } finally {
    registerLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3f7fe8;
}

.login-card {
  width: 460px;
  padding: 52px 42px 30px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.14);
}

.login-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 42px;
}

.login-label {
  font-size: 16px;
  color: #303133;
  margin-bottom: 12px;
  font-weight: 500;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-input__wrapper) {
  min-height: 44px;
  border-radius: 8px;
}

.captcha-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.captcha-box {
  width: 112px;
  height: 44px;
  border-radius: 8px;
  background: linear-gradient(135deg, #eef3ff 0%, #f8fbff 100%);
  border: 1px solid #d9e4ff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
  overflow: hidden;
}

.captcha-char {
  display: inline-block;
  font-size: 30px;
  font-weight: 700;
  line-height: 1;
}

.login-btn {
  width: 100%;
  height: 44px;
  margin-top: 8px;
  border-radius: 8px;
}

.login-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}
</style>