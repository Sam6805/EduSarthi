    def generate_answer(self,
                        question: str,
                        context: str,
                        language: str = "en",
                        simple: bool = True,
                        detailed: bool = False) -> Dict[str, Any]:
        """Generate answer — Gemini first, then Claude, then offline."""

        # 1. Try Gemini (your configured provider)
        if self.provider == "gemini" and self.api_key:
            result = _call_gemini_api(question, context, language, self.api_key, self.model)
            if result:
                logger.info("Answer generated via Gemini API")
                return result

        # 2. Try Claude (if key available)
        if self.claude_api_key:
            result = _call_claude_api(question, context, language, self.claude_api_key)
            if result:
                logger.info("Answer generated via Claude API")
                return result

        # 3. Try OpenAI (if configured)
        if self.provider == "openai" and self.api_key:
            result = _call_openai_api(question, context, language, self.api_key, self.model)
            if result:
                logger.info("Answer generated via OpenAI API")
                return result

        # 4. Offline KB match
        result = _find_offline_answer(question, language)
        if result:
            logger.info("Answer from offline KB")
            return result

        # 5. Offline context extraction (last resort)
        logger.info("Using offline context extraction")
        return _generic_offline_answer(question, context, language)
