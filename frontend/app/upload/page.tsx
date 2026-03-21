'use client';

import { useState, useEffect } from 'react';
import { UploadTextbook } from '@/components/upload/UploadTextbook';
import { UploadedFilesList } from '@/components/upload/UploadedFilesList';
import { Card, CardContent } from '@/components/ui/Card';
import { UploadedFile } from '@/types';
import { deleteTextbook } from '@/lib/mockApi';

const STORAGE_KEY = 'uploadedFiles_v2';

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [deleteStatus, setDeleteStatus] = useState<string | null>(null);

  useEffect(() => {
    // Clean up old storage key to prevent stale duplicates in selector
    localStorage.removeItem('uploadedFiles');

    // Load from new key
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored).map((f: any) => ({
          ...f,
          uploadedAt: new Date(f.uploadedAt),
        }));
        setUploadedFiles(parsed);
      } catch {}
    }
  }, []);

  const saveToStorage = (files: UploadedFile[]) => {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify(files.map((f) => ({ ...f, uploadedAt: f.uploadedAt.toISOString() })))
    );
    window.dispatchEvent(new Event('storage'));
  };

  const handleFileSelect = async (file: File) => {
    setUploading(true);
    try {
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const formData = new FormData();
      formData.append('file', file);
      formData.append('textbook_name', file.name.replace('.pdf', ''));
      formData.append('class_level', 'Auto-detected');
      formData.append('subject', 'General');

      let realChapters = 1;
      let backendId: string | undefined;

      try {
        const response = await fetch(`${backendUrl}/api/ingest/upload`, {
          method: 'POST',
          body: formData,
        });
        if (response.ok) {
          const data = await response.json();
          realChapters = data.chapters_extracted ?? 1;
          backendId = data.textbook_id;
          console.log(`Upload success: ${realChapters} chapters, ID: ${backendId}`);
        }
      } catch (err) {
        console.warn('Backend upload failed:', err);
      }

      const newFile: UploadedFile = {
        id: backendId || `uploaded-${Math.random().toString(36).substr(2, 9)}`,
        filename: file.name,
        uploadedAt: new Date(),
        size: file.size / (1024 * 1024),
        chapters: realChapters,
        textbook_id: backendId,
      };

      const updated = [...uploadedFiles, newFile];
      setUploadedFiles(updated);
      saveToStorage(updated);
    } catch (err) {
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (fileId: string) => {
    const file = uploadedFiles.find((f) => f.id === fileId);
    if (!file) return;

    const confirmed = window.confirm(`Delete "${file.filename}"? This cannot be undone.`);
    if (!confirmed) return;

    setDeleteStatus('Deleting...');
    const idToDelete = file.textbook_id || file.id;
    if (idToDelete) {
      const ok = await deleteTextbook(idToDelete);
      if (!ok) console.warn('Backend delete failed – removing from UI only');
    }

    const updated = uploadedFiles.filter((f) => f.id !== fileId);
    setUploadedFiles(updated);
    saveToStorage(updated);
    setDeleteStatus(`"${file.filename}" deleted`);
    setTimeout(() => setDeleteStatus(null), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">

        <div className="mb-16 space-y-4 animate-slide-up">
          <div className="inline-block">
            <span className="px-4 py-2 bg-amber-100 text-amber-700 font-semibold text-sm rounded-full">
              📚 Manage Your Textbooks
            </span>
          </div>
          <h1 className="text-gray-900">Upload Your Textbooks and Start Learning</h1>
          <p className="text-xl text-gray-600 max-w-2xl">
            Add your school PDFs in seconds. Indexed once into FAISS — no re-processing per query.
          </p>
        </div>

        {deleteStatus && (
          <div className="mb-6 px-4 py-3 bg-red-50 border border-red-200 text-red-800 rounded-lg text-sm">
            {deleteStatus}
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Add New Textbook</h2>
            <UploadTextbook onFileSelect={handleFileSelect} loading={uploading} />
            <Card className="bg-green-50 border-green-100">
              <CardContent className="pt-6">
                <p className="text-sm text-green-900 font-semibold flex items-start gap-3">
                  <span className="text-lg flex-shrink-0">✓</span>
                  <span>
                    <strong>One-time processing:</strong> Your textbook is extracted, chunked, and
                    indexed into FAISS. All future questions are answered from the index — no re-processing.
                  </span>
                </p>
              </CardContent>
            </Card>
          </div>

          <div className="lg:col-span-1 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Upload Tips</h2>
            <Card>
              <CardContent className="pt-6 space-y-6 text-sm text-gray-700">
                <div>
                  <p className="font-bold text-gray-900 mb-3">✓ What works best</p>
                  <ul className="space-y-2 ml-4">
                    <li>• Clear, text-based PDFs</li>
                    <li>• NCERT / State board textbooks</li>
                    <li>• Complete chapters</li>
                    <li>• Under 100MB</li>
                  </ul>
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <p className="font-bold text-gray-900 mb-3">✗ Not supported</p>
                  <ul className="space-y-2 ml-4">
                    <li>• Scanned / image PDFs</li>
                    <li>• Handwritten notes</li>
                    <li>• Over 100MB</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Your Textbooks{' '}
            <span className="text-base font-normal text-gray-500">({uploadedFiles.length})</span>
          </h2>
          <UploadedFilesList files={uploadedFiles} onDelete={handleDelete} />
        </div>

      </div>
    </div>
  );
}
