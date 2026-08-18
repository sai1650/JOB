import React, { useEffect, useState, useRef } from 'react'
import api from '../services/api'
import Button from '../components/Button'

type Question = {
  id: string
  text: string
  topic?: string
  difficulty?: string
  number?: number
  sources?: any[]
}

export default function InterviewScreen() {
  const [question, setQuestion] = useState<Question | null>(null)
  const [answer, setAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [progress, setProgress] = useState({ current: 0, total: 0 })
  const sessionRef = useRef<string | null>(null)

  useEffect(() => {
    const sid = localStorage.getItem('session_id')
    sessionRef.current = sid
    if (!sid) return
    loadCurrent()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const loadCurrent = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/api/interviews/${sessionRef.current}/current-question`)
      const currentQuestion = res.data.question ?? null
      setQuestion(currentQuestion)
      setProgress(res.data.progress ?? { current: 0, total: 0 })
    } catch (err: any) {
      console.error(err)
      setQuestion(null)
      setProgress({ current: 0, total: 0 })
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async () => {
    if (!question) return
    if (!answer.trim()) return alert('Please enter an answer')
    setSubmitting(true)
    try {
      await api.post(`/api/interviews/${sessionRef.current}/answer`, {
        question_id: question.id,
        answer_text: answer,
      })
      await api.post(`/api/interviews/${sessionRef.current}/next`)
      setAnswer('')
      await loadCurrent()
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Submission failed')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-violet-50 p-5 md:p-8">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-600">Live interview</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-900">Candidate screening session</h1>
          </div>
          <div className="rounded-full border border-blue-200 bg-blue-100 px-3 py-1 text-sm font-semibold text-blue-700">
            {progress.current || 0}/{progress.total || 0} answered
          </div>
        </div>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.5fr_0.8fr]">
          <div className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-lg shadow-slate-200/50 backdrop-blur-sm">
            {loading ? (
              <div className="flex min-h-[420px] items-center justify-center text-center">
                <div>
                  <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-4 border-blue-200 border-t-blue-600" />
                  <p className="text-lg font-medium text-slate-700">Preparing your next question…</p>
                </div>
              </div>
            ) : question ? (
              <>
                <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-sm font-medium text-slate-500">
                      Question {question.number} of {progress.total || 1}
                    </p>
                    <h2 className="mt-1 text-2xl font-semibold text-slate-900">{question.topic ?? 'General'}</h2>
                  </div>
                  <span className="rounded-full bg-violet-100 px-3 py-1 text-sm font-semibold text-violet-700">
                    {question.difficulty ?? 'medium'}
                  </span>
                </div>

                <div className="rounded-xl border border-slate-200 bg-slate-50 p-5 text-lg leading-8 text-slate-800">
                  {question.text}
                </div>

                <details className="mt-6 rounded-xl border border-slate-200 bg-white p-4">
                  <summary className="cursor-pointer list-none text-sm font-medium text-slate-600">
                    Sources used
                  </summary>
                  <div className="mt-3 space-y-2 text-sm text-slate-600">
                    {(question.sources || []).slice(0, 5).map((s: any, i: number) => (
                      <div key={i} className="rounded-md bg-slate-50 px-3 py-2">
                        {s.source_title ?? s.source ?? 'Knowledge source'}
                      </div>
                    ))}
                  </div>
                </details>

                <div className="mt-6">
                  <label className="mb-2 block text-sm font-medium text-slate-700">Candidate response</label>
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    rows={8}
                    className="w-full rounded-xl border border-slate-200 bg-white p-4 text-slate-800 shadow-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    placeholder="Type the candidate's answer here..."
                  />
                </div>

                <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="text-sm font-medium text-slate-600">
                    Progress: {progress.current}/{progress.total}
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <Button
                      variant="ghost"
                      onClick={() => navigator.clipboard?.writeText(answer)}
                      className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700"
                    >
                      Save Draft
                    </Button>
                    <Button
                      onClick={onSubmit}
                      disabled={submitting}
                      className="rounded-lg bg-gradient-to-r from-blue-600 to-violet-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/20"
                    >
                      {submitting ? 'Submitting…' : 'Submit Answer'}
                    </Button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex min-h-[420px] items-center justify-center text-center">
                <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-8 py-10">
                  <p className="text-lg font-semibold text-slate-700">No active question</p>
                  <p className="mt-2 text-slate-500">This interview may be complete or the next question is being prepared.</p>
                </div>
              </div>
            )}
          </div>

          <aside className="rounded-2xl border border-slate-200 bg-white/90 p-6 shadow-lg shadow-slate-200/50 backdrop-blur-sm">
            <div className="mb-5">
              <p className="text-sm font-medium uppercase tracking-[0.2em] text-slate-500">Interview progress</p>
              <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-slate-200">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-blue-600 to-violet-600"
                  style={{ width: `${progress.total ? ((progress.current || 0) / progress.total) * 100 : 0}%` }}
                />
              </div>
            </div>

            <div className="space-y-5">
              <div className="rounded-xl bg-slate-50 p-4">
                <p className="text-sm text-slate-500">Candidate</p>
                <p className="mt-2 text-lg font-semibold text-slate-900">John Doe</p>
                <p className="text-sm text-slate-600">AI/ML Engineer</p>
              </div>

              <div className="rounded-xl bg-gradient-to-r from-blue-50 to-violet-50 p-4">
                <p className="text-sm text-slate-500">Estimated remaining</p>
                <p className="mt-2 text-2xl font-bold text-slate-900">
                  {Math.max(0, (progress.total - progress.current) * 2)} min
                </p>
              </div>

              <div className="flex flex-col gap-2">
                <Button variant="ghost" className="justify-center rounded-lg border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700">
                  RAG Trace
                </Button>
                <Button variant="ghost" className="justify-center rounded-lg border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700">
                  Candidate Profile
                </Button>
                <Button variant="ghost" className="justify-center rounded-lg border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700">
                  End Interview
                </Button>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </div>
  )
}
