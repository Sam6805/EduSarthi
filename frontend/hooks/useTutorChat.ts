'use client';

import { useState, useCallback, useEffect } from 'react';
import { ChatMessage, TutorAnswer } from '@/types';
import { askQuestion } from '@/lib/mockApi';
import { generateId } from '@/lib/utils';

export function useTutorChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [answers, setAnswers] = useState<TutorAnswer[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedTextbook, setSelectedTextbook] = useState<string>('class6-science');
  const [language, setLanguage] = useState<'en' | 'hi'>('en');

  // Listen for storage changes (when files are uploaded in another component)
  useEffect(() => {
    const handleStorageChange = () => {
      // Just trigger a re-render by accessing localStorage
      localStorage.getItem('uploadedFiles');
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const sendQuestion = useCallback(
    async (question: string) => {
      if (!question.trim()) return;

      // Add user message
      const userMessage: ChatMessage = {
        id: generateId(),
        role: 'user',
        content: question,
        timestamp: new Date(),
        textbookId: selectedTextbook,
      };

      setMessages((prev) => [...prev, userMessage]);
      setLoading(true);

      try {
        // Call mock API
        const answer = await askQuestion(question, selectedTextbook, language);
        setAnswers((prev) => [...prev, answer]);

        // Add assistant message
        const assistantMessage: ChatMessage = {
          id: generateId(),
          role: 'assistant',
          content: answer.simpleExplanation,
          timestamp: new Date(),
          textbookId: selectedTextbook,
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (error) {
        console.error('Error asking question:', error);
      } finally {
        setLoading(false);
      }
    },
    [selectedTextbook, language]
  );

  const clearChat = useCallback(() => {
    setMessages([]);
    setAnswers([]);
  }, []);

  return {
    messages,
    answers,
    loading,
    selectedTextbook,
    setSelectedTextbook,
    language,
    setLanguage,
    sendQuestion,
    clearChat,
  };
}
