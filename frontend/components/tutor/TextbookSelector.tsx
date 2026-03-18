import { useEffect, useState } from 'react';
import { TEXTBOOKS, UPLOADED_TEXTBOOKS } from '@/constants/textbooks';

interface TextbookSelectorProps {
  selectedId: string;
  onSelect: (id: string) => void;
}

export function TextbookSelector({ selectedId, onSelect }: TextbookSelectorProps) {
  const [allTextbooks, setAllTextbooks] = useState(TEXTBOOKS);

  useEffect(() => {
    // Load uploaded files from localStorage
    const stored = localStorage.getItem('uploadedFiles');
    if (stored) {
      try {
        const uploadedFiles = JSON.parse(stored);
        // Combine sample textbooks with uploaded files
        setAllTextbooks([
          ...TEXTBOOKS,
          ...uploadedFiles.map((file: any) => ({
            id: file.id,
            name: file.filename.replace('.pdf', '').replace(/_/g, ' '),
            chapters: file.chapters,
            isUploaded: true,
          })),
        ]);
      } catch (error) {
        console.error('Failed to load uploaded files:', error);
        setAllTextbooks(TEXTBOOKS);
      }
    } else {
      setAllTextbooks(TEXTBOOKS);
    }
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
          {TEXTBOOKS.map((textbook) => (
            <option key={textbook.id} value={textbook.id}>
              {textbook.name} ({textbook.chapters} chapters)
            </option>
          ))}
        </optgroup>
        {allTextbooks.some((t) => 'isUploaded' in t) && (
          <optgroup label="Your Uploads">
            {allTextbooks
              .filter((t) => 'isUploaded' in t)
              .map((textbook) => (
                <option key={textbook.id} value={textbook.id}>
                  📄 {textbook.name} ({textbook.chapters} chapters)
                </option>
              ))}
          </optgroup>
        )}
      </select>
    </div>
  );
}
