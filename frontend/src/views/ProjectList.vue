<template>
  <div>
    <div class="top-navbar">
      <div class="top-navbar-title">等保测评辅助系统</div>

      <el-dropdown trigger="hover">
        <div class="user-avatar">
          {{ currentUser?.username?.slice(0, 1)?.toUpperCase() || 'U' }}
        </div>

        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item disabled>
              {{ currentUser?.username || '未登录' }}
            </el-dropdown-item>
            <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div style="padding: 24px;">
      <el-card>
        <template #header>
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 18px; font-weight: 600;">项目列表</span>
            <el-button v-if="activeTab !== 'archived'" type="primary" @click="openCreateDialog">新建项目</el-button>
          </div>
        </template>

        <el-tabs v-model="activeTab" style="margin-bottom: 16px;">
          <el-tab-pane label="未归档项目" name="active" />
          <el-tab-pane label="已归档项目" name="archived" />
        </el-tabs>

        <el-table :data="filteredProjects" border style="width: 100%" v-loading="loading"
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
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { getProjectList, createProject, updateProject, deleteProject, archiveProject } from '../api/project'

const currentUser = ref(JSON.parse(localStorage.getItem('currentUser') || 'null'))
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
  router.push(`/projects/${row.id}`)
}

const handleLogout = () => {
  localStorage.removeItem('currentUser')
  ElMessage.success('已退出登录')
  router.push('/login')
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
      fetchProjects()
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
      fetchProjects()
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
    fetchProjects()
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
    fetchProjects()
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
</style>
