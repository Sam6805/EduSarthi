import { Badge } from '@/components/ui/Badge';

interface SourceBadgeProps {
  chapter: string;
  pageNumber?: number;
}

export function SourceBadge({ chapter, pageNumber }: SourceBadgeProps) {
  return (
    <Badge variant="secondary">
      📍 {chapter}
      {pageNumber && ` • Page ${pageNumber}`}
    </Badge>
  );
}
