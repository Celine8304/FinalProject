<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">等保测评辅助系统</div>

      <el-form :model="loginForm" label-width="0">
        <el-form-item>
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item>
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" style="width: 100%;" :loading="loading" @click="handleLogin">
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
  password: ''
})

const registerForm = ref({
  username: '',
  password: ''
})

const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/users/login', loginForm.value)
    localStorage.setItem('currentUser', JSON.stringify(res.data))
    ElMessage.success('登录成功')
    router.push('/projects')
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
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
  background: #f5f7fa;
}

.login-card {
  width: 420px;
  padding: 32px 28px 20px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
}

.login-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 28px;
}

.login-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #909399;
}
</style>