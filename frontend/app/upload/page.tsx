'use client';

import { useState, useEffect } from 'react';
import { UploadTextbook } from '@/components/upload/UploadTextbook';
import { UploadedFilesList } from '@/components/upload/UploadedFilesList';
import { UPLOADED_TEXTBOOKS } from '@/constants/textbooks';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { UploadedFile } from '@/types';

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>(UPLOADED_TEXTBOOKS);

  // Load uploaded files from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('uploadedFiles');
    if (stored) {
      try {
        const parsed = JSON.parse(stored).map((file: any) => ({
          ...file,
          uploadedAt: new Date(file.uploadedAt),
        }));
        setUploadedFiles([...UPLOADED_TEXTBOOKS, ...parsed]);
      } catch (error) {
        console.error('Failed to load uploaded files:', error);
      }
    } else {
      setUploadedFiles(UPLOADED_TEXTBOOKS);
    }
  }, []);

  const handleFileSelect = async (file: File) => {
    setUploading(true);
    // Simulate upload processing
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Create new uploaded file
    const newFile: UploadedFile = {
      id: `uploaded-${Math.random().toString(36).substr(2, 9)}`,
      filename: file.name,
      uploadedAt: new Date(),
      size: file.size / (1024 * 1024), // Convert to MB
      chapters: Math.floor(Math.random() * 20) + 10,
    };

    // Add to list
    setUploadedFiles((prev) => [...prev, newFile]);

    // Save to localStorage (only custom uploads, not defaults)
    const customUploads = uploadedFiles.filter((f) => f.id.startsWith('uploaded-'));
    const newCustomUploads = [...customUploads, newFile];
    localStorage.setItem(
      'uploadedFiles',
      JSON.stringify(newCustomUploads.map((f) => ({ ...f, uploadedAt: f.uploadedAt.toISOString() })))
    );

    setUploading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 via-white to-orange-50">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        {/* Header */}
        <div className="mb-16 space-y-4 animate-slide-up">
          <div className="inline-block">
            <span className="px-4 py-2 bg-amber-100 text-amber-700 font-semibold text-sm rounded-full">
              📚 Manage Your Textbooks
            </span>
          </div>
          <h1 className="text-gray-900">
            Upload Your Textbooks and Start Learning
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl">
            Add your school PDFs in seconds. We'll index them and make every concept instantly searchable.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 mb-16">
          {/* Upload card */}
          <div className="lg:col-span-2 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Add New Textbook</h2>
            <UploadTextbook onFileSelect={handleFileSelect} loading={uploading} />
            <Card className="bg-green-50 border-green-100">
              <CardContent className="pt-6">
                <p className="text-sm text-green-900 font-semibold flex items-start gap-3">
                  <span className="text-lg flex-shrink-0">✓</span>
                  <span>
                    <strong>Upload successful!</strong> Your textbook will be processed in minutes. You can then start asking questions about any concept.
                  </span>
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Info card */}
          <div className="lg:col-span-1 space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">Upload Tips</h2>
            <Card>
              <CardContent className="pt-6 space-y-6 text-sm text-gray-700">
                <div>
                  <p className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <span className="text-lg">✓</span> What works best
                  </p>
                  <ul className="space-y-2 text-gray-700 ml-8">
                    <li>• Clear, readable PDFs</li>
                    <li>• Textbooks (NCERT / State board)</li>
                    <li>• Complete chapters</li>
                    <li>• Under 100MB</li>
                  </ul>
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <p className="font-bold text-gray-900 mb-3 flex items-center gap-2">
                    <span className="text-lg">✗</span> Not supported
                  </p>
                  <ul className="space-y-2 text-gray-700 ml-8">
                    <li>• Handwritten or blurry PDFs</li>
                    <li>• Unknown languages</li>
                    <li>• Sample papers only</li>
                    <li>• Copyrighted without permission</li>
                  </ul>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Uploaded files */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Your Textbooks <span className="text-base font-normal text-gray-500">({uploadedFiles.length})</span>
          </h2>
          <UploadedFilesList files={uploadedFiles} />

          {uploadedFiles.length === 0 && (
            <Card>
              <CardContent className="pt-12 text-center py-16">
                <div className="text-5xl mb-4">📖</div>
                <p className="text-lg text-gray-600">No textbooks uploaded yet.</p>
                <p className="text-gray-500">Upload your first PDF to get started with smart learning!</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
