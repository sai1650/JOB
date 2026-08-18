import React, { useState, useEffect } from 'react'
import api from '../services/api'
import { useNavigate } from 'react-router-dom'
import RoleCard from '../components/RoleCard'
import Button from '../components/Button'

export default function RoleSelection() {
  const [roles, setRoles] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<string | null>(null)
  const navigate = useNavigate()

  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/api/roles')
        setRoles(res.data.roles || [])
      } catch {
        setRoles([
          {id:'ml', title:'AI/ML Engineer', desc:'Modeling, deep learning, and ML infra', topics:['ML','NLP','Deep Learning']},
          {id:'backend', title:'Backend Engineer', desc:'APIs, services, and systems', topics:['APIs','Databases','Scaling']},
        ])
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const onNext = () => {
    if (!selected) return
    localStorage.setItem('role', selected)
    navigate('/setup')
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-2xl font-semibold mb-2">Choose Your Interview Role</h2>
        <p className="text-gray-600 mb-6">The interview adapts to the skills and knowledge expected for your selected role.</p>

        {loading ? <div>Loading roles…</div> : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {roles.map((r:any)=> (
              <div key={r.id || r.name} onClick={()=> setSelected(r.name || r.id)}>
                <RoleCard role={r.name||r.title||'Role'} desc={r.description||r.desc||''} topics={r.core_topics||r.topics||['Core skills']} selected={selected===(r.name||r.id)} onSelect={()=> setSelected(r.name || r.id)} />
              </div>
            ))}
          </div>
        )}

        <div className="flex justify-end">
          <Button disabled={!selected} onClick={onNext}>Continue</Button>
        </div>
      </div>
    </div>
  )
}
