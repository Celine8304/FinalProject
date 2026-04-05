import axios from 'axios'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
})

export function getRecordsByAsset(assetId) {
  return request.get(`/records/asset/${assetId}`)
}

export function updateRecord(recordId, data) {
  return request.put(`/records/${recordId}`, data)
}

export function getPriorityByAsset(assetId) {
  return request.get(`/records/priority/asset/${assetId}`)
}

export function getPriorityAiAdviceByAsset(assetId) {
  return request.get(`/ai/priority/asset/${assetId}`)
}