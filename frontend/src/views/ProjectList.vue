<template>
  <div>
    <div class="top-navbar">
      <div class="top-navbar-title">等保测评辅助系统</div>

      <template v-if="currentUser">
        <div class="user-avatar" @click="userDrawerVisible = true">
          {{ currentUser?.username?.slice(0, 1)?.toUpperCase() || 'U' }}
        </div>
      </template>

      <template v-else>
        <div class="user-avatar" @click="loginDrawerVisible = true">
          U
        </div>
      </template>
    </div>

    <div style="padding: 24px;">
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; font-weight: 600;">项目列表</span>
            <el-button v-if="currentUser && activeTab !== 'archived'" type="primary" @click="openCreateDialog">新建项目</el-button>
          </div>
        </template>

        <el-tabs v-model="activeTab" style="margin-bottom: 16px;">
          <el-tab-pane label="未归档项目" name="active" />
          <el-tab-pane label="已归档项目" name="archived" />
        </el-tabs>

        <template v-if="currentUser">
          <el-table :data="filteredProjects" border style="width: 100%" v-loading="loading"
            empty-text="当前用户暂无项目"
            @row-dblclick="handleRowDblClick">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="project_code" label="项目编号" width="140" />
            <el-table-column label="项目名称">
              <template #default="scope">
                <div style="display: flex; align-items: center; gap: 8px;">
                  <span>{{ scope.row.project_name }}</span>
                  <el-tag v-if="scope.row.is_archived" type="info" size="small">已归档</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="system_name" label="系统名称" />
            <el-table-column prop="organization_name" label="被测单位" />
            <el-table-column prop="level" label="安全保护等级" width="140" />
            <el-table-column prop="standard_system" label="标准体系" width="160" />
            <el-table-column label="操作" width="100" align="center">
              <template #default="scope">
                <el-dropdown trigger="click" @command="(command) => handleCommand(command, scope.row)">
                  <el-button text>
                    ⋯
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <template v-if="!scope.row.is_archived">
                        <el-dropdown-item command="edit">编辑</el-dropdown-item>
                        <el-dropdown-item command="archive">归档</el-dropdown-item>
                        <el-dropdown-item command="delete">删除</el-dropdown-item>
                      </template>
                      <template v-else>
                        <el-dropdown-item command="unarchive">取消归档</el-dropdown-item>
                      </template>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
        </template>

        <template v-else>
          <el-empty description="请先登录后查看项目">
            <el-button type="primary" @click="loginDrawerVisible = true">去登录</el-button>
          </el-empty>
        </template>
      </el-card>

      <!-- 新建项目弹窗 -->
      <el-dialog v-model="createDialogVisible" title="新建项目" width="600px">
        <el-form ref="createFormRef" :model="createForm" :rules="formRules" label-width="120px">
          <el-form-item label="项目编号" prop="project_code">
            <el-input v-model="createForm.project_code" />
          </el-form-item>
          <el-form-item label="项目名称" prop="project_name">
            <el-input v-model="createForm.project_name" />
          </el-form-item>
          <el-form-item label="系统名称" prop="system_name">
            <el-input v-model="createForm.system_name" />
          </el-form-item>
          <el-form-item label="被测单位" prop="organization_name">
            <el-input v-model="createForm.organization_name" />
          </el-form-item>
          <el-form-item label="安全保护等级" prop="level">
            <el-select v-model="createForm.level" placeholder="请选择安全保护等级" style="width: 100%">
              <el-option label="一级" value="一级" />
              <el-option label="二级" value="二级" />
              <el-option label="三级" value="三级" />
              <el-option label="四级" value="四级" />
            </el-select>
          </el-form-item>
          <el-form-item label="标准体系" prop="standard_system">
            <el-select v-model="createForm.standard_system" placeholder="请选择标准体系" style="width: 100%">
              <el-option label="新国标-正式版" value="新国标-正式版" />
              <el-option label="新国标-民用航空" value="新国标-民用航空" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="creating" @click="handleCreateProject">保存</el-button>
        </template>
      </el-dialog>

      <!-- 编辑项目弹窗 -->
      <el-dialog v-model="editDialogVisible" title="编辑项目" width="600px">
        <el-form ref="editFormRef" :model="editForm" :rules="formRules" label-width="120px">
          <el-form-item label="项目编号" prop="project_code">
            <el-input v-model="editForm.project_code" />
          </el-form-item>
          <el-form-item label="项目名称" prop="project_name">
            <el-input v-model="editForm.project_name" />
          </el-form-item>
          <el-form-item label="系统名称" prop="system_name">
            <el-input v-model="editForm.system_name" />
          </el-form-item>
          <el-form-item label="被测单位" prop="organization_name">
            <el-input v-model="editForm.organization_name" />
          </el-form-item>
          <el-form-item label="安全保护等级" prop="level">
            <el-select v-model="editForm.level" placeholder="请选择安全保护等级" style="width: 100%">
              <el-option label="一级" value="一级" />
              <el-option label="二级" value="二级" />
              <el-option label="三级" value="三级" />
              <el-option label="四级" value="四级" />
            </el-select>
          </el-form-item>
          <el-form-item label="标准体系" prop="standard_system">
            <el-select v-model="editForm.standard_system" placeholder="请选择标准体系" style="width: 100%">
              <el-option label="新国标-正式版" value="新国标-正式版" />
              <el-option label="新国标-民用航空" value="新国标-民用航空" />
            </el-select>
          </el-form-item>
        </el-form>

        <template #footer>
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="handleUpdate">保存</el-button>
        </template>
      </el-dialog>


      <el-drawer v-model="loginDrawerVisible" title="用户登录" size="420px">
        <div class="login-drawer-body">
          <div class="login-drawer-title">等保测评辅助系统</div>

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
              <el-button type="primary" class="login-btn" :loading="loginLoading" @click="handleDrawerLogin">
                登录
              </el-button>
            </el-form-item>

            <div class="login-footer">
              <span>还没有账号？</span>
              <el-button link type="primary" @click="registerDialogVisible = true">注册用户</el-button>
            </div>
          </el-form>
        </div>
      </el-drawer>

      <el-drawer v-model="userDrawerVisible" title="用户中心" size="420px">
        <div class="user-drawer-body">
          <div class="user-drawer-title">{{ currentUser?.username || '未登录' }}</div>

          <div class="user-section-card">
            <div class="user-section-label">登录记录</div>
            <div class="user-section-text">登录 IP：{{ loginRecord.ip || currentUser?.login_ip || '127.0.0.1' }}</div>
            <div class="user-section-text">登录地址：{{ loginRecord.location || currentUser?.login_location || '本地开发环境' }}</div>
          </div>

          <div class="user-section-card">
            <div class="user-section-row">
              <span class="user-section-label">深夜/白天模式</span>
              <el-switch v-model="isDarkMode" active-text="深夜" inactive-text="白天" />
            </div>
          </div>

          <div class="user-section-card">
            <div class="user-section-label">更改账户密码</div>
            <el-form :model="changePasswordForm" label-width="0">
              <el-form-item>
                <el-input v-model="changePasswordForm.oldPassword" type="password" show-password placeholder="请输入原密码" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="changePasswordForm.newPassword" type="password" show-password placeholder="请输入新密码" />
              </el-form-item>
              <el-form-item>
                <el-input v-model="changePasswordForm.confirmPassword" type="password" show-password placeholder="请再次输入新密码" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" plain class="change-password-btn" :loading="changePasswordLoading" @click="handleChangePassword">
  修改密码
</el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-button type="danger" plain class="delete-account-btn" @click="deleteAccountDialogVisible = true">注销账户</el-button>
          <el-button type="danger" class="logout-btn" @click="handleLogout">退出登录</el-button>
        </div>
      </el-drawer>

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
      <el-dialog v-model="deleteAccountDialogVisible" title="注销账户" width="420px">
  <div style="margin-bottom: 16px; color: #606266; line-height: 1.8;">
    注销账户后，将删除该用户下的项目、资产及核查记录，此操作不可恢复。
  </div>

  <el-form :model="deleteAccountForm" label-width="90px">
    <el-form-item label="确认密码">
      <el-input
        v-model="deleteAccountForm.password"
        type="password"
        show-password
        placeholder="请输入当前账户密码"
      />
    </el-form-item>
  </el-form>

  <template #footer>
    <el-button @click="deleteAccountDialogVisible = false">取消</el-button>
    <el-button type="danger" :loading="deleteAccountLoading" @click="handleDeleteAccount">
      确认注销
    </el-button>
  </template>
</el-dialog>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getProjectList, createProject, updateProject, deleteProject, archiveProject } from '../api/project'
import axios from 'axios'

const currentUser = ref(JSON.parse(localStorage.getItem('currentUser') || 'null'))

const loginDrawerVisible = ref(false)
const userDrawerVisible = ref(false)
const isDarkMode = ref(false)

const loginRecord = ref({
  ip: '127.0.0.1',
  location: '本地开发环境'
})

const changePasswordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const changePasswordLoading = ref(false)
const resetLoginForm = () => {
  loginForm.value = {
    username: '',
    password: '',
    captcha: ''
  }
}

const resetChangePasswordForm = () => {
  changePasswordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
}
const resetDeleteAccountForm = () => {
  deleteAccountForm.value = {
    password: ''
  }
}
const loginLoading = ref(false)
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

const deleteAccountDialogVisible = ref(false)
const deleteAccountLoading = ref(false)
const deleteAccountForm = ref({
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
const applyTheme = (dark) => {
  document.documentElement.classList.toggle('dark-mode', dark)
  document.body.classList.toggle('dark-mode', dark)
}

watch(isDarkMode, (value) => {
  localStorage.setItem('isDarkMode', value ? '1' : '0')
  applyTheme(value)
})
const router = useRouter()
const projects = ref([])
const loading = ref(false)

const activeTab = ref('active')

const createDialogVisible = ref(false)
const creating = ref(false)
const createFormRef = ref()

const editDialogVisible = ref(false)
const saving = ref(false)
const editFormRef = ref()

const createForm = ref({
  project_code: '',
  project_name: '',
  system_name: '',
  organization_name: '',
  level: '',
  standard_system: '',
  is_archived: false
})

const editForm = ref({
  id: null,
  project_code: '',
  project_name: '',
  system_name: '',
  organization_name: '',
  level: '',
  standard_system: '',
  is_archived: false
})

const formRules = {
  project_code: [{ required: true, message: '请输入项目编号', trigger: 'blur' }],
  project_name: [{ required: true, message: '请输入项目名称', trigger: 'blur' }],
  system_name: [{ required: true, message: '请输入系统名称', trigger: 'blur' }],
  organization_name: [{ required: true, message: '请输入被测单位', trigger: 'blur' }],
  level: [{ required: true, message: '请选择安全保护等级', trigger: 'change' }],
  standard_system: [{ required: true, message: '请选择标准体系', trigger: 'change' }]
}

const fetchProjects = async () => {
  if (!currentUser.value) {
    projects.value = []
    return
  }

  try {
    const username = currentUser.value?.username || ''
    const res = await getProjectList(username)
    projects.value = res.data
  } catch (error) {
    console.error(error)
    ElMessage.error('获取项目列表失败')
  }
}

const filteredProjects = computed(() => {
  if (activeTab.value === 'active') {
    return projects.value.filter(item => !item.is_archived)
  }
  return projects.value.filter(item => item.is_archived)
})

const handleRowDblClick = (row) => {
  if (!currentUser.value) {
    ElMessage.warning('请先登录后查看项目详情')
    return
  }
  router.push(`/projects/${row.id}`)
}

const handleLogout = () => {
  localStorage.removeItem('currentUser')
  currentUser.value = null
  projects.value = []
  userDrawerVisible.value = false
  loginDrawerVisible.value = false
  deleteAccountDialogVisible.value = false
  resetLoginForm()
  resetChangePasswordForm()
  resetDeleteAccountForm()
  loginRecord.value = {
    ip: '127.0.0.1',
    location: '本地开发环境'
  }
  generateCaptcha()
  ElMessage.success('已退出登录')
}

const handleChangePassword = async () => {
  if (!changePasswordForm.value.oldPassword || !changePasswordForm.value.newPassword || !changePasswordForm.value.confirmPassword) {
    ElMessage.warning('请完整填写密码信息')
    return
  }

  if (changePasswordForm.value.newPassword !== changePasswordForm.value.confirmPassword) {
    ElMessage.error('两次输入的新密码不一致')
    return
  }

  if (changePasswordForm.value.oldPassword === changePasswordForm.value.newPassword) {
    ElMessage.warning('新密码不能与原密码相同')
    return
  }

  changePasswordLoading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/users/change-password', {
      username: currentUser.value?.username,
      old_password: changePasswordForm.value.oldPassword,
      new_password: changePasswordForm.value.newPassword
    })

    changePasswordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    ElMessage.success('密码修改成功，请重新登录')
    handleLogout()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '修改密码失败'
    ElMessage.error(msg)
  } finally {
    changePasswordLoading.value = false
  }
}

const handleDeleteAccount = async () => {
  if (!deleteAccountForm.value.password) {
    ElMessage.warning('请输入当前账户密码')
    return
  }

  deleteAccountLoading.value = true
  try {
    await axios.post('http://127.0.0.1:8000/users/delete-account', {
      username: currentUser.value?.username,
      password: deleteAccountForm.value.password
    })

    ElMessage.success('账户已注销')
    handleLogout()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '注销账户失败'
    ElMessage.error(msg)
  } finally {
    deleteAccountLoading.value = false
  }
}

const handleDrawerLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    ElMessage.warning('请输入用户名和密码')
    return
  }

  if (!loginForm.value.captcha) {
    ElMessage.warning('请输入验证码')
    return
  }

  if (loginForm.value.captcha.trim().toUpperCase() !== captchaText.value) {
    ElMessage.error('验证码错误，请重新输入')
    loginForm.value.captcha = ''
    generateCaptcha()
    return
  }

  loginLoading.value = true
  try {
    const res = await axios.post('http://127.0.0.1:8000/users/login', {
      username: loginForm.value.username,
      password: loginForm.value.password
    })
    localStorage.setItem('currentUser', JSON.stringify(res.data))
    currentUser.value = res.data
    loginRecord.value = {
      ip: res.data?.login_ip || '127.0.0.1',
      location: res.data?.login_location || '本地开发环境'
    }
    loginDrawerVisible.value = false
    userDrawerVisible.value = false
    loginForm.value.password = ''
    loginForm.value.captcha = ''
    generateCaptcha()
    ElMessage.success('登录成功')
    await fetchProjects()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '登录失败'
    ElMessage.error(msg)
    generateCaptcha()
  } finally {
    loginLoading.value = false
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
loginForm.value.captcha = ''
registerForm.value = {
  username: '',
  password: ''
}
userDrawerVisible.value = false
loginDrawerVisible.value = true
generateCaptcha()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '注册失败'
    ElMessage.error(msg)
  } finally {
    registerLoading.value = false
  }
}

const openCreateDialog = () => {
  createForm.value = {
    project_code: '',
    project_name: '',
    system_name: '',
    organization_name: '',
    level: '',
    standard_system: '',
    is_archived: false
  }
  createDialogVisible.value = true
}

const handleCreateProject = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    creating.value = true
    try {
      const payload = {
        ...createForm.value,
        user_id: currentUser.value?.id
      }
      await createProject(payload)
      ElMessage.success('项目创建成功')
      createDialogVisible.value = false
      await fetchProjects()
    } catch (error) {
      console.error(error)
      const msg = error?.response?.data?.detail || '项目创建失败'
      ElMessage.error(msg)
    } finally {
      creating.value = false
    }
  })
}

const openEditDialog = (row) => {
  editForm.value = {
    id: row.id,
    project_code: row.project_code || '',
    project_name: row.project_name || '',
    system_name: row.system_name || '',
    organization_name: row.organization_name || '',
    level: row.level || '',
    standard_system: row.standard_system || '',
    is_archived: !!row.is_archived
  }
  editDialogVisible.value = true
}

const handleUpdate = async () => {
  if (!editFormRef.value) return

  await editFormRef.value.validate(async (valid) => {
    if (!valid) return

    saving.value = true
    try {
      const { id, ...payload } = editForm.value
      await updateProject(id, payload)
      ElMessage.success('项目修改成功')
      editDialogVisible.value = false
      await fetchProjects()
    } catch (error) {
      console.error(error)
      const msg = error?.response?.data?.detail || '项目修改失败'
      ElMessage.error(msg)
    } finally {
      saving.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确认删除项目「${row.project_name}」吗？`,
      '删除确认',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteProject(row.id)
    ElMessage.success('项目删除成功')
    await fetchProjects()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      const msg = error?.response?.data?.detail || '项目删除失败'
      ElMessage.error(msg)
    }
  }
}

const handleArchive = async (row, isArchived) => {
  try {
    await archiveProject(row.id, isArchived)
    ElMessage.success(isArchived ? '归档成功' : '已取消归档')
    await fetchProjects()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || (isArchived ? '归档失败' : '取消归档失败')
    ElMessage.error(msg)
  }
}

const handleCommand = (command, row) => {
  if (command === 'edit') {
    if (row.is_archived) {
      ElMessage.warning('已归档项目默认只读，请先取消归档后再编辑')
      return
    }
    openEditDialog(row)
  } else if (command === 'delete') {
    if (row.is_archived) {
      ElMessage.warning('已归档项目默认只读，请先取消归档后再删除')
      return
    }
    handleDelete(row)
  } else if (command === 'archive') {
    handleArchive(row, true)
  } else if (command === 'unarchive') {
    handleArchive(row, false)
  }
}

onMounted(() => {
  isDarkMode.value = localStorage.getItem('isDarkMode') === '1'
  applyTheme(isDarkMode.value)

  if (currentUser.value) {
    loginRecord.value = {
      ip: currentUser.value?.login_ip || '127.0.0.1',
      location: currentUser.value?.login_location || '本地开发环境'
    }
  }

  fetchProjects()
})
</script>

<style scoped>
.top-navbar {
  height: 64px;
  background: #fff;
  border-bottom: 1px solid #ebeef5;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.top-navbar-title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #409eff;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  cursor: pointer;
  user-select: none;
}

.login-drawer-body {
  padding: 8px 4px;
}

.login-drawer-title {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 28px;
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

.user-drawer-body {
  padding: 8px 4px 20px;
}

.user-drawer-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  margin-bottom: 28px;
}

.user-section-card {
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 12px;
  background: #fafafa;
  margin-bottom: 18px;
}

.user-section-label {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.user-section-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

.user-section-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.change-password-btn {
  width: 100%;
  height: 42px;
  border-radius: 8px;
}

.delete-account-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  text-align: center;
  box-sizing: border-box;
}
.delete-account-btn:hover,
.delete-account-btn:focus {
  background: #fff5f5;
  border-color: #f3b3b3;
  color: #e06a6a;
}

.logout-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  text-align: center;
  box-sizing: border-box;
  transform: translateX(-10px);
}

:deep(.delete-account-btn > span),
:deep(.logout-btn > span) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}
:global(body.dark-mode) {
  background: #141414;
}

:global(.dark-mode .top-navbar) {
  background: #1f1f1f;
  border-bottom: 1px solid #303030;
}

:global(.dark-mode .top-navbar-title) {
  color: #f5f5f5;
}

:global(.dark-mode .el-card) {
  background: #1f1f1f;
  color: #f5f5f5;
}

:global(.dark-mode .el-card__header) {
  border-bottom: 1px solid #303030;
}

:global(.dark-mode .user-section-card) {
  background: #262626;
  border-color: #303030;
}

:global(.dark-mode .user-drawer-title),
:global(.dark-mode .user-section-label),
:global(.dark-mode .login-drawer-title),
:global(.dark-mode .login-label) {
  color: #f5f5f5;
}

:global(.dark-mode .user-section-text),
:global(.dark-mode .login-footer) {
  color: #d9d9d9;
}
</style>
