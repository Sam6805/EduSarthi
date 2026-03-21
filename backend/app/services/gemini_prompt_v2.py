def _call_gemini_api(question: str, context: str, language: str,
                     api_key: str, model: str,
                     from_pdf: bool = False) -> Optional[Dict[str, Any]]:
    if not api_key:
        return None

    lang_note = "Respond ONLY in Hindi (Devanagari script)." if language == "hi" else "Respond in English."
    context_trimmed = context[:2000] if len(context) > 2000 else context

    if from_pdf and context_trimmed:
        # Answer strictly from uploaded PDF
        prompt = (
            f"You are EduSarthi, a friendly AI tutor. {lang_note}\n\n"
            "Use ONLY the following textbook context to answer.\n\n"
            f"Context:\n{context_trimmed}\n\nQuestion: {question}\n\n"
            "1. Simple explanation (2-3 sentences)\n"
            "2. Detailed explanation (4-5 sentences)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    elif context_trimmed:
        # Sample textbook — curriculum info as context, answer aligned to class level
        prompt = (
            f"You are EduSarthi, a friendly AI tutor for Indian school students. {lang_note}\n\n"
            f"{context_trimmed}\n\n"
            f"Student question: {question}\n\n"
            "Give a curriculum-aligned answer appropriate for the class level above.\n"
            "1. Simple explanation (2-3 sentences, very easy for the student)\n"
            "2. Detailed explanation (4-5 sentences with examples)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    else:
        # No context at all — general answer with note
        not_found = (
            "यह प्रश्न आपकी पाठ्यपुस्तक में नहीं मिला, लेकिन सामान्य उत्तर:"
            if language == "hi"
            else "This topic wasn't found in your textbook, but here's a general answer:"
        )
        prompt = (
            f"You are EduSarthi, a friendly AI tutor for Indian school students. {lang_note}\n\n"
            f"Question: {question}\n\n"
            f"Start simple_answer with: '{not_found}'\n"
            "Then give a helpful general educational answer.\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )