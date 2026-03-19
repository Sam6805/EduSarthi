"""LLM-based answer generation service."""

from typing import Dict, Any, Optional
import json

from app.utils.helpers import setup_logger
from app.config import LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, LLM_TEMPERATURE

logger = setup_logger(__name__)


class LLMGenerator:
    """Generate student-friendly answers using an LLM."""
    
    def __init__(self, provider: str = LLM_PROVIDER, api_key: str = LLM_API_KEY):
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = LLM_MODEL
        self.temperature = LLM_TEMPERATURE
    
    def generate_answer(self,
                       question: str,
                       context: str,
                       language: str = "en",
                       simple: bool = True,
                       detailed: bool = False) -> Dict[str, Any]:
        """
        Generate an answer based on question and context.
        
        Returns:
            {
                "simple_answer": str,
                "detailed_answer": str (optional),
                "source_info": {...}
            }
        """
        if self.provider == "mock":
            return self._generate_mock_answer(question, context, language, simple, detailed)
        elif self.provider == "openai":
            return self._generate_openai_answer(question, context, language, simple, detailed)
        elif self.provider == "gemini":
            return self._generate_gemini_answer(question, context, language, simple, detailed)
        else:
            logger.warning(f"Unknown provider {self.provider}, using mock")
            return self._generate_mock_answer(question, context, language, simple, detailed)
    
    def _generate_openai_answer(self,
                               question: str,
                               context: str,
                               language: str,
                               simple: bool,
                               detailed: bool) -> Dict[str, Any]:
        """Generate answer using OpenAI API."""
        if not self.api_key:
            logger.warning("OpenAI API key not configured, using mock")
            return self._generate_mock_answer(question, context, language, simple, detailed)
        
        try:
            import openai
            openai.api_key = self.api_key
            
            system_prompt = self._build_system_prompt(language, simple, detailed)
            user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=1000
            )
            
            answer_text = response.choices[0].message.content
            
            return {
                "simple_answer": answer_text,
                "detailed_answer": None,
                "reason_for_answer": "Generated using OpenAI LLM",
                "provider": "openai",
                "model": self.model
            }
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            return self._generate_mock_answer(question, context, language, simple, detailed)
    
    def _generate_gemini_answer(self,
                               question: str,
                               context: str,
                               language: str,
                               simple: bool,
                               detailed: bool) -> Dict[str, Any]:
        """Generate answer using Google Gemini API."""
        if not self.api_key:
            logger.warning("Gemini API key not configured, using mock")
            return self._generate_mock_answer(question, context, language, simple, detailed)
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            system_prompt = self._build_system_prompt(language, simple, detailed)
            user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
            
            model = genai.GenerativeModel(self.model, system_instruction=system_prompt)
            response = model.generate_content(user_prompt)
            
            return {
                "simple_answer": response.text,
                "detailed_answer": None,
                "reason_for_answer": "Generated using Google Gemini API",
                "provider": "gemini",
                "model": self.model
            }
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}")
            return self._generate_mock_answer(question, context, language, simple, detailed)
    
    def _generate_mock_answer(self,
                             question: str,
                             context: str,
                             language: str,
                             simple: bool,
                             detailed: bool) -> Dict[str, Any]:
        """Generate a mock answer for demo purposes."""
        # Extract key concepts from context
        sentences = context.split('.')
        key_sentences = [s.strip() for s in sentences[:3] if s.strip()]
        
        if language == "hi":
            simple_answer = f"आपका सवाल: '{question}'\n\nजवाब: {' '.join(key_sentences[:2])}। यह हमारे पाठ्यक्रम में महत्वपूर्ण विषय है।"
            detailed_answer = f"विस्तृत जवाब: {' '.join(key_sentences)}। अधिक जानने के लिए अपने पाठ्यक्रम में देखें।"
        else:
            simple_answer = f"Based on the textbook:\n\n{' '.join(key_sentences[:2])} This is an important concept in your curriculum."
            detailed_answer = f"Detailed explanation:\n\n{' '.join(key_sentences)} Understanding this concept will help you solve more problems."
        
        return {
            "simple_answer": simple_answer,
            "detailed_answer": detailed_answer if detailed else None,
            "reason_for_answer": "Generated using mock LLM (demo mode)",
            "provider": "mock",
            "model": "mock_model",
            "language": language
        }
    
    def _build_system_prompt(self, language: str, simple: bool, detailed: bool) -> str:
        """Build the system prompt for the LLM."""
        if language == "hi":
            base_prompt = "आप एक शिक्षक हैं जो भारतीय स्कूल के पाठ्यक्रम में दिए गए विषयों की व्याख्या करते हैं।"
        else:
            base_prompt = "You are a helpful tutor explaining concepts from Indian school textbooks. "
        
        base_prompt += "\n\nAnswer requirements:\n"
        base_prompt += "1. Use only the provided context\n"
        base_prompt += "2. Keep answers clear and appropriate for school students\n"
        base_prompt += "3. Use simple language\n"
        base_prompt += "4. Include examples if possible\n"
        
        if simple and not detailed:
            base_prompt += "5. Keep answer brief (2-3 sentences)\n"
        
        return base_prompt
    
    def supports_language(self, language: str) -> bool:
        """Check if language is supported."""
        return language in ["en", "hi"]
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the LLM generator."""
        return {
            "provider": self.provider,
            "model": self.model if self.provider != "mock" else "mock_model",
            "temperature": self.temperature,
            "has_api_key": bool(self.api_key),
            "supported_languages": ["en", "hi"]
        }
