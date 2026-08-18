import React, { useState } from 'react'
import { uploadResume } from '../services/api'
import { useNavigate } from 'react-router-dom'
import FileUpload from '../components/FileUpload'
import Button from '../components/Button'

const MAX_FILE_BYTES = 5 * 1024 * 1024

type CandidateProfile = {
  skills: string[]
  technologies: string[]
  domains: string[]
  projects: string[]
}

function readStoredProfile(): CandidateProfile | null {
  try {
    const raw = localStorage.getItem('candidate_profile')
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return {
      skills: parsed.skills || [],
      technologies: parsed.technologies || [],
      domains: parsed.domains || [],
      projects: parsed.projects || [],
    }
  } catch {
    return null
  }
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  const kb = bytes / 1024
  if (kb < 1024) return `${kb.toFixed(1)} KB`
  return `${(kb / 1024).toFixed(1)} MB`
}

function getFileExt(name: string) {
  return name.split('.').pop()?.toLowerCase() || ''
}

function validateResumeFile(file: File): string | null {
  const ext = getFileExt(file.name)
  if (ext !== 'pdf' && ext !== 'txt') {
    return 'Please upload a PDF or TXT file.'
  }
  if (file.size > MAX_FILE_BYTES) {
    return 'File size must be less than 5 MB.'
  }
  return null
}

export default function ResumeUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [profile, setProfile] = useState<CandidateProfile | null>(() => readStoredProfile())
  const [profileFilename, setProfileFilename] = useState<string | null>(
    () => localStorage.getItem('candidate_filename') || null
  )
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'ready' | 'done'>('idle')
  const navigate = useNavigate()

  const onFileSelected = (file: File) => {
    setSelectedFile(file)
    setError(null)
    setUploadStatus('ready')
  }

  const onFileError = (message: string | null) => {
    if (message) {
      setSelectedFile(null)
      setUploadStatus('idle')
      setError(message)
      return
    }
    setError(null)
  }

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (loading) return
    if (!selectedFile) return setError('Please select a file')

    const validationError = validateResumeFile(selectedFile)
    if (validationError) {
      setError(validationError)
      return
    }

    setLoading(true)
    setError(null)
    console.log('[DEBUG] Starting resume upload for:', selectedFile.name)
    console.log('[DEBUG] baseURL from env:', import.meta.env.VITE_API_URL || 'using /api proxy')
    
    try {
      const res = await uploadResume(selectedFile)
      
      // Verify we got a successful response
      if (!res || !res.data) {
        throw new Error('Empty response from server')
      }
      
      console.log('[DEBUG] Resume upload successful, status:', res.status)
      console.log('[DEBUG] Response candidate_id:', res.data.candidate_id)
      
      const cid = res.data.candidate_id
      if (!cid) {
        throw new Error('No candidate_id in response')
      }
      
      localStorage.setItem('candidate_id', cid)
      const uploadedFilename = res.data?.filename || selectedFile.name
      setProfileFilename(uploadedFilename)
      localStorage.setItem('candidate_filename', uploadedFilename)

      const parsedProfile: CandidateProfile = {
        skills: res.data?.profile?.skills || res.data?.skills || [],
        technologies: res.data?.profile?.technologies || res.data?.technologies || [],
        domains: res.data?.profile?.domains || res.data?.domains || [],
        projects: res.data?.profile?.projects || [],
      }
      setProfile(parsedProfile)
      localStorage.setItem('candidate_profile', JSON.stringify(parsedProfile))
      setUploadStatus('done')
      // navigate to role selection after short delay for UX
      setTimeout(() => navigate('/roles'), 900)
    } catch (err: any) {
      console.error('[ERROR] Full error object:', err)
      console.error('[ERROR] Error status:', err?.response?.status)
      console.error('[ERROR] Error message:', err?.message)
      console.error('[ERROR] Error code:', err?.code)
      
      // Timeout error
      if (err?.code === 'ECONNABORTED') {
        setError('Resume processing service is unavailable. Please try again.')
      }
      // Network errors
      else if (err?.code === 'ERR_NETWORK' || err?.code === 'ENOTFOUND' || err?.message?.includes('Network')) {
        setError('Network error. Please check your internet connection and try again.')
      }
      // Bad request or file size errors (4xx)
      else if (err?.response?.status === 400) {
        setError(err?.response?.data?.detail || 'Please upload a valid PDF or TXT file.')
      } else if (err?.response?.status === 413) {
        setError('File size must be less than 5 MB.')
      }
      // CORS or other client errors
      else if (err?.response?.status && err?.response?.status >= 400 && err?.response?.status < 500) {
        setError(err?.response?.data?.detail || `Upload error: ${err?.response?.status}`)
      }
      // Server errors (5xx)
      else if (err?.response?.status && err?.response?.status >= 500) {
        console.error('[ERROR] Server returned:', err?.response?.status, err?.response?.data)
        setError(err?.response?.data?.detail || `Server error (${err?.response?.status}). Please try again.`)
      }
      // Response validation error (e.g., no candidate_id)
      else if (err?.message?.includes('candidate_id') || err?.message?.includes('Empty response')) {
        console.error('[ERROR] Response validation failed:', err?.message)
        setError('Server response was invalid. Please try again.')
      }
      // Fallback: show actual error message
      else {
        const errorMsg = err?.response?.data?.detail || err?.message || 'Unable to process this resume.'
        console.error('[ERROR] Fallback error:', errorMsg)
        setError(errorMsg)
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-start justify-center bg-gray-50 p-8">
      <div className="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h2 className="text-2xl font-semibold mb-4">Understand the Candidate First</h2>
          <p className="text-gray-600 mb-6">Upload a resume and let the AI build a candidate profile before the interview begins.</p>
          <form onSubmit={onSubmit}>
            <FileUpload
              onChange={onFileSelected}
              onError={onFileError}
              validateFile={validateResumeFile}
              accept=".pdf,.txt,text/plain,application/pdf"
              disabled={loading}
            >
              <div>
                <div className="text-2xl font-semibold mb-2">Drop your resume here</div>
                <div className="text-sm text-gray-500">PDF or TXT • Maximum 5 MB</div>
              </div>
            </FileUpload>

            {selectedFile && (
              <div className="mt-3 text-sm text-gray-700">
                <div className="font-medium">{selectedFile.name}</div>
                <div>{formatFileSize(selectedFile.size)}</div>
                <div>{selectedFile.type || getFileExt(selectedFile.name).toUpperCase()}</div>
                {uploadStatus === 'ready' && (
                  <div className="text-green-600">✓ Ready to analyze</div>
                )}
                {uploadStatus === 'done' && (
                  <div className="text-green-600">Resume Analyzed ✓</div>
                )}
              </div>
            )}

            {error && <div className="text-red-600 mt-3">{error}</div>}
            <div className="mt-4 flex justify-end">
              <Button disabled={loading || !selectedFile}>
                {loading ? (
                  <span className="inline-flex items-center gap-2">
                    <span className="h-4 w-4 border-2 border-white/70 border-t-transparent rounded-full animate-spin" />
                    Analyzing Resume...
                  </span>
                ) : (
                  'Upload & Analyze'
                )}
              </Button>
            </div>
          </form>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-3">AI Candidate Profile</h3>
          {!profile ? (
            <div className="p-4 bg-white rounded-lg subtle-shadow">
              <div className="text-sm text-gray-500">No resume processed yet</div>
              <div className="text-sm text-gray-400 mt-2">Upload a resume to see extracted skills, technologies, and domains.</div>
            </div>
          ) : (
            <div className="p-4 bg-white rounded-lg subtle-shadow">
              <div className="text-sm text-gray-500">{profileFilename || 'Resume uploaded'}</div>
              <div className="mt-3">
                <div className="text-xs text-gray-500 mb-2">Skills</div>
                <div className="flex flex-wrap gap-2">{(profile.skills||[]).map((s:string,i:number)=>(<div key={i} className="chip">{s}</div>))}</div>
              </div>
              <div className="mt-3">
                <div className="text-xs text-gray-500 mb-2">Technologies</div>
                <div className="flex flex-wrap gap-2">{(profile.technologies||[]).map((s:string,i:number)=>(<div key={i} className="chip">{s}</div>))}</div>
              </div>
              <div className="mt-3">
                <div className="text-xs text-gray-500 mb-2">Domains</div>
                <div className="flex flex-wrap gap-2">{(profile.domains||[]).map((s:string,i:number)=>(<div key={i} className="chip">{s}</div>))}</div>
              </div>
              {profile.projects.length > 0 && (
                <div className="mt-3">
                  <div className="text-xs text-gray-500 mb-2">Projects</div>
                  <div className="flex flex-wrap gap-2">{profile.projects.map((s:string,i:number)=>(<div key={i} className="chip">{s}</div>))}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
