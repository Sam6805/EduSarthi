    if from_pdf and context_trimmed:
        prompt = (
            f"You are EduSarthi, a friendly AI tutor. {lang_note}\n\n"
            "Use ONLY the following textbook context to answer.\n\n"
            f"Context:\n{context_trimmed}\n\nQuestion: {question}\n\n"
            "1. Simple explanation (2-3 sentences)\n2. Detailed explanation (4-5 sentences)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    elif context_trimmed:
        # Sample textbook — curriculum context provided, answer based on it
        prompt = (
            f"You are EduSarthi, a friendly AI tutor for Indian school students. {lang_note}\n\n"
            f"{context_trimmed}\n\n"
            f"Student question: {question}\n\n"
            "Give a curriculum-aligned answer appropriate for the class level mentioned.\n"
            "1. Simple explanation (2-3 sentences, easy for a student)\n"
            "2. Detailed explanation (4-5 sentences with examples)\n\n"
            'Reply ONLY with JSON: {"simple_answer": "...", "detailed_answer": "..."}'
        )
    else: