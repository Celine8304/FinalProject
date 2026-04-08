import axios from 'axios'

const request = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  timeout: 5000,
})

export function archiveProject(projectId, isArchived = true) {
  return request.put(`/projects/${projectId}/archive`, null, {
    params: {
      is_archived: isArchived
    }
  })
}

export function getProjectList(username) {
  return request.get('/projects/', {
    params: { username }
  })
}

export function createProject(data) {
  return request.post('/projects/', data)
}

export function updateProject(id, data) {
  return request.put(`/projects/${id}`, data)
}

export function deleteProject(id) {
  return request.delete(`/projects/${id}`)
}