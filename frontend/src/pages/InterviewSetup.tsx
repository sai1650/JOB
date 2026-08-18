import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

export default function InterviewSetup() {
  const [numQuestions, setNumQuestions] = useState(5)
  const [difficulty, setDifficulty] = useState('medium')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const estimatedTime = numQuestions * 3
  const difficultyLabel = { easy: '⚡ Easy', medium: '🎯 Medium', hard: '🔥 Advanced' }

  const onStart = async () => {
    const candidate_id = localStorage.getItem('candidate_id')
    const role = localStorage.getItem('role')
    if (!candidate_id || !role) return alert('Missing candidate or role')
    setLoading(true)
    try {
      const res = await api.post('/api/interviews', {
        candidate_id,
        role,
        num_questions: numQuestions,
        difficulty,
      })
      const session_id = res.data.session_id
      localStorage.setItem('session_id', session_id)
      navigate('/interview')
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to create interview')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 p-6">
      <div className="max-w-2xl mx-auto py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-slate-900 mb-3">Interview Setup</h1>
          <p className="text-lg text-slate-600">Configure your technical interview</p>
        </div>

        {/* Main Card */}
        <div className="bg-white/80 backdrop-blur-lg border border-slate-200 rounded-2xl shadow-lg p-8 space-y-8">
          
          {/* Number of Questions */}
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <div>
                <label className="block text-sm font-semibold text-slate-900">Number of Questions</label>
                <p className="text-sm text-slate-500 mt-1">More questions = more comprehensive assessment</p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-blue-600">{numQuestions}</div>
                <div className="text-xs text-slate-500 mt-1">questions</div>
              </div>
            </div>
            
            <input
              type="range"
              min={1}
              max={20}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            
            <div className="flex justify-between text-xs text-slate-500 px-1">
              <span>1 question</span>
              <span>10 questions</span>
              <span>20 questions</span>
            </div>
          </div>

          {/* Difficulty Level */}
          <div className="space-y-4 border-t pt-8">
            <div className="flex justify-between items-center">
              <div>
                <label className="block text-sm font-semibold text-slate-900">Difficulty Level</label>
                <p className="text-sm text-slate-500 mt-1">Determines question complexity & depth</p>
              </div>
              <div className="text-right">
                <div className="text-2xl">{difficulty === 'easy' ? '⚡' : difficulty === 'medium' ? '🎯' : '🔥'}</div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {['easy', 'medium', 'hard'].map((level) => (
                <button
                  key={level}
                  onClick={() => setDifficulty(level)}
                  className={`p-4 rounded-lg border-2 transition-all font-semibold text-center ${
                    difficulty === level
                      ? 'border-blue-500 bg-blue-50 text-blue-900'
                      : 'border-slate-200 bg-white text-slate-600 hover:border-slate-300'
                  }`}
                >
                  <div className="text-lg mb-1">{level === 'easy' ? '⚡' : level === 'medium' ? '🎯' : '🔥'}</div>
                  <div className="capitalize">{level}</div>
                  <div className="text-xs text-slate-500 mt-1">
                    {level === 'easy' && 'Basic concepts'}
                    {level === 'medium' && 'Real-world scenarios'}
                    {level === 'hard' && 'Complex challenges'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Summary Card */}
          <div className="space-y-4 border-t pt-8 bg-gradient-to-r from-blue-50 to-purple-50 -mx-8 -mb-8 px-8 py-8 rounded-b-2xl">
            <h3 className="font-semibold text-slate-900">Interview Summary</h3>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white rounded-lg p-4 border border-slate-100">
                <div className="text-sm text-slate-600">Total Questions</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">{numQuestions}</div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-slate-100">
                <div className="text-sm text-slate-600">Est. Duration</div>
                <div className="text-2xl font-bold text-slate-900 mt-1">~{estimatedTime} min</div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-slate-100 col-span-2">
                <div className="text-sm text-slate-600">Difficulty</div>
                <div className="text-lg font-bold text-slate-900 mt-1 capitalize">
                  {difficultyLabel[difficulty as keyof typeof difficultyLabel]}
                </div>
              </div>
            </div>

            <div className="bg-blue-100 border border-blue-200 text-blue-800 px-4 py-3 rounded-lg text-sm">
              ✨ AI will adapt question complexity based on candidate performance
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mt-8">
          <button
            onClick={() => navigate(-1)}
            className="flex-1 px-6 py-3 border-2 border-slate-200 text-slate-900 rounded-lg font-semibold hover:bg-slate-50 transition-colors"
          >
            Go Back
          </button>
          <button
            onClick={onStart}
            disabled={loading}
            className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span> Starting Interview…
              </span>
            ) : (
              '🚀 Start Interview'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
