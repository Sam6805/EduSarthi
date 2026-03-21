    def generate_answer(self,
                        question: str,
                        context: str,
                        language: str = "en",
                        simple: bool = True,
                        detailed: bool = False,
                        from_pdf: bool = False) -> Dict[str, Any]:
        """
        Generate answer with 3 smart modes:
        - from_pdf=True  + context  → answer from PDF via Gemini
        - from_pdf=False + no ctx   → general Gemini answer (question unrelated to book)
        - no API                    → offline KB / context extraction
        """

        # 1. Gemini (pure HTTP — no package needed)
        if self.provider == "gemini" and self.api_key:
            result = _call_gemini_api(
                question, context, language,
                self.api_key, self.model,
                from_pdf=from_pdf
            )
            if result:
                logger.info(f"Answer via Gemini ({'PDF context' if from_pdf else 'general'}) ✓")
                return result
            logger.warning("Gemini failed — trying fallbacks")

        # 2. Claude (pure HTTP)
        if self.claude_api_key:
            result = _call_claude_api(question, context, language, self.claude_api_key)
            if result:
                logger.info("Answer via Claude ✓")
                return result

        # 3. Offline KB
        result = _find_offline_answer(question, language)
        if result:
            logger.info("Answer from offline KB ✓")
            return result

        # 4. Offline context extraction
        logger.info("Using offline context extraction ✓")
        return _generic_offline_answer(question, context, language)

    def supports_language(self, language: str) -> bool:
        return language in ["en", "hi"]

    def get_info(self) -> Dict[str, Any]:
        return {
            "primary_provider": self.provider,
            "gemini_configured": self.provider == "gemini" and bool(self.api_key),
            "claude_configured": bool(self.claude_api_key),
            "model": self.model,
            "offline_kb_topics": list(OFFLINE_KB.keys()),
            "supported_languages": ["en", "hi"],
        }
