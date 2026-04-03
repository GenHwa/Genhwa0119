import axios from 'axios'

export const BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') ? 'http://localhost:520' : `http://${window.location.hostname}:520`

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000
})

// Stats
export const getStats = () => api.get('/api/stats')

// User search
export const searchUsers = (q) => api.get('/api/users/search', { params: { q } })
export const searchPhotos = (q, token = '') => api.get('/api/photos/search', { params: { q, token } })
export const searchMessages = (q, token = '') => api.get('/api/messages/search', { params: { q, token } })
export const getUserPhotos = (userId, token = '') => api.get(`/api/users/${userId}/photos`, { params: { token } })
export const followUser = (userId, token) => api.post(`/api/users/${userId}/follow`, new URLSearchParams({ token }))
export const getFollowStatus = (userId, token = '') => api.get(`/api/users/${userId}/follow/status`, { params: { token } })

// Auth
export const register = (data) => api.post('/api/auth/register', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const login = (data) => api.post('/api/auth/login', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const getMe = (token) => api.get('/api/auth/me', { params: { token } })
export const uploadAvatar = (formData) => api.post('/api/auth/avatar', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const updateProfile = (data) => api.put('/api/auth/profile', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const changePassword = (data) => api.put('/api/auth/password', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})

// Get token helper
export function getToken() {
  return localStorage.getItem('diary_token') || ''
}

// Messages
export const getMessages = (token = '') => api.get('/api/messages', { params: { token } })
export const createMessage = (data) => api.post('/api/messages', data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const updateMessage = (id, data) => api.put(`/api/messages/${id}`, data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteMessage = (id, token) => api.delete(`/api/messages/${id}`, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  data: new URLSearchParams({ token })
})
export const likeMessage = (id, userHash) => api.post(`/api/messages/${id}/like`, new URLSearchParams({ user_hash: userHash }))

// Photos
export const getPhotos = (token = '') => api.get('/api/photos', { params: { token } })
export const getMyPhotos = (token = '') => api.get('/api/photos/my', { params: { token } })
export const getMyMessages = (token = '') => api.get('/api/messages/my', { params: { token } })
export const uploadPhoto = (formData) => api.post('/api/photos', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const updatePhoto = (id, data) => api.put(`/api/photos/${id}`, data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const likePhoto = (id, userHash) => api.post(`/api/photos/${id}/like`, new URLSearchParams({ user_hash: userHash }))
export const getComments = (photoId) => api.get(`/api/photos/${photoId}/comments`)
export const addComment = (photoId, data) => api.post(`/api/photos/${photoId}/comments`, data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const updateComment = (commentId, data) => api.put(`/api/comments/${commentId}`, data, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteComment = (commentId, token) => api.delete(`/api/comments/${commentId}`, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  data: new URLSearchParams({ token })
})
export const deletePhoto = (id, token) => api.delete(`/api/photos/${id}`, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  data: new URLSearchParams({ token })
})

export default api
