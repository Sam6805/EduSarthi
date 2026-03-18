interface LanguageToggleProps {
  language: 'en' | 'hi';
  onLanguageChange: (lang: 'en' | 'hi') => void;
}

export function LanguageToggle({ language, onLanguageChange }: LanguageToggleProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
      <div className="flex gap-2">
        <button
          onClick={() => onLanguageChange('en')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            language === 'en'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
          }`}
        >
          English
        </button>
        <button
          onClick={() => onLanguageChange('hi')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            language === 'hi'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-200 text-gray-900 hover:bg-gray-300'
          }`}
        >
          हिंदी
        </button>
      </div>
    </div>
  );
}
