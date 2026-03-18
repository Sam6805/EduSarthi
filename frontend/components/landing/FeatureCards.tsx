import { Card, CardContent } from '@/components/ui/Card';

const FEATURES = [
  {
    icon: '📚',
    title: 'Textbook Aligned',
    description: 'Every answer links to exact chapters and page numbers from your textbook.',
    color: 'from-blue-500 to-blue-600',
  },
  {
    icon: '💡',
    title: 'Simple to Complex',
    description: 'Get simple explanations first, then dive deep with detailed insights.',
    color: 'from-indigo-500 to-indigo-600',
  },
  {
    icon: '🌍',
    title: 'In Your Language',
    description: 'Learn in English or Hindi. Explanations matched to your comfort level.',
    color: 'from-purple-500 to-purple-600',
  },
  {
    icon: '⚡',
    title: 'Lightning Fast',
    description: 'Get answers in seconds, even on 2G networks. Optimized for low bandwidth.',
    color: 'from-amber-500 to-orange-600',
  },
  {
    icon: '✨',
    title: 'Smart Context',
    description: 'AI finds the most relevant sections automatically. No irrelevant info.',
    color: 'from-green-500 to-emerald-600',
  },
  {
    icon: '🔒',
    title: 'Privacy First',
    description: 'Your data stays private. No tracking. No ads. Just learning.',
    color: 'from-rose-500 to-pink-600',
  },
];

export function FeatureCards() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          <h2 className="text-gray-900">
            Built for Students,
            <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              Optimized for India
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Everything you need to learn better from your textbooks, designed with rural India in mind.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((feature, index) => (
            <Card key={index} className="hover:shadow-premium transition-all duration-300 hover:-translate-y-1">
              <CardContent className="pt-8 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="text-5xl">{feature.icon}</div>
                  <div className={`w-1 h-12 bg-gradient-to-b ${feature.color} rounded-full`}></div>
                </div>
                <div>
                  <h3 className="font-bold text-lg text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
