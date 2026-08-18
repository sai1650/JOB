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

export const uploadResume = (file: File, name: string = '', email: string = '') => {
  const formData = new FormData()
  formData.append('file', file)
  
  // Backend expects name and email as QUERY PARAMETERS, not form fields
  // Build URL with query parameters
  const params = new URLSearchParams()
  if (name.trim()) params.append('name', name.trim())
  if (email.trim()) params.append('email', email.trim())
  
  const uploadUrl = `/api/resume/upload${params.toString() ? '?' + params.toString() : ''}`
  
  console.log(`[DEBUG] Upload URL: ${baseURL}${uploadUrl}`, {
    filename: file.name,
    size: file.size,
    type: file.type,
    withName: !!name.trim(),
    withEmail: !!email.trim(),
  })
  
  return api.post(uploadUrl, formData)
    .then(response => {
      console.log('[DEBUG] Upload response status:', response.status)
      console.log('[DEBUG] Upload response data:', response.data)
      return response
    })
    .catch(err => {
      console.error('[ERROR] Resume upload failed:', {
        status: err?.response?.status,
        statusText: err?.response?.statusText,
        code: err?.code,
        message: err?.message,
        data: err?.response?.data,
        requestUrl: err?.config?.url,
      })
      throw err
    })
}

export default api
