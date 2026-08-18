import axios from 'axios'

// Production: use VITE_API_URL (https://job-ztog.onrender.com)
// Development: use / to leverage Vite proxy for /api routes
const envBaseUrl = (import.meta.env.VITE_API_URL as string | undefined)?.trim()
const baseURL = envBaseUrl && envBaseUrl.length > 0 ? envBaseUrl : '/'

console.log('[INIT] API baseURL:', baseURL)

const api = axios.create({
  baseURL,
  timeout: 30000,
  // In production, credentials are needed for cross-origin requests
  withCredentials: true,
})

// Add request interceptor to log all requests
api.interceptors.request.use(config => {
  console.log('[REQUEST]', config.method?.toUpperCase(), config.baseURL + config.url)
  return config
}, error => {
  console.error('[REQUEST ERROR]', error)
  return Promise.reject(error)
})

// Add response interceptor to log all responses
api.interceptors.response.use(response => {
  console.log('[RESPONSE]', response.status, response.config.url)
  return response
}, error => {
  console.error('[RESPONSE ERROR]', error.response?.status, error.config.url, error.response?.data)
  return Promise.reject(error)
})

export const uploadResume = (file: File, name: string = '', email: string = '') => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Backend expects name and email as QUERY PARAMETERS, not form fields
  // Build URL with query parameters
  const params = new URLSearchParams()
  if (name.trim()) params.append('name', name.trim())
  if (email.trim()) params.append('email', email.trim())
  
  const uploadUrl = `/api/resume/upload${params.toString() ? '?' + params.toString() : ''}`
  
  console.log('[UPLOAD] Full request URL:', `${baseURL}${uploadUrl}`)
  console.log('[UPLOAD] File details:', {
    filename: file.name,
    size: file.size,
    type: file.type,
  })
  console.log('[UPLOAD] Query params:', {
    name: name.trim() || '(empty)',
    email: email.trim() || '(empty)',
  })
  
  return api.post(uploadUrl, formData)
}

export default api
