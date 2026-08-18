import React from 'react'

export default function ScoreCircle({score}:{score:number}){
  const pct = Math.round((score||0)*100)
  return (
    <div className="flex items-center gap-4">
      <div className="w-20 h-20 rounded-full flex items-center justify-center bg-gradient-to-br from-[#3b4cca] to-[#7c3aed] text-white text-xl font-bold">{pct}%</div>
    </div>
  )
}
