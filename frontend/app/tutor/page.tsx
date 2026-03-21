'use client';

import { useState, useRef, useEffect } from 'react';
import { useTutorChat } from '@/hooks/useTutorChat';
import { TextbookSelector } from '@/components/tutor/TextbookSelector';
import { LanguageToggle } from '@/components/tutor/LanguageToggle';
import { LowDataToggle } from '@/components/tutor/LowDataToggle';
import { ChatBox } from '@/components/tutor/ChatBox';
import { MessageBubble } from '@/components/tutor/MessageBubble';
import { AnswerCard } from '@/components/tutor/AnswerCard';
import { SampleQuestions } from '@/components/tutor/SampleQuestions';
import { Card, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getSampleQuestionsForTextbook } from '@/constants/sampleQuestions';
import { TEXTBOOKS } from '@/constants/textbooks';

const STORAGE_KEY = 'uploadedFiles_v2';

function isUploadedTextbook(id: string): boolean {
  // Sample textbooks have known IDs like 'class6-science'
  const sampleIds = TEXTBOOKS.map((t) => t.id);
  return !sampleIds.includes(id);
}

export default function TutorPage() {
  const {
    messages,
    answers,
    loading,
    selectedTextbook,
    setSelectedTextbook,
    language,
    setLanguage,
    sendQuestion,
    clearChat,
  } = useTutorChat();

  const [lowDataMode, setLowDataMode] = useState(false);
  const [showDetailed, setShowDetailed] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const isUploadedFile = isUploadedTextbook(selectedTextbook);
  const sampleQuestions = getSampleQuestionsForTextbook(selectedTextbook);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const isEmpty = messages.length === 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-4 gap-6 mb-6">

          {/* Controls Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <Card className="sticky top-24 shadow-premium">
              <CardContent className="pt-6 space-y-6">
                <div>
                  <TextbookSelector selectedId={selectedTextbook} onSelect={setSelectedTextbook} />
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <LanguageToggle language={language} onLanguageChange={setLanguage} />
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <LowDataToggle enabled={lowDataMode} onToggle={setLowDataMode} />
                </div>
                {!isEmpty && (
                  <Button variant="secondary" onClick={clearChat} className="w-full">
                    Clear Chat
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3 space-y-6">
            {isEmpty ? (
              <Card className="shadow-premium">
                <CardContent className="pt-8">
                  <div className="text-center py-20 space-y-8 animate-fade-in">
                    <div className="space-y-4">
                      <div className="text-7xl mb-4">📖</div>
                      <h2 className="text-3xl font-bold text-gray-900">Welcome to EduSarthi!</h2>
                      <p className="text-lg text-gray-600 max-w-xl mx-auto">
                        {isUploadedFile
                          ? 'You have selected an uploaded textbook. Ask me anything — answers come directly from your PDF.'
                          : 'Ask me about anything from your textbook and I\'ll explain it simply. Quick answers or deep dives — you choose.'}
                      </p>
                    </div>

                    {!isUploadedFile && (
                      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
                        <p className="text-sm font-semibold text-gray-900 mb-4">👇 Try asking one of these:</p>
                        <SampleQuestions questions={sampleQuestions} onSelectQuestion={sendQuestion} />
                      </div>
                    )}

                    {isUploadedFile && (
                      <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-xl p-6 border border-amber-200">
                        <p className="text-sm text-amber-900 font-semibold flex items-start gap-2">
                          <span className="text-lg">💡</span>
                          <span>
                            <strong>Tip:</strong> Ask any question about your uploaded PDF.
                            EduSarthi will use Context Pruning to find the most relevant sections
                            and answer directly from your file — no re-processing needed.
                          </span>
                        </p>
                      </div>
                    )}

                    <div className="grid md:grid-cols-3 gap-4 text-left">
                      {[
                        ['💡', 'Ask Anything', 'Concepts, definitions, explanations from your textbook'],
                        ['📍', 'See Sources', 'Every answer links to the exact chapter'],
                        ['⚡', 'Instant Help', 'Answers in seconds, even on slow internet'],
                      ].map(([icon, title, desc], i) => (
                        <div key={i} className="space-y-2">
                          <div className="text-2xl">{icon}</div>
                          <p className="font-semibold text-gray-900 text-sm">{title}</p>
                          <p className="text-xs text-gray-600">{desc}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-6">
                <Card className="shadow-premium">
                  <CardContent className="pt-6 max-h-96 overflow-y-auto space-y-4">
                    {messages.map((message) => (
                      <MessageBubble key={message.id} message={message} />
                    ))}
                    {loading && (
                      <div className="flex justify-start">
                        <div className="bg-gradient-to-r from-blue-100 to-indigo-100 text-gray-800 rounded-lg rounded-bl-none px-4 py-3 shadow-sm">
                          <div className="flex space-x-2">
                            {[0, 0.2, 0.4].map((delay, i) => (
                              <div
                                key={i}
                                className="w-3 h-3 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full animate-pulse-slow"
                                style={{ animationDelay: `${delay}s` }}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </CardContent>
                </Card>

                {answers.length > 0 && (
                  <div className="space-y-4 animate-slide-up">
                    <div className="flex items-center justify-between">
                      <h3 className="font-bold text-lg text-gray-900">Answer</h3>
                      <button
                        onClick={() => setShowDetailed(!showDetailed)}
                        className="text-sm text-blue-600 hover:text-blue-700 font-semibold transition-colors"
                      >
                        {showDetailed ? '−' : '+'} Detailed explanation
                      </button>
                    </div>
                    <AnswerCard answer={answers[answers.length - 1]} showDetailed={showDetailed} />
                  </div>
                )}
              </div>
            )}

            <Card className="shadow-premium sticky bottom-0 z-40">
              <CardContent className="pt-6">
                <ChatBox onSendMessage={sendQuestion} disabled={loading} />
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
