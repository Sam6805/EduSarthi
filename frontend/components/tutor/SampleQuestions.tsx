interface SampleQuestionsProps {
  questions: string[];
  onSelectQuestion: (question: string) => void;
  disabled?: boolean;
}

export function SampleQuestions({
  questions,
  onSelectQuestion,
  disabled = false,
}: SampleQuestionsProps) {
  return (
    <div className="mb-6">
      <p className="text-sm font-medium text-gray-700 mb-3">Try asking:</p>
      <div className="flex flex-wrap gap-2">
        {questions.slice(0, 4).map((question, index) => (
          <button
            key={index}
            onClick={() => onSelectQuestion(question)}
            disabled={disabled}
            className="px-3 py-2 text-sm bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {question}
          </button>
        ))}
      </div>
    </div>
  );
}
