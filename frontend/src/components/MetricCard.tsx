import React from 'react'

export default function MetricCard({label, value, hint}:{label:string,value:any,hint?:string}){
  return (
    <div className="p-4 bg-white rounded-lg subtle-shadow">
      <div className="text-sm text-gray-500">{label}</div>
      <div className="text-2xl font-bold mt-1">{value}</div>
      {hint && <div className="text-xs text-gray-400 mt-1">{hint}</div>}
    </div>
  )
}
