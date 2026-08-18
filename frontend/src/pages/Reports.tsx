import React, { useState, useEffect } from 'react'
import api from '../services/api'

export default function Reports() {
  const [reports, setReports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedReport, setSelectedReport] = useState<any>(null)
  const [filterRole, setFilterRole] = useState('all')

  useEffect(() => {
    const loadReports = async () => {
      try {
        const res = await api.get('/api/reports')
        setReports(res.data.reports || [])
      } catch {
        // Mock data if API fails
        setReports([
          {
            id: 1,
            candidateName: 'Alex Johnson',
            role: 'Backend Engineer',
            date: '2024-08-15',
            score: 8.2,
            status: 'completed',
            questionsAsked: 5,
            questionsCorrect: 4
          },
          {
            id: 2,
            candidateName: 'Sarah Chen',
            role: 'AI/ML Engineer',
            date: '2024-08-14',
            score: 7.5,
            status: 'completed',
            questionsAsked: 5,
            questionsCorrect: 4
          },
          {
            id: 3,
            candidateName: 'James Wilson',
            role: 'Data Scientist',
            date: '2024-08-13',
            score: 6.8,
            status: 'completed',
            questionsAsked: 5,
            questionsCorrect: 3
          },
        ])
      } finally {
        setLoading(false)
      }
    }
    loadReports()
  }, [])

  const filteredReports = filterRole === 'all' ? reports : reports.filter(r => r.role === filterRole)
  const roles = ['all', ...new Set(reports.map(r => r.role))]

  const getScoreColor = (score: number) => {
    if (score >= 8) return 'text-green-600 bg-green-50'
    if (score >= 6) return 'text-yellow-600 bg-yellow-50'
    return 'text-red-600 bg-red-50'
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Reports</h1>
          <p className="text-gray-600">View and analyze completed interview assessments.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Reports List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
                <select
                  value={filterRole}
                  onChange={(e) => setFilterRole(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                >
                  {roles.map(role => (
                    <option key={role} value={role}>
                      {role === 'all' ? 'All Roles' : role}
                    </option>
                  ))}
                </select>
              </div>

              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading reports...</div>
              ) : filteredReports.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">No reports available</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Candidate</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Role</th>
                        <th className="text-left py-3 px-4 font-semibold text-gray-900">Date</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">Score</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">Accuracy</th>
                        <th className="text-center py-3 px-4 font-semibold text-gray-900">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredReports.map((report:any) => (
                        <tr key={report.id} className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedReport(report)}>
                          <td className="py-3 px-4 text-gray-900 font-medium">{report.candidateName}</td>
                          <td className="py-3 px-4 text-gray-700">{report.role}</td>
                          <td className="py-3 px-4 text-gray-600">{report.date}</td>
                          <td className={`py-3 px-4 text-center font-semibold rounded ${getScoreColor(report.score)}`}>
                            {report.score.toFixed(1)}
                          </td>
                          <td className="py-3 px-4 text-center text-gray-700">
                            {Math.round((report.questionsCorrect / report.questionsAsked) * 100)}%
                          </td>
                          <td className="py-3 px-4 text-center">
                            <button className="text-indigo-600 hover:text-indigo-700 text-sm font-medium">View</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Report Details */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h3 className="text-lg font-semibold mb-4">Report Details</h3>
              {selectedReport ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-600">Candidate Name</label>
                    <p className="font-medium text-gray-900">{selectedReport.candidateName}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Role</label>
                    <p className="font-medium text-gray-900">{selectedReport.role}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Interview Date</label>
                    <p className="font-medium text-gray-900">{selectedReport.date}</p>
                  </div>
                  <div className="pt-2 border-t border-gray-200">
                    <label className="text-sm text-gray-600">Overall Score</label>
                    <div className={`text-3xl font-bold ${selectedReport.score >= 7 ? 'text-green-600' : selectedReport.score >= 5 ? 'text-yellow-600' : 'text-red-600'}`}>
                      {selectedReport.score.toFixed(1)}/10
                    </div>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Accuracy</label>
                    <div className="flex items-end gap-2">
                      <span className="text-2xl font-bold text-indigo-600">
                        {Math.round((selectedReport.questionsCorrect / selectedReport.questionsAsked) * 100)}%
                      </span>
                      <span className="text-sm text-gray-600">({selectedReport.questionsCorrect}/{selectedReport.questionsAsked})</span>
                    </div>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                    View Full Report
                  </button>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Select a report to view details</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
