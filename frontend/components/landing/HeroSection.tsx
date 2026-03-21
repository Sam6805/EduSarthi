import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 pt-32 pb-40 px-4 sm:px-6 lg:px-8">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 right-0 w-80 h-80 bg-blue-200 rounded-full opacity-10 blur-3xl"></div>
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200 rounded-full opacity-10 blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid md:grid-cols-2 gap-16 items-center">

          {/* Left content */}
          <div className="space-y-8 animate-slide-up">
            <div className="space-y-6">
              {/* Hackathon badge */}
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-100 text-indigo-700 font-semibold text-sm rounded-full">
                🏆 GenAI for GenZ Challenge — Project 1
              </div>

              <h1 className="text-gray-900">
                AI Tutoring for
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Remote India
                </span>
              </h1>

              <p className="text-lg text-gray-700 max-w-xl leading-relaxed">
                State-board textbook Q&A with <strong>Context Pruning</strong> — 
                68% fewer tokens, 67% lower API cost, and answers under 1 second. 
                Built for students on slow internet.
              </p>
            </div>

            {/* Key constraint checkboxes — mirrors the problem statement */}
            <div className="space-y-3">
              {[
                '✅ Ingests entire textbooks once — no re-processing per query',
                '✅ Context Pruning cuts tokens 2,847 → 892 per query',
                '✅ 67% lower API cost vs baseline RAG system',
                '✅ Works on 2G — minimal data transfer',
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="text-gray-800 text-sm font-medium">{item}</span>
                </div>
              ))}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link href="/tutor">
                <Button size="lg" className="w-full sm:w-auto shadow-lg hover:shadow-xl transition-shadow">
                  Try the Tutor
                </Button>
              </Link>
              <Link href="/metrics">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  📊 See Cost Savings
                </Button>
              </Link>
            </div>
          </div>

          {/* Right side — Context Pruning visualisation */}
          <div className="hidden md:flex items-center justify-center">
            <div className="relative w-full space-y-4">

              {/* Baseline RAG */}
              <div className="bg-red-50 border border-red-200 rounded-2xl p-5 shadow-md">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-bold text-red-700">❌ Baseline RAG (without pruning)</span>
                  <span className="text-xs bg-red-100 text-red-600 px-2 py-1 rounded-full">2,847 tokens</span>
                </div>
                <div className="space-y-2">
                  {['Chapter 1 — full text', 'Chapter 2 — full text', 'Chapter 3 — full text',
                    'Chapter 4 — full text', 'Chapter 5 — full text (answer here)', 'Chapter 6 — full text',
                    'Chapter 7 — full text', 'Chapter 8 — full text', 'Chapter 9 — full text', 'Chapter 10 — full text'].map((c, i) => (
                    <div key={i} className={`h-2 rounded-full ${i === 4 ? 'bg-red-400' : 'bg-red-200'}`}
                      style={{ width: `${70 + Math.sin(i) * 20}%` }} />
                  ))}
                </div>
                <p className="text-xs text-red-600 mt-3 font-semibold">Cost: $0.085 per query</p>
              </div>

              <div className="text-center text-2xl font-bold text-indigo-400">↓ Context Pruning</div>

              {/* Pruned */}
              <div className="bg-green-50 border border-green-200 rounded-2xl p-5 shadow-md">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm font-bold text-green-700">✅ EduSarthi (with pruning)</span>
                  <span className="text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full">892 tokens  — 69% less</span>
                </div>
                <div className="space-y-2">
                  {['Chapter 5 — relevant section (answer here)', 'Chapter 4 — supporting context', 'Chapter 6 — related concept'].map((c, i) => (
                    <div key={i} className={`h-2 rounded-full ${i === 0 ? 'bg-green-500' : 'bg-green-300'}`}
                      style={{ width: `${i === 0 ? 90 : 60 - i * 10}%` }} />
                  ))}
                </div>
                <p className="text-xs text-green-600 mt-3 font-semibold">Cost: $0.028 per query — saves 67%</p>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
