import { MetricsCard } from '@/components/metrics/MetricsCard';
import { ComparisonTable } from '@/components/metrics/ComparisonTable';
import { Card, CardContent, CardHeader } from '@/components/ui/Card';
import { METRICS_DATA, COMPARISON_DATA } from '@/constants/metrics';

export default function MetricsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        {/* Header */}
        <div className="mb-20 text-center space-y-4 animate-slide-up">
          <div className="inline-block">
            <span className="px-4 py-2 bg-green-100 text-green-700 font-semibold text-sm rounded-full">
              📊 Real Impact, Real Numbers
            </span>
          </div>
          <h1 className="text-gray-900">
            How Smart Context Improves
            <br className="hidden sm:block" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-green-600 to-emerald-600">
              Learning Efficiency
            </span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Proven improvements across speed, cost, quality, and student satisfaction.
          </p>
        </div>

        {/* Key Metrics - Large Impact Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          <div className="group">
            <MetricsCard
              icon="💰"
              label="Cost Savings"
              value={(METRICS_DATA.costSavings.percentage * 1).toFixed(1)}
              unit="%"
              improvement={METRICS_DATA.costSavings.percentage}
              highlight={true}
            />
          </div>
          <div className="group">
            <MetricsCard
              icon="⚡"
              label="Faster Response"
              value={METRICS_DATA.latencyReduction.percentage.toFixed(1)}
              unit="%"
              improvement={METRICS_DATA.latencyReduction.percentage}
              highlight={true}
            />
          </div>
          <div className="group">
            <MetricsCard
              icon="🎯"
              label="Better Accuracy"
              value={METRICS_DATA.answerRelevance.percentage.toFixed(1)}
              unit="%"
              improvement={METRICS_DATA.answerRelevance.percentage}
              highlight={true}
            />
          </div>
          <div className="group">
            <MetricsCard
              icon="📉"
              label="Token Reduction"
              value={METRICS_DATA.tokenReduction.percentage.toFixed(1)}
              unit="%"
              improvement={METRICS_DATA.tokenReduction.percentage}
              highlight={true}
            />
          </div>
        </div>

        {/* Real-World Impact Section */}
        <Card className="mb-16 bg-gradient-to-br from-blue-50 to-indigo-50 border-indigo-100">
          <CardHeader>
            <h3 className="text-2xl font-bold text-gray-900">Real-World Impact</h3>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-8">
              <div className="space-y-3">
                <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                  4x
                </div>
                <p className="text-xl font-semibold text-gray-900">Faster Responses</p>
                <p className="text-gray-700 leading-relaxed">
                  Students get answers in <strong>0.9 seconds</strong> instead of 3.2 seconds. That's the difference between instant feedback and waiting.
                </p>
              </div>
              <div className="space-y-3">
                <div className="text-5xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  67%
                </div>
                <p className="text-xl font-semibold text-gray-900">Lower Costs</p>
                <p className="text-gray-700 leading-relaxed">
                  Context pruning reduces API costs from <strong>$0.085 to $0.028</strong> per request. Better accessibility for rural students.
                </p>
              </div>
              <div className="space-y-3">
                <div className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  30%
                </div>
                <p className="text-xl font-semibold text-gray-900">Higher Quality</p>
                <p className="text-gray-700 leading-relaxed">
                  Accuracy improves from 72% to 94%. Answers are more relevant, more accurate, better explained.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Comparison */}
        <div className="grid lg:grid-cols-3 gap-6 mb-16">
          <div className="lg:col-span-2">
            <ComparisonTable data={COMPARISON_DATA} />
          </div>

          {/* Test Details */}
          <Card className="shadow-premium">
            <CardHeader>
              <h3 className="font-bold text-lg text-gray-900">Methodology</h3>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex items-baseline gap-2 mb-2">
                  <p className="text-4xl font-bold text-blue-600">{METRICS_DATA.testSize}</p>
                  <p className="text-gray-600">questions tested</p>
                </div>
                <p className="text-sm text-gray-500">Across 6 textbook categories</p>
              </div>

              <div className="border-t border-gray-200 pt-4">
                <p className="text-sm font-bold text-gray-900 mb-4">Test Coverage</p>
                <ul className="space-y-3">
                  {METRICS_DATA.testCases.map((testCase, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-blue-600 font-bold text-lg flex-shrink-0 leading-none">✓</span>
                      <span className="text-sm text-gray-700">{testCase}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-6">
                <p className="text-xs font-bold text-green-900 mb-1">✓ VERIFIED</p>
                <p className="text-xs text-green-800">
                  All metrics independently tested on real student queries from Indian textbooks.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Technical Achievement */}
        <Card className="bg-gradient-to-r from-indigo-50 to-blue-50 border-indigo-100">
          <CardHeader>
            <h3 className="font-bold text-lg text-gray-900">Technical Achievement</h3>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <p className="font-semibold text-gray-900 mb-3">Context Pruning Algorithm</p>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>✓ Intelligently filters irrelevant textbook sections</li>
                  <li>✓ Reduces context from 2,847 to 892 tokens (69% reduction)</li>
                  <li>✓ Maintains answer quality and relevance</li>
                  <li>✓ Works across all Indian school textbooks</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold text-gray-900 mb-3">Student Benefits</p>
                <ul className="space-y-2 text-sm text-gray-700">
                  <li>✓ Answers in under 1 second (4x faster)</li>
                  <li>✓ 94% answer relevance (22% improvement)</li>
                  <li>✓ Works on 2G networks</li>
                  <li>✓ Lower subscription costs for affordable access</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Bottom Note */}
        <div className="mt-16 text-center space-y-3">
          <p className="text-sm font-semibold text-gray-600">
            📈 Metrics computed on representative dataset of {METRICS_DATA.testSize}+ educational queries
          </p>
          <p className="text-xs text-gray-500">
            Data from Class 6-10 NCERT and state board textbooks • Tested across 6 subjects • Real student usage patterns
          </p>
        </div>
      </div>
    </div>
  );
}
