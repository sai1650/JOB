import React, { useState, useEffect } from 'react'
import api from '../services/api'

export default function KnowledgeBase() {
  const [documents, setDocuments] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDoc, setSelectedDoc] = useState<any>(null)

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const res = await api.get('/api/knowledge-base')
        setDocuments(res.data.documents || [])
      } catch {
        // Mock data if API fails
        setDocuments([
          {id: 1, title: 'Python Best Practices', category: 'Backend', size: '1.2 MB', uploadedAt: '2024-08-10'},
          {id: 2, title: 'System Design Patterns', category: 'Architecture', size: '2.5 MB', uploadedAt: '2024-08-09'},
          {id: 3, title: 'Machine Learning Fundamentals', category: 'AI/ML', size: '3.1 MB', uploadedAt: '2024-08-08'},
        ])
      } finally {
        setLoading(false)
      }
    }
    loadDocuments()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Base</h1>
          <p className="text-gray-600">Manage the documents and sources used for grounding interview questions.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Documents List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Documents</h2>
                <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                  Upload Document
                </button>
              </div>

              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading documents...</div>
              ) : documents.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500 mb-4">No documents uploaded yet</p>
                  <button className="px-4 py-2 border border-indigo-600 text-indigo-600 rounded-md hover:bg-indigo-50 transition">
                    Start by uploading a document
                  </button>
                </div>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc:any) => (
                    <div
                      key={doc.id}
                      onClick={() => setSelectedDoc(doc)}
                      className={`p-4 border rounded-lg cursor-pointer transition ${
                        selectedDoc?.id === doc.id
                          ? 'border-indigo-600 bg-indigo-50'
                          : 'border-gray-200 hover:border-indigo-300 bg-white'
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{doc.title}</h3>
                          <div className="flex gap-4 mt-2 text-sm text-gray-500">
                            <span>{doc.category}</span>
                            <span>{doc.size}</span>
                            <span>Uploaded: {doc.uploadedAt}</span>
                          </div>
                        </div>
                        <button className="text-red-600 hover:text-red-700 text-sm">Delete</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Document Preview */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6 sticky top-8">
              <h3 className="text-lg font-semibold mb-4">Document Details</h3>
              {selectedDoc ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-gray-600">Title</label>
                    <p className="font-medium">{selectedDoc.title}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Category</label>
                    <p className="font-medium">{selectedDoc.category}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Size</label>
                    <p className="font-medium">{selectedDoc.size}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-600">Uploaded</label>
                    <p className="font-medium">{selectedDoc.uploadedAt}</p>
                  </div>
                  <button className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition">
                    View Full Document
                  </button>
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">Select a document to view details</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
