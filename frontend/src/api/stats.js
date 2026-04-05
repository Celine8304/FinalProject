import axios from 'axios'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
})

export function getProjectStats(projectId) {
  return request.get(`/stats/project/${projectId}`)
}