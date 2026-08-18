import React from 'react'

export default function Button({children, onClick, variant='primary', className='', disabled=false}:{children:any,onClick?:any,variant?:string,className?:string,disabled?:boolean}){
  const base = variant==='primary'? 'btn-primary':'btn-ghost'
  return (
    <button onClick={onClick} disabled={disabled} className={`${base} ${className} disabled:opacity-60`}>
      {children}
    </button>
  )
}
