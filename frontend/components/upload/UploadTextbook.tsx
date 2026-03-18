'use client';

import { useRef } from 'react';
import { Card, CardContent } from '@/components/ui/Card';

interface UploadTextbookProps {
  onFileSelect: (file: File) => void;
  loading?: boolean;
}

export function UploadTextbook({ onFileSelect, loading = false }: UploadTextbookProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  const handleClick = () => {
    inputRef.current?.click();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      const file = files[0];
      if (file.type === 'application/pdf') {
        onFileSelect(file);
      }
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      onFileSelect(files[0]);
    }
  };

  return (
    <Card className="shadow-premium">
      <CardContent className="pt-8">
        <div
          onClick={handleClick}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-300 ${
            loading
              ? 'border-blue-400 bg-blue-50'
              : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            className="hidden"
            disabled={loading}
          />

          <div className="space-y-4">
            <div className="text-6xl font-bold">
              {loading ? '⏳' : '📄'}
            </div>
            <h3 className="font-bold text-lg text-gray-900">
              {loading ? 'Processing your PDF...' : 'Drop your textbook here'}
            </h3>
            <p className="text-gray-600">
              {loading
                ? 'Indexing chapters and preparing for instant answers'
                : 'Drag and drop a PDF, or click to browse your files'}
            </p>
            {!loading && (
              <div className="pt-3">
                <p className="text-xs text-gray-500 font-medium">
                  📋 PDF only • Up to 100MB • Typical processing: 2-5 minutes
                </p>
              </div>
            )}
            {loading && (
              <div className="flex justify-center gap-1 pt-4">
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-slow"></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-slow" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse-slow" style={{ animationDelay: '0.4s' }}></div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
