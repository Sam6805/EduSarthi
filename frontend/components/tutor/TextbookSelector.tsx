'use client';

import { useEffect, useState } from 'react';
import { TEXTBOOKS } from '@/constants/textbooks';

interface UploadedEntry {
  id: string;
  filename: string;
  chapters: number;
  textbook_id?: string;
}

interface TextbookSelectorProps {
  selectedId: string;
  onSelect: (id: string) => void;
}

const STORAGE_KEY = 'uploadedFiles_v2'; // must match upload/page.tsx

function loadUploaded(): UploadedEntry[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    return JSON.parse(raw) as UploadedEntry[];
  } catch {
    return [];
  }
}

export function TextbookSelector({ selectedId, onSelect }: TextbookSelectorProps) {
  const [uploaded, setUploaded] = useState<UploadedEntry[]>([]);

  const refresh = () => setUploaded(loadUploaded());

  useEffect(() => {
    // Load on mount
    refresh();

    // Refresh whenever upload page saves new files
    window.addEventListener('storage', refresh);
    return () => window.removeEventListener('storage', refresh);
  }, []);

  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">Select Textbook</label>
      <select
        value={selectedId}
        onChange={(e) => onSelect(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      >
        <optgroup label="Sample Textbooks">
          {TEXTBOOKS.map((tb) => (
            <option key={tb.id} value={tb.id}>
              {tb.name} ({tb.chapters} chapters)
            </option>
          ))}
        </optgroup>

        {uploaded.length > 0 && (
          <optgroup label="Your Uploads">
            {uploaded.map((file) => {
              // Use backend textbook_id for querying if available, else fallback to file.id
              const queryId = file.textbook_id || file.id;
              const displayName = file.filename
                .replace(/\.pdf$/i, '')
                .replace(/_/g, ' ')
                .replace(/-/g, ' ');
              return (
                <option key={file.id} value={queryId}>
                  📄 {displayName} ({file.chapters} chapters)
                </option>
              );
            })}
          </optgroup>
        )}
      </select>
    </div>
  );
}
