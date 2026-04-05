import axios from 'axios'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
})

export function getAssetsByProject(projectId) {
  return request.get(`/assets/project/${projectId}`)
}

export function createAsset(data) {
  return request.post('/assets/', data)
}

export function updateAsset(id, data) {
  return request.put(`/assets/${id}`, data)
}

export function deleteAsset(id) {
  return request.delete(`/assets/${id}`)
}

export function getAssetProgressByProject(projectId) {
  return request.get(`/assets/project/${projectId}/progress`)
} 