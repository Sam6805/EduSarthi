import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export function CTASection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
      {/* Decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl -ml-32 -mb-32"></div>
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        <h2 className="text-white mb-6">
          Ready to Learn Smarter?
        </h2>
        <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto leading-relaxed">
          Join thousands of students across rural India who are getting better grades with AI tutoring. Start learning from your textbooks today — it only takes seconds to get started.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-10">
          <Link href="/tutor">
            <Button
              size="lg"
              className="bg-white text-blue-600 hover:bg-gray-50 w-full sm:w-auto font-bold shadow-lg hover:shadow-2xl transition-all"
            >
              Start Learning Now
            </Button>
          </Link>
          <Link href="/upload">
            <Button
              variant="outline"
              size="lg"
              className="border-2 border-white text-white hover:bg-white hover:bg-opacity-10 w-full sm:w-auto font-bold"
            >
              Upload Your Textbook
            </Button>
          </Link>
        </div>

        <p className="text-blue-100 text-sm">
          No sign-up required • No internet restrictions • Works on slow networks • 100% private
        </p>
      </div>
    </section>
  );
}
