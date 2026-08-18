import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Landing from './pages/Landing'
import ResumeUpload from './pages/ResumeUpload'
import RoleSelection from './pages/RoleSelection'
import InterviewSetup from './pages/InterviewSetup'
import InterviewScreen from './pages/InterviewScreen'
import ResultsDashboard from './pages/ResultsDashboard'
import KnowledgeBase from './pages/KnowledgeBase'
import Reports from './pages/Reports'
import Header from './components/Header'

export default function App() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="pt-6">
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<ResumeUpload />} />
          <Route path="/roles" element={<RoleSelection />} />
          <Route path="/setup" element={<InterviewSetup />} />
          <Route path="/interview" element={<InterviewScreen />} />
          <Route path="/results" element={<ResultsDashboard />} />
          <Route path="/knowledge" element={<KnowledgeBase />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </main>
    </div>
  )
}
