import axios from 'axios'

export const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string | undefined)?.trim() ||
  (import.meta.env.PROD ? 'https://job-ztog.onrender.com' : '')

if (!import.meta.env.PROD) {
  console.log('[DEV] Final API base URL:', API_BASE_URL || 'relative / (Vite proxy)')
}

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  withCredentials: true,
})

api.interceptors.request.use(config => {
  const requestUrl = config.baseURL ? `${config.baseURL}${config.url ?? ''}` : config.url ?? ''
  console.log('[REQUEST]', config.method?.toUpperCase(), requestUrl)
  return config
}, error => {
  console.error('[REQUEST ERROR]', error)
  return Promise.reject(error)
})

api.interceptors.response.use(response => {
  console.log('[RESPONSE]', response.status, response.config.url)
  return response
}, error => {
  console.error('[RESPONSE ERROR]', error.response?.status, error.config?.url, error.response?.data)
  return Promise.reject(error)
})

export const uploadResume = (file: File, name: string = '', email: string = '') => {
  const formData = new FormData()
  formData.append('file', file)

  const trimmedName = name.trim()
  const trimmedEmail = email.trim()
  const params = new URLSearchParams()

  if (trimmedName) params.append('name', trimmedName)
  if (trimmedEmail) params.append('email', trimmedEmail)

  const uploadPath = `/api/resume/upload${params.toString() ? `?${params.toString()}` : ''}`

  console.log('[UPLOAD] Final request URL:', `${API_BASE_URL}${uploadPath}`)
  console.log('[UPLOAD] File details:', {
    filename: file.name,
    size: file.size,
    type: file.type,
  })
  console.log('[UPLOAD] Query params:', {
    name: trimmedName || '(empty)',
    email: trimmedEmail || '(empty)',
  })

  return api.post(uploadPath, formData)
}

export default api
