import { Badge } from '@/components/ui/Badge';
import { TutorAnswer } from '@/types';

interface AnswerCardProps {
  answer: TutorAnswer;
  showDetailed?: boolean;
}

export function AnswerCard({ answer, showDetailed = false }: AnswerCardProps) {
  return (
    <div className="bg-white rounded-2xl border border-blue-100 overflow-hidden shadow-premium hover:shadow-lg transition-shadow animate-slide-up"
      style={{
        boxShadow: '0 4px 6px rgba(37, 99, 235, 0.08), 0 10px 20px rgba(37, 99, 235, 0.12)',
      }}>
      {/* Header with question */}
      <div className="px-6 sm:px-8 py-5 border-b border-blue-50 bg-gradient-to-r from-blue-50 to-indigo-50">
        <p className="text-sm font-semibold text-blue-700 mb-1">Your Question</p>
        <p className="font-bold text-gray-900 text-lg">{answer.question}</p>
      </div>

      {/* Content */}
      <div className="px-6 sm:px-8 py-8 space-y-8">
        {/* Simple Explanation */}
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
              <span className="text-sm font-bold text-white">✓</span>
            </div>
            <h4 className="font-bold text-lg text-gray-900">Simple Explanation</h4>
          </div>
          <p className="text-gray-700 leading-relaxed ml-11 text-base">{answer.simpleExplanation}</p>
        </div>

        {/* Detailed Explanation (if requested) */}
        {showDetailed && (
          <div className="space-y-3 pt-4 border-t-2 border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center">
                <span className="text-sm font-bold text-white">📖</span>
              </div>
              <h4 className="font-bold text-lg text-gray-900">Detailed Explanation</h4>
            </div>
            <p className="text-gray-700 leading-relaxed ml-11 text-base">{answer.detailedExplanation}</p>
          </div>
        )}
      </div>

      {/* Footer with source info */}
      <div className="px-6 sm:px-8 py-5 bg-gradient-to-r from-blue-50 to-indigo-50 border-t border-blue-100 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-semibold text-gray-600">📍 Source:</span>
          <Badge variant="secondary">
            {answer.sourceChapter}
            {answer.pageNumber && ` • Page ${answer.pageNumber}`}
          </Badge>
        </div>
        {answer.language === 'hi' && (
          <Badge variant="primary">हिंदी</Badge>
        )}
      </div>
    </div>
  );
}
