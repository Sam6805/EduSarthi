'use client';

import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { UploadedFile } from '@/types';
import { formatDate, formatFileSize } from '@/lib/utils';

interface UploadedFilesListProps {
  files: UploadedFile[];
  onDelete?: (fileId: string) => void;
}

export function UploadedFilesList({ files, onDelete }: UploadedFilesListProps) {
  if (files.length === 0) {
    return (
      <Card>
        <CardContent className="pt-8 text-center py-12">
          <p className="text-gray-600">No textbooks uploaded yet. Upload one to get started!</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {files.map((file) => (
        <Card
          key={file.id}
          className="hover:shadow-premium transition-all duration-300 hover:-translate-y-0.5"
        >
          <CardContent className="py-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 flex items-start gap-4">
                <div className="text-4xl flex-shrink-0 pt-1">📕</div>
                <div className="flex-1 min-w-0">
                  <p className="font-bold text-gray-900 text-lg truncate">{file.filename}</p>
                  <div className="flex flex-wrap gap-4 mt-2">
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold text-gray-900">{file.chapters}</span> chapters
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="font-semibold text-gray-900">{formatFileSize(file.size)}</span>
                    </p>
                    <p className="text-sm text-gray-500">
                      Added {formatDate(file.uploadedAt)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Right side: badge + delete */}
              <div className="flex flex-col items-end gap-2 flex-shrink-0">
                <Badge variant="success" className="whitespace-nowrap">
                  ✓ Ready to use
                </Badge>
                {onDelete && (
                  <button
                    onClick={() => onDelete(file.id)}
                    className="text-xs text-red-500 hover:text-red-700 hover:underline transition-colors"
                    title="Delete this textbook"
                  >
                    🗑 Delete
                  </button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
