#!/usr/bin/env python3
"""
Simple test script for the new memory-efficient chunking functions.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ingest.chunker import (
    chunk_large_text_streaming, 
    chunk_large_text_batched,
    count_tokens
)


def test_streaming_chunker():
    """Test the streaming chunker with a large text sample."""
    print("🧪 Testing Streaming Chunker")
    print("=" * 40)
    
    # Create a large text sample (simulating welcome_english.pdf)
    sample_text = ""
    for i in range(1000):  # 1000 lines
        sample_text += f"This is line number {i} with some additional content to make it longer. "
        sample_text += f"It contains information about NYC services and various programs available to residents. "
        sample_text += f"Line {i} continues with more details about eligibility requirements and application processes.\n"
    
    print(f"📝 Sample text: {len(sample_text)} characters, {count_tokens(sample_text)} tokens")
    
    # Test streaming chunker
    chunk_size = 200
    overlap = 25
    
    print(f"🔪 Chunking with size={chunk_size}, overlap={overlap}")
    
    chunks = list(chunk_large_text_streaming(sample_text, chunk_size, overlap))
    print(f"✅ Created {len(chunks)} chunks")
    
    # Validate chunks
    max_tokens = 0
    min_tokens = float('inf')
    total_tokens = 0
    
    for i, chunk in enumerate(chunks[:5]):  # Show first 5 chunks
        token_count = count_tokens(chunk)
        max_tokens = max(max_tokens, token_count)
        min_tokens = min(min_tokens, token_count)
        total_tokens += token_count
        
        print(f"  Chunk {i+1}: {token_count} tokens, {len(chunk)} chars")
        print(f"    Preview: {chunk[:100]}...")
    
    if len(chunks) > 5:
        print(f"  ... and {len(chunks) - 5} more chunks")
    
    print(f"\n📊 Chunk Statistics:")
    print(f"  Total chunks: {len(chunks)}")
    print(f"  Max tokens per chunk: {max_tokens}")
    print(f"  Min tokens per chunk: {min_tokens}")
    print(f"  Total tokens: {total_tokens}")
    print(f"  Average tokens per chunk: {total_tokens / len(chunks):.1f}")
    
    # Validate that no chunk exceeds the limit
    oversized_chunks = [i for i, chunk in enumerate(chunks) if count_tokens(chunk) > chunk_size]
    if oversized_chunks:
        print(f"❌ Found {len(oversized_chunks)} chunks that exceed {chunk_size} tokens")
        for i in oversized_chunks:
            print(f"    Chunk {i+1}: {count_tokens(chunks[i])} tokens")
    else:
        print(f"✅ All chunks are within {chunk_size} token limit")


def test_batched_chunker():
    """Test the batched chunker."""
    print("\n🧪 Testing Batched Chunker")
    print("=" * 40)
    
    # Create sample text
    sample_text = ""
    for i in range(500):  # 500 lines
        sample_text += f"Sample line {i} with content about NYC services and programs. "
        sample_text += f"This line provides information about eligibility and application processes.\n"
    
    print(f"📝 Sample text: {len(sample_text)} characters, {count_tokens(sample_text)} tokens")
    
    # Test batched chunker
    chunk_size = 150
    overlap = 20
    batch_size = 5
    
    print(f"🔪 Chunking with size={chunk_size}, overlap={overlap}, batch_size={batch_size}")
    
    batches = list(chunk_large_text_batched(sample_text, chunk_size, overlap, batch_size))
    print(f"✅ Created {len(batches)} batches")
    
    total_chunks = sum(len(batch) for batch in batches)
    print(f"📊 Total chunks across all batches: {total_chunks}")
    
    for i, batch in enumerate(batches):
        print(f"  Batch {i+1}: {len(batch)} chunks")
        for j, chunk in enumerate(batch):
            token_count = count_tokens(chunk)
            print(f"    Chunk {j+1}: {token_count} tokens")


def test_memory_efficiency():
    """Test that chunking doesn't consume excessive memory."""
    print("\n🧪 Testing Memory Efficiency")
    print("=" * 40)
    
    import psutil
    import os
    
    def get_memory():
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    initial_memory = get_memory()
    print(f"💾 Initial memory: {initial_memory:.1f}MB")
    
    # Create very large text
    large_text = ""
    for i in range(2000):  # 2000 lines
        large_text += f"This is a very long line number {i} with extensive content about NYC services. "
        large_text += f"It includes detailed information about various programs, eligibility requirements, "
        large_text += f"application processes, documentation needed, and contact information for assistance.\n"
    
    print(f"📝 Large text created: {len(large_text)} characters, {count_tokens(large_text)} tokens")
    
    # Process with streaming chunker
    chunk_count = 0
    for chunk in chunk_large_text_streaming(large_text, chunk_size=100, overlap=10):
        chunk_count += 1
        if chunk_count % 100 == 0:
            current_memory = get_memory()
            print(f"  Processed {chunk_count} chunks, memory: {current_memory:.1f}MB")
    
    final_memory = get_memory()
    print(f"✅ Final memory: {final_memory:.1f}MB")
    print(f"📊 Memory change: {final_memory - initial_memory:+.1f}MB")
    print(f"🔪 Total chunks processed: {chunk_count}")


if __name__ == "__main__":
    print("🚀 NYC Services GPT - Chunker Testing")
    print("=" * 50)
    
    try:
        test_streaming_chunker()
        test_batched_chunker()
        test_memory_efficiency()
        
        print("\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
