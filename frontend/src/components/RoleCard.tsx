import React from 'react'

export default function RoleCard({role, desc, topics, selected, onSelect}:{role:string,desc:string,topics:string[],selected?:boolean,onSelect?:any}){
  return (
    <div onClick={onSelect} className={`p-4 rounded-lg cursor-pointer transition-transform hover:-translate-y-1 ${selected? 'ring-2 ring-indigo-300 shadow-lg':'bg-white subtle-shadow'}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-lg font-semibold">{role}</div>
          <div className="text-sm text-gray-500">{desc}</div>
        </div>
        <div className={`w-10 h-10 rounded-md flex items-center justify-center ${selected? 'bg-indigo-600 text-white':'bg-gray-100 text-gray-700'}`}>R</div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {topics.map(t=> <div key={t} className="chip">{t}</div>)}
      </div>
    </div>
  )
}
