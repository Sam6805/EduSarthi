import Link from 'next/link';
import { Button } from '@/components/ui/Button';

export function CTASection() {
  return (
    <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 right-0 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl -mr-32 -mt-32"></div>
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-white opacity-10 rounded-full blur-3xl -ml-32 -mb-32"></div>
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10 space-y-8">

        {/* Problem statement summary */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-white bg-opacity-20 text-white font-semibold text-sm rounded-full">
          🏆 GenAI for GenZ — Project 1: The Education Tutor for Remote India
        </div>

        <h2 className="text-white">EduSarthi Solves It</h2>

        {/* Constraint checklist */}
        <div className="grid sm:grid-cols-2 gap-4 text-left max-w-2xl mx-auto">
          {[
            ['✅', 'Ingests large PDFs once — FAISS indexed, never re-processed'],
            ['✅', '67% API cost reduction vs baseline RAG (measured)'],
            ['✅', 'Context Pruning strips irrelevant chapters before LLM call'],
            ['✅', 'Minimal data transfer — works on 2G networks'],
          ].map(([icon, text], i) => (
            <div key={i} className="flex items-start gap-3 bg-white bg-opacity-10 rounded-xl px-4 py-3">
              <span className="text-lg flex-shrink-0">{icon}</span>
              <span className="text-sm text-white font-medium">{text}</span>
            </div>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/tutor">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-50 w-full sm:w-auto font-bold shadow-lg">
              Try the Tutor
            </Button>
          </Link>
          <Link href="/metrics">
            <Button variant="outline" size="lg"
              className="border-2 border-white text-white hover:bg-white hover:bg-opacity-10 w-full sm:w-auto font-bold">
              📊 View Cost Metrics
            </Button>
          </Link>
          <Link href="/upload">
            <Button variant="outline" size="lg"
              className="border-2 border-white text-white hover:bg-white hover:bg-opacity-10 w-full sm:w-auto font-bold">
              📚 Upload Textbook
            </Button>
          </Link>
        </div>

        <p className="text-blue-100 text-sm">
          Gemini 1.5 Flash · FAISS vector search · Context Pruning · Hindi + English
        </p>
      </div>
    </section>
  );
}
