<template>
  <el-dialog
    v-model="visibleProxy"
    title="AI整改建议"
    width="720px"
    @close="handleClose"
  >
    <div v-loading="loading" style="min-height: 180px;">
      <el-empty v-if="!loading && !data" description="暂无建议内容" />

      <div v-if="data" style="display: flex; flex-direction: column; gap: 16px;">
        <el-card>
          <template #header>
            <span>问题描述</span>
          </template>
          <div class="ai-text">{{ data.problem_description }}</div>
        </el-card>

        <el-card>
          <template #header>
            <span>可能原因</span>
          </template>
          <div class="ai-text">{{ data.possible_causes }}</div>
        </el-card>

        <el-card>
          <template #header>
            <span>整改建议</span>
          </template>
          <div class="ai-text">{{ data.rectification_suggestion }}</div>
        </el-card>
      </div>
    </div>

    <template #footer>
      <el-button @click="visibleProxy = false">关闭</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  recordId: {
    type: Number,
    default: null
  }
})

const emit = defineEmits(['update:modelValue'])

const loading = ref(false)
const data = ref(null)

const visibleProxy = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const fetchSuggestion = async () => {
  if (!props.recordId) return
  loading.value = true
  data.value = null
  try {
    const res = await axios.get(`http://127.0.0.1:8000/ai/record/${props.recordId}`)
    data.value = res.data
  } catch (error) {
    console.error(error)
    const msg = error?.response?.data?.detail || '获取 AI 整改建议失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const handleClose = () => {
  data.value = null
}

watch(
  () => props.modelValue,
  (val) => {
    if (val && props.recordId) {
      fetchSuggestion()
    }
  }
)
</script>

<style scoped>
.ai-text {
  white-space: pre-wrap;
  line-height: 1.8;
  color: #303133;
}
</style>