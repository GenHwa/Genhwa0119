import axios from 'axios'

export const BASE_URL = ''
export const UPLOAD_BASE = '/uploads/'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000
})

// Stats
export const getStats = () => api.get('/api/stats')

// User search
export const searchUsers = (q) => api.get('/api/users/search', { params: { q } })
export const searchPhotos = (q, token = '') => api.get('/api/photos/search', { params: { q, token } })
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

// Photos (with pagination & feed filter)
export const getPhotos = (token = '', page = 1, limit = 10, feed = 'all') =>
  api.get('/api/photos', { params: { token, page, limit, feed } })
export const getMyPhotos = (token = '') => api.get('/api/photos/my', { params: { token } })
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

// Bookmarks
export const toggleBookmark = (photoId, token) => api.post(`/api/photos/${photoId}/bookmark`, new URLSearchParams({ token }))
export const getBookmarks = (token = '', page = 1, limit = 10) =>
  api.get('/api/bookmarks', { params: { token, page, limit } })
export const getBookmarkCount = (token = '') => api.get('/api/bookmarks/count', { params: { token } })

// Followers & Following
export const getFollowers = (userId, token = '') => api.get(`/api/users/${userId}/followers`, { params: { token } })
export const getFollowing = (userId, token = '') => api.get(`/api/users/${userId}/following`, { params: { token } })
export const removeFollower = (followerId, token) => api.delete(`/api/users/${followerId}/followers/remove`, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  data: new URLSearchParams({ token })
})

// DM (Direct Messages)
export const getDmHistory = (otherUserId, token = '') => api.get(`/api/dm/${otherUserId}`, { params: { token } })
export const sendDm = (otherUserId, content, token) => api.post(`/api/dm/${otherUserId}`, null, {
  params: { token, content }
})
export const getUnreadDmCount = (token = '') => api.get('/api/dm/unread', { params: { token } })
export const deleteDmConversation = (otherUserId, token = '') => api.delete(`/api/dm/${otherUserId}`, { params: { token } })
export const pinDmConversation = (otherUserId, pin, token = '') => api.put(`/api/dm/${otherUserId}/pin`, null, {
  params: { token, pin }
})
export const markDmAsRead = (otherUserId, token = '') => api.put(`/api/dm/${otherUserId}/read`, null, { params: { token } })
export const getDmConversations = (token = '') => api.get('/api/dm/conversations', { params: { token } })

// WebSocket URL helper - auto-detect protocol
export function getWsUrl() {
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${proto}//${location.host}/api/dm/ws`
}

// Stories
export const getStories = (token = '') => api.get('/api/stories', { params: { token } })
export const uploadStory = (formData) => api.post('/api/stories', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
export const deleteStory = (storyId, token) => api.delete(`/api/stories/${storyId}`, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  data: new URLSearchParams({ token })
})

export default api
