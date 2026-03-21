"""Query handler — passes textbook context to LLM even for sample textbooks."""

from typing import Dict, Any
import time

from app.services.retriever import Retriever
from app.services.context_pruner import ContextPruner
from app.services.llm_generator import LLMGenerator
from app.utils.helpers import setup_logger, estimate_tokens
from app.schemas import QueryRequest, QueryResponse, GeneratedAnswer, RetrievedChunk

logger = setup_logger(__name__)

# ── Sample textbook metadata (used when no PDF is uploaded) ───────────────
SAMPLE_TEXTBOOKS = {
    "class6-science": {
        "name": "Class 6 Science (NCERT)",
        "subject": "Science",
        "class": "6",
        "topics": "food, sorting materials, fibre to fabric, living organisms, body movements, plants, motion, light, electricity, magnets, water, air"
    },
    "class7-geography": {
        "name": "Class 7 Geography (NCERT)",
        "subject": "Geography",
        "class": "7",
        "topics": "environment, inside earth, air, water, natural vegetation, human environment, life in deserts, cold desert, tribes"
    },
    "class8-mathematics": {
        "name": "Class 8 Mathematics (NCERT)",
        "subject": "Mathematics",
        "class": "8",
        "topics": "rational numbers, linear equations, quadrilaterals, data handling, squares, cubes, direct proportion, algebraic expressions, mensuration, exponents, factorisation, graphs, introduction to graphs"
    },
    "class8-science": {
        "name": "Class 8 Science (NCERT)",
        "subject": "Science",
        "class": "8",
        "topics": "crop production, microorganisms, materials metals non-metals, coal petroleum, combustion, plants reproduction, animal reproduction, force pressure, friction, sound, chemical effects, natural phenomena, light, stars planets, pollution"
    },
    "class9-history": {
        "name": "Class 9 History (NCERT)",
        "subject": "History",
        "class": "9",
        "topics": "French Revolution, Russian Revolution, Nazism, forest society, pastoralists, peasants, sports, clothing"
    },
    "class10-english": {
        "name": "Class 10 English (NCERT)",
        "subject": "English",
        "class": "10",
        "topics": "prose, poetry, grammar, writing skills, letter writing, comprehension passages, formal letters, notice writing"
    },
}


def _build_sample_context(textbook_id: str, question: str) -> str:
    """Build a descriptive context string for sample textbooks without a PDF."""
    info = SAMPLE_TEXTBOOKS.get(textbook_id)
    if not info:
        return ""
    return (
        f"Textbook: {info['name']}\n"
        f"Class: {info['class']}\n"
        f"Subject: {info['subject']}\n"
        f"Curriculum topics: {info['topics']}\n\n"
        f"Answer the student's question based on the {info['name']} curriculum."
    )


class QueryHandler:
    """Handle questions end-to-end: retrieve → prune → generate."""

    def __init__(self):
        self.retriever = Retriever()
        self.pruner = ContextPruner()
        self.generator = LLMGenerator()
        self.query_history = []

    def handle_query(self, request: QueryRequest) -> QueryResponse:
        pipeline_start = time.time()
        logger.info(f"Query: '{request.question[:60]}' | book: {request.textbook_id}")

        # ── Step 1: Try FAISS retrieval ───────────────────────────────────
        try:
            stats = self.retriever.get_vector_store_stats()
            has_index = stats.get("total_chunks", 0) > 0
        except Exception:
            has_index = False

        retrieved_chunks = []
        pruned_chunks = []
        retrieval_latency = 0.0
        pruning_latency = 0.0
        from_pdf = False

        if has_index:
            retrieval_result = self.retriever.retrieve_with_pruning(
                question=request.question,
                textbook_id=request.textbook_id,
                apply_pruning=request.use_pruning,
            )
            retrieved_chunks = retrieval_result["retrieved_chunks"]
            pruned_chunks = retrieval_result["pruned_chunks"]
            retrieval_latency = retrieval_result["retrieval_latency"]
            pruning_latency = retrieval_result["pruning_latency"]
            from_pdf = len(pruned_chunks) > 0
            logger.info(f"FAISS: {len(retrieved_chunks)} retrieved → {len(pruned_chunks)} pruned")

        # ── Step 2: Build context ─────────────────────────────────────────
        if pruned_chunks:
            # Real PDF context — best case
            context = self.pruner.build_pruned_context(pruned_chunks, include_metadata=True)
            logger.info("Using PDF context ✓")
        elif request.textbook_id in SAMPLE_TEXTBOOKS:
            # Sample textbook — build curriculum context so Gemini answers correctly
            context = _build_sample_context(request.textbook_id, request.question)
            logger.info(f"Using sample textbook context for {request.textbook_id} ✓")
        else:
            # Uploaded PDF but not indexed yet, or unknown book
            context = ""
            logger.info("No context available — general answer mode")

        # ── Step 3: Token estimates ───────────────────────────────────────
        tokens_before = estimate_tokens(self._chunks_to_text(retrieved_chunks))
        tokens_after  = estimate_tokens(self._chunks_to_text(pruned_chunks))

        # ── Step 4: Generate answer ───────────────────────────────────────
        gen_start = time.time()
        answer_data = self.generator.generate_answer(
            question=request.question,
            context=context,
            language=request.language,
            from_pdf=from_pdf,
        )
        generation_latency = (time.time() - gen_start) * 1000

        # ── Step 5: Source info ───────────────────────────────────────────
        source_chapter = answer_data.get("source_chapter")
        source_pages: set = set()
        for chunk in pruned_chunks[:3]:
            if not source_chapter and chunk.get("chapter_title"):
                source_chapter = chunk["chapter_title"]
            if chunk.get("page_number"):
                source_pages.add(chunk["page_number"])

        # ── Step 6: Build response ────────────────────────────────────────
        response = QueryResponse(
            question=request.question,
            answer=GeneratedAnswer(
                simple_answer=answer_data.get("simple_answer", ""),
                detailed_answer=answer_data.get("detailed_answer"),
                source_chapter=source_chapter,
                source_pages=sorted(list(source_pages)),
            ),
            retrieved_chunks_count=len(retrieved_chunks),
            retrieved_chunks=self._format_chunks_for_response(retrieved_chunks[:5]),
            pruned_chunks_count=len(retrieved_chunks) - len(pruned_chunks),
            pruning_applied=request.use_pruning,
            token_estimate_before_pruning=tokens_before,
            token_estimate_after_pruning=tokens_after,
            token_reduction_percentage=(
                (1 - tokens_after / tokens_before) * 100 if tokens_before > 0 else 0.0
            ),
            retrieval_latency_ms=retrieval_latency,
            pruning_latency_ms=pruning_latency,
            generation_latency_ms=generation_latency,
            total_latency_ms=(time.time() - pipeline_start) * 1000,
            textbook_used=request.textbook_id or "all",
        )

        self._record_query(response)
        return response

    # ── Helpers ───────────────────────────────────────────────────────────
    def _chunks_to_text(self, chunks):
        return " ".join(c.get("content", "") for c in chunks)

    def _format_chunks_for_response(self, chunks):
        result = []
        for chunk in chunks:
            result.append(RetrievedChunk(
                chunk_id=chunk.get("chunk_id", ""),
                textbook_name=chunk.get("textbook_name", ""),
                chapter_title=chunk.get("chapter_title"),
                page_number=chunk.get("page_number"),
                content=chunk.get("content_preview", chunk.get("content", ""))[:300],
                relevance_score=chunk.get("relevance_score", 0.0),
                is_pruned=False,
            ))
        return result

    def _record_query(self, response: QueryResponse):
        self.query_history.append({
            "question": response.question,
            "retrieved_chunks": response.retrieved_chunks_count,
            "pruned_chunks": response.pruned_chunks_count,
            "tokens_before": response.token_estimate_before_pruning,
            "tokens_after": response.token_estimate_after_pruning,
            "reduction_percent": response.token_reduction_percentage,
            "latency_ms": response.total_latency_ms,
        })

    def get_metrics_summary(self) -> Dict[str, Any]:
        if not self.query_history:
            return {"total_queries": 0, "avg_chunks_retrieved": 0,
                    "avg_chunks_pruned": 0, "avg_token_reduction": 0, "total_tokens_saved": 0}
        total = len(self.query_history)
        return {
            "total_queries": total,
            "avg_retrieved_chunks": round(sum(q["retrieved_chunks"] for q in self.query_history) / total, 2),
            "avg_pruned_chunks": round(sum(q["pruned_chunks"] for q in self.query_history) / total, 2),
            "avg_token_reduction_percentage": round(sum(q["reduction_percent"] for q in self.query_history) / total, 2),
            "total_tokens_saved": sum(q["tokens_before"] - q["tokens_after"] for q in self.query_history),
            "recent_queries": self.query_history[-5:],
        }

    def get_vector_store_stats(self):
        return self.retriever.get_vector_store_stats()
