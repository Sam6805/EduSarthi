import { Card, CardContent } from '@/components/ui/Card';

const WORKFLOW_STEPS = [
  {
    number: '1',
    icon: '📚',
    title: 'Select / Upload',
    description: 'Choose from available textbooks or upload your own PDF.',
  },
  {
    number: '2',
    icon: '💭',
    title: 'Ask Question',
    description: 'Type or ask any concept. Our AI listens and understands.',
  },
  {
    number: '3',
    icon: '🎯',
    title: 'Smart Retrieval',
    description: 'Finds relevant chapters in milliseconds using context pruning.',
  },
  {
    number: '4',
    icon: '✨',
    title: 'Get Answer',
    description: 'Clear explanation + source chapter linked to your textbook.',
  },
];

export function WorkflowSection() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-gray-900">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Four simple steps to instant learning
          </p>
        </div>

        <div className="grid md:grid-cols-4 gap-6">
          {WORKFLOW_STEPS.map((step, index) => (
            <div key={index} className="relative group">
              <Card className="h-full hover:shadow-premium transition-all duration-300">
                <CardContent className="pt-8 space-y-4 text-center">
                  <div className="text-5xl mb-2">{step.icon}</div>
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center mx-auto">
                    <span className="text-white font-bold text-lg">{step.number}</span>
                  </div>
                  <h3 className="font-bold text-lg text-gray-900">{step.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{step.description}</p>
                </CardContent>
              </Card>

              {/* Arrow connecting steps */}
              {index < WORKFLOW_STEPS.length - 1 && (
                <div className="hidden md:flex absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                  <div className="text-3xl text-gray-300 font-bold">→</div>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Bottom highlight */}
        <div className="mt-16 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 text-center border border-blue-100">
          <p className="text-lg font-semibold text-gray-900 mb-2">
            ⚡ The entire process takes less than 2 seconds
          </p>
          <p className="text-gray-600">
            Thanks to intelligent context pruning, you get accurate answers instantly, even on slow internet.
          </p>
        </div>
      </div>
    </section>
  );
}
