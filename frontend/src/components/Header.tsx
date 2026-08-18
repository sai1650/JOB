import React from 'react'
import { Link, useLocation } from 'react-router-dom'

function Logo(){
  return (
    <div className="flex items-center gap-3">
      <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-gradient-to-br from-[#3b4cca] to-[#7c3aed] text-white font-bold">AI</div>
      <div className="text-lg font-semibold">AI Interviewer</div>
    </div>
  )
}

export default function Header(){
  const loc = useLocation()
  const nav = [
    {to: '/', label: 'Dashboard'},
    {to: '/interview', label: 'Interviews'},
    {to: '/roles', label: 'Candidates / Roles'},
    {to: '/knowledge', label: 'Knowledge Base'},
    {to: '/reports', label: 'Reports'},
  ]
  return (
    <header className="w-full bg-white/60 glass-card subtle-shadow">
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        <Logo />
        <nav className="hidden md:flex items-center gap-6">
          {nav.map(n=> (
            <Link key={n.to} to={n.to} className={`text-sm ${loc.pathname===n.to? 'text-indigo-600 font-semibold':''} text-gray-700`}>{n.label}</Link>
          ))}
        </nav>
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-3">
            <div className="text-sm text-gray-600">John Doe</div>
            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-sm">JD</div>
          </div>
        </div>
      </div>
    </header>
  )
}
