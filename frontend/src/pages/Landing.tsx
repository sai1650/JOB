import React, { useEffect, useState } from 'react'
import api from '../services/api'
import Button from '../components/Button'

export default function Landing() {
  const [status, setStatus] = useState<string>('loading')

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.get('/api/health')
        setStatus(res.data.status)
      } catch (err) {
        setStatus('unreachable')
      }
    }
    fetch()
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-6 py-24">
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <div className="space-y-8">
            <div className="space-y-4">
              <div className="inline-block px-4 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-semibold">
                ✨ AI-Powered Interview Platform
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold text-slate-900 leading-tight">
                Technical Interviews<br />
                <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">Reimagined</span>
              </h1>
              <p className="text-xl text-slate-600 max-w-lg leading-relaxed">
                Evaluate candidates with resume-aware, role-specific interviews grounded in trusted technical knowledge. Save time, hire smarter.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <a href="/upload" className="w-fit">
                <Button className="px-8 py-3 text-base">Get Started Free</Button>
              </a>
              <a href="#how" className="w-fit">
                <Button variant="ghost" className="px-8 py-3 text-base">Learn More</Button>
              </a>
            </div>

            <div className="flex items-center gap-2 pt-4">
              <div className={`w-3 h-3 rounded-full ${status === 'ok' ? 'bg-green-500' : 'bg-yellow-500'}`} />
              <span className="text-sm text-slate-600">System: <strong className="text-slate-900">{status}</strong></span>
            </div>
          </div>

          {/* Right side - Product Flow Card */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl blur-2xl opacity-10" />
            <div className="relative bg-white/80 backdrop-blur-lg border border-white/20 rounded-2xl p-8 shadow-xl">
              <div className="space-y-1 mb-8">
                <h3 className="text-sm font-semibold text-blue-600">HOW IT WORKS</h3>
                <p className="text-2xl font-bold text-slate-900">Three-Step Process</p>
              </div>
              
              <div className="space-y-6">
                {[
                  { num: '1', title: 'Upload Resume', desc: 'Extract skills & experience automatically' },
                  { num: '2', title: 'Grounded Questions', desc: 'AI generates role-specific questions' },
                  { num: '3', title: 'Smart Evaluation', desc: 'AI scores responses & generates report' }
                ].map((item, idx) => (
                  <div key={idx} className="flex gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold text-sm">
                      {item.num}
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-slate-900">{item.title}</div>
                      <div className="text-sm text-slate-500 mt-1">{item.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section id="how" className="mt-32 space-y-12">
          <div className="text-center space-y-4 max-w-2xl mx-auto">
            <h2 className="text-4xl font-bold text-slate-900">Enterprise Features</h2>
            <p className="text-lg text-slate-600">Built for technical hiring teams who demand quality</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { 
                icon: '📄', 
                title: 'Resume Intelligence', 
                desc: 'AI extracts skills, technologies & experience from resumes automatically'
              },
              { 
                icon: '🎯', 
                title: 'Adaptive Difficulty', 
                desc: 'Questions evolve based on candidate performance in real-time'
              },
              { 
                icon: '📚', 
                title: 'Knowledge Grounding', 
                desc: 'Every question cites trusted role-specific knowledge sources'
              },
              { 
                icon: '📊', 
                title: 'Detailed Reports', 
                desc: 'Comprehensive evaluations with actionable hiring recommendations'
              }
            ].map((feature, idx) => (
              <div key={idx} className="group p-8 bg-white/60 backdrop-blur-lg border border-slate-200 rounded-xl hover:border-blue-300 hover:shadow-lg transition-all duration-300">
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="font-semibold text-slate-900 mb-2 text-lg">{feature.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Stats Section */}
        <section className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { label: 'Time Saved', value: '70%', desc: 'Faster hiring process' },
            { label: 'Accuracy', value: '95%', desc: 'Candidate assessment accuracy' },
            { label: 'Teams Using', value: '500+', desc: 'Technical teams worldwide' }
          ].map((stat, idx) => (
            <div key={idx} className="text-center p-8 rounded-xl bg-white/60 backdrop-blur-lg border border-slate-200">
              <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                {stat.value}
              </div>
              <div className="font-semibold text-slate-900 mt-2">{stat.label}</div>
              <div className="text-sm text-slate-600 mt-1">{stat.desc}</div>
            </div>
          ))}
        </section>

        {/* CTA Section */}
        <section className="mt-32 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12 text-white text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to Transform Your Hiring?</h2>
          <p className="text-lg text-blue-100 mb-8 max-w-2xl mx-auto">
            Start conducting smarter technical interviews today. No credit card required.
          </p>
          <a href="/upload">
            <Button className="px-8 py-3 bg-white text-blue-600 hover:bg-slate-50 text-base font-semibold">
              Begin Your First Interview
            </Button>
          </a>
        </section>
      </div>
    </div>
  )
}
