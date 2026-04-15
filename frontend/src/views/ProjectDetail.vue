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
    <el-card style="margin-bottom: 16px;">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-size: 18px; font-weight: 600;">
            {{ project?.project_name || '项目详情' }}
          </span>
          <el-button @click="goBack">返回项目列表</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border v-if="project">
        <el-descriptions-item label="项目编号">{{ project.project_code }}</el-descriptions-item>
        <el-descriptions-item label="项目名称">{{ project.project_name }}</el-descriptions-item>
        <el-descriptions-item label="系统名称">{{ project.system_name }}</el-descriptions-item>
        <el-descriptions-item label="被测单位">{{ project.organization_name }}</el-descriptions-item>
        <el-descriptions-item label="安全保护等级">{{ project.level }}</el-descriptions-item>
        <el-descriptions-item label="标准体系">{{ project.standard_system }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
    <el-alert
      v-if="project?.is_archived"
      title="当前项目已归档，默认只读。如需修改，请先返回项目列表取消归档。"
      type="info"
      :closable="false"
      style="margin-bottom: 16px;"
    />

    <el-tabs v-model="activeMainTab">
      <el-tab-pane label="系统构成" name="assetStructure">
        <el-tabs v-model="activeAssetTab">
          <el-tab-pane label="服务器/存储设备" name="server_storage" />
          <el-tab-pane label="数据库管理系统" name="database" />
        </el-tabs>

        <div style="margin-bottom: 16px; display: flex; justify-content: flex-end;">
          <el-button type="primary" @click="openCreateDialog" :disabled="project?.is_archived">新增资产</el-button>
        </div>

        <el-table :data="filteredAssets" border style="width: 100%" v-loading="loadingAssets">
          <el-table-column prop="id" label="资产ID" width="90" />
          <el-table-column prop="asset_name" label="资产名称" />
          <el-table-column prop="ip_address" label="IP地址" width="180" />
          <el-table-column prop="os_or_db_type" label="作业指导书类型" width="180" />
          <el-table-column prop="remark" label="备注" />
          <el-table-column label="操作" width="100" align="center">
            <template #default="scope">
              <el-dropdown
                trigger="click"
                popper-class="asset-action-dropdown"
                @command="(command) => handleAssetCommand(command, scope.row)"
              >
                <el-button text class="more-btn">⋯</el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item :disabled="project?.is_archived" command="edit">编辑</el-dropdown-item>
                    <el-dropdown-item :disabled="project?.is_archived" command="delete">删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="现场核查" name="checkRecord">
        <div style="display: flex; gap: 16px; align-items: flex-start;">
          <el-card style="width: 320px; flex-shrink: 0;">
            <template #header>
              <span>当前项目资产列表</span>
            </template>

            <el-tree :data="assetTreeData" node-key="nodeKey" default-expand-all :expand-on-click-node="false"
              :highlight-current="false" class="asset-tree" @node-click="handleTreeNodeClick">
              <template #default="{ data }">
                <div v-if="data.isGroup" class="asset-tree-group">
                  {{ data.label }}
                </div>

                <div v-else class="asset-tree-node" :class="{ 'is-selected': selectedAsset?.id === data.id }">
                  <div class="asset-tree-node-name"
                    :title="`${data.label}（${data.completed_count}/${data.total_count}）`">
                    {{ data.label }}
                    <span class="asset-tree-progress">（{{ data.completed_count }}/{{ data.total_count }}）</span>
                  </div>
                  <div class="asset-tree-node-sub" :title="data.os_or_db_type">
                    {{ data.os_or_db_type }}
                  </div>
                </div>
              </template>
            </el-tree>
          </el-card>

          <el-card style="flex: 1; min-width: 0;">
            <template #header>
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <span>
                  现场核查记录
                  <span v-if="selectedAsset"> - {{ selectedAsset.asset_name }}</span>
                </span>

                <div class="record-action-row">
                  <el-upload
                    v-if="selectedAsset && !project?.is_archived"
                    class="record-action-upload"
                    :show-file-list="false"
                    :before-upload="handleImportExcel"
                    accept=".xlsx"
                  >
                    <el-button type="success" class="record-action-btn">导入 Excel</el-button>
                  </el-upload>

                  <el-button v-if="selectedAsset" type="primary" class="record-action-btn" @click="handleExportExcel">
                    导出 Excel
                  </el-button>

                  <el-button
                    v-if="selectedAsset && !project?.is_archived"
                    type="primary"
                    class="record-action-btn"
                    :disabled="dirtyCount === 0"
                    :loading="bulkSaving"
                    @click="handleSaveAllRecords"
                  >
                    一键保存<span v-if="dirtyCount > 0">（{{ dirtyCount }}）</span>
                  </el-button>

                  <el-button v-if="selectedAsset" type="warning" class="record-action-btn" @click="openPriorityDrawer">
                    优先级排序
                  </el-button>

                  <el-tooltip
                    v-if="selectedAsset"
                    content="AI建议仅针对“部分符合”和“不符合”项显示。"
                    placement="top"
                  >
                    <div class="record-tip-icon">!</div>
                  </el-tooltip>
                </div>
              </div>
            </template>

            <el-empty v-if="!selectedAsset" description="请先选择左侧资产" />

            <div v-if="selectedAsset" class="record-table-wrapper">
              <el-table
                :data="records"
                border
                class="check-record-table"
                style="width: max-content; min-width: 100%"
                v-loading="loadingRecords"
                :max-height="tableMaxHeight"
                :header-cell-style="{ textAlign: 'center' }"
              >
                <el-table-column prop="seq_no" label="序号" width="80" />
                <el-table-column prop="control_point" label="控制点" width="140" />
                <el-table-column label="控制项" width="150">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.control_item || '-'" placement="top">
                      <div class="ellipsis-text">{{ truncateText(scope.row.control_item, 20) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="importance_level" label="重要程度" width="100" />
                <el-table-column label="检查内容" min-width="180">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.check_content || '-'" placement="top">
                      <div class="ellipsis-text">{{ truncateText(scope.row.check_content, 20) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column label="判断标准" min-width="180">
                  <template #default="scope">
                    <el-tooltip :content="scope.row.judgment_standard || '-'" placement="top">
                      <div class="ellipsis-text">{{ truncateText(scope.row.judgment_standard, 20) }}</div>
                    </el-tooltip>
                  </template>
                </el-table-column>
                <el-table-column prop="check_method" label="检查方法" min-width="280" />
                <el-table-column prop="recommended_value" label="推荐值" min-width="240" />
                <el-table-column prop="template_remark" label="备注" min-width="180" />

                <el-table-column label="结果记录" min-width="220">
                  <template #default="scope">
                    <el-input
                      v-model="scope.row.result_record"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入结果记录"
                      :disabled="project?.is_archived"
                      @input="updateRecordDirtyState(scope.row)"
                    />
                  </template>
                </el-table-column>

                <el-table-column label="符合情况" width="160">
                  <template #default="scope">
                    <el-select
                      v-model="scope.row.compliance_status"
                      placeholder="请选择"
                      style="width: 100%"
                      :disabled="project?.is_archived"
                      @change="updateRecordDirtyState(scope.row)"
                    >
                      <el-option label="符合" value="compliant" />
                      <el-option label="部分符合" value="partial" />
                      <el-option label="不符合" value="non_compliant" />
                    </el-select>
                  </template>
                </el-table-column>



                <el-table-column label="操作" width="180" fixed="right">
                  <template #default="scope">
                    <div class="record-action-cell">
                      <div v-if="scope.row.isDirty" class="dirty-tip">
                        ● 未保存
                      </div>

                      <div style="display: flex; gap: 8px; justify-content: center;">
                        <el-button
                          type="primary"
                          link
                          :disabled="project?.is_archived"
                          :loading="savingRecordId === scope.row.id"
                          @click="handleSaveRecord(scope.row)"
                        >
                          保存
                        </el-button>

                        <el-button
                          type="warning"
                          link
                          :disabled="project?.is_archived || scope.row.isDirty || !(scope.row.compliance_status === 'partial' || scope.row.compliance_status === 'non_compliant')"
                          @click="openAiSuggestion(scope.row)"
                        >
                          AI建议
                        </el-button>
                      </div>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>


      <el-tab-pane label="结果统计" name="resultStats">
        <div style="display: flex; flex-direction: column; gap: 16px;">
          <el-row :gutter="16">
            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number">{{ statsSummary.asset_total }}</div>
                  <div class="stats-label">资产总数</div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number">{{ statsSummary.record_total }}</div>
                  <div class="stats-label">检查项总数</div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number">{{ statsSummary.completed_total }}</div>
                  <div class="stats-label">已完成项数</div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number stats-number-green">{{ statsSummary.compliant_total }}</div>
                  <div class="stats-label">符合数</div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number stats-number-yellow">{{ statsSummary.partial_total }}</div>
                  <div class="stats-label">部分符合数</div>
                </div>
              </el-card>
            </el-col>

            <el-col :span="4">
              <el-card>
                <div class="stats-card">
                  <div class="stats-number stats-number-red">{{ statsSummary.non_compliant_total }}</div>
                  <div class="stats-label">不符合数</div>
                </div>
              </el-card>
            </el-col>
          </el-row>

          <el-card>
            <template #header>
              <span>资产统计明细</span>
            </template>

            <el-table :data="assetStats" border style="width: 100%">
              <el-table-column prop="asset_name" label="资产名称" min-width="180" />
              <el-table-column label="资产类型" width="140">
                <template #default="scope">
                  {{ scope.row.asset_type === 'server_storage' ? '服务器/存储设备' : '数据库' }}
                </template>
              </el-table-column>
              <el-table-column prop="os_or_db_type" label="作业指导书类型" min-width="160" />
              <el-table-column prop="record_total" label="检查项总数" width="120" />
              <el-table-column prop="completed_total" label="已完成数" width="120" />
              <el-table-column prop="compliant_total" label="符合数" width="100" class-name="col-green" />
              <el-table-column prop="partial_total" label="部分符合数" width="120" class-name="col-yellow" />
              <el-table-column prop="non_compliant_total" label="不符合数" width="100" class-name="col-red" />
              <el-table-column label="完成率" width="120">
                <template #default="scope">
                  {{ scope.row.completed_total }}/{{ scope.row.record_total }}
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
    <el-dialog v-model="dialogVisible" :title="assetDialogMode === 'create' ? '新增资产' : '编辑资产'" width="600px">
      <el-form :model="assetForm" label-width="120px">
        <el-form-item label="资产类型">
          <el-input :value="assetTypeLabel" disabled />
        </el-form-item>

        <el-form-item label="资产名称">
          <el-input v-model="assetForm.asset_name" />
        </el-form-item>

        <el-form-item label="IP地址">
          <el-input v-model="assetForm.ip_address" />
        </el-form-item>

        <el-form-item label="作业指导书类型">
          <el-select v-model="assetForm.os_or_db_type" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in guideOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="assetForm.remark" type="textarea" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmitAsset">保存</el-button>
      </template>
    </el-dialog>
    <AiSuggestionDialog
  v-model="aiDialogVisible"
  :record-id="currentAiRecordId"
/>

<el-drawer
  v-model="priorityDrawerVisible"
  title="整改优先级排序"
  size="560px"
>
  <div style="display: flex; flex-direction: column; gap: 16px;">
    <div class="priority-header-card">
      <div class="priority-header-title">
        {{ selectedAsset?.asset_name || '-' }} / {{ selectedAsset?.os_or_db_type || '-' }}
      </div>
      <div class="priority-header-desc">
        以下顺序基于检查项符合情况与权重计算生成，排序结果仅供整改处理参考。
      </div>
    </div>

    <el-empty
  v-if="priorityTableData.length === 0"
  description="当前资产暂无部分符合或不符合项，无需生成整改优先级排序"
/>

      <el-table v-else :data="priorityTableData" border style="width: 100%">
      <el-table-column prop="rank" label="排序" width="70" align="center" />
      <el-table-column prop="seq_no" label="序号" width="70" align="center" />
      <el-table-column prop="control_item" label="控制项" min-width="220" show-overflow-tooltip />
      <el-table-column label="符合情况" width="110" align="center">
        <template #default="scope">
          <el-tag :type="getComplianceTagType(scope.row.compliance_status)">
            {{ getComplianceText(scope.row.compliance_status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="权重" width="80" align="center">
  <template #default="scope">
    {{ formatPriorityScore(scope.row.weight) }}
  </template>
</el-table-column>
      <el-table-column label="优先值" width="90" align="center">
  <template #default="scope">
    <span class="priority-score-text">
      {{ formatPriorityScore(scope.row.priority_score) }}
    </span>
  </template>
</el-table-column>
    </el-table>

    <el-card v-if="priorityTableData.length > 0" class="priority-ai-card">
  <template #header>
    <span>AI补充意见</span>
  </template>

  <div v-loading="priorityAiLoading" class="priority-ai-text">
    <div v-if="priorityAiItems.length === 0">暂无补充意见</div>

    <div
      v-for="(item, index) in priorityAiItems"
      :key="index"
      class="priority-ai-item"
    >
      <span class="priority-ai-seq">
        建议关注序号{{ item.seq_refs.join('、') }}：
      </span>
      <span>{{ item.text }}</span>
    </div>
  </div>
</el-card>
  </div>
</el-drawer>
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { getAssetsByProject, getAssetProgressByProject, createAsset, updateAsset, deleteAsset } from '../api/asset'
import { getRecordsByAsset, getPriorityByAsset, getPriorityAiAdviceByAsset, updateRecord } from '../api/record'
import { getProjectStats } from '../api/stats'
import AiSuggestionDialog from '../components/project/AiSuggestionDialog.vue'

const currentUser = ref(JSON.parse(localStorage.getItem('currentUser') || 'null'))
const loginDrawerVisible = ref(false)
const userDrawerVisible = ref(false)
const loginLoading = ref(false)
const registerLoading = ref(false)
const registerDialogVisible = ref(false)
const isDarkMode = ref(false)

const loginRecord = ref({
  ip: '127.0.0.1',
  location: '本地开发环境'
})

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
const priorityAiLoading = ref(false)
const priorityAiItems = ref([])
const aiDialogVisible = ref(false)
const priorityDrawerVisible = ref(false)
const currentAiRecordId = ref(null)
const route = useRoute()
const router = useRouter()
const projectId = route.params.id

const project = ref(null)
const assets = ref([])
const assetProgressMap = ref({})
const loadingAssets = ref(false)

const activeMainTab = ref('assetStructure')
const activeAssetTab = ref('server_storage')

const dialogVisible = ref(false)
const saving = ref(false)
const assetDialogMode = ref('create')
const editingAssetId = ref(null)

const selectedAsset = ref(null)
const records = ref([])
const statsSummary = ref({
  asset_total: 0,
  record_total: 0,
  completed_total: 0,
  compliant_total: 0,
  partial_total: 0,
  non_compliant_total: 0
})

const assetStats = ref([])
const loadingRecords = ref(false)
const savingRecordId = ref(null)


const tableMaxHeight = ref('600px')
const priorityTableData = ref([])

const dirtyRecords = computed(() => records.value.filter(item => item.isDirty))
const dirtyCount = computed(() => dirtyRecords.value.length)
const bulkSaving = ref(false)

const markRecordOriginalState = (list) => {
  return list.map(item => ({
    ...item,
    original_result_record: item.result_record ?? '',
    original_compliance_status: item.compliance_status ?? '',
    isDirty: false
  }))
}

const updateRecordDirtyState = (row) => {
  row.isDirty =
    (row.result_record ?? '') !== (row.original_result_record ?? '') ||
    (row.compliance_status ?? '') !== (row.original_compliance_status ?? '')
}

const truncateText = (text, max = 20) => {
  const value = text ?? ''
  if (value.length <= max) return value || '-'
  return `${value.slice(0, max)}...`
}

const fetchPriorityData = async () => {
  if (!selectedAsset.value) {
    priorityTableData.value = []
    return
  }

  try {
    const res = await getPriorityByAsset(selectedAsset.value.id)
    priorityTableData.value = res.data
  } catch (error) {
    console.error(error)
    ElMessage.error('获取整改优先级排序失败')
  }
}

const fetchPriorityAiAdvice = async () => {
  if (!selectedAsset.value) {
    priorityAiItems.value = []
    return
  }

  if (priorityTableData.value.length === 0) {
    priorityAiItems.value = []
    return
  }

  try {
    priorityAiLoading.value = true
    const res = await getPriorityAiAdviceByAsset(selectedAsset.value.id)
    priorityAiItems.value = res.data.items || []
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '获取 AI 补充意见失败'
    ElMessage.error(msg)
    priorityAiItems.value = []
  } finally {
    priorityAiLoading.value = false
  }
}

const formatPriorityScore = (value) => {
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return num.toFixed(1)
}

const assetForm = ref({
  asset_name: '',
  ip_address: '',
  os_or_db_type: '',
  remark: ''
})

const fetchProjectDetail = async () => {
  try {
    const res = await axios.get(`http://127.0.0.1:8000/projects/${projectId}`)
    project.value = res.data
  } catch (error) {
    console.error(error)
    ElMessage.error('获取项目详情失败')
  }
}

const fetchAssets = async () => {
  loadingAssets.value = true
  try {
    const res = await getAssetsByProject(projectId)
    assets.value = res.data

    if (selectedAsset.value) {
      const latest = res.data.find(item => item.id === selectedAsset.value.id)
      if (latest) {
        selectedAsset.value = latest
      }
    }

    await fetchAssetProgress()
  } catch (error) {
    console.error(error)
    ElMessage.error('获取资产列表失败')
  } finally {
    loadingAssets.value = false
  }
}

const fetchAssetProgress = async () => {
  try {
    const res = await getAssetProgressByProject(projectId)
    const map = {}
    res.data.forEach(item => {
      map[item.asset_id] = {
        total_count: item.total_count,
        completed_count: item.completed_count
      }
    })
    assetProgressMap.value = map
  } catch (error) {
    console.error(error)
    ElMessage.error('获取资产进度失败')
  }
}

const openAiSuggestion = (row) => {
  currentAiRecordId.value = row.id
  aiDialogVisible.value = true
}

const openPriorityDrawer = async () => {
  if (!selectedAsset.value) {
    ElMessage.warning('请先选择资产')
    return
  }

  await fetchPriorityData()
  priorityDrawerVisible.value = true
  await fetchPriorityAiAdvice()
}

const getComplianceTagType = (status) => {
  if (status === 'non_compliant') return 'danger'
  if (status === 'partial') return 'warning'
  if (status === 'compliant') return 'success'
  return 'info'
}

const getComplianceText = (status) => {
  if (status === 'non_compliant') return '不符合'
  if (status === 'partial') return '部分符合'
  if (status === 'compliant') return '符合'
  return '-'
}

const fetchRecords = async (assetId) => {
  loadingRecords.value = true
  try {
    const res = await getRecordsByAsset(assetId)
    records.value = markRecordOriginalState(res.data)
  } catch (error) {
    console.error(error)
    ElMessage.error('获取核查记录失败')
  } finally {
    loadingRecords.value = false
  }
}

const fetchProjectStats = async () => {
  try {
    const res = await getProjectStats(projectId)
    statsSummary.value = res.data.summary
    assetStats.value = res.data.asset_stats
  } catch (error) {
    console.error(error)
    ElMessage.error('获取结果统计失败')
  }
}

const filteredAssets = computed(() => {
  return assets.value.filter(item => item.asset_type === activeAssetTab.value)
})

const assetTreeData = computed(() => {
  const serverAssets = assets.value
    .filter(item => item.asset_type === 'server_storage')
    .map(item => {
      const progress = assetProgressMap.value[item.id] || {
        total_count: 0,
        completed_count: 0
      }

      return {
        nodeKey: `asset-${item.id}`,
        id: item.id,
        label: item.asset_name,
        os_or_db_type: item.os_or_db_type,
        isGroup: false,
        raw: item,
        total_count: progress.total_count,
        completed_count: progress.completed_count
      }
    })

  const databaseAssets = assets.value
    .filter(item => item.asset_type === 'database')
    .map(item => {
      const progress = assetProgressMap.value[item.id] || {
        total_count: 0,
        completed_count: 0
      }

      return {
        nodeKey: `asset-${item.id}`,
        id: item.id,
        label: item.asset_name,
        os_or_db_type: item.os_or_db_type,
        isGroup: false,
        raw: item,
        total_count: progress.total_count,
        completed_count: progress.completed_count
      }
    })

  return [
    {
      nodeKey: 'group-server',
      label: '服务器/存储设备',
      isGroup: true,
      children: serverAssets
    },
    {
      nodeKey: 'group-database',
      label: '数据库管理系统',
      isGroup: true,
      children: databaseAssets
    }
  ]
})

const assetTypeLabel = computed(() => {
  return activeAssetTab.value === 'server_storage'
    ? '服务器/存储设备'
    : '数据库管理系统'
})

const guideOptions = computed(() => {
  if (activeAssetTab.value === 'server_storage') {
    return ['Redhat Linux']
  }
  return ['达梦']
})

const openCreateDialog = () => {
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再新增资产')
    return
  }

  assetDialogMode.value = 'create'
  editingAssetId.value = null
  assetForm.value = {
    asset_name: '',
    ip_address: '',
    os_or_db_type: '',
    remark: ''
  }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再编辑资产')
    return
  }

  assetDialogMode.value = 'edit'
  editingAssetId.value = row.id
  assetForm.value = {
    asset_name: row.asset_name || '',
    ip_address: row.ip_address || '',
    os_or_db_type: row.os_or_db_type || '',
    remark: row.remark || ''
  }
  dialogVisible.value = true
}

const handleSubmitAsset = async () => {
  saving.value = true
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再保存资产')
    saving.value = false
    return
  }
  try {
    const payload = {
      project_id: Number(projectId),
      asset_type: activeAssetTab.value,
      asset_name: assetForm.value.asset_name,
      ip_address: assetForm.value.ip_address,
      os_or_db_type: assetForm.value.os_or_db_type,
      remark: assetForm.value.remark
    }

    if (assetDialogMode.value === 'create') {
      await createAsset(payload)
      ElMessage.success('资产新增成功')
    } else {
      await updateAsset(editingAssetId.value, {
        asset_type: activeAssetTab.value,
        asset_name: assetForm.value.asset_name,
        ip_address: assetForm.value.ip_address,
        os_or_db_type: assetForm.value.os_or_db_type,
        remark: assetForm.value.remark
      })
      ElMessage.success('资产修改成功')
    }

    dialogVisible.value = false
    await fetchAssets()
    await fetchProjectStats()

    if (selectedAsset.value && editingAssetId.value === selectedAsset.value.id) {
      await fetchRecords(selectedAsset.value.id)
    }
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '保存资产失败'
    ElMessage.error(msg)
  } finally {
    saving.value = false
  }
}

const handleDeleteAsset = async (row) => {
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再删除资产')
    return
  }
  try {
    await ElMessageBox.confirm(
      `确认删除资产「${row.asset_name}」吗？`,
      '删除确认',
      {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await deleteAsset(row.id)
    ElMessage.success('资产删除成功')

    if (selectedAsset.value?.id === row.id) {
      selectedAsset.value = null
      records.value = []
    }

    await fetchAssets()
    await fetchProjectStats()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      console.error(error)
      const msg = error?.response?.data?.detail || '资产删除失败'
      ElMessage.error(msg)
    }
  }
}

const handleAssetCommand = (command, row) => {
  if (command === 'edit') {
    openEditDialog(row)
  } else if (command === 'delete') {
    handleDeleteAsset(row)
  }
}

const selectAsset = (item) => {
  selectedAsset.value = item
  fetchRecords(item.id)
}

const handleTreeNodeClick = (data) => {
  if (data.isGroup) return
  selectAsset(data.raw)
}

const handleSaveRecord = async (row) => {
  savingRecordId.value = row.id
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再保存核查记录')
    savingRecordId.value = null
    return
  }
  try {
    await updateRecord(row.id, {
      result_record: row.result_record,
      compliance_status: row.compliance_status
    })

    row.original_result_record = row.result_record ?? ''
    row.original_compliance_status = row.compliance_status ?? ''
    row.isDirty = false

    ElMessage.success('保存成功')
    await fetchAssetProgress()
    await fetchProjectStats()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
  } finally {
    savingRecordId.value = null
  }
}

const handleSaveAllRecords = async () => {
  if (dirtyRecords.value.length === 0) {
    ElMessage.info('当前没有需要保存的修改')
    return
  }

  const saveCount = dirtyRecords.value.length
  bulkSaving.value = true
  try {
    for (const row of dirtyRecords.value) {
      await updateRecord(row.id, {
        result_record: row.result_record,
        compliance_status: row.compliance_status
      })
      row.original_result_record = row.result_record ?? ''
      row.original_compliance_status = row.compliance_status ?? ''
      row.isDirty = false
    }

    ElMessage.success(`已保存 ${saveCount} 条记录`)
    await fetchAssetProgress()
    await fetchProjectStats()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '批量保存失败'
    ElMessage.error(msg)
  } finally {
    bulkSaving.value = false
  }
}




const goBack = () => {
  router.push('/projects')
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
    await fetchProjectDetail()
    await fetchAssets()
    await fetchProjectStats()
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

    resetChangePasswordForm()
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

const handleLogout = () => {
  localStorage.removeItem('currentUser')
  currentUser.value = null
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
  router.push('/projects')
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

const handleExportExcel = () => {
  if (!selectedAsset.value) {
    ElMessage.warning('请先选择资产')
    return
  }

  window.open(
    `http://127.0.0.1:8000/records/export/asset/${selectedAsset.value.id}`,
    '_blank'
  )
}

const handleImportExcel = async (file) => {
  if (!selectedAsset.value) {
    ElMessage.warning('请先选择资产')
    return false
  }
  if (project.value?.is_archived) {
    ElMessage.warning('当前项目已归档，请先取消归档后再导入 Excel')
    return false
  }

  try {
    const formData = new FormData()
    formData.append('file', file)

    await axios.post(
      `http://127.0.0.1:8000/records/import/asset/${selectedAsset.value.id}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    ElMessage.success('导入成功')
    await fetchRecords(selectedAsset.value.id)
    await fetchAssetProgress()
    await fetchProjectStats()
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '导入失败'
    ElMessage.error(msg)
  }

  return false
}

onMounted(async () => {
  isDarkMode.value = localStorage.getItem('isDarkMode') === '1'
  applyTheme(isDarkMode.value)

  if (!currentUser.value) {
    ElMessage.warning('请先登录后查看项目详情')
    router.push('/projects')
    return
  }

  loginRecord.value = {
    ip: currentUser.value?.login_ip || '127.0.0.1',
    location: currentUser.value?.login_location || '本地开发环境'
  }

  await fetchProjectDetail()
  await fetchAssets()
  await fetchProjectStats()
})


</script>

<style scoped>
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
  height: 42px;
  border-radius: 8px;
  margin-top: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
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
  padding: 0;
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
  border-color: #303030;
  box-shadow: none;
}

:global(.dark-mode .el-card__header) {
  border-bottom: 1px solid #303030;
  color: #f5f5f5;
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

/* 抽屉样式 */
:global(.dark-mode .el-drawer) {
  background-color: #141414;
  color: #f5f5f5;
}

:global(.dark-mode .el-drawer__header) {
  border-bottom: 1px solid #303030;
}

:global(.dark-mode .el-drawer__title) {
  color: #f5f5f5;
}

:global(.dark-mode .el-drawer__body) {
  color: #f5f5f5;
  background-color: #141414;
}

/* 表单输入框样式 */
:global(.dark-mode .el-input__inner) {
  color: #f5f5f5;
  background-color: #262626;
  border-color: #409eff;
}

:global(.dark-mode .el-input__wrapper) {
  background-color: #262626;
  box-shadow: 0 0 0 1px #303030 inset;
}

:global(.dark-mode .el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #4b5563 inset;
}

:global(.dark-mode .el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #66b1ff inset, 0 0 0 2px rgba(64, 158, 255, 0.14);
}

:global(.dark-mode .el-button--primary) {
  box-shadow: none;
}

:global(.dark-mode .el-button--primary:not(.is-disabled):hover) {
  filter: brightness(1.05);
}

:global(.dark-mode .el-button--success:not(.is-disabled):hover),
:global(.dark-mode .el-button--warning:not(.is-disabled):hover),
:global(.dark-mode .el-button--danger:not(.is-disabled):hover) {
  filter: brightness(1.04);
}

:global(.dark-mode .el-select-dropdown),
:global(.dark-mode .el-popper) {
  background: #1f1f1f;
  border-color: #303030;
}

:global(.dark-mode .el-select-dropdown__item) {
  color: #f5f5f5;
}

:global(.dark-mode .el-select-dropdown__item.hover),
:global(.dark-mode .el-select-dropdown__item:hover) {
  background: #262626;
}

:global(.dark-mode .el-select-dropdown__item.selected) {
  color: #6cb6ff;
}

:global(.dark-mode .el-tree-node:focus > .el-tree-node__content) {
  background-color: transparent;
}

:global(.dark-mode .asset-tree) {
  background: #1f1f1f;
}

:global(.dark-mode .asset-tree-node) {
  background: transparent;
}

:global(.dark-mode .asset-tree-node.is-selected) {
  background: #1d3557;
  border-color: #3b82f6;
  box-shadow: inset 0 0 0 1px rgba(59, 130, 246, 0.15);
}

:global(.dark-mode .record-table-wrapper),
:global(.dark-mode .record-table-scroll-top) {
  background: transparent;
}

:global(.dark-mode .check-record-table .el-table__inner-wrapper::before) {
  background-color: #303030;
}

:global(.dark-mode .check-record-table .el-table__fixed-right::before),
:global(.dark-mode .check-record-table .el-table__fixed::before) {
  background-color: #303030;
}

:global(.dark-mode .check-record-table .el-table__fixed-right),
:global(.dark-mode .check-record-table .el-table__fixed) {
  box-shadow: none;
}

:global(.dark-mode .check-record-table .el-textarea__inner::placeholder),
:global(.dark-mode .check-record-table .el-input__inner::placeholder) {
  color: #8c8c8c;
}

:global(.dark-mode .check-record-table .el-button.is-link.is-disabled),
:global(.dark-mode .check-record-table .el-button.is-link:disabled) {
  color: #6b7280;
}

:global(.dark-mode .check-record-table .el-button--warning.is-link:not(.is-disabled)) {
  color: #f0b54a;
}

:global(.dark-mode .check-record-table .el-button--primary.is-link:not(.is-disabled)) {
  color: #6cb6ff;
}

:global(.dark-mode .record-action-cell) {
  color: #d9d9d9;
}

:global(.dark-mode .ellipsis-text) {
  color: #f5f5f5;
}

:global(.dark-mode .priority-header-card),
:global(.dark-mode .priority-ai-card) {
  background: #262626;
  border-color: #303030;
  box-shadow: none;
}

:global(.dark-mode .stats-card) {
  background: transparent;
}

:global(.dark-mode .more-btn) {
  color: #d9d9d9;
}

:global(.dark-mode .more-btn:hover) {
  color: #6cb6ff;
}

:global(.dark-mode .asset-action-dropdown .el-dropdown-menu__item.is-disabled) {
  color: #6b7280;
}

:global(.dark-mode .el-switch__core) {
  background: #303030;
  border-color: #303030;
}

:global(.dark-mode .el-empty__image svg) {
  opacity: 0.72;
}
:global(.dark-mode .el-table--border::before),
:global(.dark-mode .el-table--group::after),
:global(.dark-mode .el-table::before) {
  background-color: #303030;
}
:global(.dark-mode .el-table__inner-wrapper),
:global(.dark-mode .el-table__header-wrapper),
:global(.dark-mode .el-table__body-wrapper),
:global(.dark-mode .el-table__empty-block),
:global(.dark-mode .el-table__empty-text),
:global(.dark-mode .el-scrollbar__view) {
  background: #1f1f1f;
  color: #f5f5f5;
}

:global(.dark-mode .el-table__header thead tr th.el-table__cell) {
  background: #262626 !important;
  color: #d9d9d9 !important;
}

:global(.dark-mode .el-table__body tbody tr td.el-table__cell) {
  background: #1f1f1f !important;
  color: #f5f5f5 !important;
}

:global(.dark-mode .el-table__body tbody tr:hover > td.el-table__cell) {
  background: #262626 !important;
}

:global(.dark-mode .el-table td.el-table__cell),
:global(.dark-mode .el-table th.el-table__cell) {
  border-color: #303030 !important;
}

:global(.dark-mode .el-table .cell),
:global(.dark-mode .el-table__empty-text) {
  color: #f5f5f5;
}

:global(.dark-mode .el-tabs__content) {
  color: #f5f5f5;
}
:global(.dark-mode .el-descriptions__content) {
  background: #1f1f1f;
  color: #f5f5f5;
}
:global(.dark-mode .el-descriptions) {
  background: #1f1f1f;
  color: #f5f5f5;
}

:global(.dark-mode .el-descriptions__table) {
  background: #1f1f1f;
  color: #f5f5f5;
}

:global(.dark-mode .el-descriptions__body) {
  background: #1f1f1f;
}

:global(.dark-mode .el-descriptions__cell) {
  border-color: #303030 !important;
}

:global(.dark-mode .el-descriptions__label.el-descriptions__cell.is-bordered-label) {
  background: #262626 !important;
  color: #d9d9d9 !important;
}

:global(.dark-mode .el-descriptions__content.el-descriptions__cell.is-bordered-content) {
  background: #1f1f1f !important;
  color: #f5f5f5 !important;
}

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

.priority-ai-item {
  margin-bottom: 10px;
  line-height: 1.8;
}

.priority-ai-item:last-child {
  margin-bottom: 0;
}

.priority-ai-seq {
  font-weight: 700;
  color: #303133;
}

.priority-score-text {
  font-weight: 700;
  color: #303133;
}

.more-btn {
  font-size: 22px;
  line-height: 1;
  color: #666;
}

:deep(.asset-action-dropdown) {
  min-width: 110px;
}

:deep(.asset-action-dropdown .el-dropdown-menu__item) {
  justify-content: center;
  min-width: 110px;
  height: 40px;
  font-size: 18px;
}

.record-table-scroll-top {
  overflow-x: auto;
  overflow-y: hidden;
  position: sticky;
  top: 0;
  z-index: 5;
  background: #fff;
  margin-bottom: 8px;
}

.record-table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 600px;
}

.record-table-wrapper::-webkit-scrollbar {
  width: 10px;
  height: 10px;
}

.record-table-wrapper::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 999px;
}

:global(.dark-mode .record-table-wrapper::-webkit-scrollbar-thumb) {
  background: #4b5563;
}


.asset-tree {
  background: #fff;
}

:deep(.asset-tree .el-tree-node__content) {
  height: auto;
  min-height: 38px;
  padding: 4px 0;
  border-radius: 6px;
}

:deep(.asset-tree .el-tree-node__content:hover) {
  background-color: #f5f7fa;
}

:deep(.asset-tree .el-tree-node__expand-icon) {
  color: #909399;
}

.asset-tree-group {
  font-size: 15px;
  font-weight: 700;
  color: #303133;
  padding: 6px 0;
}

.asset-tree-node {
  width: 100%;
  padding: 8px 10px;
  border-radius: 6px;
  box-sizing: border-box;
  transition: all 0.2s;
}

.asset-tree-node.is-selected {
  background: #ecf5ff;
  border: 1px solid #b3d8ff;
}

.asset-tree-node-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  line-height: 20px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.asset-tree-node-sub {
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
  line-height: 18px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.asset-tree-progress {
  color: #909399;
  font-weight: 400;
  margin-left: 2px;
}

.stats-card {
  text-align: center;
  padding: 8px 0;
}

.stats-number {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
  line-height: 1.2;
}

.stats-label {
  margin-top: 8px;
  font-size: 14px;
  color: #909399;
}

.stats-number-green {
  color: #67c23a;
}

.stats-number-yellow {
  color: #e6a23c;
}

.stats-number-red {
  color: #f56c6c;
}

:deep(.col-green .cell) {
  color: #67c23a;
  font-weight: 600;
}

:deep(.col-yellow .cell) {
  color: #e6a23c;
  font-weight: 600;
}

:deep(.col-red .cell) {
  color: #f56c6c;
  font-weight: 600;
}

.priority-header-card {
  padding: 14px 16px;
  border: 1px solid #ebeef5;
  border-radius: 10px;
  background: #fafafa;
}

.priority-header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.priority-header-desc {
  font-size: 14px;
  color: #909399;
  line-height: 1.6;
}

.priority-ai-card {
  background: #fafafa;
}

.priority-ai-text {
  font-size: 14px;
  color: #606266;
  line-height: 1.8;
}

.record-tip-icon {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 1px solid #c0c4cc;
  color: #909399;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  box-sizing: border-box;
}

.record-action-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.dirty-tip {
  font-size: 12px;
  color: #909399;
  line-height: 1;
}

.ellipsis-text {
  display: block;
  width: 100%;
  white-space: normal;
  word-break: break-all;
  line-height: 1.5;
}

:deep(.check-record-table .cell) {
  word-break: break-word;
}

:deep(.check-record-table .el-table__cell) {
  vertical-align: middle;
}

:deep(.check-record-table .el-table__body td:nth-child(1) .cell),
:deep(.check-record-table .el-table__body td:nth-child(2) .cell),
:deep(.check-record-table .el-table__body td:nth-child(4) .cell),
:deep(.check-record-table .el-table__body td:nth-child(10) .cell),
:deep(.check-record-table .el-table__body td:nth-child(13) .cell) {
  text-align: center;
}

.record-action-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.record-action-row {
  flex-wrap: wrap;
}

.record-action-upload {
  display: flex;
  align-items: center;
}

:deep(.record-action-upload .el-upload) {
  display: flex;
  align-items: center;
}

:deep(.record-action-btn) {
  min-width: 98px;
  margin: 0 !important;
}

:global(.dark-mode .record-action-btn) {
  box-shadow: none;
}
</style>