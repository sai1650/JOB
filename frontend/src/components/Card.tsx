import React from 'react'

export default function Card({children, className=''}:{children:any, className?:string}){
  return (
    <div className={`p-4 bg-white rounded-lg subtle-shadow ${className}`}>
      {children}
    </div>
  )
}
