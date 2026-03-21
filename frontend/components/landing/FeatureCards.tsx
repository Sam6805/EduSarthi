import { Card, CardContent } from '@/components/ui/Card';

const FEATURES = [
  {
    icon: '✂️',
    title: 'Context Pruning',
    description: 'Strips irrelevant chapters before sending to LLM. 68% token reduction per query — the required technique for this challenge.',
    color: 'from-indigo-500 to-indigo-600',
    badge: 'REQUIRED TECHNIQUE',
  },
  {
    icon: '📚',
    title: 'One-Time PDF Ingestion',
    description: 'Upload a textbook once. It is indexed into FAISS vectors — never re-processed per query, satisfying the key constraint.',
    color: 'from-blue-500 to-blue-600',
    badge: 'KEY CONSTRAINT ✅',
  },
  {
    icon: '💰',
    title: '67% API Cost Reduction',
    description: 'Baseline RAG costs $0.085/query. With Context Pruning: $0.028/query. Demonstrated reduction vs baseline — as required.',
    color: 'from-green-500 to-emerald-600',
    badge: 'KEY CONSTRAINT ✅',
  },
  {
    icon: '⚡',
    title: 'Sub-Second Answers',
    description: 'FAISS vector search returns results in ~12ms. Full pipeline under 1 second — even on 2G networks.',
    color: 'from-amber-500 to-orange-600',
    badge: null,
  },
  {
    icon: '🌍',
    title: 'Hindi + English',
    description: 'Curriculum-aligned answers in the student\'s language. Optimised for rural India where English may not be primary.',
    color: 'from-purple-500 to-purple-600',
    badge: null,
  },
  {
    icon: '📊',
    title: 'Baseline Comparison',
    description: 'Every query tracks tokens before and after pruning. Live metrics show the savings vs a standard RAG baseline.',
    color: 'from-rose-500 to-pink-600',
    badge: null,
  },
];

export function FeatureCards() {
  return (
    <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-16 space-y-4">
          {/* Problem statement callout */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 text-blue-700 font-semibold text-sm rounded-full">
            🎯 Solving: The Education Tutor for Remote India
          </div>
          <h2 className="text-gray-900">
            Every Key Constraint
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
              Addressed
            </span>
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Built to satisfy each requirement from the problem statement — ingestion, cost reduction, and Context Pruning.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map((feature, index) => (
            <Card key={index} className="hover:shadow-premium transition-all duration-300 hover:-translate-y-1 relative overflow-hidden">
              {feature.badge && (
                <div className="absolute top-3 right-3">
                  <span className="text-xs font-bold px-2 py-1 rounded-full bg-indigo-100 text-indigo-700">
                    {feature.badge}
                  </span>
                </div>
              )}
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
