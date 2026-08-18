import React, { useEffect, useState } from 'react'
import api from '../services/api'
import MetricCard from '../components/MetricCard'
import ScoreCircle from '../components/ScoreCircle'

function SimpleBarChart({data}:{data:Record<string, number>}){
  const keys = Object.keys(data)
  const max = Math.max(...Object.values(data), 0.0001)
  return (
    <div className="space-y-3">
      {keys.map(k => (
        <div key={k} className="flex items-center">
          <div className="w-36 text-sm text-gray-700">{k}</div>
          <div className="flex-1 ml-2 bg-gray-100 h-4 rounded overflow-hidden">
            <div style={{width: `${(data[k]/max)*100}%`}} className="h-4 bg-gradient-to-r from-[#3b4cca] to-[#7c3aed]" />
          </div>
          <div className="w-12 text-right text-sm ml-2">{(data[k]*100).toFixed(0)}%</div>
        </div>
      ))}
    </div>
  )
}

export default function ResultsDashboard(){
  const [report, setReport] = useState<any | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const sid = localStorage.getItem('session_id')

  useEffect(() => {
    if (!sid) {
      setLoading(false)
      setError('No session selected')
      return
    }
    const load = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await api.get(`/api/interviews/${sid}/report`)
        setReport(res.data)
      } catch (err: any) {
        console.error(err)
        setError(err?.response?.data?.detail || 'Failed to load report')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [sid])

  if (loading) return <div className="p-6">Loading report…</div>
  if (error) return <div className="p-6 text-red-600">{error}</div>
  if (!report) return <div className="p-6">No report available</div>

  const dims = {correctness:0, technical_depth:0, reasoning:0, count:0}
  report.questions?.forEach((q:any)=>{
    const ev = q.evaluation || {}
    if (ev && typeof ev === 'object'){
      dims.correctness += (ev.correctness || 0)
      dims.technical_depth += (ev.technical_depth || 0)
      dims.reasoning += (ev.reasoning || 0)
      dims.count += 1
    }
  })
  const avg = (v:number) => dims.count? (v/dims.count):0

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="col-span-2 p-6 bg-white rounded-lg subtle-shadow">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">Candidate</div>
                <div className="text-2xl font-bold">John Doe • AI/ML Engineer</div>
              </div>
              <div>
                <ScoreCircle score={report.overall_score || 0} />
              </div>
            </div>

            {report.generated_report && (
              <div className="mt-4 p-4 bg-gray-50 rounded">
                <div className="text-sm text-gray-500">Executive Summary</div>
                <div className="mt-1 text-gray-800">{report.generated_report.executive_summary}</div>
                <div className="mt-2 text-sm text-gray-600">Recommendation: <strong>{report.generated_report.hiring_recommendation}</strong></div>
              </div>
            )}
          </div>

          <div className="p-6 bg-white rounded-lg subtle-shadow">
            <MetricCard label="Questions" value={report.num_questions} />
            <div className="mt-4"><MetricCard label="Recommendation" value={report.recommendation ?? 'N/A'} /></div>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="p-4 bg-white rounded-lg subtle-shadow">
            <h3 className="font-semibold mb-2">Topic Performance</h3>
            {Object.keys(report.topic_performance || {}).length === 0 ? (
              <div className="text-sm text-gray-500">No topic data</div>
            ) : (
              <SimpleBarChart data={report.topic_performance} />
            )}
          </div>

          <div className="p-4 bg-white rounded-lg subtle-shadow">
            <h3 className="font-semibold mb-2">Difficulty Performance</h3>
            {Object.keys(report.difficulty_performance || {}).length === 0 ? (
              <div className="text-sm text-gray-500">No difficulty data</div>
            ) : (
              <SimpleBarChart data={report.difficulty_performance} />
            )}
          </div>

          <div className="p-4 bg-white rounded-lg subtle-shadow">
            <h3 className="font-semibold mb-2">Score Progression</h3>
            <div className="h-32 flex items-end gap-1">
              {(report.score_progression || []).map((p:any, i:number)=> (
                <div key={i} style={{height:`${(p.score||0)*100}%`}} className="flex-1 bg-gradient-to-r from-[#3b4cca] to-[#7c3aed]" title={`Step ${p.step}: ${(p.score||0)*100}%`} />
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="p-4 bg-white rounded-lg subtle-shadow">
            <h3 className="font-semibold mb-2">Strengths</h3>
            <ul className="list-disc pl-5">{(report.strengths||[]).map((s:string,i:number)=>(<li key={i}>{s}</li>))}</ul>
          </div>
          <div className="p-4 bg-white rounded-lg subtle-shadow">
            <h3 className="font-semibold mb-2">Weaknesses</h3>
            <ul className="list-disc pl-5">{(report.weaknesses||[]).map((s:string,i:number)=>(<li key={i}>{s}</li>))}</ul>
          </div>
        </div>

        <h3 className="font-semibold mb-2">Questions & Answers</h3>
        {(report.questions||[]).length === 0 ? (
          <div className="text-sm text-gray-500">No answers recorded</div>
        ) : (
          <div className="space-y-4">
            {(report.questions||[]).map((q:any, i:number)=>(
              <div key={i} className="p-4 bg-white rounded-lg subtle-shadow">
                <div className="text-sm text-gray-600">Q{ i+1 } • {q.topic} • {q.difficulty}</div>
                <div className="font-medium mt-1">{q.question_text}</div>
                <div className="mt-2 text-sm">Answer: {q.answer_text}</div>
                <div className="mt-2 text-sm text-gray-700">Score: {(q.evaluation_score||0)*100}%</div>
                <div className="mt-2 text-sm text-gray-600">Feedback: {q.evaluation_feedback}</div>
                <details className="mt-2 text-sm">
                  <summary className="cursor-pointer text-indigo-600">View structured evaluation</summary>
                  <pre className="bg-gray-50 p-2 mt-2 rounded overflow-auto">{JSON.stringify(q.evaluation,null,2)}</pre>
                </details>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
