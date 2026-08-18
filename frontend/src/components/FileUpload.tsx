import React, { useState } from 'react'

type FileUploadProps = {
  onChange: (f: File) => void
  onError?: (message: string | null) => void
  accept?: string
  children?: React.ReactNode
  disabled?: boolean
  validateFile?: (f: File) => string | null
}

export default function FileUpload({
  onChange,
  onError,
  accept,
  children,
  disabled = false,
  validateFile,
}: FileUploadProps) {
  const [isDragging, setIsDragging] = useState(false)

  const handleFile = (file?: File) => {
    if (!file || disabled) return
    const validationError = validateFile ? validateFile(file) : null
    if (validationError) {
      onError?.(validationError)
      return
    }
    onError?.(null)
    onChange(file)
  }

  const onDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault()
    if (disabled) return
    setIsDragging(true)
  }

  const onDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const onDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault()
    if (disabled) return
    setIsDragging(false)
    handleFile(e.dataTransfer.files?.[0])
  }

  return (
    <label
      className={`block p-8 border-2 border-dashed rounded-lg text-center bg-white subtle-shadow transition ${
        disabled ? 'cursor-not-allowed opacity-80' : 'cursor-pointer hover:shadow-md'
      } ${isDragging ? 'border-blue-400' : ''}`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      <input
        type="file"
        accept={accept}
        disabled={disabled}
        onChange={(e) => handleFile(e.target.files?.[0])}
        className="hidden"
      />
      <div className="mx-auto max-w-xs">{children}</div>
    </label>
  )
}
