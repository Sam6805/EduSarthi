import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export function HeroSection() {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 pt-32 pb-40 px-4 sm:px-6 lg:px-8">
      {/* Decorative background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 right-0 w-80 h-80 bg-blue-200 rounded-full opacity-10 blur-3xl"></div>
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-indigo-200 rounded-full opacity-10 blur-3xl"></div>
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          {/* Left content */}
          <div className="space-y-8 animate-slide-up">
            <div className="space-y-6">
              <div className="inline-block">
                <span className="px-4 py-2 bg-blue-100 text-blue-700 font-semibold text-sm rounded-full">
                  🚀 Powered by AI Context Pruning
                </span>
              </div>
              <h1 className="text-gray-900">
                Smart Learning from Your
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  Textbooks
                </span>
              </h1>
              <p className="text-lg text-gray-700 max-w-xl leading-relaxed">
                Get instant, crystal-clear explanations for any concept in your school textbooks. Built for students in rural India. Works on slow internet.
              </p>
            </div>

            {/* Key benefits */}
            <div className="space-y-3">
              {['Simple, tailored explanations', 'Links to your textbook chapters', 'Works offline-friendly'].map(
                (benefit, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-5 h-5 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-green-600 text-xs font-bold">✓</span>
                    </div>
                    <span className="text-gray-700 font-medium">{benefit}</span>
                  </div>
                )
              )}
            </div>

            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Link href="/tutor">
                <Button size="lg" className="w-full sm:w-auto shadow-lg hover:shadow-xl transition-shadow">
                  Start Learning Now
                </Button>
              </Link>
              <Link href="/metrics">
                <Button variant="outline" size="lg" className="w-full sm:w-auto">
                  See Our Impact
                </Button>
              </Link>
            </div>
          </div>

          {/* Right side - Visual showcase */}
          <div className="hidden md:flex items-center justify-center">
            <div className="relative w-full h-96">
              {/* Card 1 - Question */}
              <div className="absolute top-0 right-0 w-80 bg-white rounded-2xl shadow-premium p-6 border border-gray-100 animate-slide-up"
                style={{ animationDelay: '0.1s' }}>
                <p className="text-sm text-gray-600 font-medium mb-3">Student Question:</p>
                <p className="text-gray-900 font-semibold mb-4">
                  Explain photosynthesis in simple words?
                </p>
                <div className="inline-block px-3 py-1 bg-blue-50 text-blue-700 text-xs font-medium rounded-full">
                  Class 6 Science
                </div>
              </div>

              {/* Card 2 - Answer */}
              <div className="absolute bottom-0 left-0 w-80 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-premium p-6 border border-blue-100 animate-slide-up"
                style={{ animationDelay: '0.2s' }}>
                <p className="text-sm text-blue-700 font-bold mb-3">✨ AI Answer:</p>
                <p className="text-gray-900 text-sm leading-relaxed mb-4">
                  Plants make food using sunlight, water, and air. This process creates oxygen we breathe.
                </p>
                <div className="flex gap-2">
                  <span className="text-xs px-2 py-1 bg-white text-gray-700 rounded border border-gray-200">
                    📖 Chapter 3
                  </span>
                  <span className="text-xs px-2 py-1 bg-white text-gray-700 rounded border border-gray-200">
                    Page 42
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
