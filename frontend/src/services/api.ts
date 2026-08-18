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
  // Backend expects name and email parameters (defaults handled server-side)
  formData.append('name', '')
  formData.append('email', '')
  
  console.log(`[DEBUG] Uploading resume to: ${baseURL}/api/resume/upload`, {
    filename: file.name,
    size: file.size,
    type: file.type,
  })
  
  return api.post('/api/resume/upload', formData).catch(err => {
    console.error('[ERROR] Resume upload failed:', {
      status: err?.response?.status,
      statusText: err?.response?.statusText,
      message: err?.message,
      data: err?.response?.data,
      url: err?.config?.url,
    })
    throw err
  })
}

export default api
