import { Card, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { UploadedTextbook } from '@/types';
import { formatDate, formatFileSize } from '@/lib/utils';

interface UploadedFilesListProps {
  files: UploadedTextbook[];
}

export function UploadedFilesList({ files }: UploadedFilesListProps) {
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
      {files.map((file, index) => (
        <Card
          key={file.id}
          className="hover:shadow-premium transition-all duration-300 hover:-translate-y-0.5"
          style={{
            animationDelay: `${index * 0.05}s`,
            animation: 'fadeIn 0.5s ease-out',
          }}
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
              <div className="flex-shrink-0">
                <Badge variant="success" className="whitespace-nowrap">
                  ✓ Ready to use
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
