"""Script to compare baseline vs context-pruned retrieval pipelines."""

import json
import time
from pathlib import Path
from typing import List, Dict, Any

from app.core.ingestion_pipeline import IngestionPipeline
from app.core.query_handler import QueryHandler
from app.services.retriever import Retriever
from app.services.context_pruner import ContextPruner
from app.utils.helpers import setup_logger, estimate_tokens

logger = setup_logger(__name__)


SAMPLE_QUESTIONS = [
    {
        "question": "What is photosynthesis?",
        "expected_chapter": "Food and Digestion"
    },
    {
        "question": "How do plants make food?",
        "expected_chapter": "Food and Digestion"
    },
    {
        "question": "What are natural materials?",
        "expected_chapter": "Materials and Their Properties"
    },
    {
        "question": "Explain the types of materials",
        "expected_chapter": "Materials and Their Properties"
    },
    {
        "question": "What is a habitat?",
        "expected_chapter": "Living Organisms and Their Habitats"
    },
]


def evaluate_baseline_vs_pruned():
    """
    Evaluate both retrieval approaches:
    1. Baseline: All retrieved chunks
    2. Pruned: After context pruning
    """
    logger.info("=== Starting Baseline vs Pruned Evaluation ===")
    
    # Initialize pipeline
    ingestion = IngestionPipeline()
    query_handler = QueryHandler()
    pruner = ContextPruner()
    
    # Create demo textbook if needed
    textbooks = ingestion.get_textbooks()
    if not textbooks:
        logger.info("Ingesting demo textbook...")
        ingestion.process_demo_textbook()
    
    results = []
    
    # Run each question
    for i, q_data in enumerate(SAMPLE_QUESTIONS, 1):
        question = q_data["question"]
        logger.info(f"\n[{i}/{len(SAMPLE_QUESTIONS)}] Question: {question}")
        
        # Retrieve chunks
        retrieval_result = query_handler.retriever.retrieve_with_pruning(
            question=question,
            apply_pruning=True
        )
        
        baseline_chunks = retrieval_result["retrieved_chunks"]
        pruned_chunks = retrieval_result["pruned_chunks"]
        
        # Calculate metrics
        baseline_tokens = estimate_tokens(" ".join([c.get("content", "") for c in baseline_chunks]))
        pruned_tokens = estimate_tokens(" ".join([c.get("content", "") for c in pruned_chunks]))
        
        result = {
            "question": question,
            "expected_chapter": q_data.get("expected_chapter"),
            
            # Baseline metrics
            "baseline": {
                "chunks_retrieved": len(baseline_chunks),
                "tokens": baseline_tokens,
            },
            
            # Pruned metrics
            "pruned": {
                "chunks_kept": len(pruned_chunks),
                "tokens": pruned_tokens,
            },
            
            # Improvement
            "improvement": {
                "chunks_reduction": len(baseline_chunks) - len(pruned_chunks),
                "chunks_reduction_pct": round((1 - len(pruned_chunks) / len(baseline_chunks)) * 100, 2) if baseline_chunks else 0,
                "token_reduction": baseline_tokens - pruned_tokens,
                "token_reduction_pct": round((1 - pruned_tokens / baseline_tokens) * 100, 2) if baseline_tokens > 0 else 0,
            },
            
            "latencies": {
                "retrieval_ms": retrieval_result["retrieval_latency"],
                "pruning_ms": retrieval_result["pruning_latency"],
                "total_ms": retrieval_result["total_latency"]
            }
        }
        
        results.append(result)
        
        # Print summary
        logger.info(f"  Baseline: {result['baseline']['chunks_retrieved']} chunks, {result['baseline']['tokens']} tokens")
        logger.info(f"  Pruned:   {result['pruned']['chunks_kept']} chunks, {result['pruned']['tokens']} tokens")
        logger.info(f"  Reduction: {result['improvement']['chunks_reduction']} chunks ({result['improvement']['chunks_reduction_pct']}%), "
                   f"{result['improvement']['token_reduction']} tokens ({result['improvement']['token_reduction_pct']}%)")
    
    # Save results
    save_results(results)
    print_summary(results)
    
    return results


def save_results(results: List[Dict[str, Any]]) -> Path:
    """Save evaluation results to JSON."""
    output_path = Path(__file__).parent / "results.json"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"\nResults saved to {output_path}")
    return output_path


def print_summary(results: List[Dict[str, Any]]) -> None:
    """Print evaluation summary."""
    if not results:
        return
    
    print("\n" + "="*80)
    print("EVALUATION SUMMARY: Baseline vs Context Pruning")
    print("="*80)
    
    # Aggregate metrics
    total_baseline_chunks = sum(r["baseline"]["chunks_retrieved"] for r in results)
    total_pruned_chunks = sum(r["pruned"]["chunks_kept"] for r in results)
    total_baseline_tokens = sum(r["baseline"]["tokens"] for r in results)
    total_pruned_tokens = sum(r["pruned"]["tokens"] for r in results)
    total_chunk_reduction = total_baseline_chunks - total_pruned_chunks
    total_token_reduction = total_baseline_tokens - total_pruned_tokens
    
    avg_chunk_reduction_pct = (1 - total_pruned_chunks / total_baseline_chunks) * 100 if total_baseline_chunks > 0 else 0
    avg_token_reduction_pct = (1 - total_pruned_tokens / total_baseline_tokens) * 100 if total_baseline_tokens > 0 else 0
    
    print(f"\nTotal Questions Evaluated: {len(results)}")
    print(f"\nChunks:")
    print(f"  Baseline Total: {total_baseline_chunks}")
    print(f"  After Pruning: {total_pruned_chunks}")
    print(f"  Reduction: {total_chunk_reduction} ({avg_chunk_reduction_pct:.1f}%)")
    
    print(f"\nTokens:")
    print(f"  Baseline Total: {total_baseline_tokens}")
    print(f"  After Pruning: {total_pruned_tokens}")
    print(f"  Reduction: {total_token_reduction} ({avg_token_reduction_pct:.1f}%)")
    
    print(f"\nAverage per question:")
    print(f"  Chunks: {total_baseline_chunks/len(results):.1f} → {total_pruned_chunks/len(results):.1f}")
    print(f"  Tokens: {total_baseline_tokens/len(results):.1f} → {total_pruned_tokens/len(results):.1f}")
    
    print("\n" + "="*80)
    
    # Print individual results
    print("\nDetailed Results:")
    print("-"*80)
    for i, r in enumerate(results, 1):
        print(f"\n{i}. {r['question']}")
        print(f"   Baseline: {r['baseline']['chunks_retrieved']} chunks ({r['baseline']['tokens']} tokens)")
        print(f"   Pruned:   {r['pruned']['chunks_kept']} chunks ({r['pruned']['tokens']} tokens)")
        print(f"   Saved:    {r['improvement']['token_reduction']} tokens ({r['improvement']['token_reduction_pct']:.1f}%)")


if __name__ == "__main__":
    results = evaluate_baseline_vs_pruned()
