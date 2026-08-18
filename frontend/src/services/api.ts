import axios from 'axios'

// Production: use VITE_API_URL (https://job-ztog.onrender.com)
// Development: use / to leverage Vite proxy for /api routes
const envBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
const baseURL = envBaseUrl && envBaseUrl.length > 0 ? envBaseUrl : '/'

const api = axios.create({
  baseURL,
  timeout: 30000,
  // In production, credentials are needed for cross-origin requests
  withCredentials: true,
})

export const uploadResume = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/resume/upload', formData)
}

export default api
