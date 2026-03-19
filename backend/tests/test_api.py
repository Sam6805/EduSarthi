"""Simple test file for the Education Tutor API."""

import asyncio
import json
from pathlib import Path

# Test ingestion
from app.core.ingestion_pipeline import IngestionPipeline


async def test_ingestion():
    """Test PDF ingestion pipeline."""
    print("=" * 80)
    print("TEST 1: Ingestion Pipeline")
    print("=" * 80)
    
    pipeline = IngestionPipeline()
    result = pipeline.process_demo_textbook()
    
    print(f"\nIngestion Result:")
    print(json.dumps(result, indent=2))
    
    assert result["status"] == "success"
    assert result["chapters_extracted"] > 0
    assert result["chunks_created"] > 0
    print("\n✓ Ingestion test passed")
    
    return result["textbook_id"]


async def test_retrieval(textbook_id: str):
    """Test retrieval and ranking."""
    print("\n" + "=" * 80)
    print("TEST 2: Retrieval Pipeline")
    print("=" * 80)
    
    from app.core.query_handler import QueryHandler
    from app.schemas import QueryRequest
    
    handler = QueryHandler()
    
    request = QueryRequest(
        question="What is photosynthesis?",
        textbook_id=textbook_id,
        language="en",
        use_pruning=False  # Test without pruning first
    )
    
    response = handler.handle_query(request)
    
    print(f"\nQuestion: {response.question}")
    print(f"Answer: {response.answer.simple_answer[:200]}...")
    print(f"Retrieved Chunks: {response.retrieved_chunks_count}")
    print(f"Source Chapter: {response.answer.source_chapter}")
    print(f"Latency: {response.total_latency_ms:.2f}ms")
    
    assert response.retrieved_chunks_count > 0
    print("\n✓ Retrieval test passed")


async def test_pruning(textbook_id: str):
    """Test context pruning."""
    print("\n" + "=" * 80)
    print("TEST 3: Context Pruning")
    print("=" * 80)
    
    from app.core.query_handler import QueryHandler
    from app.schemas import QueryRequest
    
    handler = QueryHandler()
    
    # Test with pruning
    request = QueryRequest(
        question="What are the types of materials?",
        textbook_id=textbook_id,
        language="en",
        use_pruning=True
    )
    
    response = handler.handle_query(request)
    
    print(f"\nQuestion: {response.question}")
    print(f"Tokens Before Pruning: {response.token_estimate_before_pruning}")
    print(f"Tokens After Pruning: {response.token_estimate_after_pruning}")
    print(f"Token Reduction: {response.token_reduction_percentage:.1f}%")
    print(f"Chunks Retrieved: {response.retrieved_chunks_count}")
    print(f"Chunks Pruned: {response.pruned_chunks_count}")
    
    assert response.token_estimate_after_pruning <= response.token_estimate_before_pruning
    print("\n✓ Pruning test passed")


async def test_metrics():
    """Test metrics collection."""
    print("\n" + "=" * 80)
    print("TEST 4: Metrics")
    print("=" * 80)
    
    from app.core.query_handler import QueryHandler
    
    handler = QueryHandler()
    metrics = handler.get_metrics_summary()
    
    print(f"\nMetrics Summary:")
    print(json.dumps(metrics, indent=2))
    
    assert metrics["total_queries"] >= 0
    print("\n✓ Metrics test passed")


async def test_health_check():
    """Test health check endpoint."""
    print("\n" + "=" * 80)
    print("TEST 5: Health Check")
    print("=" * 80)
    
    from app.api.routes_health import health_check
    
    health = await health_check()
    
    print(f"\nHealth Status: {health['status']}")
    print(f"Version: {health['version']}")
    print(f"Components: {json.dumps(health['components'], indent=2)}")
    
    assert health["status"] in ["healthy", "degraded"]
    print("\n✓ Health check test passed")


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("🚀 EDUCATION TUTOR BACKEND - TEST SUITE")
    print("=" * 80 + "\n")
    
    try:
        # Test 1: Ingestion
        textbook_id = await test_ingestion()
        
        # Test 2: Retrieval
        await test_retrieval(textbook_id)
        
        # Test 3: Pruning
        await test_pruning(textbook_id)
        
        # Test 4: Metrics
        await test_metrics()
        
        # Test 5: Health
        await test_health_check()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
